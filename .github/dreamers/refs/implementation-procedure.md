# Implementation Procedure (canonical)

This ref is the SOLE source of truth for the Dreamers implementation phase (one cycle per plan). Both `/dreamers-implement` (standalone) and `/dreamers-full` (end-to-end pipeline) follow this procedure for each plan in their sequence. There is no composed-mode branching.

---

## Inputs

- A **plan file path** (`.dreamers/plans/feature-<slug>/plan-NN-<name>.md`).
- The branch the cycle runs on (the orchestrator handles branch setup before invoking this procedure; this procedure assumes the correct branch is already checked out).
- Optional **shared context payload** when invoked from a manifest-mode pipeline run — the manifest's Shared constraints / design decisions / data models / end-to-end ACs are threaded into the per-cycle reviewer prompts. Skip if no shared context was passed.

## Outputs

- One commit on the branch (the cycle's commit, with `Plan: feature-<slug>/plan-NN-<name>` in the body).
- Updated `./test-benchmarks.md` row if the project uses one.

This procedure runs ONE cycle per invocation. Multi-plan sequences run this procedure N times.

The orchestrator's todo (a single list owned by the top-level skill) records cycle completion.

---

## Subagent failure recovery (applies to any reviewer invocation below)

Per `agent-recovery.md`: if Sentinel, Probe, or Hone hits a rate limit, crashes, or times out mid-run:

1. Read whatever the failing reviewer managed to write before failing (chat output, any staged files via `git status`).
2. Determine which checks completed and which remain.
3. Complete remaining work inline (the orchestrator has Read/Write/Edit/Bash) OR re-spawn the affected reviewer scoped to only the remaining work. The other two reviewers' outputs are unaffected — do not re-spawn them.
4. Do not re-run steps that already completed — build on partial progress.

---

## Step 1 — Read plan + write failing tests

Read the plan file passed as input.

Read the plan's Acceptance Criteria (numbered Given/When/Then with `*Layer: ...*` annotations per `plan-writing-guide.md`). For each AC, write at least one failing test that would verify it, at the layer the annotation specifies. There is no separate Test Cases section in the new plan format — the ACs are the test specification.

- Tests live wherever the project's test convention specifies (consult `.github/copilot-instructions.md`).
- Stage with `git add`.
- Do not run yet — they should fail.

## Step 2 — Implement

**HARD STOP — implementation is inline.** The orchestrator (running this procedure in its context) edits files directly using Edit / Write / Bash tools. **Do NOT spawn any subagent to write code.** Specifically:
- ❌ `agent_type: "general-purpose"` → FORBIDDEN. There is no general-purpose fallback for implementation.
- ❌ Any other host-runtime agent → FORBIDDEN.
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `delegation.md`).
- ✅ The only `agent_type` values you may spawn during this procedure are `sentinel` / `probe` / `hone` in Step 5 (parallel review). Nothing else.

If you reach the implementation step and find yourself thinking "let me delegate this to an agent," that's the bug. The orchestrator does the implementation.

Follow the **Implementation discipline** rules in `orchestrator-discipline.md`:
- Edit only files in the plan's scope.
- No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- All `import` statements at the top of each file.
- Method-signature changes: grep the full codebase for every call site before staging.
- No spec-arguing comments in source.
- No dependency installs without explicit user approval — surface and ask first if a new dependency is required.
- Stage with `git add` as work progresses.

## Step 3 — Type-check + run tests

1. Run the project's type-check command. Fix any errors before proceeding.
2. Run the project's test command (scoped to the new tests if the runner supports it; else full suite). Use the recommended timeout from `./test-benchmarks.md` if the file exists.

If tests fail:
- Diagnose. Fix inline (production code, not the tests — the tests express the spec).
- Re-run. Repeat up to 3 attempts.
- If still failing after 3 attempts, stop and surface to the user. Do not loosen the tests to make them pass.

Update `./test-benchmarks.md` with the actual run time after the suite passes (per `testing-mandate.md`).

## Step 4 — Coverage sweep (mandatory, unskippable checklist)

After tests are green, run the coverage sweep before invoking the reviewers:

- [ ] **AC coverage matrix:** for every plan AC, name the test(s) that cover it. Any AC without a covering test → write one now.
- [ ] **Layer audit — Unit:** for each changed file, are there functions, branches, or error paths with no unit test?
- [ ] **Layer audit — Integration:** are there layer boundaries (repo↔DB, service↔API, function↔trigger) exercised by this change without an integration test?
- [ ] **Layer audit — UI / E2E:** are there user-facing flows, screen states, or navigation paths introduced or changed without a UI / E2E test? (Navigation change = E2E required, not optional.)
- [ ] **Negative + edge cases:** for each piece of non-trivial logic, is there a test for invalid input, boundary values, empty/null/max, error states?
- [ ] **Regression risks:** anything in the change that touches existing behavior — is the most likely regression covered?
- [ ] **Final missed-AC check:** re-read the plan's Acceptance Criteria one last time and confirm every AC has a green test. Hard gate.

Any gap → write the test now. Re-run the test command. Loop until all checklist items pass.

## Step 5 — Parallel review (Sentinel + Probe + Hone)

Spawn **three reviewers in parallel** in a single batched `task` call. All three are read-only / report-only; each returns structured findings in the format from `orchestrator-discipline.md`. None of them edits files.

**Subagent prompt rule (every spawn):** include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in each subagent's prompt. Subagents must not touch the todo mechanism — that's the orchestrator's lane.

Common prompt context for all three:
- Plan file path
- Scope: list of changed files from `git status`
- Branch + default branch names
- What the orchestrator has done: written failing tests, implemented, type-checked, ran tests (passing), completed coverage sweep.
- **Shared context (if applicable)** — when manifest-mode is in effect, the orchestrator passes the manifest's Shared constraints + Shared design decisions + Shared data models + End-to-end ACs verbatim under a "Feature context" header. Reviewers use this to evaluate the current plan in light of the full feature.

Per-reviewer prompt addition:

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`):
- Lenses: correctness, security, maintainability.
- Out of scope: test coverage (Probe's lane), simplicity (Hone's lane).
- Return: structured findings per the spec, plus plan-alignment summary.

**Probe** (`agent_type: "probe"`, `mode: "sync"`):
- Lens: test coverage (AC matrix, layer audit, edge cases, gaps).
- Out of scope: correctness/security/maintainability (Sentinel's lane), simplicity (Hone's lane).
- Return: structured findings per the spec, plus plan AC coverage table.

**Hone** (`agent_type: "hone"`, `mode: "sync"`):
- Lens: simplicity / over-engineering / redundancy / architectural quality.
- Out of scope: correctness/security/maintainability (Sentinel's lane), test coverage (Probe's lane).
- Return: structured findings per the spec.
- **Mandate reinforcement (include in Hone's prompt verbatim):** "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor — do not soften, hedge, or omit findings because the fix is big. When the suggested fix has architectural scope (touches files outside the plan, requires a new module, requires schema or symbol changes, or amounts to a full refactor of a subsystem), state the scope explicitly in the suggested-fix text. The orchestrator's major-refactor finding gate (per `orchestrator-discipline.md`) routes those findings through the user for apply-now vs defer decisions. Your job is to surface; the gate handles disposition."

## Step 6 — Apply findings inline (orchestrator-as-fixer)

Concatenate findings from all three reviewers per the orchestrator-as-fixer behavior in `orchestrator-discipline.md`:

1. **Sort by severity** (critical → high → medium → low).
2. **Resolve conflicts** per the conflict-resolution rule: correctness > simplicity. Genuine ambiguity → surface to user before applying.
3. **Evaluate each finding against the Major-refactor finding gate** per `orchestrator-discipline.md` § "Major-refactor finding gate." For each finding, check the closed 6-criterion checklist (new module / schema change / cross-cutting refactor / new exported symbols / files outside plan scope / Hone-recommended full refactor). If ANY criterion fires, call `request_information` with the 3-choice template from the canonical rule (`Apply now — refactor in this cycle` / `Defer — create follow-up plan` / `Other`) and route per the user's answer. On `Defer`, create the stub plan file at `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md` per the canonical template; do NOT apply the fix. The orchestrator NEVER silently applies a gate-triggering finding, regardless of severity.
4. **Apply each (non-deferred) fix inline** as a targeted Edit. Stage with `git add` as you go. Findings that didn't trigger the gate, OR that the user opted to `Apply now` via the gate, apply here.
5. **Re-run type-check + tests** after all fixes applied. If regressions appear, diagnose + re-fix inline (up to 3 attempts, then surface to user).

Handle non-finding outputs:
- Any reviewer returns **`Blocked — <reason>`** → halt cycle; surface; resolve; re-spawn the affected reviewer only.
- Any reviewer returns **open questions** → present each to the user before proceeding. Capture decisions; apply.
- All three return **`Approved — no findings`** → proceed to Step 7 directly. No fix application needed.

After fix application (or skip + any deferred stubs written), proceed to Step 7.

## Step 7 — User testing (if required)

Check the plan's `User-testing-required` field.

- **`no`** → proceed directly to Step 8.
- **`yes`** → pause the cycle by calling `request_information`. Do not commit until the user explicitly approves.

The `request_information` call MUST include every item below:

- **Plan being tested:** ID + full path (e.g. `plan-01-section-scorer` → `.dreamers/plans/feature-plan-quality-scoring/plan-01-section-scorer.md`).
- **Build / distribution details:** check for `.github/instructions/build.instructions.md` at the project root.
  - **If present:** follow it exactly. Execute only the steps it explicitly authorises the orchestrator to run. Surface every user-action step verbatim.
  - **If absent:** state plainly that there is no `build.instructions.md`. Ask the user to either build/distribute the test build themselves and confirm when ready, OR provide the steps so a `build.instructions.md` can be created. Do not invent build steps.
- **What changed in this cycle:** 1–3 bullets summarising the user-visible behaviour delivered.
- **Step-by-step test steps:** numbered, concrete, reproducible. Derive directly from the plan's Acceptance Criteria (Given/When/Then with Layer annotations).
- **Known limitations / out-of-scope:** anything the user might try that this cycle deliberately doesn't cover.
- **How to respond:**
  - `Approved — continue` (procedure proceeds to Step 8)
  - `Bug: <description>` (procedure fixes inline, re-runs tests, re-distributes per `build.instructions.md` rules, re-calls `request_information` with refreshed test steps)
  - Freeform notes / corrections are also accepted and treated as bugs unless clearly approving.

**Resume rules:**
- On `Approved — continue` → proceed to Step 8.
- On any bug or correction → **fix inline.** No Sentinel re-invocation: during user-testing rounds, the user IS the test layer. Diagnose → fix in production code → re-run the test command → re-build/distribute → re-call `request_information` with refreshed test steps. Do NOT commit until explicit approval.

## Step 8 — Commit the cycle

Run `git status` to confirm staged content. Run `git commit` with a message following the project's commit-message style (see `.github/instructions/git.instructions.md` if present).

**Plan reference (mandatory):** the commit body MUST include a line of the form:

```
Plan: feature-<slug>/plan-NN-<name>
```

Repo-relative plan path WITHOUT the `.md` extension and WITHOUT the `.dreamers/plans/` prefix. Example: `Plan: feature-plan-quality-scoring/plan-01-section-scorer`. This format is required for `/dreamers-close-out` standalone auto-detection to find the plan.

One commit per cycle. Do NOT push — push happens at close-out per `pr-procedure.md`.

---

## What happens after this procedure ends

This procedure ends at Step 8 commit. What happens next depends on the consuming skill:

- **`/dreamers-full`** (end-to-end pipeline): the orchestrator's todo records this cycle complete and moves to the next plan in the sequence (if multi-plan) OR proceeds to close-out (if last plan).
- **`/dreamers-implement`** (standalone): exit with success. Surface the commit hash and AC coverage matrix to the user. Next step (their choice): more cycles via another `/dreamers-implement` invocation against the next plan, OR `/dreamers-close-out` if all plans are shipped.

Either consumer maintains its own todo (single-owner rule). This procedure does not touch the todo.
