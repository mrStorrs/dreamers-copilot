# Probe Runbook — dreamers-full approval/orchestrator cleanup

## Preconditions
- Working directory: `C:\projects-gh\dreamers-copilot`
- No project `CLAUDE.md` was present in or above the repo root.
- Change is docs-only; use content inspection only.

## Commands

### 1. Verify approval-gate wording, scoped `Atlas` removal, orchestrator clarity, and provenance
```powershell
$ErrorActionPreference='Stop'
Write-Host 'TC1: Approval gate wording'
Select-String -Path '.github/skills/dreamers-full/SKILL.md' -Pattern 'Phase 2 — Approval gate','ask_user','Approved','inline freeform corrections','non-approval freeform response','Corrections needed' | ForEach-Object { "{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }

Write-Host "`nTC2: Whole-word Atlas scan (scoped committed .github files)"
$scopedFiles = @(
  '.github/skills/dreamers-full/SKILL.md',
  '.github/copilot-instructions.dreamers.md',
  '.github/agents/echo.agent.md',
  '.github/agents/forge.agent.md',
  '.github/agents/probe.agent.md',
  '.github/agents/sage.agent.md',
  '.github/agents/sentinel.agent.md'
)
$atlasMatches = Select-String -Path $scopedFiles -Pattern '\bAtlas\b'
if ($atlasMatches) {
  $atlasMatches | ForEach-Object { "{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
} else {
  'No scoped Atlas matches.'
}

Write-Host "`nTC3: Orchestrator handoff clarity"
Select-String -Path '.github/copilot-instructions.dreamers.md','.github/agents/echo.agent.md','.github/agents/forge.agent.md','.github/agents/probe.agent.md','.github/agents/sage.agent.md','.github/agents/sentinel.agent.md' -Pattern 'orchestrator','passes task context directly in the prompt','reads them directly','plans, delegates, and coordinates','routes to Forge' | ForEach-Object { "{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }

Write-Host "`nTC4: Branch provenance in implementation notes"
Select-String -Path '.dreamers/forge/implementation.md' -Pattern 'local `master`','user-approved fallback','no `origin` remote was configured' | ForEach-Object { "{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
```

**Expected output**
- `SKILL.md:24` shows `ask_user` with choice `["Approved"]` and inline freeform corrections handled in the same interaction.
- Scoped `.github` scan prints `No scoped Atlas matches.`
- Shared instructions and changed agent files print orchestrator wording that explicitly says the orchestrator passes prompt context, reads workspace outputs, plans/delegates, or routes follow-up work.
- `forge/implementation.md:35` prints the local-`master` / missing-`origin` fallback note.

### 2. Verify the obsolete correction branch is gone and document the absent `hone` scope item
```powershell
$ErrorActionPreference='Stop'
Write-Host 'TC1b: Negative check for separate correction choice'
$skillPath = '.github/skills/dreamers-full/SKILL.md'
$correctionsNeeded = Select-String -Path $skillPath -Pattern 'Corrections needed'
if ($correctionsNeeded) {
  $correctionsNeeded | ForEach-Object { "FOUND {0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
  exit 1
} else {
  'No "Corrections needed" choice remains in SKILL.md.'
}

Write-Host "`nScope note: hone.agent.md presence check"
if (Test-Path '.github/agents/hone.agent.md') {
  '.github/agents/hone.agent.md exists.'
} else {
  '.github/agents/hone.agent.md does not exist; plan scope item is not applicable to committed files.'
}
```

**Expected output**
- `No "Corrections needed" choice remains in SKILL.md.`
- `.github/agents/hone.agent.md does not exist; plan scope item is not applicable to committed files.`

## Result
- All commands passed.
- No bugs found.
- Ready for Echo / close-out from Probe's side.
