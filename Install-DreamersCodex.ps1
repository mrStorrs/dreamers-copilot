<#
.SYNOPSIS
    Installs Dreamers Codex-managed files into the user's Codex home.

.DESCRIPTION
    Copies agents, skills, shared Dreamers resources, and instructions from
    this package into $env:CODEX_HOME, or ~/.codex when CODEX_HOME is not set.

    Only manages Dreamers-owned files. Does not remove user files from shared
    Codex directories.
#>
[CmdletBinding()]
param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$SourceRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$RepoRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("dreamers-codex-" + [guid]::NewGuid())
try {
    & (Join-Path $SourceRoot "scripts/Build-DreamersCodex.ps1") -OutputDirectory $RepoRoot
    & (Join-Path $SourceRoot "scripts/Update-CodexInstructions.ps1") -Action check -CodexHome $CodexHome


$legacyAgentNames = @("echo", "forge", "hone", "nova", "probe", "sage", "sentinel")
$legacyAgentTomlNames = @("bolt", "forge", "nova", "sage")
$obsoleteManagedFiles = @(
    "dreamers/instructions/comment-rules.instructions.md"
    "dreamers/instructions/git.instructions.md"
    "dreamers/templates/plan-writing-guide.md"
    "dreamers/refs/hone-architecture-rubric.md"
    "dreamers/refs/plan-quality.md"
    "dreamers/refs/plan-selection.md"
    "dreamers/templates/plan-guide-selector.md"
    "dreamers/templates/plan-guide-lite.md"
    "dreamers/templates/plan-guide-standard.md"
    "dreamers/templates/plan-guide-complex.md"
)

function Copy-DreamersFiles {
    param(
        [string]$From,
        [string]$To,
        [string]$Label
    )
    if (-not (Test-Path $From)) {
        Write-Warning "Source not found, skipping: $From"
        return 0
    }
    if (-not (Test-Path $To)) {
        New-Item -ItemType Directory -Path $To -Force | Out-Null
    }

    $count = 0
    foreach ($file in Get-ChildItem $From -File) {
        $dest = Join-Path $To $file.Name
        if ((Test-Path $dest) -and -not $Force) {
            Write-Host "  SKIP (exists): $Label/$($file.Name) - use -Force to overwrite" -ForegroundColor Yellow
            continue
        }
        Copy-Item -Path $file.FullName -Destination $dest -Force
        if ((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $dest).Hash) {
            throw "Verification failed: $dest"
        }
        Write-Host "  OK: $Label/$($file.Name)" -ForegroundColor Green
        $count++
    }
    return $count
}

function Remove-LegacyAgentFiles {
    param(
        [string]$TargetDir
    )
    if (-not (Test-Path $TargetDir)) { return 0 }

    $count = 0
    foreach ($name in $legacyAgentNames) {
        $target = Join-Path $TargetDir "$name.md"
        if (-not (Test-Path $target)) { continue }
        Remove-Item -LiteralPath $target -Force
        Write-Host "  REMOVED legacy: dreamers/agents/$name.md" -ForegroundColor DarkGray
        $count++
    }

    $remaining = Get-ChildItem $TargetDir -Force
    if ($remaining.Count -eq 0) {
        Remove-Item -LiteralPath $TargetDir -Force
        Write-Host "  REMOVED empty legacy dir: dreamers/agents" -ForegroundColor DarkGray
    }
    return $count
}

function Remove-LegacyAgentTomls {
    param(
        [string]$TargetDir
    )
    if (-not (Test-Path $TargetDir)) { return 0 }

    $count = 0
    foreach ($name in $legacyAgentTomlNames) {
        $target = Join-Path $TargetDir "$name.toml"
        if (-not (Test-Path $target)) { continue }
        Remove-Item -LiteralPath $target -Force
        Write-Host "  REMOVED legacy: agents/$name.toml" -ForegroundColor DarkGray
        $count++
    }
    return $count
}

function Remove-ObsoleteManagedFiles {
    $count = 0
    foreach ($rel in $obsoleteManagedFiles) {
        $target = Join-Path $CodexHome ($rel -replace '/', [System.IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path $target)) { continue }
        Remove-Item -LiteralPath $target -Force
        Write-Host "  REMOVED obsolete managed file: $rel" -ForegroundColor DarkGray
        $count++
    }
    return $count
}

function Remove-LegacySkillFiles {
    param([string]$SkillsRoot)

    $count = 0
    foreach ($skillName in @("dreamers-full", "dreamers-research")) {
        $directory = Join-Path $SkillsRoot $skillName
        foreach ($fileName in @("SKILL.md", "readme.md")) {
            $path = Join-Path $directory $fileName
            if (-not (Test-Path $path)) { continue }
            Remove-Item -LiteralPath $path -Force
            Write-Host "  REMOVED legacy managed file: skills/$skillName/$fileName" -ForegroundColor DarkGray
            $count++
        }
        if (Test-Path $directory) {
            $remaining = Get-ChildItem $directory -Force
            if ($remaining.Count -eq 0) {
                Remove-Item -LiteralPath $directory -Force
                Write-Host "  REMOVED empty legacy dir: skills/$skillName" -ForegroundColor DarkGray
            }
        }
    }
    return $count
}

Write-Host "`nDreamers Codex Installer" -ForegroundColor Cyan
Write-Host "Source:  $RepoRoot"
Write-Host "Target:  $CodexHome`n"

$total = 0
$legacyRemoved = 0

Write-Host "[agents]" -ForegroundColor Cyan
$total += Copy-DreamersFiles -From (Join-Path $RepoRoot "agents") -To (Join-Path $CodexHome "agents") -Label "agents"

Write-Host "[skills]" -ForegroundColor Cyan
$skillsRoot = Join-Path $RepoRoot "skills"
if (Test-Path $skillsRoot) {
    Get-ChildItem $skillsRoot -Directory | Where-Object { $_.Name -eq "dreamers" -or $_.Name -like "dreamers-*" } | ForEach-Object {
        $total += Copy-DreamersFiles -From $_.FullName -To (Join-Path (Join-Path $CodexHome "skills") $_.Name) -Label "skills/$($_.Name)"
    }
}

Write-Host "[dreamers]" -ForegroundColor Cyan
foreach ($name in @("refs", "templates", "instructions")) {
    $total += Copy-DreamersFiles -From (Join-Path (Join-Path $RepoRoot "dreamers") $name) -To (Join-Path (Join-Path $CodexHome "dreamers") $name) -Label "dreamers/$name"
}

Write-Host "[global instructions]" -ForegroundColor Cyan
& (Join-Path $SourceRoot "scripts/Update-CodexInstructions.ps1") -Action install -CodexHome $CodexHome -PackageRoot $RepoRoot -Force:$Force

Write-Host "[legacy]" -ForegroundColor Cyan
$legacyRemoved += Remove-LegacySkillFiles -SkillsRoot (Join-Path $CodexHome "skills")
$legacyRemoved += Remove-LegacyAgentTomls -TargetDir (Join-Path $CodexHome "agents")
$legacyRemoved += Remove-LegacyAgentFiles -TargetDir (Join-Path (Join-Path $CodexHome "dreamers") "agents")
$legacyRemoved += Remove-ObsoleteManagedFiles

Write-Host "`nInstalled $total Dreamers Codex file(s); removed $legacyRemoved legacy/obsolete file(s).`n" -ForegroundColor Cyan

} finally {
    if (Test-Path -LiteralPath $RepoRoot) {
        Remove-Item -LiteralPath $RepoRoot -Recurse -Force
    }
}
