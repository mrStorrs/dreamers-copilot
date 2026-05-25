---
name: dreamers-fix
description: 'Lightweight bug-fix pipeline. Cuts a fresh branch from origin/<default>, implements inline, runs project tests + Sentinel review in parallel, optionally invokes Echo for docs, pushes + opens PR. Self-contained — does NOT call /dreamers-plan, /dreamers-implement, or /dreamers-close-out. Escalates to /dreamers-full on scope blowup. Triggers: /dreamers-fix, fix this bug, bug fix, address the bug.'
argument-hint: '<bug description> [--issue <#|url>]'
---

## What this skill does

Lightweight, self-contained pipeline for bug fixes:

1. Cuts `fix/<slug>` from fresh `origin/<default>`.
2. Surveys the scope before any edit. If scope blows up (new module / schema change / cross-cutting refactor / new exported symbols), halts and surfaces an escalation choice — does NOT auto-route to `/dreamers-full`.
3. Writes a failing regression test (if test infra exists), then implements the fix inline.
4. Spawns Sentinel review + runs the project test command in a single parallel batch.
5. Applies Sentinel findings inline; re-runs tests (hard cap: 3 fix attempts).
6. AI-judgment Echo gate — spawns Echo subagent inline only if the change touches user-facing behavior, public API, config/setup, or test commands.
7. User approval gate before push.
8. Commits, then follows `pr-procedure.md` inline for push + PR creation (with `--issue` forwarded if provided).

**No plan file is written.** No retro, no improvements append, no plan archive, no Probe spawn, no Hone spawn. This skill is the entire pipeline for trivial-to-moderate bug fixes.

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + logging + test-writing + git rules
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, staging, push discipline
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage expectations + benchmark contract
- `~/.copilot/dreamers/refs/delegation.md` — Sentinel + Echo invocation protocol + subagent allowlist
- `~/.copilot/dreamers/refs/agent-recovery.md` — recovery if Sentinel crashes mid-run
- `~/.copilot/dreamers/refs/pr-procedure.md` — push + PR procedure (followed inline in Step 8)

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, **test commands** (binding).
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.
- `./test-benchmarks.md` (project root, if present) — recommended test timeouts per `testing-mandate.md`.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Argument parsing

Parse `$ARGUMENTS`:

- Bare text up to (but not including) any `--<flag>` token → **bug description** (required).
- `--issue <#|url>` → **issue reference**; forwarded verbatim into `pr-procedure.md` Step 4 at Step 8. Accepts a bare issue number or a full GitHub issue URL.
- If `$ARGUMENTS` is empty or contains only flags → halt: "Usage: /dreamers-fix <bug description> [--issue <#|url>]." Do not invent a description.

Derive **slug** from the bug description: lowercase, kebab-case, drop articles and trailing punctuation, truncate to ~5–7 meaningful words. Example: "navbar misaligned on mobile after rotation" → `navbar-misaligned-mobile-rotation`.

**Slug sanitization (mandatory).** After transformation, strip every character not matching `[a-z0-9-]`. The slug must contain no spaces, slashes (beyond the `fix/` prefix added at branch creation), backticks, dollar signs, semicolons, parentheses, or any other shell metacharacter. If the sanitized slug is empty (e.g., bug description was non-ASCII-only), halt with: "Bug description does not yield a usable slug; rephrase using ASCII keywords."

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Step 1 — branch setup
- [ ] Step 2 — scope survey + escalation check
- [ ] Step 3 — implement fix inline + regression test
- [ ] Step 4 — parallel Sentinel review + test run
- [ ] Step 5 — apply Sentinel findings + re-run tests
- [ ] Step 6 — Echo gate (docs if applicable)
- [ ] Step 7 — user approval gate
- [ ] Step 8 — commit + push + PR

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Branch setup (inline)

Per `git-workflow.md`:

1. **Dirty-tree check FIRST (before any git write command).** Run `git status --porcelain`. If output is non-empty, halt and surface: "Working tree has uncommitted changes on `<current branch>`; resolve before invoking `/dreamers-fix`." Do not stash or discard without user approval.
2. **Current-branch check.** Run `git branch --show-current`. If the current branch is neither the default branch nor empty (i.e., user is on an unrelated feature branch), surface a confirmation via `request_information`: "Current branch is `<name>` (not default). Continuing will check out the default branch and cut a new `fix/<slug>` branch from it. Confirm to proceed." Choices: `["Continue", "Halt", "Other"]`. On Halt → stop. On Other → freeform redirect, halt.
3. Detect default branch (canonical two-step):
   ```bash
   DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
4. **Anchor to remote truth:** `git fetch origin && git log origin/$DEFAULT --oneline -5`. Never build off a stale local default.
5. `git checkout $DEFAULT && git pull origin $DEFAULT`.
6. `git checkout -b fix/<slug>` — cut from the now-fresh default. Branch name MUST be passed quoted to git to defeat any residual metacharacter (slug is already sanitized per the Argument parsing section, but quoting is defense in depth).
7. Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edit.
8. `git log --oneline -3` and confirm branch + recent commits match expectation.

---

## Step 2 — Scope survey + escalation check (BEFORE any code edit)

Survey the codebase to locate the bug and identify the minimum set of files that need to change. Use Read / Glob / Grep — no Edit / Write yet.

**Escalation criteria (mandatory check — if ANY hold, HALT before any edit):**

- Needs a new module or new top-level directory.
- Requires a schema or data-model change (migration, table alter, persisted shape change).
- Requires a cross-cutting refactor across unrelated subsystems (multiple disjoint feature areas).
- Introduces new public exported symbols (functions / classes / types / API endpoints).

If any criterion hits, call `request_information`:

```
**Scope analysis — this exceeds bug-fix scope.**

Bug: <description>

Triggered criterion: <one-line citing which of the four it hit, and why>.
Survey notes: <one or two lines on what the survey found — affected files / proposed shape>.

Lightweight fix is not appropriate here. Recommended path: `/dreamers-full <bug description>` to run the full plan + implement + close-out flow.

Options:
- Continue lightweight anyway — proceed with the fix on this branch (you accept the absence of planning + multi-reviewer review)
- Restart on /dreamers-full — abandon this branch; re-invoke as /dreamers-full
- Other — freeform redirect
```

Choices: `["Continue lightweight anyway", "Restart on /dreamers-full", "Other"]`.

- **Continue lightweight anyway** → proceed to Step 3 with user-acknowledged risk; note the escalation skip in the final Step 7 summary.
- **Restart on /dreamers-full** → output: `Branch fix/<slug> is unused. Delete with: git checkout $DEFAULT && git branch -D fix/<slug>. Re-invoke as: /dreamers-full <bug description>.` Then stop. Do not auto-invoke `/dreamers-full` — user re-runs.
- **Other** → surface the freeform back to the user as a redirect; halt (no auto-resume, no auto-commit).

If NO escalation criterion holds, proceed directly to Step 3.

---

## Step 3 — Implement fix inline + regression test

**HARD STOP — implementation is inline.** The orchestrator (this skill, running in your context) edits files directly using Edit / Write / Bash tools. **Do NOT spawn any subagent to write code, write tests, or run tests for the fix.** Specifically:
- ❌ `agent_type: "general-purpose"` → FORBIDDEN. There is no general-purpose fallback for implementation.
- ❌ `agent_type: "claude"` or any other host-runtime agent → FORBIDDEN.
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `delegation.md`).
- ✅ The only `agent_type` values you may spawn from this skill are `sentinel` in Step 4 (parallel with the inline test run) and `echo` in Step 6 (only if the Echo gate fires). Nothing else.

If you reach the implementation step and find yourself thinking "let me delegate this to an agent," that's the bug. The orchestrator does the implementation. Write the regression test inline, edit the file inline, run the test command inline, stage with `git add`.

Follow the **Implementation discipline** rules from `orchestrator-discipline.md`.

1. **Regression test first** (if test infra exists per `.github/copilot-instructions.md`):
   - Write a failing test that captures the buggy behavior. The test should fail on the current (broken) code.
   - Stage with `git add`.
   - If no test infra is available for the affected surface (UI-only with no harness, etc.), skip and note the absence — this fact surfaces in Step 7's user approval block.

2. **Implement the fix** following discipline rules:
   - Only edit files in the bug's scope. No while-I'm-here cleanup, no unrelated refactors mixed in.
   - All `import` statements at the top of each file.
   - Method-signature changes: grep the full codebase for every call site before staging.
   - No spec-arguing comments in source.
   - No dependency installs without explicit user approval — if a new dependency is required, surface and ask first.
   - Stage with `git add` as work progresses.

3. **Type-check.** Run the project's type-check command (from `.github/copilot-instructions.md`). Fix any errors before Step 4. Do not proceed to review with type errors outstanding.

---

## Step 4 — Parallel Sentinel review + test run

Spawn the Sentinel review and run the test command **in a single batched tool call** — one Agent sub-tool-use + one Bash sub-tool-use, both fired concurrently. Wait for both to complete before Step 5.

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`):
- Lenses: correctness, security, maintainability.
- Out of scope: test coverage (no Probe in this pipeline; orchestrator covers it via the regression test in Step 3), simplicity (no Hone in this pipeline).
- Prompt context (per `delegation.md`):
  - **Context:** lightweight bug fix; bug description verbatim.
  - **Prior work:** files changed (output of `git status`), regression test path (or "skipped — no harness"), type-check result.
  - **What is needed:** structured findings per `orchestrator-discipline.md` format. Focus on whether the fix actually resolves the bug, side-effects, and security/maintainability impact.
  - **Constraints:** read-only; no Write/Edit; report only.
  - **Definition of Done:** structured findings block returned (status line + findings + optional observations/open questions).

**Test run** (Bash):
- Use the test command from `.github/copilot-instructions.md`. If `./test-benchmarks.md` has a row for that command, set the timeout per the file's `max(last_run_time × 2, 30s)` formula. After the run, update the benchmark row with the new duration.
- Scope to the new + nearby tests if the runner supports it; otherwise run the full suite.

**Subagent failure recovery (Sentinel):** per `agent-recovery.md`, if Sentinel crashes or times out, read whatever it managed to write, determine the gap, and either complete inline (orchestrator has Read access to the diff) or re-spawn Sentinel scoped to the remaining check.

---

## Step 5 — Apply Sentinel findings + re-run tests

Per the **Orchestrator-as-fixer** rules in `orchestrator-discipline.md`:

1. **If Sentinel returns `Approved — no findings`** AND tests passed in Step 4 → skip fix application; proceed to Step 6.
2. **If Sentinel returns `Findings reported — N items`:**
   - Sort findings by severity (critical → high → medium → low).
   - Apply each fix as a targeted Edit. Stage with `git add`.
   - Re-run the test command after all fixes applied. Update the benchmark row.
   - If tests regress after fix application → diagnose + re-fix inline. **Hard cap: 3 fix attempts total.** On the 3rd failure, halt and surface to the user — do not auto-loop.
3. **If Sentinel returns `Blocked — <reason>`** → halt the cycle; surface the block; resolve (user input if needed); re-spawn Sentinel scoped only to the affected area.
4. **If Sentinel surfaces open questions** → present each to the user before proceeding. Apply decisions; if the fix changes meaningfully, re-run tests once before moving on.

Tests must be green before Step 6. If they cannot be made green within 3 attempts, the skill stops at Step 5 and waits for user direction.

---

## Step 6 — Echo gate (judgment-based docs invocation)

Inspect `git diff --cached` (the staged change). Decide whether to spawn Echo as a subagent inline.

**Invoke Echo if ANY of these hold:**

- **User-facing behavior changed** — UI copy, layout, navigation, error messages the user sees, fixed user-visible flows.
- **Public API / interface contract changed** — exported function signatures, request / response shapes, CLI flags, public type definitions.
- **Setup / config / install steps changed** — `.env` keys, install commands, build commands, runtime environment requirements.
- **Test commands changed** — anything Bolt-style git agents or Probe rely on.
- **Significant new file or exported symbol** — rare in fix scope (usually caught by Step 2 escalation), but possible.

**Skip Echo if NONE hold** — cosmetic-only fixes, internal logic fixes with no surface change, error-log-string adjustments not user-visible, etc.

If invoking, spawn Echo via the `task` tool (`agent_type: "echo"`, `mode: "sync"`). Pass in the prompt (per `delegation.md`):
- Plan file paths: `none — bug fix, no plan file; use changed-files list as sole signal`.
- Changed files: output of `git diff --name-only origin/$DEFAULT...HEAD`.
- Diff base: `origin/$DEFAULT`.
- Sentinel summary string: the chat output from Step 4 (with severity counts).

Echo's prompt MUST include: "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `orchestration-flow.md` § "Single-owner todo").

Wait for Echo to signal completion. Capture Echo's doc-changes log + any open questions. Resolve open questions before proceeding.

Stage any new doc edits with `git add`.

If skipping, record the decision (one-line: "Echo skipped — <reason>") for the Step 7 summary.

---

## Step 7 — User approval gate (MANDATORY)

Before following `pr-procedure.md` inline, present this block:

```
**Bug fix ready to ship.**

Bug: <description>
Branch: fix/<slug>

Files changed (<N>):
- <file 1> — one-line summary
- <file 2> — one-line summary
- ...

Regression test: <path, or "skipped — no harness for this surface">
Test run: <pass/fail + duration; e.g. "pass in 18s">
Sentinel: <"Approved — no findings" | "Findings reported — N items applied (severity breakdown)">
Echo: <"invoked — N docs touched (paths)" | "skipped — <reason>">
Escalation note: <"none" | "user opted Continue lightweight anyway despite scope-blowup signal">

Issue reference: <number/URL, or "none">

Options:
- Approved — push + PR (proceed to Step 8)
- Halt for now (stop here; branch preserved on fix/<slug>; no push)
- Other (freeform corrections)
```

Call `request_information` with choices `["Approved — push + PR", "Halt for now", "Other"]`.

- **Approved — push + PR** → proceed to Step 8.
- **Halt for now** → output: `Stopping before push. Branch fix/<slug> is preserved with all current edits and commits. To continue, re-invoke /dreamers-fix with the same bug description — note that Step 1 will re-cut the branch from a fresh origin/<default>, so cherry-pick or merge work from the preserved branch onto the new one before continuing.` Stop.
- **Other** → treat as not-yet-approved. Apply corrections inline. If code touched, re-run tests. If logic changed materially, re-spawn Sentinel. Re-present this gate. Loop until approved.

This is the last point where the user can halt before the PR goes live.

---

## Step 8 — Commit, push, PR

1. **Stage any remaining working-tree changes.**
   - `git status` to inspect.
   - If the working tree shows unstaged changes (orphaned edits from inline work, Echo doc edits not yet staged, etc.), stage them explicitly with `git add <files>` — list each file, never `-A` blanket. This is the last chance before the commit; do NOT skip even if Steps 3 / 5 / 6 are believed to have staged everything.
   - After staging, re-run `git status` to confirm a clean working tree (only staged content remaining).

2. **Final commit (inline).**
   - `git commit` with message per `.github/instructions/git.instructions.md` (if present) or conventional-commits style. Subject: `fix: <one-line summary derived from bug description>`. Body MUST include `Bug: <description>` line so the fix is traceable without a plan file (downstream `pr-procedure.md` reads this).
   - Commit trailer (mandatory per `orchestrator-discipline.md` git rules): `Co-authored-by: The Dreamers System <noreply@dreamers.local>`.

3. **Follow `~/.copilot/dreamers/refs/pr-procedure.md` inline** (read the full ref via the `view` tool — must-read rule per `orchestration-flow.md`). Pass these inputs to the procedure:
   - Branch name: `fix/<slug>` (from `git branch --show-current`).
   - Default branch name: `$DEFAULT`.
   - Plan file paths: explicit `none — bug fix, no plan file` — this is a recognized sentinel value that `pr-procedure.md` Step 2 handles via its bug-fix Summary fallback (derived from the commit body's `Bug:` line + Sentinel summary instead of a plan title).
   - Retro file path: **omitted** (no retro in fix flow).
   - Sentinel summary string: the structured-findings output from Step 4 (with severity counts and the fixes applied).
   - Issue reference: forwarded from `$ARGUMENTS`'s `--issue` flag if provided; else omitted.
   - Final commit hash: from the commit just created.

The procedure runs inline (pre-push verification → Step 1 push → Step 2 draft body → Step 3 open PR → Step 4 issue close if applicable). Capture the PR URL it returns.

This skill does NOT invoke any other skill — the PR-creation procedure runs inline from `pr-procedure.md`.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (yes / no / n/a).
- Files changed (count + path list).
- Test result (pass + duration).
- Sentinel summary (one line: findings count + severity breakdown).
- Echo verdict (invoked + docs touched, or skipped + reason).
- Escalation note (if user opted Continue lightweight anyway).

Tell the user: post-PR discipline applies — no auto-commit of further changes (review comments, CI failures); ask first before any post-PR push. This skill does NOT run the `/dreamers-close-out` post-PR project-state scan; that scan lives in `/dreamers-close-out` for milestone flows. For a single fix, the user reviews the PR and merges manually.

---

## What this skill does NOT do

- Does NOT write a plan file. The bug description is the only input artifact; the commit body's `Bug:` line is the durable record.
- Does NOT invoke `/dreamers-plan`, `/dreamers-implement`, or `/dreamers-close-out`. It is a complete, self-contained pipeline.
- Does NOT spawn Probe or Hone. Sentinel is the only reviewer; the regression test (Step 3) covers what Probe would have spawned for.
- Does NOT auto-escalate to `/dreamers-full`. On scope blowup, Step 2 surfaces the choice and stops — user re-invokes the other skill themselves.
- Does NOT touch `.dreamers/improvements.md` or write a retro file. Lightweight by design.
- Does NOT push between steps — there is only one push, via `pr-procedure.md` Step 1 (invoked inline at Step 8).

---

## When this skill is NOT the right tool

- **A genuine new feature** masquerading as a "bug" → use `/dreamers-full <feature description>` directly.
- **Multi-plan refactor** → use `/dreamers-full` with variadic plan paths or manifest mode.
- **Doc-only typo fix** → just edit the doc and commit. Don't spin up a pipeline.
- **Question about existing behavior** (not a real bug) → answer in chat; no pipeline.
- **Bug that triggers Step 2 escalation criteria and the user chooses to plan it properly** → `/dreamers-full` is the right tool, not this one.
