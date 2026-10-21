# Documentation workflow

Execute this workflow inline with the supplied input. Resolve links relative to this ref. Read the linked standards before acting. Keep the active skill's todo, gates, and delivery state.

## Todo - Before you begin.
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

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
- Files Echo touched. The caller commits (this workflow does NOT commit, push, or open a PR).

## Dreamers Kernel
Read and apply [dreamers-kernel](dreamers-kernel.md).
