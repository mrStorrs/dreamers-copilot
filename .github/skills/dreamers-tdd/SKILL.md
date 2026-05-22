---
name: dreamers-tdd
description: 'TDD pipeline with inline implementation. Plan → write failing tests → implement → run tests → Sentinel-TDD review → user-test → close-out, all inline except a single Sentinel-TDD subagent pass per cycle. Faster than /dreamers-full for small-to-medium features. Triggers: /dreamers-tdd, tdd pipeline, fast pipeline, plan-tests-implement.'
---

## What this skill does (and how it differs from `/dreamers-full`)

A parallel pipeline that collapses Forge / Probe / Hone / Bolt into the orchestrator. Two subagents are kept: **Sentinel-TDD** (`sentinel-tdd.agent.md`) for the fresh-eyes review pass in each cycle, and **Echo** for the project-doc update at close-out. Nova in `replan` mode remains available as a cold-storage escape valve for genuine drift recovery.

The thesis: every subagent spawn pays a re-read tax (globals + project instructions + plan + prompt) before useful work starts. For most features that tax exceeds the work itself. Keep the work where the context lives — except for the two roles where fresh-eyes or specialised-doc-knowledge is worth the spawn (Sentinel-TDD's review, Echo's doc audit).

**What's preserved from `/dreamers-full`:** the planning conversation and approval gates (Phase 1), the user-testing pause via `request_info`, the plan-archive + improvements.md milestone discipline, the single-push-at-PR rule, the umbrella + sub-plans option for genuinely multi-stage features, **Echo's project-docs update at close-out**.

**What's collapsed inline:** implementation, test writing, test execution, plan re-verify between sub-plans, retro, push, PR creation.

**What's reviewed by a subagent:** Sentinel-TDD does correctness + security + maintainability + simplicity + test-coverage-gaps in one pass with fix-on-sight across BOTH production and test files.

`/dreamers-full` stays in place as the fallback. This skill is for validation before any consolidation.

## Recommended session model

This skill is tuned for **`gpt-5.4`** (set with `/model gpt-5.4` in your Copilot CLI session before invoking). Both the orchestrator AND any subagent spawn currently run on the session's default model — Copilot CLI ignores the `model:` frontmatter in agent files today (known parity gap with VS Code; future CLI releases are expected to honour it). Once parity lands, `sentinel-tdd.agent.md` will pin to `gpt-5.4` independently of the session.

## Pre-flight reads

Read these refs once at startup (use the `view` tool, full file — never `cat`/`head`/`tail`/`Select-String`, which truncate):

**Always-load (every run):**
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, push, Probe workspace wipe
- `~/.copilot/dreamers/refs/plan-content.md` — plan structure
- `~/.copilot/dreamers/refs/plan-rules.md` — plan naming
- `~/.copilot/dreamers/refs/planning-protocol.md` — the three-phase planning conversation rules
- `~/.copilot/dreamers/refs/citation-accuracy.md` — verify before citing existing artifacts in plans
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layers (the orchestrator IS the test writer here)
- `~/.copilot/dreamers/refs/comment-rules.md` — comment discipline (orchestrator is also implementer)
- `~/.copilot/dreamers/templates/logging-standards.md` — logging discipline (orchestrator writes log calls inline)
- `~/.copilot/dreamers/refs/delegation.md` — protocol for invoking Sentinel-TDD and Echo
- `~/.copilot/dreamers/refs/agent-recovery.md` — what to do if a spawned subagent crashes / times out
- `~/.copilot/dreamers/refs/close-out.md` — retro and post-PR procedure

**Load when umbrella mode is selected:**
- `~/.copilot/dreamers/refs/feature-decomposition.md` — how to split into independently shippable sub-plans

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, **test commands**, build commands. Binding — overrides defaults.
- `.github/instructions/build.instructions.md` (root, if present) — user-testing build/distribute playbook.
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Inline-discipline rules (non-negotiable)

When the orchestrator is doing work that would normally be delegated, it MUST follow these rules. These are baked in here because the agent files for Forge / Probe are not loaded in this pipeline.

### Implementation discipline (replaces Forge)

- **Plan adherence:** only edit files in the plan's scope (or that the plan's scope clearly entails). No "while I'm here" cleanup, no unrelated refactors mixed with feature work. If a refactor is genuinely needed for the plan's work, do it as a separate inline step and note it in chat.
- **Incremental edits:** make changes in small, coherent steps. Stage with `git add` as work progresses.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern. If a section permits something, cite the exact section number. When in doubt, implement the cleanest separation and let Sentinel-TDD judge.
- **All imports at the top of the file.** Every `import` statement before any declaration, function, or expression. Never insert imports mid-file or at the bottom.
- **Method signature changes:** when changing a signature (sync→async, parameter added/removed/renamed), grep the full codebase for every call site before staging. The plan's listed files are necessary but not sufficient.
- **Zustand creator objects:** never use ES getters (they're evaluated once at creation time and baked as static values, never reactive). Define computed values as exported selector functions outside the store.
- **Branch identity check:** before the first edit, run `git log --oneline -3` and confirm the branch and recent commits match the expected feature branch. If the working tree shows no feature commits for this milestone, stop and surface the discrepancy.
- **Data-model changes:** when a plan supersedes an earlier plan's data model, discard the old model completely. Cite the specific interface definitions from the plan's §Data Models (or equivalent) section before writing any new tables or classes.
- **No dependency installs without permission.** Do not add new packages, run `npm install <pkg>`, `pip install <pkg>`, or equivalent without explicit user approval. If a new dependency is needed for the plan, surface it in chat and ask before installing.
- **Type-check before declaring implementation done.** Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before moving to the test-run step.

### Comment-writing discipline (mandatory — orchestrator is also the implementer)

Pulled from `comment-rules.md`. The orchestrator now writes comments inline, so these rules apply directly to every code edit:

- **No plan/ticket references in source.** Never mention plan files, milestone names (e.g. `D25`, `plan-3`), ticket numbers, agent names, or sub-plan letters in source code (production OR test).
- **No separator comments.** Never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers.
- **No spec rationalization comments.** Implement cleanly; let review judge.
- **No redundant JSDoc/KDoc** that only repeats the function signature.
- **Style:** one line when possible; never exceed two lines for inline comments. Write *why*, never *what*. If a comment would need more than two lines to be useful, the code needs refactoring, not more words.
- **When to comment:** non-obvious logic (hidden constraints, gotchas, workarounds for specific bugs), public API documentation callers need, TODO/FIXME with specific actionable notes, license headers.

### Logging discipline (mandatory — orchestrator writes log calls inline)

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
- **High-frequency loop internals at DEBUG are allowed** if they add traceability value. Mark them with a `// high-freq` comment so Sentinel-TDD can assess noise risk.

### Test-writing discipline (replaces Probe)

- **Tests-first:** write failing tests against the plan's Acceptance Criteria and Test Cases (Given/When/Then) BEFORE implementing.
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
- **Regression analysis (mandatory when the originating task is a user-reported bug fix):** when the work in this skill was triggered by a user-reported bug, the close-out retro must answer three questions explicitly (see Phase 3 Step 3):
  1. **Why wasn't this caught?** — which test layer failed (no test existed; test existed but didn't cover this path; test covered it but assertion was wrong; test was skipped/deferred)
  2. **What was added?** — specific test(s) now covering this case (names + file paths)
  3. **What else might be missing?** — adjacent cases the same gap might have left uncovered

### Closeout / retro discipline

- **Retro file:** `.dreamers/retros/retro-d<N>-<name>.md` per `close-out.md`. Orchestrator writes this inline.
- **Echo-owned section updates** to `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands): delegated to the Echo subagent — see Phase 3 Step 2.

### Git discipline (replaces Bolt mechanical steps)

- Stage with `git add` as work progresses across all phases. Never commit mid-cycle.
- **One commit per cycle** (cohesive plan = one commit total; umbrella = one commit per sub-plan).
- Commit message follows `.github/instructions/git.instructions.md` (if present) or the conventional-commits style used by recent commits on the default branch. Body MUST include `Plan: plan-{slug}` (or `Plan: plan-{slug}-a`).
- **Push exactly once**, immediately before `gh pr create` at final close-out. Never push between sub-plans.

---

## Phase 1 — Planning

Identical in shape to `/dreamers-full` Phase 1. Reproduced here so this skill is self-contained.

### Phase 1a — Hash it out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question — use the `ask_user` tool one question at a time within a single round. Do not trickle questions across multiple message turns.
4. Wait for the user's responses before proceeding.

If the task is fully unambiguous, skip to Phase 1b with a brief "I understand the goal as: …" confirmation.

### Phase 1b — User Input Audit (gate)

Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it.

### Phase 1c — Approval gate

Present this proposal block in chat:

```
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…
```

Call `ask_user` with choice `["Approved"]` and allow inline freeform corrections in the same interaction. Treat any non-approval freeform response as corrections; revise and re-present until explicit approval.

### Phase 1d — Decide plan shape

Single decision, default to cohesive:

- **Cohesive plan** (default) — one plan file, one PR. Use when the work can ship as a single coherent change.
- **Umbrella + sub-plans** — multi-cycle, still one PR at end. Use ONLY when the work genuinely needs to land in stages (e.g., risky migration with backfill, breaking change requiring shim period, multi-screen feature that needs sub-plan boundaries for git-history hygiene).

State your choice in chat with a one-sentence rationale before proceeding.

**If umbrella mode is selected, follow these decomposition criteria** (from `feature-decomposition.md`):

- Each sub-plan can be merged to main independently — no sub-plan depends on an un-merged sibling.
- A sub-plan touches at most one data-layer change + one UI surface.
- Split at natural seams: model → repository → viewmodel → screen → cloud function. These are common split points.
- If a sub-plan would take more than ~300 lines of new/changed code, split it further.
- **Testability gate:** each sub-plan must have at least one machine-verifiable assertion that can be declared pass/fail in isolation, before the next sub-plan starts. If testability requires a sibling sub-plan not yet shipped, the split boundary is wrong — reslice.
- **When NOT to decompose:** truly atomic changes (a single model field, a single bug fix, a single screen tweak) stay cohesive. Decomposition is overhead for atomic work.

### Phase 1e — Write plan file(s)

Plan filenames follow `plan-{slug}.md` (umbrella or standalone) and `plan-{slug}-a.md`, `plan-{slug}-b.md`, … (sub-plans). Slug rules per `plan-rules.md`. Plans live in `./.dreamers/plans/`.

Use templates as starting structure:
- `~/.copilot/dreamers/templates/plan-sub.md` — sub-plans and standalone (cohesive) plans
- `~/.copilot/dreamers/templates/plan-umbrella.md` — umbrella plans only

**Each plan must include:**
- Metadata: Owner, Date, Scope, (Parent + Depends-on if sub-plan), Status (Draft/Active/Completed/Superseded), User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases (Given/When/Then for non-trivial), Rollback boundary, Risks/Mitigations

**Design Decisions format** (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User-testing required:** `yes` if a human must manually verify before the next cycle begins (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Plans MUST NOT include code snippets.** One exception: interface/type contracts where the signature itself is the design decision.

### Phase 1e.1 — Component usage check (mandatory)

When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's source root from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 1e.2 — Citation accuracy

Before citing the behavior, structure, content, or API of any existing artifact in the plan — test file, test method, repository method, ViewModel property, Maestro YAML, UI assertion pattern, or any other code artifact — read and verify the source during this planning session. Claiming "method X does Y" or "test Z asserts W" without reading the file is a planning error; the plan becomes a liability when implementation builds against a wrong assumption.

- **If the artifact cannot be read** (e.g., it belongs to a future sub-plan and doesn't exist yet): state explicitly in the plan that the citation is an assumption pending verification. Do not present it as confirmed fact.
- **Maestro `assertVisible` / `assertNotVisible` collision check** (mobile UI tests): when a plan specifies asserting on visible text, read the target screen's Compose code (or equivalent) and verify no OTHER persistent UI element (filter tabs, headers, navigation labels, bottom-bar items) shares that text. If a collision exists, the plan must specify a more-specific assertion string that matches only the intended element.

### Phase 1f — Plan quality self-check (mandatory)

Before exiting Phase 1, verify the plan(s) against:
- [ ] Filenames follow `plan-{slug}[-a..n].md`
- [ ] Non-trivial features have an umbrella + sub-plans (not monolithic)
- [ ] Every sub-plan / standalone has measurable Acceptance Criteria
- [ ] Every sub-plan / standalone has Test Cases (Given/When/Then) for non-trivial cases
- [ ] Every sub-plan / standalone has Design Decisions in the structured format
- [ ] Every sub-plan / standalone has a Rollback Boundary
- [ ] Every sub-plan / standalone has a Status field (Draft / Active / Completed / Superseded)
- [ ] Plans reference only files/paths that exist (no invented paths)
- [ ] Sub-plan splits at natural seams (not arbitrary line-count cuts)
- [ ] No sub-plan's testability depends on a sibling not yet shipped
- [ ] No code snippets (exception: interface/type contracts only)

Any failure → halt and prompt the user with the specific item(s) that failed.

### Phase 1g — Implementation start approval gate (mandatory)

Phase 1c approved the high-level goal. Phase 1g approves the actual plan files before any implementation work begins.

Present this block:

```
**Plans written and ready for review:**

- `path/to/plan-{slug}.md` — [one-line summary from plan Summary]
- `path/to/plan-{slug}-a.md` — [one-line summary]  (if umbrella)
- ...

Please read the plan file(s) above. Reply "Approved — start implementation" to begin Phase 2, or describe any corrections needed.
```

Call `ask_user` with choice `["Approved — start implementation"]` and allow inline freeform corrections.

- Approval → proceed to Phase 2.
- Corrections → revise plan files, re-run Phase 1f, re-present this gate. Loop until approved.

Do not proceed to Phase 2 until the user explicitly approves the plan files at this gate.

---

## Phase 2 — Implementation cycle (inline)

### MANDATORY first actions (in order, once at Phase 2 entry)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note.
2. **Branch setup (inline, per `git-workflow.md`):**
   - Detect default branch (canonical two-step):
     ```bash
     DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
     ```
   - **Anchor to remote truth (mandatory before reading any `.dreamers/` files):** `git fetch origin && git log origin/$DEFAULT --oneline -5`. Workspace files in `.dreamers/` are local-only and may be stale; `origin/$DEFAULT` is the authoritative record of what is actually shipped.
   - `git checkout $DEFAULT && git pull origin $DEFAULT` — never build off a stale local default branch.
   - Cut `feat/d<N>-<name>` from `$DEFAULT`.
   - **Wipe stale Probe workspace files** (if a prior `/dreamers-full` run left them — this skill does not use them but they cause confusion if stale):
     ```bash
     for f in .dreamers/probe/test-plan.md .dreamers/probe/runbook.md .dreamers/probe/bugs.md .dreamers/probe/regression-analysis.md; do
       [ -f "$f" ] && printf 'No active work.\n' > "$f"
     done
     ```
   - Archive prior feature's plan files if its PR is merged (`gh pr list --state merged`; `mv` to `.dreamers/plans/archive/`, never delete).
   - Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edits.
3. **Branch identity check** — `git log --oneline -3`. Confirm branch + recent commits match the expected feature.

### Subagent failure recovery (applies to Sentinel-TDD and Echo invocations below)

Per `agent-recovery.md`: if a spawned subagent hits a rate limit, crashes, or times out mid-run:

1. Read whatever the agent managed to write before failing (chat output, any staged files via `git status`).
2. Determine which checks/fixes completed and which remain.
3. Complete remaining work inline (the orchestrator has Read/Write/Edit/Bash) OR re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.

### Per cycle loop (one cycle for cohesive plan; one cycle per sub-plan for umbrella)

For each plan / sub-plan, the orchestrator runs the following sequence inline. Each numbered step is a phase the orchestrator MUST complete before moving on.

#### Step 1 — Write failing tests

Read the plan's Acceptance Criteria and Test Cases (Given/When/Then). For each AC, write at least one test that would verify it. Cover the Given/When/Then scenarios as written.

- Tests live wherever the project's test convention specifies (consult `.github/copilot-instructions.md`).
- Stage with `git add`.
- Do not run yet — they should fail.

#### Step 2 — Implement

Follow the **Implementation discipline** rules above. Edit only files in the plan's scope. Stage with `git add` as you go.

#### Step 3 — Type-check + run tests

1. Run the project's type-check command. Fix any errors before proceeding.
2. Run the project's test command (scoped to the new tests if the runner supports it; else full suite).

If tests fail:
- Diagnose. Fix inline (production code, not the tests — the tests express the spec).
- Re-run. Repeat up to 3 attempts.
- If still failing after 3 attempts, stop and surface to the user. Do not loosen the tests to make them pass.

#### Step 4 — Coverage sweep (mandatory, unskippable checklist)

After tests are green, run the coverage sweep before invoking Sentinel-TDD. This is the structured replacement for Probe's Coverage Expansion pass. Work through item by item, do not collapse to "looks fine":

- [ ] **AC coverage matrix:** for every plan AC, name the test(s) that cover it. Any AC without a covering test → write one now.
- [ ] **Layer audit — Unit:** for each changed file, are there functions, branches, or error paths with no unit test?
- [ ] **Layer audit — Integration:** are there layer boundaries (repo↔DB, service↔API, function↔trigger) exercised by this change without an integration test?
- [ ] **Layer audit — UI / E2E:** are there user-facing flows, screen states, or navigation paths introduced or changed without a UI / E2E test? (If a navigation element changed: E2E coverage is required, not optional.)
- [ ] **Negative + edge cases:** for each piece of non-trivial logic, is there a test for invalid input, boundary values, empty/null/max, error states?
- [ ] **Regression risks:** anything in the change that touches existing behavior — is the most likely regression covered?
- [ ] **Final missed-AC check:** re-read the plan's Acceptance Criteria one last time and confirm every AC has a green test. Any AC without a covering test → write the test before signaling cycle complete. Hard gate.

Any gap → write the test now. Re-run the test command. Loop until all checklist items pass.

#### Step 5 — Sentinel-TDD review (the ONLY subagent in the cycle)

Invoke Sentinel-TDD via the Agent tool:

```
agent_type: "sentinel-tdd"
mode: "sync"
prompt:
  Context: TDD pipeline. You are the only fresh-eyes pass for this cycle.
  Plan file: <absolute path to the active plan / sub-plan>
  Scope: <list of changed files from git status, or scope description>
  Branch: <current feature branch>
  Default branch: <detected default>
  What the orchestrator has done: written failing tests, implemented, type-checked, ran tests (passing), completed coverage sweep.
  Five lenses to apply: correctness, security, maintainability, simplicity / over-engineering, test coverage gaps.
  Fix-on-sight in BOTH production and test files. Type-check + re-run tests after fixes.
  Return: status line + severity-graded lane-labelled fixes-applied list + plan-alignment summary + simplifications-not-made + design questions.
```

Wait for Sentinel-TDD to signal completion. Read its chat output.

#### Step 6 — Handle Sentinel-TDD output

- **`Approved — no fixes needed`** → proceed to step 7.
- **`Fixed and approved — N fixes applied`** → proceed to step 7. Sentinel-TDD already type-checked + re-ran tests. The orchestrator does not need to re-verify mechanically.
- **`Blocked — <reason>`** → halt cycle. Surface the block to the user. Common cases: plan AC missing, plan revision needed, scope ambiguity. Resolve via Phase 1 revision or direct user input, then resume from step 5.
- **Design questions raised** → present each question to the user before proceeding. Capture decisions inline. Apply the decisions; if implementation changes meaningfully, re-run steps 3 + 4 + 5 for the affected scope.

#### Step 7 — User testing (if required)

Check the plan's `User-testing-required` field.

- **`no`** → proceed directly to step 8.
- **`yes`** → pause the cycle by calling `request_info`. Do not commit until the user explicitly approves.

The `request_info` call MUST include every item below. Do not abbreviate. The user reads only what is in this prompt — anything missing means they cannot test:

- **Plan being tested:** ID + path (e.g. `plan-{slug}-a` → `.dreamers/plans/plan-{slug}-a.md`).
- **Build / distribution details:** check for `.github/instructions/build.instructions.md` at the project root.
  - **If present:** follow it exactly. Execute only the steps it explicitly authorises the orchestrator to run. Surface every user-action step (install on device, launch app, open URL, version/build to verify) verbatim.
  - **If absent:** state plainly that there is no `build.instructions.md`. Ask the user to either (a) build/distribute the test build themselves and confirm when ready, or (b) provide the steps so a `build.instructions.md` can be created. Do not invent build steps.
- **What changed in this cycle:** 1–3 bullets summarising the user-visible behaviour delivered.
- **Step-by-step test steps:** numbered, concrete, reproducible. Derive directly from the plan's Acceptance Criteria and Test Cases (Given/When/Then). Each step states the action and the expected observation.
- **Known limitations / out-of-scope:** anything the user might try that this cycle deliberately doesn't cover.
- **How to respond:**
  - `Approved — continue` (orchestrator proceeds to commit)
  - `Bug: <description>` (orchestrator fixes inline, re-runs tests, re-distributes per `build.instructions.md` rules, re-calls `request_info` with refreshed test steps)
  - Freeform notes / corrections are also accepted and treated as bugs unless clearly approving.

**Resume rules:**
- On `Approved — continue` → proceed to step 8.
- On any bug or correction → **the orchestrator fixes inline.** No Sentinel-TDD re-invocation: during user-testing rounds, the user IS the test layer. Steps: diagnose → fix in production code → re-run the test command to confirm no regression → re-build/distribute per `build.instructions.md` (or ask the user if no file) → re-call `request_info` with refreshed test steps that reproduce the original bug scenario plus any other steps still requiring user verification. Do NOT commit until explicit approval.

#### Step 8 — Commit the cycle

Run `git status` to confirm staged content. Run `git commit` with a message following the project's commit-message style (see `.github/instructions/git.instructions.md` if present). Message body MUST include `Plan: plan-{slug}` (or `Plan: plan-{slug}-a` for sub-plans).

One commit per cycle. Do not push yet.

#### Step 9 — Inline plan re-verify (umbrella mode only)

If this was a sub-plan and another sub-plan remains, perform an inline drift check before starting the next sub-plan. The orchestrator already has the context from having just done the work — no Nova needed.

Re-read the NEXT sub-plan file. Ask explicitly:
- Does it still apply against the codebase as it now stands?
- Did anything in this just-completed sub-plan change the file paths, function signatures, or data shapes the next sub-plan references?
- Are the next sub-plan's Acceptance Criteria still measurable against the current code?

**If yes to all three** → proceed to Step 1 of the next cycle.
**If any drift** → surface the drift items to the user. If recovery is non-trivial, the user may request escalation to Nova `replan` mode (one of the remaining subagents). Otherwise revise the sub-plan inline, re-run Phase 1f quality check, then proceed.

---

## Phase 3 — Close-out (inline)

After all cycles complete:

### Step 1 — improvements.md milestone-close

Append any new improvement suggestions from this milestone to `.dreamers/improvements.md`. Format: dated entry, one sentence each, references the retro file path.

### Step 2 — Echo (docs subagent)

Invoke Echo via the Agent tool:

```
agent_type: "echo"
mode: "sync"
prompt:
  Context: TDD pipeline close-out. The orchestrator did the implementation inline.
  Plan file(s): <absolute paths to the plan(s) shipped this milestone>
  Changed files: <output of `git diff --name-only origin/<DEFAULT_BRANCH>...HEAD`>
  Diff base: origin/<DEFAULT_BRANCH>
  Sentinel-TDD summary: <one-paragraph concatenation of Sentinel-TDD chat outputs across all cycles — status lines + fixes-applied counts + any open design questions>
  Scope: update Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands) and any other project docs that need updates based on what shipped. Skip sections the change doesn't materially affect.
  Return: doc-changes log + open questions (use "none" if empty) in chat output.
```

Wait for Echo to signal completion. Read its chat output.

If Echo flags open questions, resolve them before the final commit.

### Step 3 — Retro

Write `.dreamers/retros/retro-d<N>-<name>.md` per `close-out.md`. Required sections:
- **What worked well** — clean handoffs, agents that ran without rework, inline phases that held up
- **Friction points** — weak output, rework, unclear handoffs, places the inline discipline slipped
- **Proposed improvements** — specific, actionable edits to this skill, `sentinel-tdd.agent.md`, or refs. Reference the exact section to change and why.

Additionally, write an inline summary of:
- AC coverage matrix from this cycle (which test covers which AC) — replaces Probe's `test-plan.md`
- Bugs found during user-testing (if any) and how they were fixed — replaces Probe's `bugs.md`
- Regression analysis (if the originating task was a user-reported bug): why wasn't it caught? what test was added? what else might be missing? — replaces Probe's `regression-analysis.md`

### Step 4 — Final commit (if needed)

If Step 2 wrote any doc updates, or any other uncommitted changes exist, create a final commit:
1. `git status`
2. If changes exist: `git add` + `git commit -m "docs: final cleanup before PR"` (or appropriate)
3. If no changes: skip — never create empty commits.

### Step 5 — Push + PR (inline, no Bolt)

1. `git push -u origin <branch-name>` (this is the ONLY push in the whole pipeline)
2. Draft PR body from `~/.copilot/dreamers/templates/pr-description.md`. Capture: what shipped, AC checklist, Sentinel-TDD severity summary (concatenated across cycles), test command + result, user-testing notes.
3. `gh pr create --title "<short title>" --body "<body>" --base <DEFAULT_BRANCH>`
4. Capture the PR URL.

### Step 6 — Issue close (if applicable)

If the original task referenced a GitHub issue number / URL:
```bash
gh issue close <number> --comment "Resolved in <PR URL>"
```

### Step 7 — Plan archive

For any merged prior PR's plan file in `.dreamers/plans/`:
- Verify the PR is merged (`gh pr view <number> --json state -q .state` returns `MERGED`).
- `mv` the plan file to `.dreamers/plans/archive/` (create dir if needed). Never delete.

(The CURRENT cycle's plan stays in `.dreamers/plans/` until its own PR is merged — typically archived on the NEXT milestone.)

### Step 8 — Post-PR discipline (from `close-out.md`)

After `gh pr create` succeeds:

1. **No auto-commit after PR is created.** If any further changes are needed (e.g. addressing review comments, fixing CI failures), do NOT auto-commit and push. Ask the user first: *"I have changes ready. Should I commit and push these to the PR?"* Only commit and push after explicit user approval. Commit message: `fix: address PR feedback` (or appropriate).

2. **Surface improvements from this cycle's retro** — list each as one sentence and ask: *"Should I address any of these?"* Do not apply without user go-ahead.

3. **Project state contradiction scan** (read durable surfaces, check for drift, surface — do NOT auto-apply):
   - The just-merged PR description vs the umbrella plan (if umbrella mode was used)
   - `git log origin/$DEFAULT -10 --format=%s` — recent merged work
   - Project-level `.github/copilot-instructions.md` Echo-owned sections (Tech stack, Repo structure, Conventions, Key files) — does the codebase still match?
   - `.dreamers/improvements.md` — open items still relevant?
   - Surviving Probe artifacts (if any from prior `/dreamers-full` runs) — anything stale?

   Check for: tech stack drift, architecture pivots not reflected in instructions, milestone status drift, rule conflicts across agent definitions. **Propose all changes — do not auto-apply.** Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

4. **Post-PR push (if changes approved):** use plain `git push` (no force). The PR updates automatically.

---

## Push discipline

`git push` happens EXACTLY ONCE — Phase 3 Step 5, immediately before `gh pr create`. Never push between cycles.

## Agent inventory in this skill

- **Sentinel-TDD** — `agent_type: "sentinel-tdd"`, invoked once per cycle (Phase 2 Step 5). Fresh-eyes review across five lenses, fix-on-sight in both lanes.
- **Echo** — `agent_type: "echo"`, invoked once per milestone (Phase 3 Step 2). Project-doc updates.
- **Nova `replan` mode** — escape valve for genuine drift recovery only (Phase 2 Step 9). Rare.

No Forge, Probe, Hone, or Bolt are invoked in this skill. Their work happens inline in the orchestrator with the embedded discipline rules above.

## When to use `/dreamers-tdd` vs `/dreamers-full`

| Use `/dreamers-tdd` when | Use `/dreamers-full` when |
|---|---|
| Single cohesive feature, can fit one plan | Genuinely multi-stage feature needing umbrella decomposition by design (not just by size) |
| You want the fastest iteration cycle | You want maximum lane separation + fresh-eyes coverage across roles |
| The work is well-scoped and the orchestrator has firm context | The work spans unfamiliar code paths where Probe-style coverage expansion as a separate context adds real value |
| You're comfortable with one fresh-eyes pass (Sentinel-TDD) covering five lenses | You want each lens reviewed in its own dedicated context |

Both skills are kept active during the validation period. The user picks per task.
