---
name: dreamers-close-out
description: 'Close-out entry point. Runs the canonical close-out procedure (`close-out-procedure.md`). Two modes: FULL (default) and LIGHT (`--light <plan-path>`). Includes push + PR via `pr-procedure.md` at Step 6. Triggers: /dreamers-close-out, close out the milestone, ship the feature.'
argument-hint: '[--light <plan-path>] [--issue <#|url>]  (omit flags for full milestone close-out with no issue close)'
---

## What this skill does

Standalone entry point for the close-out phase. The user invokes this when they have completed implementation (manually or via `/dreamers-implement`) and want to ship — push + PR + docs + retro + archive.

This skill follows `~/.copilot/dreamers/refs/close-out-procedure.md` end-to-end. Echo is spawned as a subagent inline at Step 2 for project-doc updates. `pr-procedure.md` is followed inline at Step 6 for push + PR creation.

This skill does NOT invoke any other skill. Echo is spawned as a subagent inline (per close-out-procedure Step 2). PR creation is handled inline (per pr-procedure.md).

---

## Two modes

| Mode | When | Run |
|---|---|---|
| **FULL** (default) | Milestone end — all plans in the feature are implemented. Includes the case where INCREMENTAL ship-strategy is in play: the FINAL plan's close-out is always FULL. | All of close-out-procedure (Steps 1–8). |
| **LIGHT** (`--light <plan-path>`) | Mid-sequence in INCREMENTAL ship mode — one plan complete, more remain. Used by `/dreamers-full` between plans. | Steps 2 + 4 + 5 + 6 only (docs if applicable + final commit + user gate + push + PR). NO retro, NO improvements append, NO plan archive, NO post-PR discipline. |

If `$ARGUMENTS` includes `--light` followed by a plan path, run LIGHT mode. Otherwise run FULL mode.

If `$ARGUMENTS` includes `--issue <#|url>` (bare issue number or GitHub issue URL), capture it as the issue reference for `pr-procedure.md` Step 4. Do NOT prompt the user for an issue reference.

---

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit content between the XML tags — edit the source file and re-run sync.


Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions.

<orchestration-flow>
<!-- GENERATED from .github/dreamers/refs/orchestration-flow.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Orchestration flow — ref delivery, single-owner todo, continuation principle

Single source of truth for three orchestration principles that apply across all Dreamers skills.

---

## Ref delivery (HARD RULE)

Refs are delivered to skills and agents via **build-time inlining**, not runtime `view` reads. Each consumer file (skill or agent) declares the refs it depends on by placing XML marker pairs (`<NAME>...</NAME>`) at the appropriate position in its body. `scripts/sync-refs.ps1` regenerates the content between the markers from `.github/dreamers/refs/NAME.md` on every sync. CI's `verify-refs` workflow fails any PR whose inlined ref content drifts from the source.

**Implications:**
- Skills and agents no longer need to "load this ref before Step 1" instructions — the ref content is already in the prompt body, between the markers.
- To change a rule that appears in a ref, edit only the source file at `.github/dreamers/refs/NAME.md`. Run `pwsh -File scripts/sync-refs.ps1 -Sync`. Commit the regenerated consumer files alongside the ref edit.
- NEVER edit content between marker tags by hand. The auto-inserted `<!-- GENERATED ... -->` warning comment makes this visible to humans and agents.
- A consumer file MAY still reference templates, project-level files, or other non-ref artifacts at runtime — those remain runtime `view` reads (not in scope for ref inlining).

---

## Single-owner todo rule (HARD RULE)

There is exactly ONE todo list per user-invoked skill run. The skill the user invoked at the top level (`/dreamers-full`, `/dreamers-plan`, `/dreamers-implement`, `/dreamers-fix`, `/dreamers-close-out`, etc.) owns the todo for the duration of its run. No other entity touches it.

### What the orchestrator does

At skill entry:
- Declare the todo via `manage_todo_list`. Each item corresponds to one major phase or step. Declare all items upfront; do not add items mid-run.

During the run:
- Mark the active item `in_progress` when starting.
- Mark it `completed` when done.
- Never batch completions at the end. The todo is a live progress indicator, not a retrospective log.
- Before every meaningful step, re-read the todo to confirm position — the todo is the authoritative "where am I" signal, not chat context.

At skill exit:
- All items should be `completed` (or explicitly noted as deferred/skipped, with reason).

### What subagents do NOT do

Subagents spawned by the orchestrator (Sentinel, Probe, Hone, Echo, Sage) do NOT touch the todo. Their prompts MUST include the line:

> "Do NOT call `manage_todo_list`. The orchestrator owns the todo."

A subagent that creates its own todo creates a parallel state that drifts from the orchestrator's. Don't do it.

### No composed-mode handoff

There is no "composed mode" for the todo. Skills do not invoke other skills as runtime sub-routines in this system. Each user-invoked skill runs end-to-end with its own todo. When a user wants the full pipeline, they run `/dreamers-full`; when they want only planning, they run `/dreamers-plan`; etc. Each run has one owner, one todo, one exit.

This rule replaces the previous "composed vs standalone — sub-skill updates parent's matching item" pattern, which created multi-owner todo state and was the root cause of mid-pipeline progress lapses.

### Granularity

One todo item per major phase or clearly distinct step. Not one per line of work. Not one per sub-step within a phase. Scannable overview, not micro-log.

---

## Continuation principle

### Definition

The orchestrator MUST NOT silently halt mid-feature. At every natural pause — where a phase ends and a meaningful choice about what to do next exists — the orchestrator calls `request_information` with a structured choice block. The user picks `Continue`, `Halt for now`, or `Other (freeform)`. No silent forward progress; no silent stops.

### Pause-point list

The following are the canonical natural pauses where a continuation prompt is required:

1. Between ATOMIC cycles in a multi-plan loop, after each plan's commit and drift check, before the next cycle starts — only when more plans remain.
2. Between LIGHT close-outs in INCREMENTAL multi-plan mode, after each per-plan PR opens, before the next cycle starts — only when more plans remain.

**Approval gates are NOT continuation prompts.** Phase 1c (proposal approval), Phase 1g (plan-file approval), and close-out Step 5 (push approval) each carry their own decision. They do not need a follow-up "do you want to continue?" prompt after they fire. Phase 1g's `Approved — start implementation` answer is itself the proceed signal — no second gate fires between Phase 1g and Phase 1.5 / Phase 2.

### Prompt template

Use this shape for every continuation prompt:

```
<status summary — one sentence stating what just completed>

<concrete next action — one sentence stating what will happen if the user says Continue>

Options:
- label: Continue — <specific yes-action label>
- label: Halt for now — No (halt; resume later)
- label: Other — freeform redirect
```

Call `request_information` with at minimum these three choices. The `Continue` label must name the concrete next action (e.g., "start next cycle for feature-auth/plan-02-logout.md").

### Halt behavior

On `Halt for now` at any continuation prompt: halt cleanly. Output one line stating the resume command:

```
Resume by re-invoking `/dreamers-full` with the remaining plan paths: <paths>
```

(Adapt the resume command to whichever skill the user was running.)

Do not leave partial state dangling. Stage nothing new. Do not proceed.

On `Other`: treat the freeform input as a redirect instruction. Acknowledge it, confirm the new direction, and proceed accordingly.

---

## Tool naming convention

Skills in this system reference two tools by pseudonym. Runtime resolves the pseudonym to whatever Copilot CLI surfaces as the actual tool name at the time of invocation.

| Pseudonym | Tool | What it does |
|-----------|------|--------------|
| `request_information` | Copilot CLI user-prompt tool | Pauses the orchestrator, presents a message and structured choices, waits for the user's response |
| `manage_todo_list` | Copilot CLI todo tool | Creates, updates, and marks items in a persistent todo list visible to the user |

When a skill says "call `request_information`" or "declare via `manage_todo_list`", it means: invoke the tool Copilot CLI has bound to that function at runtime. The pseudonym names are stable across skill files regardless of CLI version.

### Legacy convention note

The `.github/agents/nova.agent.md` file retains the older `ask_user` pseudonym (predates this ref). It is functionally equivalent to `request_information`. Out of scope for the current alignment pass; tracked as a follow-up to harmonize agent files with the skill convention.
</orchestration-flow>

<orchestrator-discipline>
<!-- GENERATED from .github/dreamers/refs/orchestrator-discipline.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Orchestrator Discipline (mandatory)

When a Dreamers pipeline sub-skill is doing work the orchestrator handles inline — implementation, test writing, comment writing, logging, git operations — these rules apply.

Cited by `/dreamers-plan`, `/dreamers-implement`, `/dreamers-close-out`, `/dreamers-fix`, `/dreamers-pr-resolve`, `/dreamers-full`, and the three reviewer agents (Sentinel, Probe, Hone) for the structured findings format spec. This ref is inlined into every consumer by `scripts/sync-refs.ps1` and CI-verified — to change a rule, edit this file and re-run sync.

---

## Implementation discipline

- **NEVER spawn general-purpose or non-Dreamers subagents.** Implementation work (writing production code, writing tests, running tests, type-checking, running build/lint, git operations, file edits, doc updates beyond Echo-owned scope, PR creation) is done INLINE by the orchestrator using its own Edit / Write / Bash tools. The ONLY subagents Dreamers skills may spawn are: `sentinel` / `probe` / `hone` (read-only review) and `echo` (scoped doc writing) and `sage` (research). See `delegation.md` § "Subagent allowlist" for the full hard rule with the forbidden list. If you find yourself about to call `task` / Agent with `agent_type: "general-purpose"` (or any type outside the 5-item allowlist), STOP — the action belongs to the orchestrator inline or to one of the named Dreamers agents, never to a fallback.
- **Plan adherence:** only edit files in the plan's scope (or that the plan's scope clearly entails). No "while I'm here" cleanup, no unrelated refactors mixed with feature work. If a refactor is genuinely needed for the plan's work, do it as a separate inline step and note it in chat.
- **Incremental edits:** make changes in small, coherent steps. Stage with `git add` as work progresses.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern. If spec interpretation is non-obvious, document the reasoning in the PR description or commit message — never in code comments. When in doubt, implement the cleanest separation and let Sentinel judge.
- **All imports at the top of the file.** Every `import` statement before any declaration, function, or expression. Never insert imports mid-file or at the bottom.
- **Method signature changes:** when changing a signature (sync→async, parameter added/removed/renamed), grep the full codebase for every call site before staging. The plan's listed files are necessary but not sufficient.
- **Zustand creator objects:** never use ES getters (they're evaluated once at creation time and baked as static values, never reactive). Define computed values as exported selector functions outside the store.
- **Branch identity check:** before the first edit, run `git log --oneline -3` and confirm the branch and recent commits match the expected feature branch. If the working tree shows no feature commits for this milestone, stop and surface the discrepancy.
- **Data-model changes:** when a plan supersedes an earlier plan's data model, discard the old model completely. Cite the specific interface definitions from the plan's §Data Models (or equivalent) section before writing any new tables or classes.
- **No dependency installs without permission.** Do not add new packages, run `npm install <pkg>`, `pip install <pkg>`, or equivalent without explicit user approval. If a new dependency is needed for the plan, surface it in chat and ask before installing.
- **Type-check before declaring implementation done.** Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before moving to the test-run step.

---

## Comment-writing discipline (mandatory — orchestrator is also the implementer)

Pulled from `comment-rules.md`. The orchestrator now writes comments inline, so these rules apply directly to every code edit:

- **No plan/ticket references in source.** Never mention plan files, milestone names (e.g. `D25`, `plan-3`), ticket numbers, or agent names in source code (production OR test).
- **No separator comments.** Never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers.
- **No spec rationalization comments.** Implement cleanly; let review judge.
- **No redundant JSDoc/KDoc** that only repeats the function signature.
- **Style:** one line when possible; never exceed two lines for inline comments. Write *why*, never *what*. If a comment would need more than two lines to be useful, the code needs refactoring, not more words.
- **When to comment:** non-obvious logic (hidden constraints, gotchas, workarounds for specific bugs), public API documentation callers need, TODO/FIXME with specific actionable notes, license headers.

---

## Logging discipline (mandatory — orchestrator writes log calls inline)

Pulled from `logging-standards.md`. Key rules:

- **Log levels (use the right one):**
  - **ERROR** — unhandled or unexpected failures only. Always include the full error object and stack trace. Never swallow silently.
  - **WARN** — recoverable issues, unexpected-but-handled states, deprecations.
  - **INFO** — lifecycle and business signal. Use for startup config (non-secret), shutdown, incoming requests (method/path/status/duration), outbound HTTP (target/endpoint/status/duration), auth events, key business events.
  - **DEBUG** — high-traceability internal flow. Function entry/exit on non-trivial functions, every branch affecting business outcome, repository/data-layer calls (query + row count), cache hits/misses, retry attempts, state-machine transitions, middleware entries/exits.
- **Hard prohibitions — NEVER log:**
  - Passwords, API keys, tokens, secrets of any kind
  - PII: email addresses, phone numbers, names, addresses, payment data
  - Full request or response bodies (log status codes and durations instead)
- **High-frequency loop internals at DEBUG are allowed** if they add traceability value. Mark them with a `// high-freq` comment so Sentinel can assess noise risk.

---

## Test-writing discipline

- **Tests-first:** write failing tests against the plan's Acceptance Criteria (Given/When/Then with Layer annotations per `plan-content.md`) BEFORE implementing. There is no separate Test Cases section in the new plan format — the ACs are the test specification.
- **AC coverage matrix:** for every plan AC, identify the test(s) that cover it. If an AC has no covering test, write one. Do not declare the cycle done based on test count alone — verify by AC.
- **Layer audit (mandatory after implementation):** for the changed code, ask explicitly per layer:
  - *Unit:* Are there functions, branches, or error paths in the changed code with no unit test?
  - *Integration:* Are there layer boundaries (repo↔DB, service↔API, function↔trigger) exercised by this change without an integration test?
  - *UI / E2E:* Are there user-facing flows, screen states, or navigation paths introduced or changed without a UI / E2E test?
- **Navigation change rule:** when a plan changes how a nav element behaves (tab tap, modal open, screen transition), the work MUST include explicit E2E test cases — not just unit tests.
- **Negative + edge cases:** for non-trivial logic, write tests for invalid input, boundary values, empty/null/max, and error states.
- **No AC labels in test sources:** the AC coverage matrix lives in chat output / the retro. Never label tests with AC numbers, plan refs, or milestone names in source files (no `// AC-3`, no `describe('AC-7: ...')`).
- **No commented-out test bodies:** if a test must be disabled, use the runner's skip mechanism (`it.skip`, `xit`).
- **Test commands:** use ONLY the test commands defined in the project-level `.github/copilot-instructions.md`. Do not invent alternatives. Never run tests in parallel unless they are explicitly confirmed safe to run concurrently (separate runtimes, no shared daemon, no shared lock files, no shared output dirs). When in doubt, run sequentially.
- **Final missed-AC check (mandatory, last item of coverage sweep):** After the layer audit, re-read the plan's Acceptance Criteria one final time. Confirm every AC has a green test. If any AC has no covering test and no documented reason, write the test before signaling cycle complete. This is a hard gate.
- **Regression analysis (mandatory when the originating task is a user-reported bug fix):** when the work in this skill was triggered by a user-reported bug, the close-out retro must answer three questions explicitly:
  1. **Why wasn't this caught?** — which test layer failed (no test existed; test existed but didn't cover this path; test covered it but assertion was wrong; test was skipped/deferred)
  2. **What was added?** — specific test(s) now covering this case (names + file paths)
  3. **What else might be missing?** — adjacent cases the same gap might have left uncovered

---

## Closeout / retro discipline

- **Retro file:** `.dreamers/retros/retro-d<N>-<name>.md` per `close-out-procedure.md` Step 3. Orchestrator writes this inline (FULL close-out mode only).
- **Echo-owned section updates** to `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands): delegated to the Echo subagent — see `close-out-procedure.md` Step 2 for the inline invocation contract.

---

## Git discipline

- Stage with `git add` as work progresses across all phases. Never commit mid-cycle.
- **One commit per cycle = one commit per plan.** Multi-plan milestones produce N commits on the branch (one per plan in the sequence).
- Commit message follows `.github/instructions/git.instructions.md` (if present) or the conventional-commits style used by recent commits on the default branch. Body MUST include `Plan: feature-<slug>/plan-NN-<name>` — the repo-relative plan path without the `.md` extension and without the `.dreamers/plans/` prefix. Example: `Plan: feature-plan-quality-scoring/plan-01-section-scorer`.
- **Push exactly once**, immediately before `gh pr create` at final close-out. Never push between cycles, never between plans.

---

## Review phase: parallel reviewers + orchestrator-as-fixer

The review phase in `/dreamers-implement` and `/dreamers-pr-resolve` spawns **three reviewers in parallel** via a single tool-call containing 3 Agent sub-tool-uses:

- **Sentinel** — correctness, security, maintainability lenses
- **Probe** — test coverage lens (AC matrix, layer audit, edge cases, gaps)
- **Hone** — simplicity / over-engineering / architectural quality lens

**All three are read-only / report-only.** They identify findings and return them in the structured format below. **None of them edits files** — the orchestrator (which already has the code in context from implementation) applies fixes from the combined findings.

### Structured findings format (mandatory — all three reviewers MUST use)

Each reviewer returns chat output containing:

**Status line** (one of):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:
```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

Where:
- `severity` is one of: `critical`, `high`, `medium`, `low`
- `lens-tag` is one of: `correctness`, `security`, `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` is the absolute or repo-relative path + line number
- `what was wrong → suggested fix` is a one-line description + targeted fix the orchestrator can apply mechanically

**Observations** (optional, all reviewers) — out-of-scope notes that aren't findings. The orchestrator may or may not act on them.

**Open questions** (optional, all reviewers) — items needing orchestrator or user judgment. Use "none" if no questions.

### Orchestrator-as-fixer behavior

After all three reviewers return their chat output, the orchestrator:

1. **Concatenates the findings** into a single list, sorted by severity (critical → high → medium → low).
2. **Resolves conflicts.** If two findings touch the same `file:line` with contradicting fixes — e.g., Sentinel `[correctness] add defensive check` vs Hone `[simplicity] remove this as over-engineering` — apply the **conflict-resolution rule**:
   - **Correctness > simplicity always.** When in conflict, the correctness/security/maintainability finding wins.
   - **Genuine ambiguity surfaces to user.** If both arguments are equally strong (rare), present the conflict to the user before applying either.
3. **Evaluates each finding against the Major-refactor finding gate** (see sub-section below). For each finding, check the closed criteria checklist. If ANY criterion fires, route through the gate: call `request_information` with the 3-choice template; apply or defer per the user's answer. If no criterion fires, the finding is small — fall through to step 4 and apply inline. The orchestrator NEVER silently applies a finding that meets gate criteria, regardless of severity.
4. **Applies fixes inline** (only for findings that didn't trigger the gate, or that the user opted to apply via the gate). The orchestrator has Edit + Write tools; agents don't. Apply each finding's suggested fix as a targeted edit. Stage with `git add`.
5. **Re-runs type-check + tests after applying fixes** (to catch any regression introduced by fix application).
6. **Handles `Blocked` status from any reviewer** by halting the cycle and surfacing the block to the user. Resolve, then re-spawn the affected reviewer.
7. **Handles open questions** from any reviewer by presenting them to the user before declaring the review phase complete. Open questions still surface to the user; captured decisions still apply inline. The follow-up is re-run tests only — NOT a full re-spawn of Steps 3 + 4 + 5.

If the post-fix test run regresses (tests fail), the orchestrator diagnoses and re-fixes inline — up to 3 attempts, then surfaces to the user.

### Major-refactor finding gate

The orchestrator MUST NOT silently apply a finding that triggers any of the criteria below. The user decides whether to apply now in the current cycle, defer to a follow-up plan, or redirect. This is the mechanism that keeps performance and end-state code quality first-class — Hone (and any other reviewer) surfaces architectural issues without softening; the user disposes via this gate.

**The gate fires regardless of severity.** Critical / high severity findings still go through the gate when they meet the criteria — the user decides apply-now vs defer.

#### Closed criteria checklist (any ONE fires the gate)

A finding is "major-refactor scope" if its suggested fix meets ANY of:

1. **New module or top-level directory.** The fix adds a new module, package, or directory that doesn't exist in the plan's scope.
2. **Schema / data-model change.** The fix modifies a database schema, persisted shape, migration, or core data-model interface.
3. **Cross-cutting refactor.** The fix touches multiple unrelated subsystems (e.g., auth + cache + UI in one fix).
4. **New public exported symbols.** The fix introduces new exported functions, classes, types, or API endpoints not specified in the plan.
5. **Files outside the plan's scope.** The fix touches files not listed in the current plan's §Context or §Out of Scope. Bug-fix flows (`/dreamers-fix`) substitute "files outside the bug-fix surface" — same intent.
6. **Hone-recommended full refactor.** The suggested fix uses scope language like "tear out X across N files," "rewrite Y module," "remove Z abstraction and inline at N call sites" — indicating a refactor that goes beyond the immediate fix site.

The criteria are evaluated by reading the finding's suggested-fix text. If ambiguous, treat as major-refactor (fire the gate). The orchestrator does NOT invent new criteria at runtime; the checklist is closed.

#### Gate prompt template

For each finding (or batched group sharing the same refactor scope), call `request_information` with this block:

```
**Major-refactor finding surfaced.**

Reviewer: <sentinel | probe | hone>
Severity: <critical | high | medium | low>
Lens: <correctness | security | maintainability | test-coverage | simplicity>
Location: <file:line>

Finding:
<what was wrong>

Suggested fix:
<suggested fix verbatim>

Triggered criterion: <N — short label of which criterion fired>
Rationale: <one sentence explaining why criterion N fired for THIS specific finding — e.g., "This fix touches `src/auth/session.ts`, which is not listed in the current plan's scope" or "The suggested fix tears out the cache module across 12 files; meets criterion 6 (Hone-recommended full refactor)">
Breadth estimate: <files touched count, ~LOC, in-plan-scope: yes/no>

Options:
- label: Apply now — refactor in this cycle
- label: Defer — create follow-up plan
- label: Other
```

#### Routing per user's answer

- **`Apply now — refactor in this cycle`** → apply the fix inline at step 4 of orchestrator-as-fixer behavior; re-run tests at step 5; stage with `git add`. The current cycle continues — note this may expand cycle scope significantly; the user has accepted that.

- **`Defer — create follow-up plan`** → do NOT apply the fix. Create a stub plan file at `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md` using the canonical plan format from `plan-content.md`. The `<deferred-slug>` is derived from the finding's topic (kebab-case, ≤ 40 chars; e.g., "simplify-notification-factory"). The stub captures the finding verbatim but leaves real ACs / constraints / verification as TODO placeholders for the user to fill in via `/dreamers-plan` later. Stub format:

  ```
  # Plan-01: <short title derived from finding>

  **Date:** <today, YYYY-MM-DD>
  **Status:** Draft
  **Branch:** (TBD — fill in when starting work)
  **User-testing-required:** (TBD)

  ## Goal

  [Finding surfaced during review of <original-plan-path>. Captured for follow-up — fill in concrete done-state when ready to work on it.]

  ## Context

  - Surfaced by: <reviewer agent name>
  - During cycle of: <original-plan-path>
  - Finding verbatim:
    > [severity] [lens-tag] file:line — what was wrong → suggested fix
  - Triggered criterion: <criterion N>
  - Breadth estimate: <files / LOC / in-scope status>

  ## Acceptance Criteria

  <acceptance_criteria>
  1. (TBD — convert the finding's suggested fix into a verifiable AC.)
     *Layer: ___.*
  </acceptance_criteria>

  ## Out of Scope

  - (TBD)

  ## Constraints

  <constraints>
  - (TBD)
  </constraints>

  ## Verification

  - (TBD — fill in commands + files when planning this work)
  ```

  After writing the stub, surface the stub path to the user in chat and continue with the remaining findings. Do NOT mark the deferred finding as applied; do not edit the current cycle's code based on it.

- **`Other`** (freeform) → treat the response as a redirect. If the user clarifies "yes apply", route to Apply now. If they clarify "no defer", route to Defer. If they want something else (e.g., halt the cycle, revise the plan first), follow that direction. The orchestrator never silently applies or defers on `Other`.

#### Batching shared-scope findings

When multiple findings share the same refactor scope (e.g., 3 Hone findings all pointing at the same module), the orchestrator MAY combine them into a single gate call. The prompt lists all findings under one "Triggered criterion" block. The user's single answer applies to all batched findings.

Batching criteria: findings share scope when their suggested fixes touch the same module/directory AND would be implemented as a single refactor. When in doubt, do NOT batch — one gate call per finding is safe; over-batching loses granularity.

#### Severity does NOT bypass the gate

Critical and high severity findings still go through the gate when they meet the criteria. The user decides whether to apply now or defer, regardless of severity. The orchestrator surfaces; the user disposes. Use case: a critical security finding whose fix requires rewriting the entire auth module may be best deferred to a focused follow-up plan rather than mid-cycle, depending on the user's risk model. That's the user's call.

### Re-verification after fixes (mandatory)

**Snapshot first (required on both paths).** Before applying any review findings, snapshot the currently staged files via `git diff --cached --name-only` and `git diff --cached --stat`. This snapshot is the only accurate way to measure the fix-pass delta and is mandatory on the default path AND the second-pass path — without it, the significant-refactor criteria can't be evaluated at all.

After applying fixes from the first parallel review, the orchestrator re-runs the project's test command ONLY. No reviewer is re-spawned by default. A second 3-parallel pass occurs ONLY when the significant-refactor criteria fire AND the user explicitly opts in via `request_information`.

**Default path (no second pass):** snapshot → apply fixes → re-run tests → update `./test-benchmarks.md` → commit.

**Second-pass path (opt-in only):** snapshot → apply fixes → re-run tests → update `./test-benchmarks.md` → check significant-refactor criteria (see below) → if criteria fire, call `request_information` with (a) which criterion fired and the measured values, (b) one-sentence reasoning for why a second pass is recommended, (c) explicit choices `["Run second 3-parallel pass", "Skip — commit as-is", "Other"]`. On `Skip` = commit as-is. On `Other` = present the user's freeform response back to them as a redirect and halt — do not auto-commit and do not auto-spawn reviewers. On `Run second 3-parallel pass` = re-spawn Sentinel + Probe + Hone, re-apply findings, re-run tests, and update `./test-benchmarks.md` again with the second-pass run time before commit.

### Significant-refactor criteria

Diff the post-fix staged state against the snapshot captured in Re-verification (above) to measure the fix-pass delta. A second 3-parallel pass is eligible (not automatic — still requires user opt-in) when ANY ONE of the following fires:

1. More than 5 production files touched in the fix pass.
2. More than 150 LOC of production code changed in the fix pass.
3. A new file was added by the fix pass.
4. A new exported or public symbol was introduced by the fix pass.
5. Code was moved between modules in the fix pass.

**Test files are excluded from the LOC and file-count criteria** (criteria 1 and 2 only). Structural criteria (3–5) apply to all file types.

OR semantics: any single criterion firing is sufficient to make the second pass eligible.

### Parallel spawn — invocation pattern

In the skill body, the review phase is described as a single tool-call with 3 Agent sub-tool-uses (Claude Code idiom) or 3 parallel `task()` invocations (Copilot CLI idiom). Skills should specify intent ("spawn S + P + H in parallel; wait for all three to complete") and let the runtime execute per its primitives. If a runtime doesn't support parallel spawn, the skill still works — wall-clock cost increases but correctness is preserved.
</orchestrator-discipline>

<delegation>
<!-- GENERATED from .github/dreamers/refs/delegation.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Delegation Protocol

Each Agent tool invocation must include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files to read
- **What is needed** — specific deliverable expected from this agent
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

## MANDATORY — Agent mode

All agents MUST be invoked with `mode: "sync"`. The agent blocks until completion and returns its summary inline. The orchestrator gates on the result before firing anything else.

For the parallel reviewer triad in `/dreamers-implement` Step 5 and `/dreamers-pr-resolve` Step 5: spawn Sentinel + Probe + Hone in a single tool-call with 3 Agent sub-tool-uses. All three run concurrently; the orchestrator waits for all three before applying findings.

## MANDATORY — Reading templates and project files at runtime

Refs are inlined into every consumer at build time by `scripts/sync-refs.ps1`; they are part of the live prompt and do not require a runtime read. Templates (`~/.copilot/dreamers/templates/*.md`) and project files (`.github/copilot-instructions.md`, `.github/instructions/*.md`) are NOT inlined and MUST be read in full using the `view` tool when a skill or agent reaches them. Never use shell commands (`cat`, `head`, `tail`, `Select-String`) to read templates or project files — they truncate. Every line matters.

## Subagent allowlist (HARD RULE — read this twice)

The ONLY subagent types a Dreamers skill may spawn are the five below. Any other agent type is FORBIDDEN. There is no fallback, no "general-purpose for when nothing fits" escape hatch.

### Allowed (the only types you may pass as `agent_type` in a `task` / Agent tool call)

- **`sentinel`** — read-only review of correctness, security, maintainability. Returns structured findings; the orchestrator applies fixes. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-review`.
- **`probe`** — read-only review of test coverage (AC matrix, layer audit, edge cases, regression risk). Returns structured findings. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-test`.
- **`hone`** — read-only review of simplicity, over-engineering, redundancy, bad architecture. May recommend full refactors. Returns structured findings. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-simplify`.
- **`echo`** — documentation. Updates Echo-owned sections of `.github/copilot-instructions.md` plus other project docs after a cycle. Spawned inline at `close-out-procedure.md` Step 2, and by the `/dreamers-docs` standalone skill for ad-hoc doc updates.
- **`sage`** — deep multi-perspective research. Used by `/dreamers-research`. Orthogonal to the pipeline.

### Forbidden (must NEVER appear as `agent_type` from a Dreamers skill)

- **`general-purpose`** — NEVER. If you reach for general-purpose to "implement," "edit a file," "run a test," or "do git work," that is a bug. Implementation is INLINE by the orchestrator. There is no fallback.
- **`claude`**, **`claude-code-guide`**, **`Explore`**, **`Plan`** (capital-P architect agent), **`statusline-setup`**, **`vercel:*`** — host-runtime agents from other systems. NEVER spawn from a Dreamers skill.
- **`forge`**, **`nova`** — these are USER-ENTERED personas (via `/agents forge` or `/agents nova`). Skills do NOT spawn them as subagents.
- **`bolt`** — does not exist as a subagent in this Dreamers system. Implementation, git ops, and PR creation are done INLINE by the orchestrator.
- **Anything not in the 5-item allowlist above** — NEVER.

### Runtime hard stop

Before EVERY `task` / Agent tool call, check the `agent_type` argument:

- ✅ If `agent_type` is one of `sentinel` / `probe` / `hone` / `echo` / `sage` → proceed.
- ❌ If `agent_type` is anything else → STOP. Do not spawn. The action you're about to delegate either:
  - (a) belongs to the orchestrator INLINE (writing code, writing tests, running tests, git operations, doc updates, file edits, PR creation), OR
  - (b) needs the right Dreamers agent — re-evaluate which of Sentinel / Probe / Hone / Echo / Sage fits.

There is no third option. There is no "general-purpose because I'm not sure which agent to use" path.

## What implementation looks like (NO subagent)

Implementation (writing production code, writing tests, running tests, type-checking, running build / lint / format, git operations including `add` / `commit` / `push` / `mv` / `rm`, branch setup, doc updates, PR creation via `gh`) is the orchestrator's lane — done inline using the orchestrator's Edit / Write / Bash tools. The five allowed subagents are read-only reporters (Sentinel / Probe / Hone return findings) or scoped doc-writers (Echo edits docs only) — none of them write production code or run the build.

## Read-only reviewer lanes

The three reviewer agents (Sentinel, Probe, Hone) have **`tools: Read, Glob, Grep, Bash`** in their frontmatter — no Write or Edit. They cannot modify files. They return structured findings per the spec in `orchestrator-discipline.md`; the orchestrator applies fixes inline.

## Conflict resolution between reviewers

When two reviewers' findings touch the same `file:line` with contradicting fixes (e.g., Sentinel `[correctness] add defensive check` vs Hone `[simplicity] remove this as over-engineering`):

- **Correctness > simplicity always.** When in conflict, the correctness/security/maintainability finding wins.
- **Genuine ambiguity surfaces to user.** If both arguments are equally strong (rare), present the conflict before applying either.

See `orchestrator-discipline.md` § "Orchestrator-as-fixer behavior" for the full handling rules.
</delegation>

<git-workflow>
<!-- GENERATED from .github/dreamers/refs/git-workflow.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
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
  - Body: reference the plan file (e.g. `Plan: feature-auth/plan-01-login-flow`) — repo-relative path without `.md`, without `.dreamers/plans/` prefix

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Worktrees previously caused reviewers to read stale default-branch code.

## Git history is the archive
No separate archive directories. `git log` and PR diffs are the record.
</git-workflow>

<close-out-procedure>
<!-- GENERATED from .github/dreamers/refs/close-out-procedure.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Close-out Procedure (canonical)

This ref is the SOLE source of truth for the Dreamers close-out phase. Both `/dreamers-close-out` (standalone) and `/dreamers-full` (end-to-end pipeline) follow this procedure. Echo is spawned inline at Step 2 for project-doc updates.

The PR-creation half of close-out lives in `pr-procedure.md`. Step 6 below directs the orchestrator to follow that ref inline (the PR procedure is also inlined into the same consumer).

---

## Two modes

| Mode | When | Steps |
|---|---|---|
| **FULL** (default) | Milestone end — all plans in the feature are implemented. Includes the case where INCREMENTAL ship-strategy is in play: the FINAL plan's close-out is always FULL. | Steps 1–8. |
| **LIGHT** (`--light <plan-path>`) | Mid-sequence in INCREMENTAL ship mode — one plan complete, more remain. Used by `/dreamers-full` between plans. | Steps 2 + 4 + 5 + 6 only (docs if applicable + final commit + user gate + push + PR). NO retro, NO improvements append, NO plan archive, NO post-PR discipline. |

The light mode is intentionally minimal: per-plan retros would spam history, and milestone-level scan / improvements / plan-archive belong to the END of the sequence.

If the procedure is invoked with a `--light <plan-path>` argument, run LIGHT mode against that plan. Otherwise run FULL mode.

---

## Inputs

- **Plan file paths** (list shipped this milestone — one or many, all under the same `feature-<slug>/` directory).
- **Branch name** + **default branch name**.
- **Sentinel summary string** (concatenated across cycles in the milestone for FULL mode; just this plan's reviewer summary for LIGHT mode).
- **Issue reference** (number or URL, if applicable).
- **Final commit hash** (if any docs/retro/improvements were committed during this procedure).

## Outputs

- Updated docs (Echo edits committed) — if applicable.
- Retro file at `.dreamers/retros/retro-d<N>-<name>.md` (FULL mode only).
- One PR opened against the default branch.
- Plan directory archived to `.dreamers/plans/archive/feature-<slug>/` (FULL mode only, at milestone-final PR merge — actually performed in Step 7).

The orchestrator's todo (a single list owned by the top-level skill) records step completion.

---

## Step 1 — improvements.md milestone-close (FULL only)

Append any new improvement suggestions from this milestone to `.dreamers/improvements.md`. Format: dated entry, one sentence each, references the retro file path written in Step 3.

If `.dreamers/improvements.md` doesn't exist, skip — Step 3 will note this in the retro for future reference.

LIGHT mode skips this step.

## Step 2 — Docs update (Echo subagent invocation)

The orchestrator spawns Echo as a subagent here for project-doc updates.

**When to invoke Echo:**

- FULL mode: always invoke (docs are evaluated at milestone end).
- LIGHT mode: invoke only when the just-completed plan's diff has user-facing or documentable changes. Judgment criteria: user-visible behavior changed, public API changed, config/setup steps changed, test commands changed, or significant new exported symbol.

When invoking, spawn Echo via the `task` tool:

- `agent_type: "echo"`, `mode: "sync"`
- Pass in the prompt (per `delegation.md`):
  - **Context:** brief description of the milestone or plan being documented.
  - **Prior work:** plan file paths (or "n/a (bug fix)" if no plan), changed files (output of `git diff --name-only origin/<DEFAULT>...HEAD`), diff base (`origin/<DEFAULT>`), Sentinel summary string.
  - **What is needed:** review the changed files vs the plan(s) and update project docs as appropriate (README, CHANGELOG, Echo-owned sections of `.github/copilot-instructions.md`, project-specific docs the project conventions call out).
  - **Constraints:** Echo edits docs ONLY — no production code, no tests. Echo writes to its own scope per `echo.agent.md`. **Do NOT call `manage_todo_list` — the orchestrator owns the todo.**
  - **Definition of Done:** structured chat output per Echo's output discipline (status line + docs-changes log + instruction-file changes + comment audit + open questions).

Wait for Echo to signal completion. Capture the doc-changes log + open questions from chat output. If open questions are raised, resolve them with the user before proceeding.

Stage any new doc edits with `git add`.

## Step 3 — Retro (FULL only)

Write `.dreamers/retros/retro-d<N>-<name>.md`. Required sections:

- **What worked well** — clean handoffs, inline phases that held up.
- **Friction points** — weak output, rework, places the inline discipline slipped.
- **Proposed improvements** — specific, actionable edits to the skill set, agent files, or refs. Reference the exact section to change and why.

Additionally, write inline summaries:
- **AC coverage matrix** — which test covers which AC across all cycles. Roll up from each cycle's chat output.
- **Bugs found during user-testing** (if any) — what was found and how it was fixed.
- **Regression analysis** (if the originating task was a user-reported bug) — three questions per `orchestrator-discipline.md`: why wasn't it caught, what test was added, what else might be missing.

LIGHT mode skips this step.

## Step 4 — Final commit (if needed)

If Steps 1, 2, or 3 wrote any uncommitted changes (Echo's doc edits, improvements.md, retro file), create a final commit:

```bash
git status                                  # confirm uncommitted state
git add <files>                             # explicit, no `-A`
git commit -m "docs: final cleanup before PR"  # or appropriate message
```

If no uncommitted changes, skip — never create empty commits.

## Step 5 — User approval gate (MANDATORY)

Before invoking the PR-creation procedure, present this block:

```
**Milestone ready to ship.**

Plan(s) shipped:
- .dreamers/plans/feature-<slug>/plan-NN-<name>.md — one-line summary

AC coverage: <N>/<N> ACs covered (or list any uncovered with reason)

Sentinel summary: <one-paragraph from chat outputs across cycles>

Echo docs result: <status line + N files touched, or "No doc updates needed">

Retro: .dreamers/retros/retro-d<N>-<name>.md   (FULL only)

Final commit: <hash + message, or "no final commit — nothing pending">

Issue reference: <number/URL, or "none">
```

Call `request_information` with choices `["Approved — push + PR", "Halt for now", "Other"]`. Freeform corrections are accepted via Other.

- **Approved → push + PR** → proceed to Step 6.
- **Halt for now** → output "Resume by re-invoking `/dreamers-close-out`. Branch state is preserved on `<branch-name>`." and stop. No push.
- **Other / corrections** → apply inline, re-run any affected steps (e.g. re-invoke Echo if docs missed something), and re-present this gate. Loop until approved.

This is the LAST point where the user can halt before the PR goes live.

## Step 6 — Push + PR (follow `pr-procedure.md` inline)

Execute the `pr-procedure.md` content inline with the following inputs (the ref is inlined elsewhere in this consumer file via the sync markers — refer to that block, not a runtime `view`):

- Branch name + default branch name (from procedure inputs).
- Plan file paths (from procedure inputs).
- Retro file path (from Step 3 if FULL; omitted in LIGHT).
- Sentinel summary string (from procedure inputs).
- Issue reference (from procedure inputs, if applicable).
- Final commit hash (from Step 4, if any).

Capture the PR URL returned by `pr-procedure.md`.

## Step 7 — Plan archive (FULL only, whole-feature-directory)

The archive unit is the **whole feature directory** (`.dreamers/plans/feature-<slug>/`), not individual plan files. Mid-feature archiving (file-by-file) is NOT allowed.

**Trigger:** the feature is complete when ALL plans in `feature-<slug>/` have shipped (their PRs merged to main). For single-plan features this is one PR; for multi-plan features this is the last plan's PR.

**Procedure:**

1. Identify any feature directories at `.dreamers/plans/feature-<slug>/` whose plans are all referenced by merged PRs (excluding the PR just opened in Step 6, which is unmerged).
2. For each such complete feature, verify every plan's PR is merged via `gh pr view <number> --json state -q .state` returning `MERGED`. If ANY plan's PR is still open or in-flight, skip this feature — it is not yet ready to archive.
3. Move the entire feature directory: `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/` (create the archive dir if needed). Never delete files.

Skip silently if no complete feature directories are ready to archive.

LIGHT mode skips this step.

## Step 8 — Post-PR discipline (FULL only)

After `gh pr create` succeeds via Step 6:

1. **No auto-commit after PR is created.** If any further changes are needed (review comments, CI failures), do NOT auto-commit and push. Ask the user first: *"I have changes ready. Should I commit and push these to the PR?"* Only commit and push after explicit user approval. Commit message: `fix: address PR feedback` (or appropriate).

2. **Surface improvements from this cycle's retro** — list each as one sentence and ask: *"Should I address any of these?"* Do not apply without user go-ahead.

3. **Project state contradiction scan** (read durable surfaces, check for drift, surface — do NOT auto-apply):
   - The just-opened PR description vs the plan files shipped (verify the PR accurately describes what shipped).
   - `git log origin/$DEFAULT -10 --format=%s` — recent merged work.
   - Project-level `.github/copilot-instructions.md` Echo-owned sections — does the codebase still match?
   - `.dreamers/improvements.md` — open items still relevant?
   - `.dreamers/retros/` — any retro files for prior cycles that surface open improvements or stale items?

   Check for: tech stack drift, architecture pivots not reflected in instructions, milestone status drift, rule conflicts. **Propose all changes — do not auto-apply.** Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

4. **Post-PR push (if changes approved):** use plain `git push` (no force). The PR updates automatically.

LIGHT mode skips this step.

---

## What happens after this procedure ends

- **`/dreamers-full`** (end-to-end pipeline): the milestone is complete. The orchestrator's todo records final phase complete. The skill exits with the PR URL.
- **`/dreamers-close-out`** (standalone, FULL or LIGHT mode): exit with success. Surface the PR URL + summary to the user.

This procedure does not touch the todo. The consuming skill maintains it.
</close-out-procedure>

<pr-procedure>
<!-- GENERATED from .github/dreamers/refs/pr-procedure.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# PR-Creation Procedure (canonical)

This ref is the SOLE source of truth for the push + PR-creation step in the Dreamers pipeline. Consumers:

- `close-out-procedure.md` Step 6 (FULL or LIGHT close-out).
- `/dreamers-fix` Step 8.
- `/dreamers-pr-resolve` does NOT use this — it pushes updates to an existing PR, not creates a new one.

---

## Inputs

The orchestrator running this procedure must have these inputs ready (passed in the prompt context or already captured from earlier phases):

- **Branch name** — current feature branch (`fix/<slug>` for bug-fix flow, `feat/<slug>` for feature flow).
- **Default branch name** — `$DEFAULT` from earlier branch setup.
- **Plan file paths** — list of plan paths shipped this PR. Pass:
  - For milestone close-out (FULL): all plans in the feature directory.
  - For per-plan PR (LIGHT close-out, INCREMENTAL ship strategy): the single plan just completed.
  - For bug-fix flow (`/dreamers-fix`): the sentinel string `none — bug fix, no plan file` (literal value; the procedure handles the absence via the Summary fallback rule below).
- **Retro file path** — from FULL close-out Step 3. Omitted in LIGHT close-out and bug-fix flow.
- **Sentinel summary string** — concatenated reviewer outputs across cycles (FULL) or single cycle (LIGHT, bug-fix).
- **Issue reference** (optional) — number or URL. If provided, the procedure closes the issue after PR open.
- **Final commit hash** — from the most recent commit on the branch (the one being pushed).

## Outputs

- Branch pushed to origin with upstream tracking.
- PR opened against the default branch.
- Optionally: issue closed with a comment referencing the PR URL.
- PR URL returned to the caller.

The orchestrator's todo records each step's completion. This procedure does not touch the todo.

---

## Mandatory pre-push verification

Before pushing, verify:

1. **Branch identity** — `git branch --show-current` must NOT be the default branch. If on default, halt with error: "Refuse to push: working tree is on $DEFAULT, not a feature branch."
2. **Working tree clean** — `git status --porcelain` must be empty. If not, halt: "Working tree has uncommitted changes; commit them before opening the PR." (If invoked from close-out, this should already be handled by close-out Step 4 final commit; if not, surface the discrepancy.)
3. **Branch is ahead of remote** — `git log origin/$(git branch --show-current)..HEAD` should have commits, or the branch should not yet exist on remote. If the branch exists on remote and is up-to-date with local, halt: "Nothing to push." (Edge case: re-running this procedure on an already-pushed branch.)
4. **No force-push intent** — never use `--force` or `--force-with-lease` for the initial push. If a previous push exists and there's divergence, halt and ask the user.

---

## Step 1 — Push

```bash
git push -u origin <branch-name>
```

This is the ONLY push in the milestone pipeline. If push fails:
- **Rejected (non-fast-forward):** halt; surface the error. Ask the user how to proceed. Do not auto-force.
- **Network / auth error:** halt; surface; the user resolves credentials.
- **Hook failure:** halt; surface the pre-push hook output; do not skip hooks.

## Step 2 — Draft PR body

Use `~/.copilot/dreamers/templates/pr-description.md` as the base template. Fill in:

- **Summary** — one paragraph: plan title + 1–3 bullets of what was delivered + why.
  - **Bug-fix fallback (plan paths sentinel = `none — bug fix, no plan file`, OR plan paths absent):** derive the Summary from the most recent commit's body — specifically the `Bug:` line written by `/dreamers-fix` — plus 1–2 bullets drawn from the Sentinel summary string describing what changed and why. Do NOT attempt to read the sentinel string as a filesystem path. Do NOT scan `.dreamers/plans/` looking for a matching file.
- **Test counts** — only if test platforms are touched. Otherwise omit the section.
- **Fixes applied** — severity-graded list from the Sentinel summary string.

Title format: short (under 70 chars). Body details, not the title. Bug-fix invocations use the `fix:` prefix; milestone / plan invocations use the appropriate prefix per `.github/instructions/git.instructions.md` (if present).

### Co-authored attribution (mandatory)

Any co-author trailer in commit messages MUST use the standard git trailer key + this exact author identity:

```
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```

Notes:
- Key must be exactly `Co-authored-by:` (git's standard trailer key) so `git interpret-trailers` and GitHub recognize the line.
- Author name is always `The Dreamers System` — never a specific model name. The system is the contributor; model identity ages poorly.
- The `<noreply@dreamers.local>` email is a placeholder — it won't link to a GitHub profile, but it satisfies the trailer's required `Name <email>` format.

The PR body should NOT include a `Co-authored-by:` line — co-author trailers belong on commits, not on PR descriptions.

## Step 3 — Open the PR

```bash
gh pr create \
  --title "<short title>" \
  --body "<drafted body>" \
  --base <DEFAULT_BRANCH>
```

Capture the returned PR URL.

If `gh pr create` fails:
- **Authentication:** halt; ask user to `gh auth login`.
- **PR already exists for this branch:** halt; surface the existing URL.
- **Repo permission denied:** halt; surface.

## Step 4 — Issue close (if applicable)

If an issue number/URL was provided as an input:

```bash
gh issue close <number> --comment "Resolved in <PR URL>"
```

If the issue close fails, surface the error but do not roll back the PR — the PR is valid even if the issue close has problems.

---

## What happens after this procedure ends

Return the PR URL to the caller (close-out procedure, `/dreamers-fix`, etc.). The caller continues with whatever step follows in its own procedure (post-PR discipline for FULL close-out, exit-with-PR-URL for bug-fix flow, etc.).

This procedure does not touch the orchestrator's todo. The caller maintains it.
</pr-procedure>

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`.

**FULL mode:**
- [ ] Read close-out-procedure.md + pr-procedure.md
- [ ] Step 1 — improvements.md milestone-close append
- [ ] Step 2 — docs update (Echo subagent)
- [ ] Step 3 — retro write
- [ ] Step 4 — final commit (if needed)
- [ ] Step 5 — user approval gate
- [ ] Step 6 — push + PR (follow pr-procedure.md inline)
- [ ] Step 7 — plan archive (whole feature directory)
- [ ] Step 8 — post-PR discipline

**LIGHT mode:**
- [ ] Read close-out-procedure.md + pr-procedure.md
- [ ] Step 2 — docs update (if applicable)
- [ ] Step 4 — final commit (if needed)
- [ ] Step 5 — user approval gate
- [ ] Step 6 — push + PR (follow pr-procedure.md inline)

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**Subagent prompt rule:** when this skill spawns Echo in Step 2, include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in Echo's prompt. Per `orchestration-flow.md` § "Single-owner todo."

---

## Standalone-input auto-detection

Auto-detect when running standalone:

- **Branch name + default branch**: canonical two-step `git symbolic-ref` + `gh repo view`.
- **Plan paths**: extract via `git log origin/<DEFAULT>..HEAD --format=%B | grep -E "^Plan:"` and resolve each value to `.dreamers/plans/<value>.md`. The commit body format produced by `implementation-procedure.md` Step 8 is `Plan: feature-<slug>/plan-NN-<name>` — repo-relative, no `.md`, no `.dreamers/plans/` prefix. Skip lines that don't resolve to an existing file (these may be stale commits or merge artifacts).
- **Sentinel summary**: not available — pass placeholder "Standalone close-out — no Sentinel summary captured."
- **Issue reference**: parse from `$ARGUMENTS` only — accepts `--issue <#|url>` flag or a bare issue number / GitHub issue URL. If not provided, skip the issue close entirely. **Do not prompt the user.**

---

## Procedure

Follow `~/.copilot/dreamers/refs/close-out-procedure.md` in the appropriate mode (FULL or LIGHT). The procedure includes its own user approval gate at Step 5 and reads `pr-procedure.md` in full at Step 6 for the push + PR creation.

Update this skill's todo as each step completes.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (yes/no/N/A).
- Retro file path (FULL mode).
- Improvements surfaced for user follow-up (FULL mode).
- Project state scan summary (FULL mode).

For LIGHT mode, exit with the per-plan PR URL and a one-line status block per close-out-procedure's LIGHT mode exit format.

---

## What this skill does NOT do

- Does NOT invoke any other skill. Echo is spawned as a subagent inline at Step 2; PR creation runs inline at Step 6 per `pr-procedure.md`.
- Does NOT spawn agents outside the 5-item allowlist. Only Echo is used in this skill.
