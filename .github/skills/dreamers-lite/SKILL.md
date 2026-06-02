---
name: dreamers-lite
description: 'Lean end-to-end Dreamers pipeline. Reviews project context, proposes a compact plan with critique, writes the approved plan, implements tests-first, runs Vigil once, applies findings, runs docs when triggered, commits, and opens the PR. Triggers: /dreamers-lite, lite pipeline, lightweight feature, quick ship.'
argument-hint: '<task description>'
---

$ARGUMENTS

If no task description was provided, halt + ask.

## Rule

Lite removes ceremony, not standards. Preserve plan adherence, tests-first implementation, Vigil review, full-refactor surfacing, and validation.

## Todo - Before you begin.
- Declare a todo list marking all phases at entry: Phase 1 / Phase 2 / Phase 3 cycle-N / Phase 4.

## Phase 1 - Context + proposal
- Anchor to remote truth per `git-workflow`: detect default branch, fetch, read `origin/$DEFAULT_BRANCH` log.
- Read project instructions and relevant code. Verify cited artifacts before claiming behavior.
- Ask one clarification batch if required. Do not trickle questions.
- Draft a compact proposal in chat:
  - Goal
  - Plan Shape: single plan / multi-plan recommended / full recommended; manifest yes/no; why
  - Scope
  - Acceptance Criteria: numbered Given/When/Then with `*Layer: ...*`
  - Out of Scope
  - Constraints
  - Critique / Risks / Simpler Options
  - Verification
- If full is recommended, present it as optional. User may continue in lite.
- `request_information`: `Approved - write plan and implement` / `Revise` / `Halt` / `Other`.
- On `Revise`, update the proposal, re-critique, and re-present. Approval is the implementation-start gate.

## Phase 2 - Plan file + branch
- Write approved proposal into `.dreamers/plans/feature-<slug>/` as compact guide-compatible plan file(s).
- Use plan sections only: Goal, Context, Acceptance Criteria, Out of Scope, Constraints, optional Design Decisions, optional UI, Verification.
- If multiple plans share constraints, decisions, data models, or end-to-end ACs, write `manifest.md`; otherwise skip manifest.
- Self-check plan structure against `plan-writing-guide.md`. Fix violations before implementation.
- Set up branch per `git-workflow`: checkout fresh default, pull, cut `feat/<slug>`, confirm `.dreamers/` is gitignored.

## Phase 3 - Per plan implementation + Vigil

For each plan in sequence:

### Step 1 - Tests
- Read the plan. For each AC, write at least one failing test at the annotated layer. Stage with `git add`. Do not run yet.

### Step 2 - Implement
- Edit production files per plan scope, `comment-rules`, `logging-discipline`, and `testing-mandate`. Stage as you go.

### Step 3 - Validate
- Run the project's type-check and test commands from `.github/copilot-instructions.md`. Fix inline, max 3 attempts, then halt.
- Update `./test-benchmarks.md` after passing if the project uses it.

### Step 4 - Vigil review
- Spawn `vigil` once with plan path, changed-files scope, branch/default names, validation commands/results, and this line: `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`
- Require Vigil to write one `.dreamers/reviews/vigil-*.md` artifact and return only status, counts, artifact path, blocked reason, and open questions.
- Read the artifact before applying findings.
- `Blocked` -> halt and surface the artifact path.
- Open questions -> ask user once, carry decisions into finding application.

### Step 5 - Apply findings
- Sort artifact findings by severity: critical, high, medium, low.
- Conflict resolution: correctness/security > test-coverage > maintainability > simplicity. Genuine ambiguity -> ask.
- Major-refactor scope triggers a gate when any finding needs a new module/top-level directory, schema/data-model change, cross-subsystem refactor, new public exported symbol, files outside plan scope, or Vigil full-refactor wording.
- For each major-refactor group, ask: `Apply now` / `Defer - create follow-up plan` / `Continue lite scope` / `Other`.
  - `Apply now` -> fix inline, stage, re-run validation.
  - `Defer` -> create a stub plan under `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md`; do not apply now.
  - `Continue lite scope` -> do not apply; record unresolved finding for PR summary.
  - `Other` -> follow user direction.
- Apply non-deferred, non-continued findings as targeted edits. Stage. Re-run validation after fixes.

### Step 6 - User testing
- Trigger only when the plan says user testing is required, manual verification is required, the change is user-facing, build/distribution is required, Vigil requests user validation, or the user asked to test.
- When triggered, read `.github/dreamers/templates/user-testing-gate.md` and present that gate.
- On bug, fix inline, validate, decide whether to re-run Vigil based on changed risk. Re-present the gate.

### Between cycles
- If more plans remain, run an inline drift check against the next plan before continuing.
- Commit the completed plan when validation is green and user testing, if any, is approved.

## Phase 4 - Close-out
- Run `/dreamers-docs --branch` only when the diff changes user-facing behavior, public API, config/env/build, install behavior, docs, or Dreamers/project instructions.
- Commit any staged docs. Skip if nothing staged.
- Invoke `/dreamers-pr` immediately after commits are ready. No separate pre-PR approval gate.
- Exit with PR URL, plan paths, Vigil artifact paths, unresolved continued findings, docs status, and validation commands.

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
- Commit message format follows `.github/instructions/git.instructions.md` (if present). Pipeline-specific bits:
  - Subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes — see git.instructions.md for the breaking-change footer rule)

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Unless explicitly requested by the user.
</git-workflow>

<testing-mandate>
# Testing Coverage Mandate (MANDATORY)

Every plan must express its test coverage intent through the Acceptance Criteria's Layer annotations. The planner specifies *what observable outcome* the AC requires and *which test layer* covers it. The implementer (orchestrator at `/dreamers-implement` Step 1) writes the actual tests from each AC's Given/When/Then.

## How test coverage is expressed in plans (new format)

Plan ACs are numbered Given/When/Then statements with a Layer annotation per AC. See `plan-writing-guide.md` § "Acceptance Criteria format" for the canonical spec.

```
<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
3. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: E2E.*
</acceptance_criteria>
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

**Regression risks**
- Anything touching existing behavior that could break — call out the specific existing test or flow at risk in the plan's Context section.

If a layer cannot be covered automatically (e.g., camera permission flows), flag it explicitly as a manual-verification requirement in the plan's Verification section with a reason.

## Probe's layer audit (consumes the new format)

During the full-pipeline review lane that includes Probe, the layer audit reads each AC's `*Layer: ...*` annotation to verify coverage at each layer was implemented. Probe blocks the cycle if any AC's annotated layer lacks a corresponding green test.

## Test benchmarks

Each project that uses `/dreamers-implement` maintains a `./test-benchmarks.md` file at the project root. The file records measured run times per test command so the orchestrator can set realistic timeouts.

- **File path:** `./test-benchmarks.md` at the project root (committed to version control).
- **Recommended-timeout formula:** `max(last_run_time × 2, 30s)` — the 2× multiplier accounts for machine variance; 30s is a non-negotiable floor.
- **Orchestrator updates** the row for each test command after every successful test run. **Humans may edit** the `Notes` column to capture CI environment factors or known flakiness.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).
</testing-mandate>

<comment-rules>
# Comment Rules

## Core principle
Comments must add value that the code cannot express itself. Concise, no fluff, no separators — value only.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes
- License headers

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

## Strict prohibitions
- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words
</comment-rules>

<logging-discipline>
# Logging Discipline

Rules for log calls — what to write, what to flag in review.

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, it is the binding spec.
2. **Else: match surrounding code.** Existing log calls in the same module and nearest neighbors define:
   - Logger library / import path (do not introduce a new logger where one already exists).
   - Level conventions in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).
3. **Never log:** secrets, tokens, PII, full request/response bodies. No exceptions.
4. **Neither rule yields a clear answer** → raise an open question via `request_information` rather than guessing.
</logging-discipline>

<reviewer-findings-format>
# Reviewer Findings Format

**Status line** (one of):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:

```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

- `severity` ∈ `critical` / `high` / `medium` / `low`
- `lens-tag` ∈ `correctness` / `security` / `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` — absolute or repo-relative path + line number
- `what was wrong → suggested fix` — one-line description + targeted fix the caller can apply mechanically

**Observations** (optional) — out-of-scope notes that aren't findings. The caller may or may not act on them.

**Open questions** (optional) — items needing user judgment. Use "none" if no questions.

Reviewers are read-only / report-only. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
