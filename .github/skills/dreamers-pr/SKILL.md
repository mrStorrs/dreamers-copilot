---
name: dreamers-pr
description: 'PR creation skill — pushes the current branch, drafts the PR body from pr-description.md template, opens the PR via gh, optionally posts an issue resolution comment. Triggers: /dreamers-pr, open the PR, ship the branch.'
argument-hint: '[--issue <#|url>]'
---

$ARGUMENTS

Template read at runtime via `view`:
- `.github/dreamers/templates/pr-description.md` — PR body shape.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry: Step 1 / Step 2 / Step 3 / Step 4.

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

## Step 4 — Archive shipped feature plan directory
- Use the branch, PR body, and commit history (`Plan:` lines, `feature-<slug>/plan-NN-*.md`, or `feature-<slug>/manifest.md`) to identify the shipped Dreamers plan path(s) or feature directory.
- If no `.dreamers/plans/feature-<slug>/` applies, skip archive and still surface the PR URL.
- If a feature directory applies, archive only when this PR ships that feature's full remaining plan set:
  - Single-plan feature: archive after the PR is created.
  - Multi-plan ATOMIC or final INCREMENTAL PR: archive after the PR is created.
  - Early INCREMENTAL PR with later plans still remaining: do NOT archive.
- Create `.dreamers/plans/archive/` if needed, then move the whole feature directory to `.dreamers/plans/archive/feature-<slug>/` with `mv` (or `Move-Item`). Never archive file-by-file, never use `rm`, and never delete plan files.
- If the directory is already archived or the destination already exists, do not overwrite; note the archive status and continue.

## Exit
- PR URL plus archive status. Surface to the caller.

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
4. **Archive legacy unarchived feature plan directories** — fallback only. Check older feature directories whose shipping PR was created before `/dreamers-pr` archived on PR creation, then later merged (`gh pr list --state merged` or `gh pr view <number>`):
   - **Merged and still active:** move the entire feature directory from `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/` (create the archive dir if it doesn't exist). The PR description is the lasting public record; the archived feature directory is preserved locally for easy reference. Use `mv` (or `Move-Item`), not `rm` — never delete plan files.
   - **Open, unmerged, unknown, or already archived:** leave the feature directory in place.
   - **Guardrail:** this is NOT the primary archive trigger. Modern runs archive immediately after the PR that ships the feature/plan set is created. Never archive file-by-file mid-feature, and never archive a multi-plan feature after an early incremental PR if later plans remain.
5. No init commit — the first commit for the milestone is the first thing in the PR diff.

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
- Commit message format follows `.github/instructions/git.instructions.md` (if present). Pipeline-specific bits:
  - Subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes — see git.instructions.md for the breaking-change footer rule)

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Unless explicitly requested by the user.
</git-workflow>
