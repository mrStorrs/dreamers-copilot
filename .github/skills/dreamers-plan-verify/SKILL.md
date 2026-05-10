---
name: dreamers-plan-verify
description: 'Lightweight Nova-verify check on the next sub-plan against current codebase reality. Halts on drift. Triggers: /dreamers-plan-verify, verify next plan, check sub-plan applicability.'
argument-hint: 'path/to/next-subplan.md'
---

## What this skill does

Wraps Nova in `verify` mode for the between-sub-plan applicability check. Nova reads the next sub-plan, the just-completed sub-plan's git diff + commit message, and surviving Probe artifacts. Returns one of:
- `No change — proceed`
- `Drift detected — halt` (with specific drift items)

$ARGUMENTS

---

## Required argument

The first argument MUST be the path to the next sub-plan file (e.g., `.dreamers/plans/plan-foo-b.md`). If no path is provided, stop and ask before proceeding.

---

## Invocation modes

- **Standalone:** user invokes after a sub-plan completes to manually check the next one.
- **From orchestrator:** `/dreamers-full` and `/dreamers-implement` invoke this between sub-plans automatically. Functionally identical.

---

## Spawn Nova

`task(agent_type: "nova", mode: "sync")` with prompt that includes:
- `mode: "verify"` (explicit — Nova requires explicit mode for skill invocation)
- Path to the next sub-plan
- The just-completed sub-plan's commit hash (Nova reads `git diff <commit>` and `git log <commit> -1 --format=%B`)
- The default branch name
- List of surviving Probe artifact paths if available

---

## Output

Chat output is Nova's chat output (passed through):
- Mode: verify
- Decision: `No change — proceed` OR `Drift detected — halt`
- Drift items list (if drift detected)

If `Drift detected — halt`: surface the specific drift items to the user and halt the calling pipeline. The user can request escalation to Nova `replan` mode if recovery is needed.
