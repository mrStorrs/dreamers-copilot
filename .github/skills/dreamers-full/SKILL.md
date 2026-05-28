---
name: dreamers-full
description: 'End-to-end Dreamers pipeline. Invokes /dreamers-plan, implements each plan inline (writes tests + code + runs tests), invokes /dreamers-review for findings, applies findings inline (with major-refactor gate), user-testing gate per plan, then close-out (inline + /dreamers-docs + /dreamers-pr). Triggers: /dreamers-full, full pipeline, plan and implement, new feature, ship a feature.'
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

## Phase 2 — Per plan (inline implementation + review)

Branch setup once per `git-workflow` (Kernel): fetch + checkout default + pull + cut `feat/<slug>`. Confirm `.dreamers/` is gitignored. Action open items in `.dreamers/improvements.md` if present.

For each plan in sequence:

### Step 1 — Read plan + write failing tests (inline)
- Read the plan file. For each AC (G/W/T + `*Layer: ...*`), write at least one failing test at the annotated layer. Stage with `git add`. Don't run yet.

### Step 2 — Implement (inline)
- Edit production files per `comment-rules` + `logging-discipline` + `testing-mandate` (Kernel). Stage as you go.

### Step 3 — Type-check + run tests (inline)
- Run the project's type-check + test command (from `.github/copilot-instructions.md`). Fix inline (max 3 attempts) then halt.
- Update `./test-benchmarks.md` row after passing (if the project uses one).

### Step 4 — Spawn review
- Invoke `/dreamers-review`. Wait. It returns the triad's structured findings (per `reviewer-findings-format`, Kernel) — read-only.
- `Blocked` from any reviewer → halt cycle + surface verbatim.
- Open questions from any reviewer → present each via `request_information`; capture; carry decisions into Step 5.

### Step 5 — Apply findings (orchestrator-as-fixer)
- Concatenate findings from all three reviewers; sort by severity (critical → low).
- Conflict resolution: same `file:line` with contradicting fixes → correctness > simplicity. Genuine ambiguity → `request_information` before applying.
- **Major-refactor gate.** A finding is "major-refactor scope" if its suggested fix meets ANY of:
  - New module or top-level directory not in the plan's scope.
  - Schema / data-model change.
  - Cross-cutting refactor (touches multiple unrelated subsystems).
  - New public exported symbols not specified in the plan.
  - Files outside the plan's scope.
  - Hone-recommended full refactor (scope language like "tear out X across N files," "rewrite Y module").
  Closed checklist. Ambiguous → fire the gate.
- For each gate-triggering finding (or batched group sharing the same refactor scope), `request_information` with: reviewer, severity, lens, location, finding, suggested fix, triggered criterion, rationale, breadth estimate. Options: `Apply now` / `Defer — create follow-up plan` / `Other`.
  - **Apply now** → fix inline; stage; re-run tests after.
  - **Defer** → do NOT apply. Create a stub plan file at `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md` per `plan-writing-guide.md`. Surface the stub path. Continue with remaining findings.
  - **Other** → freeform redirect. Never silently apply/defer.
- Apply each non-deferred fix as a targeted Edit. Stage with `git add`. Re-run type-check + tests after applying. Regression → fix inline (max 3 attempts) before halting.

### Step 6 — User testing gate (MANDATORY, every plan)
- `request_information` with:
  - Plan ID + path
  - Summary of what changed in this cycle
  - Build/distribute steps from `.github/instructions/build.instructions.md` (or ask user to build if absent)
  - Step-by-step verify steps derived from plan ACs
  - Known limitations / out-of-scope
  - Options: `Approved — continue` / `Bug: <description>` / `Other`
- On bug → fix inline + re-prompt.
- On Approved → continue.
- No commit yet (commit happens at close-out for FULL, or in the LIGHT close-out between cycles for INCREMENTAL).

### Between cycles (more plans remain)
- **Drift check** (inline): read next plan; cited paths exist; signatures match; ACs valid vs landed diff. Drift → surface; user revises/skips/halts.
- **INCREMENTAL** (light close-out for this plan):
  - Invoke `/dreamers-docs --branch` if the just-completed plan's diff has user-facing or documentable changes.
  - `git commit` per project commit style; body includes `Plan: feature-<slug>/plan-NN-<name>`.
  - Invoke `/dreamers-pr`. Capture PR URL.
  - `request_information` Continue/Halt/Other. Continue: wait for user confirm-merged → re-cut feature branch from default → next cycle.
- **ATOMIC**:
  - `git commit` for this plan (body includes `Plan:` line). Do NOT push. → next cycle.

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
- Final commit: `git add <explicit-paths>` (no `-A`) + `git commit` per conventional-commits with `Plan:` body + trailer. Skip if nothing staged.
- **User approval gate** (MANDATORY, last halt before PR): present milestone summary. `request_information` Approved/Halt/Other. Halt → emit resume command + stop.
- Invoke `/dreamers-pr` (pass `--issue <#|url>` if `$ARGUMENTS` referenced one). Capture PR URL.
- **Plan archive**: for each `.dreamers/plans/feature-<slug>/` whose every plan's PR state is `MERGED` (`gh pr view <#> --json state -q .state`): `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/`. Whole directory only.
- **Post-PR scan**: surface open retro improvements + ask user before applying any. Flag project-state drift (PR description vs plans shipped; `git log origin/$DEFAULT -10`; `.dreamers/improvements.md` open items; `.dreamers/retros/` open items). No auto-commit after PR opens.

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

In `/dreamers-implement` Step 4 (coverage sweep) and Step 5 (parallel review with Probe), the layer audit reads each AC's `*Layer: ...*` annotation to verify coverage at each layer was implemented. Probe blocks the cycle if any AC's annotated layer lacks a corresponding green test.

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

Do not add log calls outside the plan's scope as while-I'm-here cleanup. If the plan does not call for new logging, leave existing logging untouched unless a finding requires a change.

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
