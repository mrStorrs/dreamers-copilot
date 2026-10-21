# PR workflow

Apply the embedded `dreamers-kernel`, `git-workflow`, `pr-description` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Todo - Before you begin.
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## Step 1 — Pre-push verification
- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

## Step 2 — Push
- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

## Step 3 — Open the PR
- Draft the PR body using the embedded `pr-description` template below.
- `gh pr create --base <DEFAULT> --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

## Step 4 — Archive shipped plan artifacts
- If this PR ships a Dreamers plan from `.dreamers/plans/feature-<slug>/`, archive after the PR is created.
- Single-plan feature directory: move `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/`.
- Multi-plan feature directory or manifest sequence: create `.dreamers/plans/archive/feature-<slug>/` if needed, move only the shipped `plan-NN-*.md` file(s) into it, and leave unfinished plans in the live feature directory.
- If `manifest.md` exists, keep it live while any unfinished plan file remains. After the last unfinished plan ships, move `manifest.md` into the same archive directory and remove the now-empty live feature directory.
- If no feature directory applies, skip this step.

## Exit
- PR URL. Include moved archive path(s) when Step 4 archived anything.
