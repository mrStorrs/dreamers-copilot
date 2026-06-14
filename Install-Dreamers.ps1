<#
.SYNOPSIS
    Installs the Dreamers system into the user's global ~/.copilot directory.

.DESCRIPTION
    Copies agents, skills, dreamers refs/templates/scripts, hook configs, and instructions from this
    repo's .github/ directory into the corresponding ~/.copilot/ locations.

    Only manages Dreamers-owned files. Does not touch other agents, skills, or
    configs already in ~/.copilot/.

.PARAMETER CopilotHome
    Override the target Copilot home directory. Defaults to ~/.copilot.

.PARAMETER DreamersMcpPath
    Override the local dreamers-mcp checkout used for the shared stats runtime.
    Defaults to a sibling ../dreamers-mcp checkout next to this repo.

.PARAMETER Force
    Overwrite existing files without prompting.

.EXAMPLE
    .\Install-Dreamers.ps1
    .\Install-Dreamers.ps1 -Force
    .\Install-Dreamers.ps1 -WhatIf
    .\Install-Dreamers.ps1 -CopilotHome "D:\custom\.copilot"
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$CopilotHome = (Join-Path $HOME ".copilot"),
    [string]$DreamersMcpPath,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$Source = Join-Path $RepoRoot ".github"
$RuntimeInstallStatePath = Join-Path $CopilotHome "dreamers" "install-state" "runtime-hooks.txt"

if (-not (Test-Path $Source)) {
    Write-Error "Cannot find .github/ directory at '$Source'. Run this script from the repo root or the repo directory."
    exit 1
}

function Resolve-DreamersMcpCheckout {
    param([string]$CandidatePath)

    $checkoutRoot = if ($CandidatePath) {
        $CandidatePath
    } else {
        Join-Path (Split-Path -Parent $RepoRoot) "dreamers-mcp"
    }

    $resolvedPath = Resolve-Path -LiteralPath $checkoutRoot -ErrorAction SilentlyContinue
    $resolvedRoot = if ($null -ne $resolvedPath) {
        [System.IO.Path]::GetFullPath($resolvedPath.Path)
    } else {
        [System.IO.Path]::GetFullPath($checkoutRoot)
    }
    $packageDir = Join-Path $resolvedRoot "dreamers_stats"
    $requiredFiles = @("__init__.py", "__main__.py", "cli.py", "mcp_server.py", "runtime.py")
    if (-not (Test-Path $packageDir)) {
        throw "Cannot find dreamers-mcp shared runtime at '$resolvedRoot'. Pass -DreamersMcpPath to a local dreamers-mcp checkout."
    }
    foreach ($name in $requiredFiles) {
        if (-not (Test-Path (Join-Path $packageDir $name))) {
            throw "dreamers-mcp checkout at '$resolvedRoot' is incomplete; missing dreamers_stats/$name."
        }
    }

    return $packageDir
}

function Get-ManagedRuntimeTargets {
    $targets = [System.Collections.Generic.List[string]]::new()
    if (-not (Test-Path $RuntimeInstallStatePath)) {
        return $targets
    }

    foreach ($line in Get-Content $RuntimeInstallStatePath) {
        $trimmed = $line.Trim()
        if ($trimmed) {
            $targets.Add($trimmed)
        }
    }

    return $targets
}

function Copy-Files {
    param(
        [string]$From,
        [string]$To,
        [string]$Label,
        [System.Collections.Generic.List[string]]$ManagedTargets,
        [string]$ManagedPrefix,
        [switch]$Recurse
    )
    if (-not (Test-Path $From)) {
        Write-Warning "Source not found, skipping: $From"
        return 0
    }
    if (-not (Test-Path $To)) {
        if ($PSCmdlet.ShouldProcess($To, "Create directory for $Label")) {
            New-Item -ItemType Directory -Path $To -Force | Out-Null
        }
    }
    $files = if ($Recurse) {
        Get-ChildItem $From -File -Recurse
    } else {
        Get-ChildItem $From -File
    }
    $count = 0
    foreach ($f in $files) {
        $relativePath = if ($Recurse) {
            $f.FullName.Substring($From.Length).TrimStart("\", "/")
        } else {
            $f.Name
        }
        $dest = Join-Path $To $relativePath
        $destDir = Split-Path -Parent $dest
        if (-not (Test-Path $destDir)) {
            if ($PSCmdlet.ShouldProcess($destDir, "Create directory for $Label")) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
        }
        if ((Test-Path $dest) -and -not $Force) {
            Write-Host "  SKIP (exists): $relativePath — use -Force to overwrite" -ForegroundColor Yellow
            continue
        }
        if ($PSCmdlet.ShouldProcess($dest, "Copy $Label asset")) {
            Copy-Item $f.FullName $dest -Force
            Write-Host "  OK: $relativePath" -ForegroundColor Green
            if ($null -ne $ManagedTargets -and $ManagedPrefix) {
                $ManagedTargets.Add(((Join-Path $ManagedPrefix $relativePath) -replace "\\", "/"))
            }
            $count++
        }
    }
    return $count
}

function Write-ManagedRuntimeTargets {
    param([System.Collections.Generic.List[string]]$ManagedTargets)

    if ($null -eq $ManagedTargets) { return }
    $uniqueTargets = $ManagedTargets | Sort-Object -Unique
    $installStateDir = Split-Path -Parent $RuntimeInstallStatePath

    if ($uniqueTargets.Count -eq 0) {
        if (Test-Path $RuntimeInstallStatePath) {
            if ($PSCmdlet.ShouldProcess($RuntimeInstallStatePath, "Remove runtime install state")) {
                Remove-Item $RuntimeInstallStatePath -Force
            }
        }
        if (Test-Path $installStateDir) {
            $remaining = Get-ChildItem $installStateDir -Force
            if ($remaining.Count -eq 0 -and $PSCmdlet.ShouldProcess($installStateDir, "Remove empty install-state directory")) {
                Remove-Item $installStateDir -Force
            }
        }
        return
    }

    if (-not (Test-Path $installStateDir)) {
        if ($PSCmdlet.ShouldProcess($installStateDir, "Create runtime install-state directory")) {
            New-Item -ItemType Directory -Path $installStateDir -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($RuntimeInstallStatePath, "Write runtime install state")) {
        ($uniqueTargets -join "`n") | Set-Content -Path $RuntimeInstallStatePath -Encoding utf8
    }
}

$SharedRuntimePackageSource = Resolve-DreamersMcpCheckout -CandidatePath $DreamersMcpPath

Write-Host "`nDreamers Installer" -ForegroundColor Cyan
Write-Host "Source:  $Source"
Write-Host "Runtime: $SharedRuntimePackageSource"
Write-Host "Target:  $CopilotHome`n"

$total = 0
$managedRuntimeTargets = Get-ManagedRuntimeTargets

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

# Shared runtime package
Write-Host "[dreamers/runtime]" -ForegroundColor Cyan
$total += Copy-Files -From $SharedRuntimePackageSource -To (Join-Path $CopilotHome "dreamers" "runtime" "dreamers_stats") -Label "runtime" -ManagedTargets $managedRuntimeTargets -ManagedPrefix "dreamers/runtime/dreamers_stats" -Recurse

# Dreamers scripts
Write-Host "[dreamers/scripts]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "dreamers" "scripts") -To (Join-Path $CopilotHome "dreamers" "scripts") -Label "scripts" -ManagedTargets $managedRuntimeTargets -ManagedPrefix "dreamers/scripts"

# User-level hooks
Write-Host "[hooks]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "dreamers" "hooks") -To (Join-Path $CopilotHome "hooks") -Label "hooks" -ManagedTargets $managedRuntimeTargets -ManagedPrefix "hooks"

# Instructions (auto-loaded by Copilot CLI from ~/.copilot/instructions/*.instructions.md)
Write-Host "[instructions]" -ForegroundColor Cyan
$total += Copy-Files -From (Join-Path $Source "instructions") -To (Join-Path $CopilotHome "instructions") -Label "instructions"

Write-ManagedRuntimeTargets -ManagedTargets $managedRuntimeTargets

Write-Host "`nInstalled $($total) file(s).`n" -ForegroundColor Cyan
