**Input:** diff scope, delivery context, and any plan paths or prior review summary. Apply the embedded `dreamers-kernel` rules.

**1. Resolve scope**

- Detect the default branch from `origin/HEAD`, falling back to `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, then `main`; store it as `$DEFAULT_BRANCH`.
- `--branch` (default): scope = `git diff --name-only origin/$DEFAULT_BRANCH...HEAD`.
- `--staged`: scope = union of `git diff --cached --name-only` and `git diff --name-only`.
- If the changed-files list is empty → return `No changes detected` without spawning Echo.

**2. Update docs**

- `task(agent_type: "echo", mode: "sync")`. Prompt MUST include `Do NOT call manage_todo_list.`
- Pass: context (ad-hoc or milestone close-out — caller-supplied), changed-files list, diff base, plan paths (if applicable), prior review summary (if applicable).
- Constraint to Echo: edits docs only — no production code, no tests. Stage with `git add`; do NOT commit.
- Wait for Echo to return its structured chat output.

**3. Handle output**

- `Docs updated — N files changed` → surface doc-changes log to user.
- `No doc updates needed` → return that result.
- Open questions → present each via `request_information`; capture answers; re-spawn Echo with clarification if needed.

**Result:** files Echo touched and the doc-changes log, or no updates needed. Leave documentation staged; do not commit, push, or open a PR.
