[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent),
    [switch]$SkipInstallSmoke
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path -LiteralPath $Root).Path

function Assert {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Invoke-RefSync {
    param([string]$Repository, [string]$Extension, [string]$Mode)
    $script = Join-Path $Repository "scripts/sync-refs.$Extension"
    $PSNativeCommandUseErrorActionPreference = $false
    $output = if ($Extension -eq "ps1") {
        $executable = Join-Path $PSHOME $(if ($IsWindows) { "pwsh.exe" } else { "pwsh" })
        & $executable -NoLogo -NoProfile -File $script $Mode 2>&1
    } else {
        & bash $script $Mode 2>&1
    }
    return @{ ExitCode = $LASTEXITCODE; Output = ($output -join "`n") }
}

function Read-Metadata {
    param([string]$Path)
    $content = Get-Content -Raw -LiteralPath $Path
    $match = [regex]::Match($content, '(?s)\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)')
    Assert $match.Success "Missing frontmatter: $Path"
    $fields = @{}
    foreach ($line in ($match.Groups[1].Value -split '\r?\n')) {
        if ($line -match '^([\w-]+):\s*(.*)$') { $fields[$Matches[1]] = $Matches[2].Trim() }
    }
    return $fields
}

function Assert-Links {
    param([string[]]$Paths)
    foreach ($path in $Paths) {
        if ([IO.Path]::GetExtension($path) -ne ".md") { continue }
        $content = Get-Content -Raw -LiteralPath $path
        foreach ($link in [regex]::Matches($content, '\[[^\]]*\]\(([^)\r\n]+)\)')) {
            $target = $link.Groups[1].Value
            if ($target -match '^(?:[a-z][a-z0-9+.-]*:|#)' -or $target -match '[<>$]') { continue }
            $target = [uri]::UnescapeDataString(($target -split '#', 2)[0])
            $resolved = Join-Path (Split-Path $path -Parent) $target
            Assert (Test-Path -LiteralPath $resolved) "Broken link in $path -> $target"
        }
    }
}

$managed = [ordered]@{}
foreach ($directory in @("agents", "skills", "dreamers/refs", "dreamers/templates", "instructions")) {
    $source = Join-Path $Root ".github/$directory"
    Assert (Test-Path -LiteralPath $source -PathType Container) "Missing package directory: $source"
    foreach ($file in Get-ChildItem -LiteralPath $source -File -Recurse | Sort-Object FullName) {
        $relative = [IO.Path]::GetRelativePath((Join-Path $Root ".github"), $file.FullName).Replace('\', '/')
        $managed[$relative] = $file.FullName
    }
}

foreach ($skill in Get-ChildItem (Join-Path $Root ".github/skills") -Directory) {
    $path = Join-Path $skill.FullName "SKILL.md"
    $meta = Read-Metadata $path
    Assert (([string]$meta.name).Trim('"', "'") -eq $skill.Name) "Skill name mismatch: $path"
    Assert (-not [string]::IsNullOrWhiteSpace($meta.description)) "Missing skill description: $path"
}
foreach ($agent in Get-ChildItem (Join-Path $Root ".github/agents") -Filter "*.agent.md") {
    $meta = Read-Metadata $agent.FullName
    Assert (([string]$meta.name).Trim('"', "'") -eq $agent.Name.Replace(".agent.md", "")) "Agent name mismatch: $agent"
    Assert (-not [string]::IsNullOrWhiteSpace($meta.description)) "Missing agent description: $agent"
}
foreach ($instruction in Get-ChildItem (Join-Path $Root ".github/instructions") -File) {
    Assert ($instruction.Name.EndsWith(".instructions.md")) "Instruction will not auto-load: $instruction"
    $meta = Read-Metadata $instruction.FullName
    Assert (-not [string]::IsNullOrWhiteSpace($meta.applyTo)) "Missing instruction applyTo: $instruction"
}
Assert-Links @($managed.Values)

$syncResult = Invoke-RefSync $Root "ps1" "-Verify"
Assert ($syncResult.ExitCode -eq 0) "Inlined reference verification failed: $($syncResult.Output)"

$catalog = Get-Content -Raw (Join-Path $Root ".github/catalog.json") | ConvertFrom-Json
$keys = @{}
foreach ($entry in @($catalog.items) + @($catalog.folderTargets)) {
    $key = "$($entry.type):$($entry.slug)"
    Assert (-not $keys.ContainsKey($key)) "Duplicate catalog entry: $key"
    $keys[$key] = $true
    $relative = if ($entry.type -eq "folder") { $entry.sourcePath } else { $entry.path }
    Assert (-not [string]::IsNullOrWhiteSpace($relative)) "Missing catalog path: $key"
    Assert (Test-Path -LiteralPath (Join-Path $Root $relative)) "Missing catalog target: $relative"
}
foreach ($collection in $catalog.collections) {
    Assert (Test-Path -LiteralPath (Join-Path $Root $collection.readmePath)) "Missing collection readme"
    foreach ($member in $collection.members) {
        Assert ($keys.ContainsKey("$($member.type):$($member.slug)")) "Unknown collection member: $($member.slug)"
    }
}

if (-not $SkipInstallSmoke) {
    $testRoot = Join-Path ([IO.Path]::GetTempPath()) ("dreamers package " + [guid]::NewGuid().ToString("N"))
    $installRoot = Join-Path $testRoot "copilot"
    New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

    function Write-Fixture {
        param([string]$Relative, [string]$Value)
        $path = Join-Path $installRoot $Relative
        New-Item -ItemType Directory -Path (Split-Path $path -Parent) -Force | Out-Null
        [IO.File]::WriteAllText($path, $Value)
    }

    function Snapshot {
        $result = [ordered]@{}
        foreach ($file in Get-ChildItem -LiteralPath $installRoot -Recurse -Force | Sort-Object FullName) {
            $relative = [IO.Path]::GetRelativePath($installRoot, $file.FullName)
            $result[$relative] = if ($file.PSIsContainer) { "directory" } else {
                (Get-FileHash -LiteralPath $file.FullName).Hash
            }
        }
        return ($result | ConvertTo-Json -Compress)
    }

    function Assert-Installed {
        foreach ($relative in $managed.Keys) {
            $target = Join-Path $installRoot $relative
            Assert (Test-Path -LiteralPath $target -PathType Leaf) "Install missed: $relative"
            Assert ((Get-FileHash -LiteralPath $target).Hash -eq
                (Get-FileHash -LiteralPath $managed[$relative]).Hash) "Install changed bytes: $relative"
        }
        Assert-Links @($managed.Keys | ForEach-Object { Join-Path $installRoot $_ })
    }

    $retired = @(
        "instructions/comment-rules.instructions.md",
        "instructions/git.instructions.md",
        "instructions/dreamers.laws.md",
        "dreamers/refs/agent-recovery.md",
        "skills/dreamers-full/SKILL.md",
        "skills/dreamers-full/readme.md"
    )
    $personal = @(
        "copilot-instructions.md",
        "instructions/personal.instructions.md",
        "agents/personal.agent.md",
        "skills/dreamers-lite/personal.md",
        "dreamers/refs/personal.md"
    )
    $sentinel = 'Personal data: $value, literal text, quotes "unchanged".'
    try {
        $syncExtensions = if ($IsWindows) { @("ps1") } else { @("ps1", "sh") }
        foreach ($extension in $syncExtensions) {
            $syncRoot = Join-Path $testRoot "sync $extension"
            $refs = Join-Path $syncRoot ".github/dreamers/refs"
            $consumers = Join-Path $syncRoot ".github/agents"
            $scripts = Join-Path $syncRoot "scripts"
            New-Item -ItemType Directory -Path $refs, $consumers, $scripts -Force | Out-Null
            Copy-Item (Join-Path $Root "scripts/sync-refs.$extension") $scripts

            $source = Join-Path $refs "sample.md"
            $consumer = Join-Path $consumers "example.agent.md"
            $stale = "<Sample>`nbefore`n<sample>`nexample café`n</sample>`nafter`n</Sample>`n"
            $expected = $stale.Replace("example café", "EXAMPLE café")
            [IO.File]::WriteAllText($source, "EXAMPLE café`n")
            [IO.File]::WriteAllText($consumer, $stale)

            $result = Invoke-RefSync $syncRoot $extension "-Verify"
            Assert ($result.ExitCode -eq 1) "$extension failed to detect reference drift: $($result.Output)"
            Assert ([IO.File]::ReadAllText($consumer) -ceq $stale) "$extension Verify wrote a consumer"

            $result = Invoke-RefSync $syncRoot $extension "-Sync"
            Assert ($result.ExitCode -eq 0) "$extension sync failed: $($result.Output)"
            Assert ([IO.File]::ReadAllText($consumer) -ceq $expected) "$extension sync changed surrounding content or missed source content"
            Assert ([IO.File]::ReadAllText($source) -ceq "EXAMPLE café`n") "$extension sync changed its source"
            $result = Invoke-RefSync $syncRoot $extension "-Verify"
            Assert ($result.ExitCode -eq 0) "$extension still reports drift after sync: $($result.Output)"
            $result = Invoke-RefSync $syncRoot $extension "-Sync"
            Assert ($result.ExitCode -eq 0) "$extension repeated sync failed: $($result.Output)"
            Assert ([IO.File]::ReadAllText($consumer) -ceq $expected) "$extension repeated sync was not idempotent"

            [IO.File]::WriteAllText($consumer, $stale)
            $malformed = Join-Path $consumers "malformed.agent.md"
            [IO.File]::WriteAllText((Join-Path $refs "second.md"), "second reference`n")
            $invalidBlocks = @(
                "<sample>`nunclosed`n",
                "</sample>`n",
                "<sample>`n</sample>`n<sample>`n</sample>`n",
                "<sample>`n<second>`n</second>`n</sample>`n"
            )
            foreach ($invalid in $invalidBlocks) {
                [IO.File]::WriteAllText($malformed, $invalid)
                $result = Invoke-RefSync $syncRoot $extension "-Sync"
                Assert ($result.ExitCode -eq 3) "$extension accepted malformed markers: $($result.Output)"
                Assert ([IO.File]::ReadAllText($consumer) -ceq $stale) "$extension partially wrote a malformed batch"
                Assert ([IO.File]::ReadAllText($malformed) -ceq $invalid) "$extension changed a malformed consumer"
            }
        }

        foreach ($relative in $personal) { Write-Fixture $relative $sentinel }
        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $installRoot 6>$null | Out-Null
        Assert-Installed

        Write-Fixture "skills/dreamers/SKILL.md" "Locally edited installed skill"
        foreach ($relative in $retired) { Write-Fixture $relative "Previous managed version" }
        $before = Snapshot
        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $installRoot 6>$null | Out-Null
        Assert ((Snapshot) -eq $before) "Non-force install changed existing files or removed legacy dependencies"

        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $installRoot -Force 6>$null | Out-Null
        Assert-Installed
        foreach ($relative in $retired) {
            Assert (-not (Test-Path -LiteralPath (Join-Path $installRoot $relative))) "Upgrade retained: $relative"
        }
        Assert (-not (Test-Path (Join-Path $installRoot "skills/dreamers-full"))) "Upgrade retained empty retired skill"

        $before = Snapshot
        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $installRoot -Force 6>$null | Out-Null
        Assert ((Snapshot) -eq $before) "Repeated force install was not idempotent"

        foreach ($relative in $retired) { Write-Fixture $relative "Previous managed version" }
        $personal += "skills/dreamers-full/personal.md"
        Write-Fixture "skills/dreamers-full/personal.md" $sentinel
        $before = Snapshot
        & (Join-Path $Root "Remove-Dreamers.ps1") -CopilotHome $installRoot -DryRun 6>$null | Out-Null
        Assert ((Snapshot) -eq $before) "DryRun changed the installation"

        & (Join-Path $Root "Remove-Dreamers.ps1") -CopilotHome $installRoot 6>$null | Out-Null
        foreach ($relative in @($managed.Keys) + $retired) {
            Assert (-not (Test-Path -LiteralPath (Join-Path $installRoot $relative))) "Uninstall retained: $relative"
        }
        foreach ($relative in $personal) {
            $path = Join-Path $installRoot $relative
            Assert (Test-Path -LiteralPath $path) "User file removed: $relative"
            Assert ([IO.File]::ReadAllText($path) -ceq $sentinel) "User file changed: $relative"
        }
        $before = Snapshot
        & (Join-Path $Root "Remove-Dreamers.ps1") -CopilotHome $installRoot 6>$null | Out-Null
        Assert ((Snapshot) -eq $before) "Repeated uninstall was not idempotent"
    }
    finally {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}

Write-Host "Dreamers package validation passed."
