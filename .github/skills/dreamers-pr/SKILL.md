---
name: dreamers-pr
description: 'PR creation skill — pushes the current branch, drafts the PR body from pr-description.md template, opens the PR via gh, optionally posts an issue resolution comment. Triggers: /dreamers-pr, open the PR, ship the branch.'
argument-hint: '[--issue <#|url>]'
---

$ARGUMENTS

Template read at runtime via `view`:
- `.github/dreamers/templates/pr-description.md` — PR body shape.

## Todo - Before you begin.
- When standalone, declare a todo list for Step 1 / Step 2 / Step 3 / Step 4. When invoked by an outer delivery skill, complete these steps under its existing todo.

## Step 1 — Pre-push verification
- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

## Step 2 — Push
- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

## Step 3 — Open the PR
- Read `pr-description.md` template via `view`.
- Draft PR body using its shape (Summary / Plans shipped / Cumulative diff / End-to-end ACs / Review summary / Test plan).
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

## Dreamers Kernel
<dreamers-kernel>
# Dreamers Kernel

## User overrides

Explicit user instructions can skip or alter phases/actions.

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

<git-workflow>
# Git Workflow (mandatory)

Every milestone uses a feature branch + PR — never work directly on the default branch.

## Startup verification (do this FIRST)
1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

## Branch setup (before invoking `/dreamers-implement`)
1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Confirm `.dreamers/` is in the project's `.gitignore`. If not, add it before any further edits.
4. No init commit — the first commit for the milestone is the first thing in the PR diff.

## Commit discipline (non-negotiable)
1. **Commit at end of each cycle** — one commit per plan in the sequence (single-plan: one commit total; multi-plan: N commits, one per plan).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

## Push discipline (non-negotiable)
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between cycles, or at any other point in the pipeline.

## Post-PR push discipline
If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

## Commit structure (one commit per cycle)
- Exactly **one** commit per plan/cycle, immediately after the reviewer findings have been applied and tests are green (and user testing, if required, is signed off).
- The orchestrator stages changes with `git add` throughout the cycle but does **not** run `git commit` until the cycle ends.
- Commit message subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes).

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Unless explicitly requested by the user.
</git-workflow>
