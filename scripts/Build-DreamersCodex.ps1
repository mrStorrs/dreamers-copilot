[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputDirectory)
$ErrorActionPreference = "Stop"
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw "Python 3.11 or newer is required to generate the Codex package." }
$arguments = @()
if ($python.Name -match '^py(\.exe)?$') { $arguments += '-3' }
$arguments += @((Join-Path $PSScriptRoot 'build-codex.py'), '--output', $OutputDirectory)
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw "Codex package generation failed (exit $LASTEXITCODE)." }
