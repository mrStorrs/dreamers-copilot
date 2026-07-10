[CmdletBinding()]
param(
    [string]$Root = $(if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }),
    [switch]$SkipInstallSmoke
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Assert-ExactSet {
    param(
        [string]$Label,
        [string[]]$Expected,
        [string[]]$Actual
    )
    foreach ($item in ($Expected | Where-Object { $_ -notin $Actual })) {
        Add-Error "Missing $Label item: $item"
    }
    foreach ($item in ($Actual | Where-Object { $_ -notin $Expected })) {
        Add-Error "Unexpected $Label item: $item"
    }
}

function Assert-Path {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) {
        Add-Error "Missing $Label at $Path"
    }
}

function Assert-Patterns {
    param(
        [string]$Path,
        [hashtable]$Patterns
    )
    if (-not (Test-Path $Path)) {
        Add-Error "Missing contract file: $Path"
        return
    }
    $content = Get-Content -Raw $Path
    $options = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor
        [System.Text.RegularExpressions.RegexOptions]::Multiline -bor
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    foreach ($entry in $Patterns.GetEnumerator()) {
        if (-not [regex]::IsMatch($content, [string]$entry.Value, $options)) {
            Add-Error "Missing $($entry.Key) contract in $Path"
        }
    }
}

function Assert-SynchronizedRefs {
    $refsRoot = Join-Path $Root ".github/dreamers/refs"
    $refs = @{}
    foreach ($ref in Get-ChildItem $refsRoot -Filter "*.md" -File) {
        $content = (Get-Content -Raw $ref.FullName).Replace(([string][char]13 + [char]10), [string][char]10).Replace([string][char]13, [string][char]10)
        $refs[$ref.BaseName] = $content.TrimEnd([char]10)
    }
    foreach ($consumer in Get-ChildItem (Join-Path $Root ".github") -Filter "*.md" -File -Recurse) {
        if ($consumer.FullName.StartsWith($refsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
            continue
        }
        $content = (Get-Content -Raw $consumer.FullName).Replace(([string][char]13 + [char]10), [string][char]10).Replace([string][char]13, [string][char]10)
        foreach ($name in $refs.Keys) {
            $escapedName = [regex]::Escape($name)
            $pattern = "(?ms)^<$escapedName>\n(.*?)\n</$escapedName>"
            $match = [regex]::Match($content, $pattern)
            if ($match.Success -and $match.Groups[1].Value -ne $refs[$name]) {
                Add-Error "Synchronized ref drift in $($consumer.FullName): $name"
            }
        }
    }
}

$expectedAgents = @("echo", "forge", "hone", "nova", "probe", "sage", "sentinel", "vigil")
$expectedSkills = @(
    "dreamers",
    "dreamers-add-logging",
    "dreamers-clean-work",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-docs",
    "dreamers-find-refactors",
    "dreamers-fix",
    "dreamers-help",
    "dreamers-implement",
    "dreamers-issue",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-plan-verify",
    "dreamers-pr",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review",
    "dreamers-simplify",
    "dreamers-test",
    "dreamers-update"
)
$expectedRefs = @(
    "agent-recovery.md",
    "comment-rules.md",
    "dreamers-kernel.md",
    "git-workflow.md",
    "hone-architecture-rubric.md",
    "logging-discipline.md",
    "planning-grill.md",
    "project-bootstrap.md",
    "review-selection.md",
    "reviewer-findings-format.md",
    "testing-mandate.md"
)
$expectedTemplates = @(
    "discovery-questions.md",
    "github-issue.md",
    "logging-standards.md",
    "manifest.md",
    "plan-guide-complex.md",
    "plan-guide-lite.md",
    "plan-guide-selector.md",
    "plan-guide-standard.md",
    "plan.md",
    "pr-description.md",
    "project-brief.md",
    "shell-plan.md",
    "test-benchmarks.md",
    "user-testing-gate.md"
)
$expectedInstructions = @(
    "comment-rules.instructions.md",
    "dreamers.instructions.md",
    "git.instructions.md"
)
$expectedSkillReadmes = @(
    "dreamers",
    "dreamers-add-logging",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-find-refactors",
    "dreamers-fix",
    "dreamers-implement",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review"
)

$agentRoot = Join-Path $Root ".github/agents"
$skillRoot = Join-Path $Root ".github/skills"
$dreamersRoot = Join-Path $Root ".github/dreamers"
$instructionsRoot = Join-Path $Root ".github/instructions"

Assert-Path $agentRoot "agents directory"
Assert-Path $skillRoot "skills directory"
Assert-Path $dreamersRoot "dreamers directory"
Assert-Path $instructionsRoot "instructions directory"

if (Test-Path $agentRoot) {
    $actualAgents = Get-ChildItem $agentRoot -Filter "*.agent.md" -File |
        ForEach-Object { $_.Name -replace "\.agent\.md$", "" }
    Assert-ExactSet -Label "agent" -Expected $expectedAgents -Actual $actualAgents
}

if (Test-Path $skillRoot) {
    $actualSkills = Get-ChildItem $skillRoot -Directory | ForEach-Object { $_.Name }
    Assert-ExactSet -Label "skill" -Expected $expectedSkills -Actual $actualSkills
    foreach ($skillName in $expectedSkills) {
        $skillFile = Join-Path (Join-Path $skillRoot $skillName) "SKILL.md"
        if (-not (Test-Path $skillFile)) {
            Add-Error "Missing SKILL.md: $skillFile"
            continue
        }
        $content = Get-Content -Raw $skillFile
        $frontmatter = [regex]::Match($content, "(?s)^---\s*\n(.*?)\n---")
        if (-not $frontmatter.Success) {
            Add-Error "Invalid frontmatter: $skillFile"
            continue
        }
        $name = [regex]::Match($frontmatter.Groups[1].Value, '(?m)^name:\s*[''"]?([^''"\n]+)')
        if (-not $name.Success -or $name.Groups[1].Value.Trim() -ne $skillName) {
            Add-Error "Skill name does not match directory: $skillFile"
        }
        if ($frontmatter.Groups[1].Value -notmatch "(?m)^description:\s*.+$") {
            Add-Error "Skill missing description: $skillFile"
        }
    }
    foreach ($skillName in $expectedSkillReadmes) {
        $readme = Join-Path (Join-Path $skillRoot $skillName) "readme.md"
        if (-not (Test-Path $readme)) {
            Add-Error "Missing skill readme: $readme"
        }
    }
}

foreach ($entry in @(
    @{ Label = "ref"; Path = (Join-Path $dreamersRoot "refs"); Expected = $expectedRefs },
    @{ Label = "template"; Path = (Join-Path $dreamersRoot "templates"); Expected = $expectedTemplates },
    @{ Label = "instruction"; Path = $instructionsRoot; Expected = $expectedInstructions }
)) {
    if (Test-Path $entry.Path) {
        $actual = Get-ChildItem $entry.Path -File | ForEach-Object { $_.Name }
        Assert-ExactSet -Label $entry.Label -Expected $entry.Expected -Actual $actual
    }
}

$catalogPath = Join-Path $Root ".github/catalog.json"
Assert-Path $catalogPath "catalog"
if (Test-Path $catalogPath) {
    try {
        $catalog = Get-Content -Raw $catalogPath | ConvertFrom-Json
        $items = @($catalog.items | ForEach-Object { "$($_.type):$($_.slug)" })
        foreach ($required in @("skill:dreamers", "skill:dreamers-help")) {
            if ($required -notin $items) { Add-Error "Catalog missing item: $required" }
        }
        foreach ($retired in @("skill:dreamers-full", "skill:dreamers-lite")) {
            if ($retired -in $items) { Add-Error "Catalog retains retired item: $retired" }
        }
        foreach ($item in $catalog.items) {
            if ($item.path -and -not (Test-Path (Join-Path $Root $item.path))) {
                Add-Error "Catalog item path does not exist: $($item.path)"
            }
        }
        foreach ($collection in $catalog.collections) {
            $members = @($collection.members | ForEach-Object { "$($_.type):$($_.slug)" })
            foreach ($required in @("skill:dreamers", "skill:dreamers-help")) {
                if ($required -notin $members) { Add-Error "Collection missing member: $required" }
            }
            foreach ($retired in @("skill:dreamers-full", "skill:dreamers-lite")) {
                if ($retired -in $members) { Add-Error "Collection retains retired member: $retired" }
            }
        }
    }
    catch {
        Add-Error "Invalid catalog JSON: $($_.Exception.Message)"
    }
}

Assert-Patterns (Join-Path $skillRoot "dreamers/SKILL.md") @{
    "help routing" = "empty|whitespace.*help|--help|-h"
    "default Grill" = "task description.*Grill.*default|Grill.*default.*task description"
    "Grill opt-out" = "--no-grill.*do not grill|--no-grill.*skip the interview"
    "artifact mode" = "plan path.*manifest.*skip.*Grill|artifact mode.*skip.*Grill"
    "branch setup" = "git-workflow branch setup.*checkout.*pull.*feature branch"
    "review selection" = "<review-selection>.*</review-selection>"
    "approval starts implementation" = "plan approval authorizes implementation"
    "user testing" = "user.testing.*trigger"
    "pre-PR approval" = "pre-PR approval"
    "PR close-out" = "/dreamers-pr"
}
Assert-Patterns (Join-Path $skillRoot "dreamers-help/SKILL.md") @{
    "read-only boundary" = "read.only"
    "delivery example" = "/dreamers\s+"
    "specialized choices" = "specialized"
    "migration note" = "retired|removed|migration"
}
Assert-Patterns (Join-Path $dreamersRoot "refs/review-selection.md") @{
    "complex triad" = "complex.*Sentinel.*Probe.*Hone"
    "low-risk Vigil" = "lite.*standard.*Vigil"
    "danger escalation" = "security.*schema.*public.*API"
    "override" = "explicit user override.*wins|user override.*authoritative"
    "ambiguity" = "ambigu.*ask"
}

Assert-SynchronizedRefs

$legacyPattern = "dreamers-(full|lite)"
$migrationPattern = "retir|remov|legacy|migrat|cleanup|clean up|previous|old command|no longer"
$scanRoots = @(
    $agentRoot,
    $skillRoot,
    $dreamersRoot,
    $instructionsRoot,
    (Join-Path $Root "README.md"),
    (Join-Path $Root ".github/README.md"),
    $catalogPath
) | Where-Object { Test-Path $_ }
foreach ($scanRoot in $scanRoots) {
    $files = if ((Get-Item $scanRoot).PSIsContainer) {
        Get-ChildItem $scanRoot -File -Recurse | Where-Object { $_.Extension -in @(".md", ".json", ".ps1") }
    } else {
        Get-Item $scanRoot
    }
    foreach ($file in $files) {
        if ($file.Name -like "Test-DreamersCopilot*") { continue }
        $lineNumber = 0
        foreach ($line in Get-Content $file.FullName) {
            $lineNumber++
            if ($line -match $legacyPattern -and $line -notmatch $migrationPattern) {
                Add-Error "Active retired-pipeline reference in $($file.FullName):$lineNumber"
            }
        }
    }
}

if (-not $SkipInstallSmoke) {
    $tmpHome = Join-Path ([System.IO.Path]::GetTempPath()) ("dreamers-copilot-test-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpHome -Force | Out-Null
    try {
        $legacyLite = Join-Path $tmpHome "skills/dreamers-lite"
        $legacyFull = Join-Path $tmpHome "skills/dreamers-full"
        foreach ($directory in @($legacyLite, $legacyFull)) {
            New-Item -ItemType Directory -Path $directory -Force | Out-Null
            Set-Content -Path (Join-Path $directory "SKILL.md") -Value "managed" -Encoding utf8NoBOM
            Set-Content -Path (Join-Path $directory "readme.md") -Value "managed" -Encoding utf8NoBOM
        }
        Set-Content -Path (Join-Path $legacyLite "user-owned.md") -Value "preserve" -Encoding utf8NoBOM

        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $tmpHome -Force | Out-Null

        foreach ($path in @(
            (Join-Path $tmpHome "skills/dreamers/SKILL.md"),
            (Join-Path $tmpHome "skills/dreamers-help/SKILL.md")
        )) {
            if (-not (Test-Path $path)) { Add-Error "Install smoke missing new skill: $path" }
        }
        foreach ($directory in @($legacyLite, $legacyFull)) {
            foreach ($managed in @("SKILL.md", "readme.md")) {
                $path = Join-Path $directory $managed
                if (Test-Path $path) { Add-Error "Install smoke retained legacy managed file: $path" }
            }
        }
        if (-not (Test-Path (Join-Path $legacyLite "user-owned.md"))) {
            Add-Error "Install smoke removed user-owned legacy file: $legacyLite"
        }
        if (Test-Path $legacyFull) {
            Add-Error "Install smoke did not prune empty legacy directory: $legacyFull"
        }

        New-Item -ItemType Directory -Path $legacyFull -Force | Out-Null
        Set-Content -Path (Join-Path $legacyFull "SKILL.md") -Value "managed" -Encoding utf8NoBOM
        Set-Content -Path (Join-Path $legacyFull "readme.md") -Value "managed" -Encoding utf8NoBOM
        & (Join-Path $Root "Remove-Dreamers.ps1") -CopilotHome $tmpHome | Out-Null

        foreach ($path in @(
            (Join-Path $tmpHome "skills/dreamers/SKILL.md"),
            (Join-Path $tmpHome "skills/dreamers-help/SKILL.md")
        )) {
            if (Test-Path $path) { Add-Error "Remove smoke retained managed skill: $path" }
        }
        if (-not (Test-Path (Join-Path $legacyLite "user-owned.md"))) {
            Add-Error "Remove smoke removed user-owned legacy file: $legacyLite"
        }
        if (Test-Path $legacyFull) {
            Add-Error "Remove smoke did not prune empty legacy directory: $legacyFull"
        }
    }
    finally {
        if (Test-Path $tmpHome) {
            Remove-Item -LiteralPath $tmpHome -Recurse -Force
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "Dreamers Copilot validation passed." -ForegroundColor Green
