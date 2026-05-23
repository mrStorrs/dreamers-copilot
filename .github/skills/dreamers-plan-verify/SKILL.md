---
name: dreamers-plan-verify
description: 'Inline drift check on a plan against current codebase reality. Re-reads the plan, compares against current state, reports drift items. No subagent — orchestrator does it inline. Triggers: /dreamers-plan-verify, verify plan, check plan applies, plan drift check.'
argument-hint: 'path/to/plan.md'
---

## What this skill does

Re-reads a plan file and checks whether it still applies to the current codebase. Useful when:
- A plan was written some time ago and the code has moved on.
- Multiple plans were written together; an earlier one shipped and may have changed paths / signatures / data shapes the later plans depend on.
- The user wants to confirm a plan is still actionable before invoking `/dreamers-implement`.

The check runs in-skill (no subagent spawn).

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — citation-accuracy rules apply to the verification (verify by reading, not from memory).
- `~/.copilot/dreamers/refs/citation-accuracy.md` — full citation-accuracy spec.
- `~/.copilot/dreamers/refs/plan-content.md` — plan structure (so the verifier knows what to check).

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Read plan file
- [ ] Read current code (cited paths, signatures, data models, test files)
- [ ] Drift assessment (compare plan assertions against current state)
- [ ] Report (no change or drift-detected list)

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-full`, do NOT declare a new list — update the parent's matching Phase 2 drift-check item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## The check

Read the plan file passed as `$ARGUMENTS`. If no plan path is provided, halt and ask the user.

For each element the plan references, verify against the current codebase:

1. **File paths cited in the plan** — does each path exist? If a plan says "modify `src/auth/login.ts`," check that the file is present.
2. **Method / function signatures** — if the plan cites an existing function (e.g., "extend `loginUser(email, password)` to accept `mfaToken`"), read the function definition and verify the current signature matches the plan's assumption.
3. **Data model shapes** — if the plan references a DB table, model class, or interface, read it and verify the plan's assumptions hold.
4. **Test files / cases** — if the plan cites existing tests as a starting point, verify those tests exist and are scoped as the plan describes.
5. **Acceptance Criteria measurability** — re-evaluate whether each AC is still measurable against the current code. (An AC like "user can filter by date" requires a filter mechanism to exist or be plannable; if the underlying API has changed, the AC may need rewording.)
6. **Constraints + Risks** — re-check whether stated constraints still hold (e.g., "must not change the existing API" — does the API still look as the plan described?).

## Output

Return ONE of:

- **`No change — proceed`** — the plan still applies as written. The user / orchestrator can invoke `/dreamers-implement <plan>` confidently.
- **`Drift detected — halt`** — list specific drift items in chat. Each item identifies WHERE in the plan (AC #, §Scope entry, Test Case ID, or line range) and WHAT diverged:
  ```
  - AC #3 — expected: filter by date range / actual: filter API removed in last cycle
  - §Scope file list — expected: src/auth/session.ts / actual: file renamed to src/auth/sessionStore.ts
  ```
  The user decides whether to:
  - Revise the plan inline (and re-run `/dreamers-plan-verify`).
  - Abandon the plan.
  - Accept the drift and proceed (rare; usually means the plan needs updating).

## What this skill does NOT do

- Does NOT modify the plan — only reports drift.
- Does NOT modify any source files.
- Does NOT run tests — verification is read-only.
- Does NOT call any subagent — fully inline.

## Use cases

- **Before invoking `/dreamers-implement`** on an older plan: catch drift early.
- **Between sequential plans in `/dreamers-full`** (multi-plan mode): orchestrator can invoke this to check the next plan against the now-current state after the previous plan shipped.
- **Standalone** sanity check when you have a plan file and want to know if it's still relevant.
