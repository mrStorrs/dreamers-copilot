[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('check', 'check-remove', 'install', 'remove')][string]$Action,
    [Parameter(Mandatory)][string]$CodexHome,
    [string]$PackageRoot,
    [switch]$Force,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw 'Python 3.11 or newer is required.' }
$arguments = @()
if ($python.Name -match '^py(\.exe)?$') { $arguments += '-3' }
$arguments += @((Join-Path $PSScriptRoot 'codex_global_instructions.py'), $Action, '--codex-home', $CodexHome)
if ($PackageRoot) { $arguments += @('--package-root', $PackageRoot) }
if ($Force) { $arguments += '--force' }
if ($DryRun) { $arguments += '--dry-run' }
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw "Global Codex instruction update failed (exit $LASTEXITCODE)." }
