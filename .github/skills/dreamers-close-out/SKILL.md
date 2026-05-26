---
name: dreamers-close-out
description: 'Close-out skill — ships the milestone. Echo docs + retro + commit + user gate + push + PR. Two modes: FULL (default, end of milestone) and LIGHT (--light <plan-path>, mid-sequence in INCREMENTAL). Triggers: /dreamers-close-out, close out the milestone, ship the feature.'
argument-hint: '[--light <plan-path>] [--issue <#|url>]'
---

$ARGUMENTS

Template read at runtime via `view`:
- `.github/dreamers/templates/pr-description.md` — PR body shape.

## Modes
- FULL (default, milestone end, all plans shipped): Steps 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8.
- LIGHT (`--light <plan-path>`, mid-sequence in INCREMENTAL): Steps 2 + 4 + 5 + 6.

LIGHT skips retro, improvements append, plan archive, post-PR scan.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry (skip LIGHT-omitted steps).

## Step 1 — improvements.md milestone-close (FULL only)
- Append new improvement suggestions from this milestone to `.dreamers/improvements.md` (dated, one sentence each, reference the retro file path from Step 3).

## Step 2 — Echo dispatch
- Spawn `echo` via `task(agent_type: "echo", mode: "sync")`. Pass: plan paths, changed files (`git diff --name-only origin/$DEFAULT...HEAD`), diff base, concatenated review summary.
- LIGHT mode: invoke Echo only when the just-completed plan's diff has user-facing or documentable changes.
- Stage Echo's edits.

## Step 3 — Retro (FULL only)
- Write `.dreamers/retros/retro-d<N>-<name>.md`:
  - What worked well
  - Friction points
  - Proposed improvements
  - AC coverage matrix (rolled up from cycles)
  - Bugs from user-testing (if any)
  - Regression analysis (only if originating task was a bug fix)

## Step 4 — Final commit
- `git add <explicit-paths>` (no `-A`).
- `git commit` with conventional-commits style + `Plan: feature-<slug>/plan-NN-<name>` body line + `Co-authored-by: The Dreamers System` trailer.
- If nothing staged, skip — no empty commits.

## Step 5 — User approval gate (MANDATORY)
- Present milestone summary (plans shipped, AC coverage, review summary, Echo result, retro path, final commit, issue ref).
- `request_information`: `Approved` / `Halt` / `Other`. Halt → emit resume command + stop. Other → apply inline corrections + re-run affected steps + re-present.

## Step 6 — Push + open PR
- Pre-push: `git status` clean; `git log --oneline -10` matches expectation.
- `git push -u origin <branch>` (never force).
- Read `pr-description.md` template via `view`. Draft PR body using its shape.
- `gh pr create --base $DEFAULT --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

## Step 7 — Plan archive (FULL only)
- For each `.dreamers/plans/feature-<slug>/` whose every plan's PR state is `MERGED` (verify via `gh pr view <#> --json state -q .state`): `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/`. Whole directory only. Skip silently if nothing ready.

## Step 8 — Post-PR scan (FULL only)
- Surface open retro improvements + ask user before applying any.
- Flag project-state drift: PR description vs plans shipped; `git log origin/$DEFAULT -10`; `.dreamers/improvements.md` open items; `.dreamers/retros/` open items.
- No auto-commit after PR opens. Review-comment/CI fixes need explicit user approval.

## Exit
- PR URL + final summary. The pipeline is done.

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
4. **Archive prior feature's plan directory** — check if the previous feature's PR is merged (`gh pr list --state merged` or `gh pr view <number>`):
   - **Merged:** move the entire feature directory from `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/` (create the archive dir if it doesn't exist). The PR description is the lasting public record; the archived feature directory is preserved locally for easy reference. Use `mv` (or `Move-Item`), not `rm` — never delete plan files. Mid-feature archive (file-by-file) is NOT allowed; only whole-feature-directory archive at the milestone-final PR merge.
   - **Not merged:** leave the feature directory in place.
   - **Note:** this step catches prior features not already archived by `/dreamers-close-out` Step 7 (the primary archive trigger). If close-out already ran on the prior feature, the source directory won't exist and the `mv` is a no-op — skip silently.
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

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
