[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$python = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) { throw "Python 3.11 or newer is required." }
$arguments = @()
if ($python.Name -match '^py(\.exe)?$') { $arguments += '-3' }
$arguments += (Join-Path $PSScriptRoot '../tests/test_codex_distribution.py')
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw "Codex validation failed (exit $LASTEXITCODE)." }
