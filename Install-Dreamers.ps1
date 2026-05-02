<#
.SYNOPSIS
    Installs the Dreamers system into the user's global ~/.copilot directory.

.DESCRIPTION
    Copies agents, skills, dreamers refs/templates, and instructions from this
    repo's .github/ directory into the corresponding ~/.copilot/ locations.

    Only manages Dreamers-owned files. Does not touch other agents, skills, or
    configs already in ~/.copilot/.

.PARAMETER CopilotHome
    Override the target Copilot home directory. Defaults to ~/.copilot.

.PARAMETER Force
    Overwrite existing files without prompting.

.EXAMPLE
    .\Install-Dreamers.ps1
    .\Install-Dreamers.ps1 -Force
    .\Install-Dreamers.ps1 -CopilotHome "D:\custom\.copilot"
#>
[CmdletBinding()]
param(
    [string]$CopilotHome = (Join-Path $HOME ".copilot"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$Source = Join-Path $RepoRoot ".github"

if (-not (Test-Path $Source)) {
    Write-Error "Cannot find .github/ directory at '$Source'. Run this script from the repo root or the repo directory."
    exit 1
}

function Copy-Files {
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
    $files = Get-ChildItem $From -File
    $count = 0
    foreach ($f in $files) {
        $dest = Join-Path $To $f.Name
        if ((Test-Path $dest) -and -not $Force) {
            Write-Host "  SKIP (exists): $($f.Name) — use -Force to overwrite" -ForegroundColor Yellow
            continue
        }
        Copy-Item $f.FullName $dest -Force
        Write-Host "  OK: $($f.Name)" -ForegroundColor Green
        $count++
    }
    return $count
}

Write-Host "`nDreamers Installer" -ForegroundColor Cyan
Write-Host "Source:  $Source"
Write-Host "Target:  $CopilotHome`n"

$total = 0

# Agents
Write-Host "[agents]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "agents") -To (Join-Path $CopilotHome "agents") -Label "agents"

# Skills (each skill is a subdirectory with SKILL.md)
Write-Host "[skills]" -ForegroundColor Cyan
$skillSource = Join-Path $Source "skills"
if (Test-Path $skillSource) {
    $skillDirs = Get-ChildItem $skillSource -Directory | Where-Object { $_.Name -like "dreamers-*" }
    foreach ($dir in $skillDirs) {
        $destDir = Join-Path $CopilotHome "skills" $dir.Name
        $total += Copy-Files -From $dir.FullName -To $destDir -Label "skills/$($dir.Name)"
    }
}

# Dreamers refs
Write-Host "[dreamers/refs]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "dreamers" "refs") -To (Join-Path $CopilotHome "dreamers" "refs") -Label "refs"

# Dreamers templates
Write-Host "[dreamers/templates]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "dreamers" "templates") -To (Join-Path $CopilotHome "dreamers" "templates") -Label "templates"

# Instructions (auto-loaded by Copilot CLI from ~/.copilot/instructions/*.instructions.md)
Write-Host "[instructions]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "instructions") -To (Join-Path $CopilotHome "instructions") -Label "instructions"

Write-Host "`nInstalled $($total) file(s).`n" -ForegroundColor Cyan
