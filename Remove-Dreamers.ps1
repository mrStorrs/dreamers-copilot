<#
.SYNOPSIS
    Removes Dreamers-installed files from the user's global ~/.copilot directory.

.DESCRIPTION
    Removes only files that the Dreamers install script would have placed.
    Does not touch other agents, skills, or configs in ~/.copilot/.

.PARAMETER CopilotHome
    Override the target Copilot home directory. Defaults to ~/.copilot.

.PARAMETER DryRun
    Show what would be removed without actually deleting anything.

.EXAMPLE
    .\Remove-Dreamers.ps1
    .\Remove-Dreamers.ps1 -DryRun
    .\Remove-Dreamers.ps1 -CopilotHome "D:\custom\.copilot"
#>
[CmdletBinding()]
param(
    [string]$CopilotHome = (Join-Path $HOME ".copilot"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$Source = Join-Path $RepoRoot ".github"

if (-not (Test-Path $Source)) {
    Write-Error "Cannot find .github/ directory at '$Source'. Run this script from the repo root or the repo directory."
    exit 1
}

function Remove-ManagedFiles {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [string]$Label
    )
    if (-not (Test-Path $SourceDir)) { return 0 }
    if (-not (Test-Path $TargetDir)) { return 0 }
    $sourceFiles = Get-ChildItem $SourceDir -File
    $count = 0
    foreach ($f in $sourceFiles) {
        $target = Join-Path $TargetDir $f.Name
        if (Test-Path $target) {
            if ($DryRun) {
                Write-Host "  WOULD REMOVE: $target" -ForegroundColor Yellow
            } else {
                Remove-Item $target -Force
                Write-Host "  REMOVED: $($f.Name)" -ForegroundColor Red
            }
            $count++
        }
    }
    # Remove empty directory (only if we manage it and it's now empty)
    if (-not $DryRun -and (Test-Path $TargetDir)) {
        $remaining = Get-ChildItem $TargetDir -Force
        if ($remaining.Count -eq 0) {
            Remove-Item $TargetDir -Force
            Write-Host "  REMOVED empty dir: $TargetDir" -ForegroundColor DarkGray
        }
    }
    return $count
}

$verb = if ($DryRun) { "Dreamers Remover (DRY RUN)" } else { "Dreamers Remover" }
Write-Host "`n$verb" -ForegroundColor Cyan
Write-Host "Source:  $Source"
Write-Host "Target:  $CopilotHome`n"

$total = 0

# Agents
Write-Host "[agents]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "agents") -TargetDir (Join-Path $CopilotHome "agents") -Label "agents"

# Skills
Write-Host "[skills]" -ForegroundColor Cyan
$skillSource = Join-Path $Source "skills"
if (Test-Path $skillSource) {
    $skillDirs = Get-ChildItem $skillSource -Directory | Where-Object { $_.Name -like "dreamers-*" }
    foreach ($dir in $skillDirs) {
        $targetDir = Join-Path $CopilotHome "skills" $dir.Name
        $total += Remove-ManagedFiles -SourceDir $dir.FullName -TargetDir $targetDir -Label "skills/$($dir.Name)"
    }
}

# Dreamers refs
Write-Host "[dreamers/refs]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "dreamers" "refs") -TargetDir (Join-Path $CopilotHome "dreamers" "refs") -Label "refs"

# Dreamers templates
Write-Host "[dreamers/templates]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "dreamers" "templates") -TargetDir (Join-Path $CopilotHome "dreamers" "templates") -Label "templates"

# Clean up empty dreamers directory
if (-not $DryRun -and (Test-Path (Join-Path $CopilotHome "dreamers"))) {
    $remaining = Get-ChildItem (Join-Path $CopilotHome "dreamers") -Force -Recurse
    if ($remaining.Count -eq 0) {
        Remove-Item (Join-Path $CopilotHome "dreamers") -Force -Recurse
        Write-Host "  REMOVED empty dir: dreamers/" -ForegroundColor DarkGray
    }
}

# Instructions
Write-Host "[instructions]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "instructions") -TargetDir (Join-Path $CopilotHome "instructions") -Label "instructions"

$action = if ($DryRun) { "Would remove" } else { "Removed" }
Write-Host "`n$action $total file(s).`n" -ForegroundColor Cyan
