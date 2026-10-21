---
name: dreamers-lite
description: 'Deliver a task without planning: implement, test, review with Vigil, update docs, and request PR approval.'
argument-hint: '<task description>'
---

$ARGUMENTS

## Setup

If the task is missing, halt and ask. Keep one todo for setup, implementation/tests, review, docs, and close-out. The skill owns the branch, scope, gates, review count, and next phase throughout. Follow `Delivery continuation` in `dreamers.instructions.md` across follow-ups; resume pending work instead of repeating setup.

Workflow blocks are local operations: supply the inputs stated at each phase, apply their write boundaries only during that operation, and use their results to continue here. Do not invoke other skills or load their `SKILL.md` files. The rules and formats at the end are shared across phases.

Apply the Core rules and Git workflow: fetch, update the default branch, and cut `fix/<slug>` before editing. Inspect scope and raise ambiguities or critiques through `request_information`; otherwise continue.

## Implement and validate

Supply the task, agreed scope, and any accepted fixes. Retain the existing feature branch.

<implementation-workflow>

**Input:** task requirements or an approved plan, agreed scope, and any shared context or accepted findings. Apply the embedded `dreamers-kernel`, `git-workflow`, `testing-mandate`, `comment-rules`, and `logging-discipline` rules.

1. **Implement.** Make the scoped code and test changes inline on the prepared feature branch. For tasks, use the stated requirements as acceptance criteria; no plan file is needed. Stage explicit paths as work progresses.
2. **Validate.** Run the project's type-check and test commands from `.github/copilot-instructions.md`. Fix failures inline, allowing at most 3 fix attempts; halt if validation still fails. After passing, update the corresponding `./test-benchmarks.md` row if the project uses one.

**Result:** requirement/AC coverage and validation results at green tests. Leave changes staged; review, commit, push, and PR creation are outside this operation.

</implementation-workflow>

## Review

After green tests, supply `--vigil --branch` and the task context, with no plan binding.

<review-workflow>

**Input:** optional plan path, task/PR context, scope flags, and reviewer selection. Apply the embedded `dreamers-kernel`, `reviewer-findings-format`, `logging-discipline`, and `agent-recovery` rules.

**Modes**

- `--full` Full triad: Sentinel + Probe + Hone in parallel.
- `--vigil` Single-agent combined review through Vigil.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).
- `--lenses <csv>` Selected-lens audit (`sentinel`, `probe`, `hone` in any non-empty combination).
- With a plan and no lane flag: select from the plan as described below.
- Without a plan or lane flag: infer a review basis, then default to the full triad.

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

**1. Establish the review basis**

- If a readable plan is supplied, use it as the review basis. A user-supplied path that cannot be read remains a blocking error; do not silently replace it with an inferred basis.
- For a supplied plan, resolve `**Grilling transcript:**` relative to the plan. If the metadata is absent, check for sibling `grilling-transcript.md` for compatibility. When a readable transcript exists, read it in full and bind its absolute path + verbatim contents alongside the plan as authoritative user-intent context. If the plan references a transcript that is missing or unreadable, block instead of silently dropping it. If no transcript exists or is referenced, continue with the plan alone.
- If no plan is supplied or no plan is available, infer the intended behavior from, in order: explicit user direction; PR title/body and branch name; commits and diff in the selected scope; changed tests; changed code and its callers; then nearby conventions and public interfaces.
- Write a concise inferred-intent summary with the observable behavior, invariants, likely regression risks, evidence paths, and confidence. Treat that summary as the review basis, not as a replacement plan.
- If the evidence does not support one reliable interpretation of the change, ask the user one concise question before spawning reviewers. Do not guess or use the full triad to decide the requirement.

**2. Spawn reviewers**

- Determine the selected reviewers in this order:
  1. Honor an explicit lane flag or explicit user direction.
  2. Honor an explicit reviewer requirement written in the plan.
  3. Otherwise read `**Plan-type:**`: `lite` = Vigil; `standard` = Sentinel + Probe; `complex` = Sentinel + Probe + Hone.
  4. If no plan or Plan-type is available, use Sentinel + Probe + Hone.
- Before spawning, record existing matching artifacts under `.dreamers/reviews/{vigil,sentinel,probe,hone}-*.md` so stale files are never mistaken for this run.
- For multiple selected reviewers, launch every reviewer in parallel through the runtime's batched-spawn mechanism, each with `mode: "sync"`. Never spawn or await reviewers sequentially.
- Vigil and single-lens modes spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Every reviewer prompt MUST include the review basis: either the absolute plan path or the inferred-intent summary with its evidence and confidence. For a plan-bound review with a resolved Grill transcript, include its absolute path and full verbatim contents; require the reviewer to use it when checking intent alignment and to report any plan/transcript conflict rather than silently choosing one. Explicitly say `no plan binding` for inferred-intent reviews.
- Every reviewer prompt MUST require exactly one artifact under `.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md` and short chat output containing only status, counts, artifact path, blocked reason, and open questions.
- Per-lens prompt context:
  - **Vigil** — combined correctness, security, maintainability, test coverage, and simplicity review with the required architecture audit. Artifact contains findings, intent alignment, requirement coverage, and architecture audit sections.
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Artifact contains findings + intent-alignment summary.
  - **Probe** — test coverage (requirement matrix, layer audit, edge cases, gaps). Artifact contains findings + requirement coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Mandate verbatim: "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly so the caller can route it through their major-refactor gate."
- Wait for all spawned reviewers to return.

**3. Report**

- For each selected reviewer, read the artifact path returned in chat. If the path is missing or unreadable, inspect only new matching artifacts created for this review; if exactly one exists for that reviewer, read it. Otherwise surface `Blocked — review artifact missing for <reviewer>` and stop.
- Return per-reviewer artifact contents verbatim to the caller, including artifact paths.
- Aggregate counts by severity + lens from the artifacts for a one-line summary.
- Surface any `Blocked` status from any artifact (caller handles).
- Surface any open questions raised by any artifact (caller handles).

**Result:** artifact-backed findings and paths, severity/lens counts, blocked reasons, and open questions.

This workflow owns reviewer selection and execution. The caller owns all finding disposition, gates, fixes, revalidation, and user testing. This workflow does not modify project code, tests, docs, config, dependencies, or git state. Each spawned reviewer is read-only for those same project files; its sole write is exactly one `.dreamers/reviews/` artifact.

</review-workflow>

## Apply findings

Apply accepted findings through Implement and validate, then Review, for at most 2 fix cycles. Ask before major refactors; record deferred findings in root `defered.md`. Halt on a blocked review or unresolved findings at the cap and report what remains. Never silently reset the count.

## Update docs

If AI or workflow issues arose, suggest relevant edits to repository AI instructions. Supply `--staged`, the task context, and the review summary.

<documentation-workflow>

**Input:** diff scope, delivery context, and any plan paths or prior review summary. Apply the embedded `dreamers-kernel` rules.

**1. Resolve scope**

- Detect the default branch from `origin/HEAD`, falling back to `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, then `main`; store it as `$DEFAULT_BRANCH`.
- `--branch` (default): scope = `git diff --name-only origin/$DEFAULT_BRANCH...HEAD`.
- `--staged`: scope = union of `git diff --cached --name-only` and `git diff --name-only`.
- If the changed-files list is empty → return `No changes detected` without spawning Echo.

**2. Update docs**

- `task(agent_type: "echo", mode: "sync")`. Prompt MUST include `Do NOT call manage_todo_list.`
- Pass: context (ad-hoc or milestone close-out — caller-supplied), changed-files list, diff base, plan paths (if applicable), prior review summary (if applicable).
- Constraint to Echo: edits docs only — no production code, no tests. Stage with `git add`; do NOT commit.
- Wait for Echo to return its structured chat output.

**3. Handle output**

- `Docs updated — N files changed` → surface doc-changes log to user.
- `No doc updates needed` → return that result.
- Open questions → present each via `request_information`; capture answers; re-spawn Echo with clarification if needed.

**Result:** files Echo touched and the doc-changes log, or no updates needed. Leave documentation staged; do not commit, push, or open a PR.

</documentation-workflow>

## Commit and approve publishing

For revisions to an open PR, use the post-PR close-out in `Delivery continuation` instead of the initial close-out below.

Stage explicit paths (`git add <paths>`, no `-A`) and commit remaining changes with a conventional subject. Present the milestone summary through `request_information`: `Approved` / `Halt` / `Other`. On approval, continue to Publish. Halt means emit a resume command and stop; Other follows user direction.

## Publish

Supply the committed branch, delivery/validation summary, and `--issue <#|url>` if input referenced an issue.

<pr-workflow>

**Input:** committed feature branch, delivery and validation summary, optional shipped plan paths, and optional `--issue <#|url>`. Enter only when publishing is authorized. Apply the embedded `dreamers-kernel`, `git-workflow`, and `pr-description` rules.

**1. Verify**

- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

**2. Push**

- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

**3. Open the PR**

- Draft the PR body using the embedded `pr-description` format.
- `gh pr create --base "$DEFAULT_BRANCH" --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

**4. Archive shipped plans**

- If this PR ships a Dreamers plan from `.dreamers/plans/feature-<slug>/`, archive after the PR is created.
- Single-plan feature directory: move `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/`.
- Multi-plan feature directory or manifest sequence: create `.dreamers/plans/archive/feature-<slug>/` if needed, move only the shipped `plan-NN-*.md` file(s) into it, and leave unfinished plans in the live feature directory.
- If `manifest.md` exists, keep it live while any unfinished plan file remains. After the last unfinished plan ships, move `manifest.md` into the same archive directory and remove the now-empty live feature directory.
- If no feature directory applies, skip this step.

**Result:** PR URL and any moved archive paths.

</pr-workflow>

Return the PR URL.

## Rules and formats

### Core rules

<dreamers-kernel>

**User overrides**

Explicit user instructions can skip or alter phases/actions.

**Subagent allowlist**

Do not use any non-Dreamers agent unless explicitly authorized by user.

**Subagent prompt — required content**

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

**Implementation discipline**

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

**Commit trailer**

Every commit body includes:

```
Co-authored-by: The Dreamers System
```

</dreamers-kernel>

### Git workflow

<git-workflow>

Every milestone uses a feature branch + PR — never work directly on the default branch.

**Startup verification (do this FIRST)**

1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

**Branch setup (before implementation)**

1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Confirm `.dreamers/` is in the project's `.gitignore`. If not, add it before any further edits.
4. No init commit — the first commit for the milestone is the first thing in the PR diff.

**Commit discipline (non-negotiable)**

1. **Commit at end of each cycle** — one commit per plan in the sequence (single-plan: one commit total; multi-plan: N commits, one per plan).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

**Push discipline (non-negotiable)**

`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between cycles, or at any other point in the pipeline.

**Post-PR push discipline**

If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

**Commit structure (one commit per cycle)**

- Exactly **one** commit per plan/cycle, immediately after the reviewer findings have been applied and tests are green (and user testing, if required, is signed off).
- The orchestrator stages changes with `git add` throughout the cycle but does **not** run `git commit` until the cycle ends.
- Commit message subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes).

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

**What gets committed**

Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

**No worktrees**

The orchestrator works directly on the feature branch. Unless explicitly requested by the user.

</git-workflow>

### Test coverage

<testing-mandate>

**Plan template**

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

**Coverage requirement (every plan)**

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

**Test benchmarks**

Each project that uses `/dreamers-implement` maintains a `./test-benchmarks.md` file at the project root. The file records measured run times per test command so the orchestrator can set realistic timeouts.

- **File path:** `./test-benchmarks.md` at the project root (committed to version control).
- **Recommended-timeout formula:** `max(last_run_time × 2, 30s)` — the 2× multiplier accounts for machine variance; 30s is a non-negotiable floor.
- **Orchestrator updates** the row for each test command after every successful test run. **Humans may edit** the `Notes` column to capture CI environment factors or known flakiness.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).

</testing-mandate>

### Comments

<comment-rules>

**Core principle**

Comments must add value that the code cannot express itself. Concise, no fluff, no separators.

**When to comment**

- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes

**When NOT to comment**

- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

**Strict prohibitions**

- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.

**Style**

- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words

</comment-rules>

### Logging

<logging-discipline>

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, it is the binding spec.
2. **Else: match surrounding code.** Existing log calls in the same module and nearest neighbors define:
   - Logger library / import path (do not introduce a new logger where one already exists).
   - Level conventions in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).

</logging-discipline>

### Review artifacts

<reviewer-findings-format>

**Artifact contract**

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

### Agent recovery

<agent-recovery>

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.

</agent-recovery>

### PR body format

<pr-description>

Use this structure for the PR body. Omit untouched platforms and the fixes section when no fixes apply.

```markdown
## Summary
plan/task summary here

- [bullet: what was delivered]
- [bullet: why / what problem it solves]

## Test counts

- Desktop Vitest: N pass
- Mobile Jest: N pass

*(Omit platforms not touched by this PR.)*

## Fixes applied

- [SEVERITY] file:line — what was fixed (from reviewer artifacts / commit messages)

*(Omit if no fixes applied.)*
```

</pr-description>
