#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Sync inlined ref content into Dreamers skill + agent files.

.DESCRIPTION
  Refs at .github/dreamers/refs/<NAME>.md are the source of truth. Consumer files
  (skills, agents, and any markdown under .github/) declare which refs they want
  inlined by placing XML-style markers on their own line at column 0:

      <NAME>
      ... (sync script replaces this region) ...
      </NAME>

  Where NAME is the filename stem of a ref. A line counts as a marker only if
  (a) NAME exactly matches a real ref file, AND (b) the tag appears on its own
  line at column 0 (no leading whitespace, no trailing content). Other XML-ish
  tags inside the body are content, not structure.

  Two modes:
    -Sync    : Regenerate inlined regions from refs/. Writes files.
    -Verify  : Exit non-zero if any consumer is out of sync. Writes nothing.

  An explicit mode flag is required. Running with no flag prints usage and
  exits 1.

  Sync is two-pass: scan every consumer for malformed markers FIRST. If any
  errors are detected, abort with exit 3 before writing any file. This prevents
  a partial mutation when one consumer has errors and another is healthy.

.PARAMETER Sync
  Regenerate inlined content from refs/ into consumer files.

.PARAMETER Verify
  Check that inlined content matches refs/ exactly. Exit 1 on drift.

.EXAMPLE
  pwsh -File scripts/sync-refs.ps1 -Sync
  pwsh -File scripts/sync-refs.ps1 -Verify
#>

[CmdletBinding(DefaultParameterSetName = 'None')]
param(
    [Parameter(ParameterSetName = 'Sync', Mandatory = $true)]
    [switch]$Sync,

    [Parameter(ParameterSetName = 'Verify', Mandatory = $true)]
    [switch]$Verify
)

if ($PSCmdlet.ParameterSetName -eq 'None') {
    Write-Host "Usage: sync-refs.ps1 -Sync | -Verify" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  -Sync    Regenerate inlined ref content in consumer files."
    Write-Host "  -Verify  Exit non-zero if any consumer is out of sync."
    Write-Host ""
    Write-Host "An explicit mode flag is required."
    exit 1
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$refsDir = Join-Path $repoRoot '.github/dreamers/refs'

if (-not (Test-Path $refsDir)) {
    Write-Host "ERROR: refs directory not found at $refsDir" -ForegroundColor Red
    exit 2
}

function Read-FileText {
    param([string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $bytes = $bytes[3..($bytes.Length - 1)]
    }
    $text = [System.Text.Encoding]::UTF8.GetString($bytes)
    return ($text -replace "`r`n", "`n") -replace "`r", "`n"
}

function Write-FileText {
    param([string]$Path, [string]$Content)
    $normalized = $Content -replace "`r`n", "`n"
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $normalized, $utf8NoBom)
}

function Split-Lines {
    param([string]$Text)
    return ($Text -replace "`r`n", "`n").Split("`n")
}

$refFiles = Get-ChildItem -Path $refsDir -Filter '*.md' -File
$refs = @{}
foreach ($f in $refFiles) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $refs[$name] = @{
        Path    = $f.FullName
        RelPath = ".github/dreamers/refs/$($f.Name)"
        Content = (Read-FileText $f.FullName).TrimEnd("`n")
    }
}

# Consumer set: every .md under .github/ EXCEPT the source refs themselves
# (a ref containing a marker would create a sync loop).
$githubDir = Join-Path $repoRoot '.github'
$allMd = Get-ChildItem -Path $githubDir -Filter '*.md' -File -Recurse
$consumers = $allMd | Where-Object { $_.FullName -notmatch '[\\/]\.github[\\/]dreamers[\\/]refs[\\/]' }

$openRegex = [regex]'^<([a-zA-Z][a-zA-Z0-9_-]*)>$'
$closeRegex = [regex]'^</([a-zA-Z][a-zA-Z0-9_-]*)>$'

function Get-ExpectedInner {
    param([hashtable]$Ref)
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("<!-- GENERATED from $($Ref.RelPath) -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->")
    foreach ($line in Split-Lines $Ref.Content) {
        $lines.Add($line)
    }
    return $lines
}

$errors = @()
$plan = @()

foreach ($consumer in $consumers) {
    $relPath = $consumer.FullName.Substring($repoRoot.Path.Length + 1).Replace('\', '/')
    $text = Read-FileText $consumer.FullName
    $lines = Split-Lines $text

    $pairs = @()
    $openStack = @{}
    $hasMarkers = $false

    for ($i = 0; $i -lt $lines.Length; $i++) {
        $openMatch = $openRegex.Match($lines[$i])
        $closeMatch = $closeRegex.Match($lines[$i])

        if ($openMatch.Success) {
            $name = $openMatch.Groups[1].Value
            if (-not $refs.ContainsKey($name)) { continue }
            $hasMarkers = $true
            if ($openStack.ContainsKey($name)) {
                $errors += "  ${relPath} line $($i + 1): duplicate opening tag <$name> (previous opening at line $($openStack[$name] + 1) not closed)."
                continue
            }
            $openStack[$name] = $i
        }
        elseif ($closeMatch.Success) {
            $name = $closeMatch.Groups[1].Value
            if (-not $refs.ContainsKey($name)) { continue }
            $hasMarkers = $true
            if (-not $openStack.ContainsKey($name)) {
                $errors += "  ${relPath} line $($i + 1): closing tag </$name> without matching opening tag."
                continue
            }
            if ($pairs.Where({ $_.Name -eq $name }).Count -gt 0) {
                $existing = ($pairs | Where-Object { $_.Name -eq $name } | Select-Object -First 1).OpenLine
                $errors += "  ${relPath}: ref '$name' appears in more than one marker pair (lines $($existing + 1) and $($openStack[$name] + 1)). Same-name duplication is forbidden."
                $openStack.Remove($name)
                continue
            }
            $pairs += @{
                Name      = $name
                OpenLine  = $openStack[$name]
                CloseLine = $i
            }
            $openStack.Remove($name)
        }
    }

    foreach ($name in $openStack.Keys) {
        $errors += "  ${relPath} line $($openStack[$name] + 1): opening tag <$name> without matching closing tag."
    }

    if (-not $hasMarkers -or $pairs.Count -eq 0) { continue }

    $pairs = $pairs | Sort-Object -Property OpenLine
    $plan += @{
        Path    = $consumer.FullName
        RelPath = $relPath
        Text    = $text
        Lines   = $lines
        Pairs   = $pairs
    }
}

if ($errors.Count -gt 0) {
    Write-Host "ERROR: malformed markers detected:" -ForegroundColor Red
    foreach ($e in $errors) { Write-Host $e -ForegroundColor Red }
    Write-Host ""
    Write-Host "No files modified." -ForegroundColor Yellow
    exit 3
}

$updatedFiles = @()
$staleFiles = @()

foreach ($entry in $plan) {
    $newLines = New-Object System.Collections.Generic.List[string]
    $cursor = 0
    $stalePairs = @()

    foreach ($p in $entry.Pairs) {
        for ($k = $cursor; $k -le $p.OpenLine; $k++) {
            $newLines.Add($entry.Lines[$k])
        }
        $expectedInner = Get-ExpectedInner -Ref $refs[$p.Name]

        $currentInner = @()
        if ($p.CloseLine - $p.OpenLine -gt 1) {
            $currentInner = $entry.Lines[($p.OpenLine + 1)..($p.CloseLine - 1)]
        }
        $currentJoined = ($currentInner -join "`n")
        $expectedJoined = ($expectedInner -join "`n")
        if ($currentJoined -ne $expectedJoined) {
            $stalePairs += $p.Name
        }

        foreach ($line in $expectedInner) { $newLines.Add($line) }
        $newLines.Add($entry.Lines[$p.CloseLine])
        $cursor = $p.CloseLine + 1
    }
    for ($k = $cursor; $k -lt $entry.Lines.Length; $k++) {
        $newLines.Add($entry.Lines[$k])
    }

    $newText = ($newLines -join "`n")

    if ($newText -ne $entry.Text) {
        if ($Sync) {
            Write-FileText -Path $entry.Path -Content $newText
            $updatedFiles += $entry.RelPath
        }
        else {
            if ($stalePairs.Count -eq 0) {
                # File-level diff fired without per-pair diff. Should not happen
                # given correct logic; surface as a warning rather than swallow.
                Write-Warning "verify-refs: $($entry.RelPath) — file-level diff detected but no per-pair diff identified. Flagging all pairs as a conservative fallback; please report this case so the drift logic can be tightened."
                $stalePairs = $entry.Pairs | ForEach-Object { $_.Name }
            }
            $staleFiles += @{ Path = $entry.RelPath; Refs = ($stalePairs | Select-Object -Unique) }
        }
    }
}

if ($Sync) {
    if ($updatedFiles.Count -eq 0) {
        Write-Host "sync-refs: no changes (tree already in sync)." -ForegroundColor Green
    }
    else {
        Write-Host "sync-refs: updated $($updatedFiles.Count) file(s):" -ForegroundColor Green
        foreach ($f in $updatedFiles) { Write-Host "  $f" }
    }
    exit 0
}

if ($Verify) {
    if ($staleFiles.Count -eq 0) {
        Write-Host "verify-refs: clean. All inlined refs match source." -ForegroundColor Green
        exit 0
    }
    Write-Host "verify-refs: DRIFT detected in $($staleFiles.Count) file(s):" -ForegroundColor Red
    foreach ($s in $staleFiles) {
        $refList = ($s.Refs -join ', ')
        Write-Host "  $($s.Path)  [refs: $refList]" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Run: pwsh -File scripts/sync-refs.ps1 -Sync" -ForegroundColor Yellow
    exit 1
}
