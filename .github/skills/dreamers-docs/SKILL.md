---
name: dreamers-docs
description: 'Docs skill — spawns Echo to update Echo-owned sections of .github/copilot-instructions.md plus other project docs (README, CHANGELOG) affected by recent changes. Echo stages edits; does not commit. Triggers: /dreamers-docs, update docs, echo docs update.'
argument-hint: '[--branch | --staged]'
---

$ARGUMENTS

## User overrides

- Explicit user instructions can skip or alter phases/actions.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry: Step 1 / Step 2 / Step 3.

## Step 1 — Resolve diff scope
- `--branch` (default): scope = `git diff --name-only origin/$DEFAULT...HEAD`.
- `--staged`: scope = union of `git diff --cached --name-only` and `git diff --name-only`.
- If the changed-files list is empty → output `No changes detected` and exit.

## Step 2 — Spawn Echo
- `task(agent_type: "echo", mode: "sync")`. Prompt MUST include `Do NOT call manage_todo_list.`
- Pass: context (ad-hoc or milestone close-out — caller-supplied), changed-files list, diff base, plan paths (if applicable), prior review summary (if applicable).
- Constraint to Echo: edits docs only — no production code, no tests. Stage with `git add`; do NOT commit.
- Wait for Echo to return its structured chat output.

## Step 3 — Handle output
- `Docs updated — N files changed` → surface doc-changes log to user.
- `No doc updates needed` → exit.
- Open questions → present each via `request_information`; capture answers; re-spawn Echo with clarification if needed.

## Exit
- Files Echo touched. The caller commits (this skill does NOT commit, push, or open a PR).

## Dreamers Kernel
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
