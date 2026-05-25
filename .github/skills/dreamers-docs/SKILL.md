---
name: dreamers-docs
description: 'Standalone docs-update entry point. Spawns Echo to update Echo-owned sections of `.github/copilot-instructions.md` plus any other project docs affected by recent changes. Triggers: /dreamers-docs, update docs, echo docs update.'
argument-hint: '[--branch | --staged] (defaults to --branch: diff vs origin/<default>)'
---

## What this skill does

Standalone entry point for ad-hoc documentation updates. The user invokes this when they have made changes (manually or via another skill) and want Echo to update project docs without running a full close-out cycle.

The skill resolves the diff scope (feature-branch diff vs default, or staged-only) and spawns Echo as a subagent with that context. Echo audits the changed files, updates Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands), and surfaces any other project docs that need updates (README, CHANGELOG, project-specific docs).

Echo stages its edits with `git add` but does NOT commit. The user handles the commit after reviewing the diff.

---

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, Echo-owned section list, tech stack.

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

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Resolve diff scope (per `--branch` or `--staged` flag)
- [ ] Spawn Echo with changed-files context
- [ ] Capture doc changes + open questions from Echo output
- [ ] Surface result to the user

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**Subagent prompt rule:** when spawning Echo below, include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in Echo's prompt. Per `orchestration-flow.md` § "Single-owner todo rule."

---

## Step 1 — Resolve diff scope

Parse `$ARGUMENTS`:

- `--branch` (default if no args) — scope to feature-branch diff vs default.
- `--staged` — scope to staged + unstaged changes on the current branch.

Detect the default branch (canonical two-step):

```bash
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
```

Resolve the changed-files list:

- `--branch` mode: `git diff --name-only origin/$DEFAULT...HEAD`
- `--staged` mode: union of `git diff --cached --name-only` and `git diff --name-only`

If the changed-files list is empty, output `No changes detected — nothing for Echo to document` and exit.

## Step 2 — Spawn Echo

Invoke Echo via the `task` tool:

- `agent_type: "echo"`, `mode: "sync"`

Pass in the prompt (per `delegation.md`):

- **Context:** ad-hoc documentation update; no plan binding. User wants project docs synced with recent changes.
- **Prior work:** changed-files list (from Step 1), diff base (`origin/$DEFAULT` for `--branch` mode, working tree for `--staged` mode).
- **What is needed:** review the changed files and update project docs as appropriate — Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands), plus README, CHANGELOG, or any project-specific docs the project conventions specify. Skip sections the change doesn't materially affect.
- **Constraints:** Echo edits docs ONLY — no production code, no tests. Stage edits with `git add` but do NOT commit (the user commits after review). **Do NOT call `manage_todo_list` — the orchestrator owns the todo.**
- **Definition of Done:** structured chat output per Echo's output discipline (status line + docs-changes log + instruction-file changes + comment audit + open questions).

Wait for Echo to signal completion. Capture the doc-changes log + any open questions.

## Step 3 — Handle Echo output

- **`Docs updated — N files changed`** → mark todo complete; proceed to Step 4 reporting.
- **`No doc updates needed`** → mark todo complete; tell the user no docs needed updating; exit.
- **Open questions raised** → surface each to the user via `request_information`. Capture answers. If an answer requires Echo to revise, re-spawn Echo with the clarification; if it's out-of-scope, note in the report and move on.

## Step 4 — Report

Tell the user:
- Files Echo touched (doc-changes log verbatim).
- Run `git status` + `git diff --cached` to review before committing.
- Suggested commit message: `docs: update for recent changes` (or appropriate).

This skill does NOT commit, does NOT push, does NOT open a PR. Echo's edits stay staged.

---

## What this skill does NOT do

- Does NOT commit Echo's edits — that's the user's call after review.
- Does NOT push or open a PR.
- Does NOT modify code or tests.
- Does NOT invoke any other skill. Echo is the only subagent spawned here.
- Does NOT spawn agents outside the 5-item allowlist (`sentinel`, `probe`, `hone`, `echo`, `sage`). In this skill, only Echo is used.
