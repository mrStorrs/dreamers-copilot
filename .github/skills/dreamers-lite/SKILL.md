---
name: dreamers-lite
description: 'Deliver a task without planning: implement, test, review with Vigil, update docs, and request PR approval.'
argument-hint: '<task description>'
---

$ARGUMENTS

## Route input

`/dreamers-lite` owns delivery and invokes only its specialized skills for phase work. Never invoke `/dreamers-lite` from itself or switch to `/dreamers` to continue delivery. Wrapped skills return control to this orchestrator without invoking either delivery skill.

Resolve related follow-ups against the existing delivery state before starting a fresh task. Questions and gate responses resume the pending phase. Related bug reports or corrections resume `Fix loop` at `Implementation`, including during user testing or after PR creation. For fresh delivery without a task description, halt + ask.

## Todo - Before you begin.
- Keep one todo for setup, implementation/tests, review, docs, and close-out. Follow `Delivery continuation` in `dreamers.instructions.md` across follow-ups; resume the pending phase instead of repeating setup.

## Phase 1: Branch setup
- Per `git-workflow` (Kernel): fetch + checkout default + pull + cut `fix/<slug>`.

- Inspect the task's scope. Raise ambiguities or critiques through `request_information`; otherwise continue.

## Phase 2: Implementation and review

### Initial implementation and review

1. Invoke `/dreamers-implement <task description and agreed scope>`.
2. Review implementation using `/dreamers-review --vigil --branch <task>`
3. For actionable findings, resume `Fix loop` at `Implementation`. Halt on a blocked review; otherwise continue to `User testing`.

### Fix loop

Retain the owning workflow, todo, task/agreed scope, and branch/PR; reopen affected later stages. Follow `Delivery continuation` for branch reuse and post-PR handling. Do not create a plan or repeat branch setup for active delivery or an open PR.

Allow at most 2 fix cycles. Keep the active count across detours; corrections after completed close-out start a new capped cycle. Before each iteration, check the cap, ask before major refactors, and record deferred findings in root `defered.md`.

Set review scope on entry: `--branch` for findings from the initial branch review; staged + unstaged for other corrections, including user-testing and post-PR bugs. Retain that scope on subsequent iterations.

1. **Implementation.** Invoke `/dreamers-implement <accepted findings or reported problem and agreed correction>` with the current task context.
2. **Review.** After green validation, invoke `/dreamers-review --vigil` with the selected scope and current task context. Actionable findings return to `Implementation` under this loop's gates and cap.
3. **Continue delivery.** Once review passes or all remaining findings are deferred, resume `User testing`, then `Phase 3 - Close out`. For an open PR, use the post-PR close-out in `Delivery continuation`.

Halt on blocked validation/review or unresolved findings at the cap; report what remains.

### User testing

Complete any required user testing before close-out. Bug reports resume `Fix loop` at `Implementation`; after the loop succeeds, request testing sign-off again.

## Phase 3 - Close out

For revisions to an open PR, use the post-PR close-out in `Delivery continuation` instead of the initial close-out below.

1. If there were any issues involving the ai or workflow suggest any edits to repository ai instruction scaffolding. 
2. invoke `/dreamers-docs --staged`
3. stage explicit paths (`git add <paths>`, no `-A`) and commit remaining changes with a conventional subject
4. present the milestone summary through `request_information`: `Approved` / `Halt` / `Other`. 
5. upon approval invoke `/dreamers-pr`; pass `--issue <#|url>` if input referenced an issue. Return the PR URL.

## Dreamers Kernel
<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

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

<testing-mandate>
## Plan template
Every plan must express its test coverage intent through the Acceptance Criteria's Layer annotations.

```
## Acceptance Criteria
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
```

Layer label set (closed): `unit` / `integration` / `E2E` / `perf`. Compound labels allowed when one assertion serves two purposes (e.g., `*Layer: integration / perf.*`).

**Test coverage intent is expressed via the `*Layer: ...*` annotation on each Acceptance Criterion — not via a standalone Test Cases section.** Do not write a separate Test Cases section in a plan; embed the test layer directly in the AC. This keeps ACs and test specification in one place so they never drift.

## Coverage requirement (every plan)

Across all of a plan's ACs, the layer mix must cover the following whenever applicable to the work — think through each layer explicitly:

**Unit layer**
- Each significant function, method, or class in isolation.
- All branches: happy path, edge cases (boundary values, empty/null/max), negative cases (invalid input, error states).
- Any pure logic that does not require a real device, network, or database.

**Integration layer**
- Interactions between layers: repository ↔ data source, ViewModel ↔ repository, service ↔ external API.
- Database reads/writes (real or in-memory, not mocked).
- Auth flows end-to-end within the backend.
- Cloud function triggers and side-effects.

**UI / E2E layer**
- Full user journeys through the UI: screen load → interaction → outcome visible on screen.
- Navigation flows between screens.
- Error and empty states rendered correctly in the UI.
- Any flow that requires a real device or emulator.
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), the plan must include at least one AC with `*Layer: E2E.*` — not just unit/integration. Probe enforces this in the layer audit and blocks if missing.

If a layer cannot be covered automatically (e.g., camera permission flows), put the manual steps, expected result, and reason under the relevant AC; set `User-testing-required: yes`.

## Test benchmarks

Each project that uses `/dreamers-implement` maintains a `./test-benchmarks.md` file at the project root. The file records measured run times per test command so the orchestrator can set realistic timeouts.

- **File path:** `./test-benchmarks.md` at the project root (committed to version control).
- **Recommended-timeout formula:** `max(last_run_time × 2, 30s)` — the 2× multiplier accounts for machine variance; 30s is a non-negotiable floor.
- **Orchestrator updates** the row for each test command after every successful test run. **Humans may edit** the `Notes` column to capture CI environment factors or known flakiness.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).
</testing-mandate>

<comment-rules>
## Core principle
Comments must add value that the code cannot express itself. Concise, no fluff, no separators.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

## Strict prohibitions
- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words
</comment-rules>
