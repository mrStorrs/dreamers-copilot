# Retro — D1 Dreamers System Cleanup

**Date:** 2026-04-17
**Cycle:** plan-1-dreamers-system-cleanup (4 sub-plans + Hone)
**Branch:** feat/d1-dreamers-system-cleanup
**Commits:** 086b287 (1a) → 9c81b28 (1b) → 02e2180 (1c) → dc6330a (1d) → 52636aa (Hone)

---

## What worked well

- **Sub-plan sequencing** — each sub-plan (1a → 1b → 1c → 1d) was independently testable and merged cleanly without cross-plan bleed.
- **Probe caught real issues mid-cycle** — TC-4 failure in 1d (POSIX commands in dreamers-new-project) and the `sub-plan-loop.md` Hone gap in 1b were both caught by Probe before commit, not after.
- **Hone's observation list was high-signal** — all 6 observations were valid; Sentinel confirmed 1 blocker and 5 advisories from them. No false positives.
- **Batching Sentinel fix rounds** — routing all 7 post-Hone findings to Forge in one pass saved at least two extra cycles.
- **Nova re-verification** — adding Nova's re-verify step between sub-plans prevented stale plan assumptions from reaching Forge; 1d needed the `sub-plan-loop.md` Hone gap scoped in, which Nova caught.

---

## Friction points

- **Sentinel findings format** — Sentinel wrote markdown prose instead of JSON in multiple rounds despite the JSON schema fix in 1a. The orchestrator had to manually reformat findings.md to JSON before routing to Forge each time. The sentinel.agent.md definition update didn't affect the already-running agent instances.
- **No origin remote** — repo has no `origin` remote, which required workarounds in the Hone pass (`git diff master...HEAD` instead of `origin/master...HEAD`) and flagged a real gap in `dreamers-simplify/SKILL.md`'s branch detection (S-01). The skill now uses the canonical two-step detection, but the offline/no-remote case remains fragile in `dreamers-cleanup-comments-branch`.
- **Sub-plan 1d POSIX gap was in scope but missed at planning** — `dreamers-new-project/SKILL.md` had `mkdir -p` and `2>/dev/null`; these were in the audit but weren't explicitly listed in the 1d scope. Probe found them on first pass.
- **Hone couldn't write its workspace file** — `.dreamers/hone/` directory didn't exist when Hone completed; the orchestrator had to create it and write `simplification.md` manually. Hone's agent definition should note that it must create the directory before writing.

---

## Proposed improvements

1. **`sentinel.agent.md` — enforce JSON output format at the prompt boundary**: The agent definition says JSON but agents wrote prose in multiple cycles. Add an explicit output example at the top of the `## Findings format` section showing the JSON array, and add a constraint: "If you output findings in any format other than this JSON array, your output will be rejected."

2. **`hone.agent.md` — add directory-creation step before writing `simplification.md`**: Currently says "Create `.dreamers/hone/` directory if it does not exist" but no command is given. Add `New-Item -ItemType Directory -Force -Path .dreamers/hone | Out-Null` as an explicit pre-write step so Hone never stalls waiting for the orchestrator.

3. **`dreamers-simplify/SKILL.md` — document no-remote fallback**: The canonical two-step detection now handles absent `origin` via the `gh repo view` fallback. Add a note that if both remote and GitHub CLI detection fail, the skill should ask the user to confirm the default branch name rather than defaulting silently to `main`.

4. **`plan-1d` scope gap — add a general POSIX sweep to platform alignment sub-plans**: Future path/platform sub-plans should explicitly include a `grep -r '2>/dev/null\|mkdir -p\|rm -rf' .github/` sweep as a required scope-gathering step so POSIX residue doesn't slip through to Probe.
