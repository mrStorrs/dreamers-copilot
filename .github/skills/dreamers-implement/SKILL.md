---
name: dreamers-implement
description: 'Implementation phase of the Dreamers pipeline. Reads an approved plan file and runs the per-cycle loop (failing tests → implement → run tests → coverage sweep → parallel review (Sentinel + Probe + Hone) → optional user-test → commit). Invokable standalone (given a plan path) or composed from `/dreamers-full` Phase 2. Triggers: /dreamers-implement, implement this plan, execute the plan.'
argument-hint: 'path/to/plan.md'
---

## What this skill does

Takes an approved plan file as input and runs one implementation cycle:

1. Write failing tests against the plan's AC + G/W/T
2. Implement per the plan
3. Type-check + run tests
4. Coverage sweep
5. Spawn Sentinel + Probe + Hone in parallel for fresh-eyes review
6. Apply findings from all three reviewers inline
7. User-testing pause (if plan requires)
8. Commit the cycle

**One cycle per invocation.** One plan = one invocation = one commit. For multi-plan work, the user (or `/dreamers-full` orchestrator) invokes this skill once per plan in the sequence.

This skill does NOT push, does NOT open a PR, does NOT update docs. That's `/dreamers-close-out`'s job.

## Pre-flight reads

Read these refs once at startup (full file, no truncation):

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — the shared discipline (implementation + comment + logging + test-writing + git rules)
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, staging, push discipline
- `~/.copilot/dreamers/refs/comment-rules.md` — comment discipline
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations
- `~/.copilot/dreamers/templates/logging-standards.md` — logging discipline
- `~/.copilot/dreamers/refs/agent-recovery.md` — recovery if Sentinel crashes mid-run
- `~/.copilot/dreamers/refs/delegation.md` — protocol for invoking reviewers (Sentinel, Probe, Hone)

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, **test commands** (binding), build commands.
- `.github/instructions/build.instructions.md` (root, if present) — user-testing build/distribute playbook.
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.

If no plan path is provided in `$ARGUMENTS`, halt and ask the user — do not invent or skip the plan. (Plan content is read in Step 1, AFTER the MANDATORY first actions below establish anchored remote state.)

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Read plan file
- [ ] Write failing tests
- [ ] Implement
- [ ] Type-check + run tests
- [ ] Coverage sweep
- [ ] Spawn parallel review (Sentinel + Probe + Hone)
- [ ] Apply reviewer findings + re-run tests
- [ ] User-test pause (if plan requires it)
- [ ] Commit the cycle

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-full`, do NOT declare a new list — update the parent's matching Phase 2 cycle item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## MANDATORY first actions (in order, once at skill entry)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note. (Skip if called from `/dreamers-full` — orchestrator handles this at Phase 2 entry, not per plan.)

2. **Branch setup (inline, per `git-workflow.md`):** (Skip if called from `/dreamers-full` — orchestrator handles this at Phase 2 entry.)
   - Detect default branch (canonical two-step):
     ```bash
     DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
     ```
   - **Anchor to remote truth (mandatory before reading any `.dreamers/` files):** `git fetch origin && git log origin/$DEFAULT --oneline -5`. Workspace files in `.dreamers/` are local-only and may be stale; `origin/$DEFAULT` is the authoritative record of what is actually shipped.
   - If currently on default branch: `git checkout $DEFAULT && git pull origin $DEFAULT`, then cut `feat/d<N>-<name>` from `$DEFAULT`.
   - If already on a feature branch: confirm via `git branch --show-current`. Stay on it.
   - Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edits.

3. **Branch identity check** — `git log --oneline -3`. Confirm branch + recent commits match the expected feature.

---

## Subagent failure recovery (applies to any reviewer invocation below)

Per `agent-recovery.md`: if Sentinel, Probe, or Hone hits a rate limit, crashes, or times out mid-run:

1. Read whatever the failing reviewer managed to write before failing (chat output, any staged files via `git status`).
2. Determine which checks completed and which remain.
3. Complete remaining work inline (this skill has Read/Write/Edit/Bash) OR re-spawn the affected reviewer scoped to only the remaining work. The other two reviewers' outputs are unaffected — do not re-spawn them.
4. Do not re-run steps that already completed — build on partial progress.

---

## Per-cycle loop (one invocation of this skill = one cycle)

### Step 1 — Read plan + write failing tests

Read the plan file passed as `$ARGUMENTS` now (deferred from pre-flight so the anchor-to-remote-truth step above runs first against stale-prone `.dreamers/` content).

Read the plan's Acceptance Criteria and Test Cases (Given/When/Then). For each AC, write at least one test that would verify it. Cover the Given/When/Then scenarios as written.

- Tests live wherever the project's test convention specifies (consult `.github/copilot-instructions.md`).
- Stage with `git add`.
- Do not run yet — they should fail.

### Step 2 — Implement

Follow the **Implementation discipline** rules in `orchestrator-discipline.md`. Edit only files in the plan's scope. Stage with `git add` as you go.

### Step 3 — Type-check + run tests

1. Run the project's type-check command. Fix any errors before proceeding.
2. Run the project's test command (scoped to the new tests if the runner supports it; else full suite).

If tests fail:
- Diagnose. Fix inline (production code, not the tests — the tests express the spec).
- Re-run. Repeat up to 3 attempts.
- If still failing after 3 attempts, stop and surface to the user. Do not loosen the tests to make them pass.

### Step 4 — Coverage sweep (mandatory, unskippable checklist)

After tests are green, run the coverage sweep before invoking the reviewers. Work through item by item, do not collapse to "looks fine":

- [ ] **AC coverage matrix:** for every plan AC, name the test(s) that cover it. Any AC without a covering test → write one now.
- [ ] **Layer audit — Unit:** for each changed file, are there functions, branches, or error paths with no unit test?
- [ ] **Layer audit — Integration:** are there layer boundaries (repo↔DB, service↔API, function↔trigger) exercised by this change without an integration test?
- [ ] **Layer audit — UI / E2E:** are there user-facing flows, screen states, or navigation paths introduced or changed without a UI / E2E test? (If a navigation element changed: E2E coverage is required, not optional.)
- [ ] **Negative + edge cases:** for each piece of non-trivial logic, is there a test for invalid input, boundary values, empty/null/max, error states?
- [ ] **Regression risks:** anything in the change that touches existing behavior — is the most likely regression covered?
- [ ] **Final missed-AC check:** re-read the plan's Acceptance Criteria one last time and confirm every AC has a green test. Any AC without a covering test → write the test before signaling cycle complete. Hard gate.

Any gap → write the test now. Re-run the test command. Loop until all checklist items pass.

### Step 5 — Parallel review (Sentinel + Probe + Hone)

Spawn **three reviewers in parallel** in a single batched tool call (whatever the runtime surfaces for parallel agent spawning). All three are read-only / report-only; each returns structured findings in the format from `orchestrator-discipline.md`. None of them edits files.

Common prompt context for all three:
- Plan file path
- Scope: list of changed files from `git status`
- Branch + default branch names
- What the orchestrator has done: written failing tests, implemented, type-checked, ran tests (passing), completed coverage sweep.
- **Shared context (if applicable)** — when invoked from `/dreamers-full` in feature-manifest mode (Mode 3), the orchestrator passes the manifest's Shared constraints + Shared design decisions + Shared data models + End-to-end ACs. Include this verbatim in every reviewer's prompt under a "Feature context" header. Reviewers use this to evaluate the current plan in light of the full feature. Skip if no shared context was passed (Mode 2 variadic or standalone invocation).

Per-reviewer prompt addition:

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`):
- Lenses: correctness, security, maintainability
- Out of scope: test coverage (Probe's lane), simplicity (Hone's lane)
- Return: structured findings per the spec, plus plan-alignment summary

**Probe** (`agent_type: "probe"`, `mode: "sync"`):
- Lens: test coverage (AC matrix, layer audit, edge cases, gaps)
- Out of scope: correctness/security/maintainability (Sentinel's lane), simplicity (Hone's lane)
- Return: structured findings per the spec, plus plan AC coverage table

**Hone** (`agent_type: "hone"`, `mode: "sync"`):
- Lens: simplicity / over-engineering / redundancy / architectural quality
- Out of scope: correctness/security/maintainability (Sentinel's lane), test coverage (Probe's lane)
- Return: structured findings per the spec

### Step 6 — Apply findings inline (orchestrator-as-fixer)

Concatenate findings from all three reviewers per the orchestrator-as-fixer behavior in `orchestrator-discipline.md`:

1. **Sort by severity** (critical → high → medium → low).
2. **Resolve conflicts** per the conflict-resolution rule: correctness > simplicity. Genuine ambiguity → surface to user before applying.
3. **Apply each fix inline** as a targeted Edit. Stage with `git add` as you go.
4. **Re-run type-check + tests** after all fixes applied. If regressions appear, diagnose + re-fix inline (up to 3 attempts, then surface to user).

Handle non-finding outputs:
- Any reviewer returns **`Blocked — <reason>`** → halt cycle; surface; resolve; re-spawn the affected reviewer only.
- Any reviewer returns **open questions** → present each to the user before proceeding. Capture decisions; apply; if implementation changes meaningfully, re-run Steps 3 + 4 + 5 for the affected scope.
- All three return **`Approved — no findings`** → proceed to Step 7 directly. No fix application needed.

After fix application (or skip), proceed to Step 7.

### Step 7 — User testing (if required)

Check the plan's `User-testing-required` field.

- **`no`** → proceed directly to step 8.
- **`yes`** → pause the cycle by calling `request_information`. Do not commit until the user explicitly approves.

The `request_information` call MUST include every item below. Do not abbreviate — the user reads only what is in this prompt:

- **Plan being tested:** ID + path (e.g. `plan-{slug}` → `.dreamers/plans/plan-{slug}.md`).
- **Build / distribution details:** check for `.github/instructions/build.instructions.md` at the project root.
  - **If present:** follow it exactly. Execute only the steps it explicitly authorises the orchestrator to run. Surface every user-action step (install on device, launch app, open URL, version/build to verify) verbatim.
  - **If absent:** state plainly that there is no `build.instructions.md`. Ask the user to either (a) build/distribute the test build themselves and confirm when ready, or (b) provide the steps so a `build.instructions.md` can be created. Do not invent build steps.
- **What changed in this cycle:** 1–3 bullets summarising the user-visible behaviour delivered.
- **Step-by-step test steps:** numbered, concrete, reproducible. Derive directly from the plan's Acceptance Criteria and Test Cases (Given/When/Then). Each step states the action and the expected observation.
- **Known limitations / out-of-scope:** anything the user might try that this cycle deliberately doesn't cover.
- **How to respond:**
  - `Approved — continue` (skill proceeds to commit)
  - `Bug: <description>` (skill fixes inline, re-runs tests, re-distributes per `build.instructions.md` rules, re-calls `request_information` with refreshed test steps)
  - Freeform notes / corrections are also accepted and treated as bugs unless clearly approving.

**Resume rules:**
- On `Approved — continue` → proceed to step 8.
- On any bug or correction → **fix inline.** No Sentinel re-invocation: during user-testing rounds, the user IS the test layer. Steps: diagnose → fix in production code → re-run the test command to confirm no regression → re-build/distribute per `build.instructions.md` (or ask the user if no file) → re-call `request_information` with refreshed test steps that reproduce the original bug scenario plus any other steps still requiring user verification. Do NOT commit until explicit approval.

### Step 8 — Commit the cycle

Run `git status` to confirm staged content. Run `git commit` with a message following the project's commit-message style (see `.github/instructions/git.instructions.md` if present). Message body MUST include `Plan: plan-{slug}`.

One commit per cycle. Do not push.

---

## Exit behavior

When called **standalone**, exit on Step 8 commit. Tell the user:
- Commit hash + summary.
- AC coverage matrix.
- Reviewer status (Sentinel + Probe + Hone).
- Next step (their choice): more cycles (next plan in sequence, via another `/dreamers-implement` invocation or by running `/dreamers-full` with multiple plan paths), or `/dreamers-close-out` if all plans are shipped.

When called **from `/dreamers-full`**, exit on Step 8 commit. Return in chat output:
- Commit hash.
- AC coverage matrix.
- Reviewer chat output summary (Sentinel + Probe + Hone combined, for the orchestrator to concatenate across cycles into the Echo prompt).
- User-testing notes (if applicable).

The orchestrator reads this chat output, runs the inline drift check (if more plans remain in the sequence), and either loops to the next plan or proceeds to Phase 3.

## Push discipline

`git push` does NOT happen in this skill. Push happens exactly once at PR close-out via `/dreamers-pr`.
