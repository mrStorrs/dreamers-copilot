<#
.SYNOPSIS
    Removes Dreamers Codex-managed files from the user's Codex home.

.DESCRIPTION
    Removes only files that the Dreamers Codex install script would place.
    Does not remove user files from shared Codex directories.
#>
[CmdletBinding()]
param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$SourceRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$RepoRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("dreamers-codex-" + [guid]::NewGuid())
try {
    & (Join-Path $SourceRoot "scripts/Build-DreamersCodex.ps1") -OutputDirectory $RepoRoot
    & (Join-Path $SourceRoot "scripts/Update-CodexInstructions.ps1") -Action check-remove -CodexHome $CodexHome


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

function Remove-DreamersFiles {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [string]$Label
    )
    if (-not (Test-Path $SourceDir)) { return 0 }
    if (-not (Test-Path $TargetDir)) { return 0 }

    $count = 0
    foreach ($file in Get-ChildItem $SourceDir -File) {
        $target = Join-Path $TargetDir $file.Name
        if (-not (Test-Path $target)) { continue }
        if ($DryRun) {
            Write-Host "  WOULD REMOVE: $Label/$($file.Name) -> $target" -ForegroundColor Yellow
        } else {
            Remove-Item -LiteralPath $target -Force
            Write-Host "  REMOVED: $Label/$($file.Name)" -ForegroundColor Red
        }
        $count++
    }

    if (-not $DryRun -and (Test-Path $TargetDir)) {
        $remaining = Get-ChildItem $TargetDir -Force
        if ($remaining.Count -eq 0) {
            Remove-Item -LiteralPath $TargetDir -Force
            Write-Host "  REMOVED empty dir: $Label" -ForegroundColor DarkGray
        }
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
        if ($DryRun) {
            Write-Host "  WOULD REMOVE: dreamers/agents/$name.md -> $target" -ForegroundColor Yellow
        } else {
            Remove-Item -LiteralPath $target -Force
            Write-Host "  REMOVED legacy: dreamers/agents/$name.md" -ForegroundColor Red
        }
        $count++
    }

    if (-not $DryRun -and (Test-Path $TargetDir)) {
        $remaining = Get-ChildItem $TargetDir -Force
        if ($remaining.Count -eq 0) {
            Remove-Item -LiteralPath $TargetDir -Force
            Write-Host "  REMOVED empty dir: dreamers/agents" -ForegroundColor DarkGray
        }
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
        if ($DryRun) {
            Write-Host "  WOULD REMOVE: agents/$name.toml -> $target" -ForegroundColor Yellow
        } else {
            Remove-Item -LiteralPath $target -Force
            Write-Host "  REMOVED legacy: agents/$name.toml" -ForegroundColor Red
        }
        $count++
    }
    return $count
}

function Remove-ObsoleteManagedFiles {
    $count = 0
    foreach ($rel in $obsoleteManagedFiles) {
        $target = Join-Path $CodexHome ($rel -replace '/', [System.IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path $target)) { continue }
        if ($DryRun) {
            Write-Host "  WOULD REMOVE: $rel -> $target" -ForegroundColor Yellow
        } else {
            Remove-Item -LiteralPath $target -Force
            Write-Host "  REMOVED obsolete managed file: $rel" -ForegroundColor Red
        }
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
            if ($DryRun) {
                Write-Host "  WOULD REMOVE: skills/$skillName/$fileName -> $path" -ForegroundColor Yellow
            } else {
                Remove-Item -LiteralPath $path -Force
                Write-Host "  REMOVED legacy managed file: skills/$skillName/$fileName" -ForegroundColor Red
            }
            $count++
        }
        if (-not $DryRun -and (Test-Path $directory)) {
            $remaining = Get-ChildItem $directory -Force
            if ($remaining.Count -eq 0) {
                Remove-Item -LiteralPath $directory -Force
                Write-Host "  REMOVED empty legacy dir: skills/$skillName" -ForegroundColor DarkGray
            }
        }
    }
    return $count
}

$verb = if ($DryRun) { "Dreamers Codex Remover (DRY RUN)" } else { "Dreamers Codex Remover" }
Write-Host "`n$verb" -ForegroundColor Cyan
Write-Host "Target: $CodexHome`n"

$total = 0

Write-Host "[global instructions]" -ForegroundColor Cyan
& (Join-Path $SourceRoot "scripts/Update-CodexInstructions.ps1") -Action remove -CodexHome $CodexHome -DryRun:$DryRun

Write-Host "[agents]" -ForegroundColor Cyan
$total += Remove-DreamersFiles -SourceDir (Join-Path $RepoRoot "agents") -TargetDir (Join-Path $CodexHome "agents") -Label "agents"

Write-Host "[skills]" -ForegroundColor Cyan
$skillsRoot = Join-Path $RepoRoot "skills"
if (Test-Path $skillsRoot) {
    Get-ChildItem $skillsRoot -Directory | Where-Object { $_.Name -eq "dreamers" -or $_.Name -like "dreamers-*" } | ForEach-Object {
        $total += Remove-DreamersFiles -SourceDir $_.FullName -TargetDir (Join-Path (Join-Path $CodexHome "skills") $_.Name) -Label "skills/$($_.Name)"
    }
}

Write-Host "[dreamers]" -ForegroundColor Cyan
foreach ($name in @("refs", "templates", "instructions")) {
    $total += Remove-DreamersFiles -SourceDir (Join-Path (Join-Path $RepoRoot "dreamers") $name) -TargetDir (Join-Path (Join-Path $CodexHome "dreamers") $name) -Label "dreamers/$name"
}

Write-Host "[legacy]" -ForegroundColor Cyan
$total += Remove-LegacySkillFiles -SkillsRoot (Join-Path $CodexHome "skills")
$total += Remove-LegacyAgentTomls -TargetDir (Join-Path $CodexHome "agents")
$total += Remove-LegacyAgentFiles -TargetDir (Join-Path (Join-Path $CodexHome "dreamers") "agents")
$total += Remove-ObsoleteManagedFiles

$action = if ($DryRun) { "Would remove" } else { "Removed" }
Write-Host "`n$action $total Dreamers Codex file(s).`n" -ForegroundColor Cyan

} finally {
    if (Test-Path -LiteralPath $RepoRoot) {
        Remove-Item -LiteralPath $RepoRoot -Recurse -Force
    }
}
