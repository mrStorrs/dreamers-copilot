---
name: dreamers-plan-verify
description: 'Inline drift check on a plan against current codebase reality. Re-reads the plan, compares against current state, reports drift items. No subagent — orchestrator does it inline. Triggers: /dreamers-plan-verify, verify plan, check plan applies, plan drift check.'
argument-hint: 'path/to/plan.md'
---

<dreamers-kernel>
# Dreamers Kernel

## Subagent allowlist (HARD RULE)

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Continuation principle

At every natural pause between phases — where the skill has produced a meaningful result and the user could redirect — call `request_information` with three choices: `Continue` / `Halt for now` / `Other` (freeform). Never silently advance; never silently stop. On `Halt`, emit a one-line resume command and stop.

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Read plan file
- [ ] Read current code (cited paths, signatures, data models, test files)
- [ ] Drift assessment (compare plan assertions against current state)
- [ ] Report (no change or drift-detected list)

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

This skill is always invoked standalone — declare its own todo. There is no composed mode (per `dreamers-kernel.md` § "Single-owner todo": skills do not invoke other skills as sub-routines in this system).

---

## The check

Read the plan file passed as `$ARGUMENTS`. If no plan path is provided, halt and ask the user.

For each element the plan references, verify against the current codebase:

1. **File paths cited in the plan** — does each path exist? If a plan says "modify `src/auth/login.ts`," check that the file is present.
2. **Method / function signatures** — if the plan cites an existing function (e.g., "extend `loginUser(email, password)` to accept `mfaToken`"), read the function definition and verify the current signature matches the plan's assumption.
3. **Data model shapes** — if the plan references a DB table, model class, or interface, read it and verify the plan's assumptions hold.
4. **Test files / cases** — if the plan cites existing tests as a starting point, verify those tests exist and are scoped as the plan describes.
5. **Acceptance Criteria measurability** — re-evaluate whether each AC is still measurable against the current code. (An AC like "user can filter by date" requires a filter mechanism to exist or be plannable; if the underlying API has changed, the AC may need rewording.)
6. **Constraints** — re-check whether stated constraints (technical, process, hard rules) still hold (e.g., "must not change the existing API" — does the API still look as the plan described?). Note: in the new plan format, risks are folded into Constraints as hard rules; there is no separate Risks section to verify.

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

## Use cases

- **Before invoking `/dreamers-implement`** on an older plan: catch drift early.
- **Between sequential plans in `/dreamers-full`** (multi-plan mode): orchestrator can invoke this to check the next plan against the now-current state after the previous plan shipped.
- **Standalone** sanity check when you have a plan file and want to know if it's still relevant.
