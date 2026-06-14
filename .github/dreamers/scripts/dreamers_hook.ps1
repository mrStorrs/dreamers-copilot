[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$EventName
)

$ErrorActionPreference = "Stop"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$CopilotHome = if ($env:COPILOT_HOME) { $env:COPILOT_HOME } else { Join-Path $HOME ".copilot" }

function Resolve-PythonCommand {
    if ($env:DREAMERS_HOOK_PYTHON) {
        return @($env:DREAMERS_HOOK_PYTHON)
    }

    foreach ($name in @("py", "python", "python3")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            if ($name -eq "py") {
                return @($command.Source, "-3")
            }
            return @($command.Source)
        }
    }

    return $null
}

function Write-HookWarning {
    param([string]$Message)
    [Console]::Error.WriteLine("dreamers hook warning: $Message")
}

if ([string]::IsNullOrWhiteSpace($EventName)) {
    Write-HookWarning "missing event name"
    exit 0
}

$pythonCommand = Resolve-PythonCommand
if ($null -eq $pythonCommand) {
    Write-HookWarning "python runtime unavailable for $EventName"
    exit 0
}

$statsScript = Join-Path $ScriptDir "dreamers_stats.py"
$payload = [Console]::In.ReadToEnd()
$pythonExecutable = $pythonCommand[0]
$pythonArgs = @()
if ($pythonCommand.Length -gt 1) {
    $pythonArgs = $pythonCommand[1..($pythonCommand.Length - 1)]
}

try {
    $payload | & $pythonExecutable @pythonArgs $statsScript hook --client copilot --home $CopilotHome --event-name $EventName
    if ($LASTEXITCODE -ne 0) {
        Write-HookWarning "$EventName stats write failed with exit $LASTEXITCODE"
    }
} catch {
    Write-HookWarning "$EventName stats write failed: $($_.Exception.Message)"
}

exit 0
