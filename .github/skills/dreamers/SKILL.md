---
name: dreamers
description: 'Adaptive end-to-end Dreamers delivery pipeline. Accepts a task description, approved plan path(s), or a feature manifest; routes empty/help input to read-only guidance; plans task input with default Grill; implements tests-first; selects Vigil or Sentinel + Probe + Hone from plan type and risk; applies artifact-backed findings; runs triggered user testing, documentation, and retrospectives; then opens a reviewed PR. Use for /dreamers, plan and implement, ship a feature, or deliver an existing Dreamers plan.'
argument-hint: '<task description> | [--no-grill] | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Route input

Normalize whitespace before routing.

- Empty or whitespace-only input, help, --help, or -h: invoke /dreamers-help as a read-only delegation and halt this delivery workflow. Do not inspect or mutate repository, git, mailbox, or external state first.
- Task description: use planning mode.
- Resolved plan path or paths: use plan mode.
- A resolved manifest.md: use manifest mode.
- Otherwise halt and ask for a task, plan path, or manifest.

Plan paths must resolve under .dreamers/plans/ and be named plan-*.md. A manifest must resolve under .dreamers/plans/ and be named manifest.md. Reject missing or escaping paths.

## Start and resolve artifacts

Declare the complete parent todo at entry. After help routing, apply git-workflow startup verification before reading .dreamers files.

### Planning mode

- Invoke /dreamers-plan with the task description. Task descriptions run Grill by default.
- Pass through --no-grill or unmistakable natural-language direction such as "do not grill" or "skip the interview"; strip control syntax from the actual task.
- Wait for /dreamers-plan to write and approve the smallest suitable plan set. Capture its paths and any manifest.
- Plan approval authorizes implementation. Do not add an implementation-start gate.
- If planning halts without approval, halt this skill.

<planning-grill>
### Phase 1A — Grill

For task descriptions, run Grill by default. Skip it only when the user supplies
--no-grill or unmistakable natural-language direction such as "do not grill"
or "skip the interview." Record the reason, remove control syntax from the task
description, and continue through proposal and plan-quality checks.

Plan path and manifest artifact modes skip Grill because the user supplied the
implementation specification. They still require artifact quality and drift
checks.

```
Interview me relentlessly about every aspect of this plan until
we reach a shared understanding. Walk down each branch of the design
tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore
the codebase instead.

When a decision still needs user input, use `request_information`.
Ask one blocking question at a time; do not dump a batch of questions
in chat. Each question must include exactly these choices:

1. Your recommended answer, labeled as recommended.
2. The strongest viable alternate.
3. `Other` for freeform direction.

After each answer, fold the decision into the shared understanding,
then continue to the next unresolved branch.
```
</planning-grill>

### Plan and manifest modes

- Skip Grill, replanning, plan rewriting, and implementation-start approval.
- Preserve supplied plan order. For a manifest, preserve its plan sequence and carry its shared constraints, decisions, contracts, and end-to-end ACs into every cycle and reviewer prompt.
- Read each plan before branch setup. Detect Plan-type, read plan-guide-selector.md, then read only plan-guide-lite.md, plan-guide-standard.md, or plan-guide-complex.md as selected.
- Reject missing required sections, placeholders, missing or invalid AC Layer annotations, unresolved open questions, and unverifiable citations presented as facts.
- A missing Plan-type is legacy input; warn and continue only with explicit user approval.

### Independent adaptive decisions

Decide independently: ship strategy, reviewer rerun, documentation need, and retrospective need. State each selected value and one-sentence rationale. Honor explicit user overrides and ask only when classification is genuinely ambiguous.

- Select INCREMENTAL for independent plans, different repositories or subsystems, or standalone value that should ship first.
- Select ATOMIC for overlapping files, ordered contract or migration work, or plans that require joint verification. Conflicting signals default to ATOMIC.
- Never add a routine strategy confirmation gate.

### Branch setup

After artifact quality checks pass, execute git-workflow branch setup once per repository: checkout the detected default branch, pull it from origin, cut the planned feature branch, confirm branch identity with the recent log, and verify .dreamers/ is ignored. Read open .dreamers/improvements.md items and action, defer with a reason, or close each relevant item before the first implementation edit. A cross-repository INCREMENTAL sequence repeats startup verification and branch setup only after the prior repository transfer gate is approved.

## Implement each plan inline

Apply dreamers-kernel, testing-mandate, comment-rules, and logging-discipline. Implementation and git work remain inline.

1. Re-read the plan and drift-check cited paths, signatures, and ACs against the landed branch diff.
2. For every Given/When/Then AC, write at least one failing test at each annotated Layer. Stage explicit test paths and do not run them yet.
3. Implement only the plan scope. Stage explicit production paths as work lands.
4. Run the project type-check, tests, build, and lint commands required by project instructions. Fix inline for at most three attempts, record each result, and update test-benchmarks.md after green runs when present.
5. Select and run the initial reviewer lane below.
6. Apply non-deferred findings, rerun required automated validation, decide whether a reviewer rerun is warranted, and process that artifact before continuing.
7. Run the triggered user-testing gate when required.

<review-selection>
# Review Selection

Use this contract for the initial review and any reviewer rerun in a PR-bearing Dreamers workflow.

## Initial lane

- A complex plan selects Sentinel + Probe + Hone through the full /dreamers-review lane.
- A low-risk lite or standard plan selects Vigil.
- Any danger or high-risk trigger overrides a smaller plan type and selects the triad:
  - Security, authentication, authorization, privacy, payment, secret, or permission changes.
  - Schema, migration, persistence, destructive-data, concurrency, or irreversible-side-effect changes.
  - Public or breaking API, dependency, build, distribution, or cross-subsystem changes.
  - Rollback that requires operator action or data recovery instead of reverting the feature commit.
- PR-bearing work receives at least Vigil unless the user explicitly requests that review be skipped.

## Decision behavior

- State the selected reviewer lane and a one-sentence rationale, then proceed without a routine confirmation gate.
- An explicit user override wins and remains authoritative. Before a requested downshift, surface the concrete risk being accepted.
- If classification is genuinely ambiguous, ask once before review. Do not silently promote or downshift.
- Record the selected lane, rationale, trigger or plan type, and any user override in the cycle summary.

## Invocation

- For Vigil, spawn vigil directly with the plan path, changed-file scope, branch and default names, validation commands/results, shared manifest context when present, and prior review artifacts when applicable.
- For the triad, invoke /dreamers-review --branch with the plan path and shared manifest context.
- Read every reviewer artifact before reporting or applying findings. Blocked halts the cycle; open questions return to the user.

## Reruns

- Decide reviewer reruns independently from plan type, ship strategy, documentation, and retrospective decisions.
- Skip a rerun when fixes are small and automated validation directly covers them; record the reason.
- Use Vigil for a normal rerun after targeted fixes.
- Escalate a rerun to the triad only when the new change set itself meets a danger/high-risk trigger. A selected /dreamers-review lane is valid when one specific lens is sufficient.
- State the rerun choice and rationale and proceed without a routine gate. Ask only when the new risk is genuinely ambiguous; explicit user overrides remain authoritative.
</review-selection>

### Reviewer handoff

- State the selected lane, rationale, and any explicit user override before invocation, then proceed without confirmation.
- Vigil writes one vigil artifact. The full /dreamers-review lane writes Sentinel, Probe, and Hone artifacts.
- Every delegated prompt includes the absolute plan path and the Dreamers kernel prompt fields. Wait for the role, then read its artifact.
- Blocked status halts the cycle and is surfaced verbatim with the artifact path. Ask each open question before applying findings.

### Apply findings

Sort findings critical to low. Resolve conflicts by correctness/security, then test coverage, then simplicity. Ask when ambiguity remains.

Apply targeted fixes inline unless the suggested fix triggers the major scope expansion gate through any of:

- A new module or top-level directory outside planned scope.
- A schema or data-model change.
- A cross-subsystem refactor or broad rewrite.
- A new public API, exported symbol, dependency, or persistence behavior not specified by the plan.
- Files outside plan scope.
- Full-refactor language from Hone or Vigil.

Present reviewer, severity, lens, location, finding, suggested fix, triggered criterion, rationale, and breadth estimate. Offer Apply now / Defer - create follow-up plan / Other. Apply now fixes and revalidates. Defer writes a right-sized stub plan under .dreamers/plans/ and continues. Never silently apply or defer.

Reviewer reruns follow review-selection. Route every rerun artifact through this same finding process.

### User-testing gate

Trigger user testing when the plan requires manual verification, the change is user-facing, build or distribution verification is required, a reviewer requests it, or the user asked to test the area. Otherwise record the skip.

Read .github/dreamers/templates/user-testing-gate.md and present its numbered Testing steps and Notes exactly. Offer exactly Approved / Bug found (enter text) / Other (enter text). A bug is fixed inline, revalidated, reviewed again when warranted, and returned to the same gate.

## Complete a cycle

- Commit exactly once per plan after review findings, validation, and required user testing are complete. Use the project conventional-commit style, an explicit Plan: feature-.../plan-... line, and the Dreamers co-author trailer.
- Before the next plan, drift-check its paths, signatures, ACs, and shared manifest context.
- INCREMENTAL: decide documentation need, invoke /dreamers-docs --branch when documentable, commit any docs in the cycle commit, present the mandatory pre-PR approval gate, invoke /dreamers-pr, and halt until the user confirms merge. Start the next repository or cycle from a fresh default branch.
- ATOMIC: commit without pushing and continue. Push exactly once at final PR creation.

## Close out

- Decide documentation need from the landed diff. Invoke /dreamers-docs --branch when user-facing or documentable; otherwise record the skip.
- Write a retro and append .dreamers/improvements.md only when triggered by multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or explicit user request. Otherwise record that retrospective and improvements were skipped.
- Include an AC coverage matrix and testing bugs in any retro; include regression analysis only for an originating bug fix.
- Stage explicit paths and create the final commit only when staged work remains.
- Present the mandatory pre-PR approval gate with milestone summary, validation, review artifacts, user-testing status, commits, and PR scope. Offer Approved / Halt / Other.
- On approval invoke /dreamers-pr, passing any referenced issue. Capture the PR URL.
- After PR creation, surface open retro improvements and project-state drift only. Do not auto-commit.

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

During any review lane that includes Probe, the layer audit reads each AC's annotated Layer to verify coverage at each layer was implemented. Probe blocks the cycle if an AC's annotated layer lacks a corresponding green test.

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

## Artifact contract

Each reviewer writes exactly one markdown artifact under `.dreamers/reviews/`:

`.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md`

Use the branch, plan slug, or task slug for `<slug>`. If unavailable, use `review`.

The artifact is the durable handoff. Chat output is only a short status pointer with the artifact path. The caller must read the artifact before reporting, applying, or deferring findings.

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

Reviewers are read-only / report-only for code, tests, docs, config, scripts, and git state. The only allowed write is the single review artifact. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
