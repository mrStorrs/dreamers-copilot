---
name: dreamers-full
description: 'End-to-end Dreamers pipeline. Invokes /dreamers-plan, then per plan /dreamers-implement → /dreamers-review, then close-out (inline: improvements, retro, archive) + /dreamers-docs (Echo) + /dreamers-pr (push + PR). Triggers: /dreamers-full, full pipeline, plan and implement, new feature, ship a feature.'
argument-hint: '<task description> | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Modes
| Mode | `$ARGUMENTS` | Phase 1 |
|---|---|---|
| 1 | Task description | Invoke `/dreamers-plan $ARGUMENTS` → capture plan paths from its output |
| 2 | Plan path(s) | Skip (plans pre-existing) |
| 3 | `manifest.md` | Skip; read manifest → capture plan sequence + shared-context payload |

## Todo - Before you begin.
- Declare a todo list marking all phases at entry: Phase 1 / Phase 1.5 / Phase 2 cycle-N / Phase 3.

## Phase 1 — Planning (Mode 1 only)
- Invoke `/dreamers-plan $ARGUMENTS`. Wait. Capture plan paths.
- Halt this skill if `/dreamers-plan` halts without approval.

## Phase 1.5 — Ship strategy (multi-plan only)
- Score against `plan-writing-guide.md` § "Ship strategy heuristics."
- `request_information`: `INCREMENTAL` / `ATOMIC` / `Halt` / `Other` + recommendation + one-sentence reasoning. Capture as `strategy`.

## Phase 2 — Per plan Implementation and review
For each plan in sequence:
- Invoke `/dreamers-implement <plan-path>`. Wait.
- Invoke `/dreamers-review`. Wait.
- Between cycles (more plans remain):
  - **Drift check** (inline): read next plan; cited paths exist; signatures match; ACs valid vs landed diff. Drift → surface; user revises/skips/halts.
  - **INCREMENTAL** (light close-out for this plan):
    - Invoke `/dreamers-docs --branch` if the just-completed plan's diff has user-facing or documentable changes.
    - `git commit` with conventional-commits style + `Plan: feature-<slug>/plan-NN-<name>` body line + `Co-authored-by: The Dreamers System` trailer.
    - User approval gate via `request_information` (Approved/Halt/Other).
    - Invoke `/dreamers-pr`. Capture PR URL.
    - `request_information` Continue/Halt/Other. Continue: wait for user confirm-merged → re-cut feature branch from default → next cycle.
  - **ATOMIC**: `request_information` Continue/Halt/Other → next cycle.

## Phase 3 — Close-out (FULL, milestone end)
- Append improvements to `.dreamers/improvements.md` (dated, one sentence each, reference retro path below).
- Invoke `/dreamers-docs --branch`. Stage Echo's edits.
- Write retro `.dreamers/retros/retro-d<N>-<name>.md`:
  - What worked well
  - Friction points
  - Proposed improvements
  - AC coverage matrix (rolled up from cycles)
  - Bugs from user-testing (if any)
  - Regression analysis (only if originating task was a bug fix)
- Final commit: `git add <explicit-paths>` (no `-A`) + `git commit` per conventional-commits style with `Plan: feature-<slug>/plan-NN-<name>` body + trailer. Skip if nothing staged.
- **User approval gate** (MANDATORY): present milestone summary (plans, AC coverage, review summary, Echo result, retro path, final commit, issue ref). `request_information` Approved/Halt/Other. Halt → emit resume command + stop.
- Invoke `/dreamers-pr` (pass `--issue <#|url>` if `$ARGUMENTS` referenced one). Capture PR URL.
- **Plan archive**: for each `.dreamers/plans/feature-<slug>/` whose every plan's PR state is `MERGED` (verify via `gh pr view <#> --json state -q .state`): `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/`. Whole directory only. Skip silently if nothing ready.
- **Post-PR scan**: surface open retro improvements + ask user before applying any. Flag project-state drift (PR description vs plans shipped; `git log origin/$DEFAULT -10`; `.dreamers/improvements.md` open items; `.dreamers/retros/` open items). No auto-commit after PR opens.

## Failure handling
- Any invoked skill returns Blocked/Halt → surface output verbatim + halt this skill with resume command pointing at the next step.

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
   - **Note:** this catches prior features not already archived by `/dreamers-full` Phase 3 (the primary archive trigger). If archive already ran, the source directory won't exist and the `mv` is a no-op — skip silently.
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
