---
name: dreamers
description: 'Deliver a task, approved plan(s), or manifest through planning, implementation, review, user testing, docs, and PR. Empty/help input opens /dreamers-help. Triggers: /dreamers, plan and implement, new feature, ship a feature.'
argument-hint: '<help | task description> | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Route input

Empty input, `help`, `--help`, or `-h`: invoke `/dreamers-help` read-only and stop before inspecting or changing repository, git, mailbox, or external state.

For delivery, declare a todo covering planning/start approval or artifact resolution, each plan cycle, and close-out. Apply `dreamers-kernel` and complete `git-workflow` startup verification before reading any `.dreamers/` files.

| Input | Route |
|---|---|
| Task description | Phase 1, then the implementation-start gate. |
| Plan path(s) | Resolve and read the plans in supplied order; skip Phase 1 and its start gate. |
| `manifest.md` | Resolve and read the manifest; capture its plan sequence and shared context; skip Phase 1 and its start gate. |

Treat `.md` path arguments, including `feature-<slug>/plan-NN-<name>.md` and `feature-<slug>/manifest.md`, as artifact input. Resolve feature-relative paths under `.dreamers/plans/`. Unrecognized input: halt and ask for a task, plan path, manifest, or help.

Supplied artifacts are implementation authorization: do not re-plan, replace them, or ask to start. 

## Phase 1: Planning and start approval (task input only)

1. Invoke `/dreamers-plan $ARGUMENTS`; capture the returned plan paths.
2. Validate the plans artifacts were created. Present paths, implementation scope, test intent, and the ship-strategy recommendation when multiple plans will run.
3. Use `request_information`:
   - Single plan: `Approved — start implementation` / `Revise plan` / `Halt` / `Other`.
   - Multiple plans: `Approved — start INCREMENTAL` / `Approved — start ATOMIC` / `Revise plan` / `Halt` / `Other`.
4. Capture the selected strategy. For revisions, apply unambiguous minor edits inline.

## Phase 2 — Per-plan cycle

Set up the feature branch once per `git-workflow`.  Process plans in sequence, carrying manifest shared context into implementation.

### Implement and review

1. Invoke `/dreamers-implement <absolute-plan-path>`
2. On success, invoke `/dreamers-review --branch <absolute-plan-path>` once.
3. If review returns non-major refactor actionable items loop implement -> review up to 3 times. If it is a major refactor then present it to the user and ask if they would they would like to defer or action on it. If defered append to a project-root `defered.md`. On the review loops use `/dreamers-review --vigil --branch <absolute-plan-path>`
4. If you reach the loop cap, ask the user if they would like you to continue the review implement -> review loop. 

### User testing

Trigger when the plan requires manual verification, the change is user-facing, build/distribution is needed, reviewers request user validation, or the user asked to test the area. Otherwise record `user testing skipped — no manual verification trigger` in the cycle summary.

When triggered, use `user-testing-gate` below. After bug fixes and automated validation, apply Review reruns before re-presenting the gate. Commit only at the applicable close-out.

### Between cycles

Before the next plan, check cited paths, signatures, and ACs against the landed diff. Surface drift for the user to revise, skip, or halt.

- **ATOMIC:** commit this plan with a `Plan: feature-<slug>/plan-NN-<name>` body line; do not push. Continue to the next cycle.
- **INCREMENTAL:** invoke `/dreamers-docs --branch` when this plan has user-facing/documentable changes; stage and commit with the `Plan:` body line. Present plan summary, validation, and PR scope through `request_information`: `Approved` / `Halt` / `Other`. On approval invoke `/dreamers-pr` and capture its URL. Wait for the user to confirm merge, then repeat feature-branch setup from updated default before the next cycle.

At either pre-PR gate, Halt means emit a resume command and stop; Other follows user direction.

## Phase 3 — Milestone close-out

1. If there were any issues involving the ai or workflow suggest any edits to repository ai instruction scaffolding. 
2. invoke `/dreamers-docs --branch`
3. stage explicit paths (`git add <paths>`, no `-A`) and commit remaining changes with a conventional subject
4. present the milestone summary through `request_information`: `Approved` / `Halt` / `Other`. 
5. upon approval invoke `/dreamers-pr`; pass `--issue <#|url>` if input referenced an issue. Capture the
6. present PR url to user. 

<dreamers-kernel>
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


<user-testing-gate>
# User Testing Gate Template

Use this template whenever the Dreamers pipeline pauses for user testing.

Call `request_information`. Do not replace this gate with an unstructured chat prompt unless the tool is unavailable.

## Prompt body

The prompt body must contain exactly these two sections, in this order:

### Testing steps

Number every required user action and verification step with `1.`, `2.`, `3.`.

Include:
- Plan ID + path.
- A one-sentence summary of what changed in this cycle.
- Every special action required before testing, including build type, packaging, deploy, install, cache reset, seed data, feature flag, account state, device/browser, or distribution steps.
- Build/distribute steps from `.github/instructions/build.instructions.md` when present.
- If `.github/instructions/build.instructions.md` is absent and a build/distribution action is needed, include a numbered step asking the user to perform the project-specific build/distribution manually.
- Every manual test the user should perform, derived from the plan ACs and any reviewer-requested validation.
- The expected result for each test step.

Do not collapse tests into a paragraph. Do not use bullets for the testing steps.

### Notes

Include:
- Known limitations and out-of-scope items.
- Relevant automated validation already run.
- Any environment assumptions or risks the user should know before approving.

Use `None` only when there are no notes.

## Options

Provide exactly these three options:

1. `Approved`
2. `Bug found (enter text)`
3. `Other (enter text)`

`Bug found (enter text)` and `Other (enter text)` must accept freeform text.

## Response handling

- `Approved` -> continue the pipeline.
- `Bug found (enter text)` -> capture the bug text, fix inline, rerun required automated validation, then present this same user-testing gate again.
- `Other (enter text)` -> follow the user's direction. If the result still needs user testing sign-off, present this same gate again.
</user-testing-gate>
