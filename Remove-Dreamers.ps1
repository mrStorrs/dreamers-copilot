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
$RuntimeInstallStatePath = Join-Path $CopilotHome "dreamers" "install-state" "runtime-hooks.txt"

if (-not (Test-Path $Source)) {
    Write-Error "Cannot find .github/ directory at '$Source'. Run this script from the repo root or the repo directory."
    exit 1
}

function Get-ManagedFileHash {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-ManagedRuntimeTargets {
    if (-not (Test-Path $RuntimeInstallStatePath)) { return @{} }

    $targets = @{}
    foreach ($line in Get-Content $RuntimeInstallStatePath) {
        $trimmed = $line.Trim()
        if ($trimmed) {
            $targets[$trimmed] = $true
        }
    }
    return $targets
}

function Test-ManagedTarget {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )
    if (-not (Test-Path $SourcePath)) { return $false }
    if (-not (Test-Path $TargetPath)) { return $false }
    return (Get-ManagedFileHash -Path $SourcePath) -eq (Get-ManagedFileHash -Path $TargetPath)
}

function Remove-EmptyDirectory {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    $remaining = Get-ChildItem $Path -Force
    if ($remaining.Count -eq 0) {
        Remove-Item $Path -Force
        Write-Host "  REMOVED empty dir: $Path" -ForegroundColor DarkGray
    }
}

function Remove-ManagedFiles {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [string]$Label,
        [hashtable]$ManagedTargets,
        [string]$ManagedPrefix
    )
    if (-not (Test-Path $SourceDir)) { return 0 }
    if (-not (Test-Path $TargetDir)) { return 0 }
    $sourceFiles = Get-ChildItem $SourceDir -File
    $count = 0
    foreach ($f in $sourceFiles) {
        $target = Join-Path $TargetDir $f.Name
        if (Test-Path $target) {
            $relativeTarget = if ($ManagedPrefix) { ((Join-Path $ManagedPrefix $f.Name) -replace "\\", "/") } else { $null }
            $isManifestOwned = $relativeTarget -and $ManagedTargets.ContainsKey($relativeTarget)
            if (-not $isManifestOwned -and -not (Test-ManagedTarget -SourcePath $f.FullName -TargetPath $target)) {
                Write-Host "  SKIP (not Dreamers-managed): $target" -ForegroundColor Yellow
                continue
            }
            if ($DryRun) {
                Write-Host "  WOULD REMOVE: $target" -ForegroundColor Yellow
            } else {
                Remove-Item $target -Force
                Write-Host "  REMOVED: $($f.Name)" -ForegroundColor Red
            }
            $count++
        }
    }
    if (-not $DryRun) {
        Remove-EmptyDirectory -Path $TargetDir
    }
    return $count
}

$verb = if ($DryRun) { "Dreamers Remover (DRY RUN)" } else { "Dreamers Remover" }
Write-Host "`n$verb" -ForegroundColor Cyan
Write-Host "Source:  $Source"
Write-Host "Target:  $CopilotHome`n"

$total = 0
$managedRuntimeTargets = Get-ManagedRuntimeTargets

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

# Dreamers scripts
Write-Host "[dreamers/scripts]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "dreamers" "scripts") -TargetDir (Join-Path $CopilotHome "dreamers" "scripts") -Label "scripts" -ManagedTargets $managedRuntimeTargets -ManagedPrefix "dreamers/scripts"

# User-level hooks
Write-Host "[hooks]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "dreamers" "hooks") -TargetDir (Join-Path $CopilotHome "hooks") -Label "hooks" -ManagedTargets $managedRuntimeTargets -ManagedPrefix "hooks"

# Instructions
Write-Host "[instructions]" -ForegroundColor Cyan
$total += Remove-ManagedFiles -SourceDir (Join-Path $Source "instructions") -TargetDir (Join-Path $CopilotHome "instructions") -Label "instructions"

if (-not $DryRun) {
    if (Test-Path $RuntimeInstallStatePath) {
        Remove-Item $RuntimeInstallStatePath -Force
    }
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "dreamers" "refs")
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "dreamers" "install-state")
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "dreamers" "templates")
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "dreamers" "scripts")
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "dreamers")
    Remove-EmptyDirectory -Path (Join-Path $CopilotHome "hooks")
}

$action = if ($DryRun) { "Would remove" } else { "Removed" }
Write-Host "`n$action $total file(s).`n" -ForegroundColor Cyan
