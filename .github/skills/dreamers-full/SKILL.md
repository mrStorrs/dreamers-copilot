---
name: dreamers-full
description: 'End-to-end Dreamers pipeline. Runs planning → implementation → close-out inline, following the canonical procedure refs. Does NOT invoke other skills as sub-routines. Owns a single todo for the entire run. Triggers: /dreamers-full, full pipeline, plan and implement, new feature, ship a feature.'
argument-hint: '<task description> | feature-<slug>/plan-NN-<name>.md [more plan paths] | feature-<slug>/manifest.md'
---

## What this skill does

This is the canonical end-to-end Dreamers pipeline. The orchestrator follows three procedure refs inline, in sequence:

1. **Planning** — `~/.copilot/dreamers/refs/planning-procedure.md` (Phase 1a–1g).
2. **Implementation** — `~/.copilot/dreamers/refs/implementation-procedure.md` (Steps 1–8, repeated per plan in multi-plan runs).
3. **Close-out** — `~/.copilot/dreamers/refs/close-out-procedure.md` (Steps 1–8, which itself reads `pr-procedure.md` at Step 6).

This skill does NOT invoke other skills (no `Invoke /dreamers-plan`, no `Invoke /dreamers-implement`, no `Invoke /dreamers-close-out`). Every phase runs inline in this skill's context. There is one todo, owned by this skill, covering the whole pipeline.

Subagents are spawned where the procedure refs call for them: Sentinel + Probe + Hone (parallel review in implementation-procedure Step 5), and Echo (docs in close-out-procedure Step 2). These are the ONLY subagent types this skill spawns — per `delegation.md` § "Subagent allowlist."

---

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + logging + test-writing + git rules
- `~/.copilot/dreamers/refs/delegation.md` — subagent allowlist + forbidden list + delegation protocol
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, staging, push discipline
- `~/.copilot/dreamers/refs/agent-recovery.md` — recovery if Sentinel/Probe/Hone/Echo crash mid-run
- `~/.copilot/dreamers/refs/feature-decomposition.md` — when to write multiple plans + manifest pattern
- `~/.copilot/dreamers/refs/plan-content.md` — plan section requirements + format
- `~/.copilot/dreamers/refs/plan-rules.md` — plan naming + directory layout
- `~/.copilot/dreamers/refs/planning-procedure.md` — Phase 1 procedure (will be followed in Phase 1)
- `~/.copilot/dreamers/refs/implementation-procedure.md` — Phase 2 procedure (will be followed per plan in Phase 2)
- `~/.copilot/dreamers/refs/close-out-procedure.md` — Phase 3 procedure (will be followed in Phase 3)
- `~/.copilot/dreamers/refs/pr-procedure.md` — PR-creation procedure (read by close-out Step 6)
- `~/.copilot/dreamers/refs/citation-accuracy.md` — verify before citing existing artifacts (used in planning)
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations
- `~/.copilot/dreamers/refs/comment-rules.md` — comment discipline

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, test commands.
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.
- `./test-benchmarks.md` (root, if present) — test run-time benchmarks for timeout selection.

$ARGUMENTS

---

## Invocation modes

**Mode 1 — no plan(s) yet:** `/dreamers-full <task description>` — orchestrator runs the planning procedure first, producing one or more plan files (and optionally a manifest), then proceeds to implementation.

**Mode 2 — plans already exist (variadic):** `/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md ...` — orchestrator skips planning and runs implementation directly for each plan in argument order. One plan path = single-plan mode; multiple paths = sequential multi-plan mode. No shared-context manifest in this mode. All plan paths must follow the per-feature directory layout from `plan-rules.md`.

**Mode 3 — feature manifest:** `/dreamers-full feature-<slug>/manifest.md` — orchestrator reads the manifest, extracts the plan sequence from its "Plan sequence" table, and runs implementation in that order. The manifest's shared constraints / design decisions / data models / end-to-end ACs are loaded as **shared context** and threaded into each cycle's reviewer prompts.

**Argument disambiguation:** the orchestrator checks the first argument:
- First argument basename is exactly `manifest.md` → Mode 3.
- First argument ends in `.md`, basename matches `plan-NN-*.md`, lives inside a `feature-<slug>/` directory → Mode 2.
- Otherwise → Mode 1 (task description).

**Legacy flat-format compatibility:** old-format plans (`.dreamers/plans/plan-<slug>.md` without a feature directory) and old-format manifests (`feature-<slug>.md` at the plans/ root) are NOT supported. Plans must follow the per-feature directory layout from `plan-rules.md`.

---

## Todo list (declared upfront — single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Phase 1 — planning (follow planning-procedure.md)
- [ ] Phase 1.5 — ship-strategy gate (multi-plan only; skipped if single-plan)
- [ ] Phase 2 cycle 1 — implement plan 1 (follow implementation-procedure.md)
- [ ] Phase 3 — close-out (follow close-out-procedure.md; includes push + PR via pr-procedure.md)

For Modes 2 and 3, declare all Phase 2 cycle items upfront based on the known plan count. For Mode 1, declare the initial items above and add Phase 2 cycle items after planning produces the plan list.

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**This skill is the sole owner of the todo.** Subagents spawned during the run (Sentinel / Probe / Hone / Echo) MUST NOT touch `manage_todo_list` — their prompts explicitly forbid it. See `orchestration-flow.md` § "Single-owner todo rule."

---

## Phase 1 — Planning (follow planning-procedure.md inline)

**Skipped in Modes 2 and 3** (plans already exist).

In Mode 1:
1. Mark "Phase 1 — planning" in_progress.
2. Read `planning-procedure.md` in full (already done in pre-flight, but re-confirm the file is loaded).
3. Follow the procedure from Phase 1a (Hash it out) through Phase 1g (Implementation start approval gate). The procedure includes its own approval gates (Phase 1c, Phase 1g). On Phase 1g's `Approved — start implementation` answer, proceed directly to Phase 1.5 / Phase 2 — do NOT issue an additional continuation prompt (per `orchestration-flow.md` § "Pause-point list," the post-Phase-1g prompt is retired).
4. Mark "Phase 1 — planning" completed.

On Phase 1g `Halt — planning only`: stop the whole pipeline cleanly. Surface the saved plan paths to the user. Do not proceed to Phase 1.5 or Phase 2.

On Phase 1c / Phase 1g `Other` (corrections): the planning procedure handles the loop internally.

In Modes 2 and 3: skip Phase 1 entirely. Mark its todo item completed at startup ("skipped — plans pre-existing"). Capture plan paths from `$ARGUMENTS` (Mode 2) or from the manifest's Plan sequence table (Mode 3).

For Mode 3, capture the manifest content (Shared constraints, Shared design decisions, Shared data models, End-to-end ACs) as the **shared context payload** for use in Phase 2 reviewer prompts.

---

## Phase 1.5 — Ship strategy gate (multi-plan only)

**Skipped if only one plan is in the sequence.** Single-plan = one cycle = one PR regardless of strategy.

For 2+ plans, the orchestrator decides ship strategy: **Incremental** (PR per plan) or **Atomic** (one PR at end).

### Recommend a strategy

Read the manifest (if any) and the plan files. Score against the heuristics from `feature-decomposition.md` § "Recommendation heuristics." Pick the strongest signal and form a one-sentence cited reason.

### Present the gate

```
**Phase 1.5 — Ship strategy**

Plans in sequence:
- .dreamers/plans/feature-<slug>/plan-01-<name>.md — [one-line summary]
- .dreamers/plans/feature-<slug>/plan-02-<name>.md — [one-line summary]
- .dreamers/plans/feature-<slug>/plan-03-<name>.md — [one-line summary]

Manifest: [.dreamers/plans/feature-<slug>/manifest.md path, or "none"]

**Recommended strategy:** [INCREMENTAL | ATOMIC]
**Reasoning:** [one sentence citing the strongest heuristic signal]

How do you want to ship?
- INCREMENTAL — PR per plan; main advances incrementally.
- ATOMIC — one PR at end; all plans ship together.
- Halt for now — stop here; I will resume later.
```

Call `request_information` with choices `["Incremental", "Atomic", "Halt for now", "Other"]`. On `Halt for now`: stop with the resume command. Capture the user's choice as the **strategy** value for Phase 2.

Mark "Phase 1.5 — ship-strategy gate" completed.

---

## Phase 2 — Implementation (sequential per plan, following implementation-procedure.md inline)

### MANDATORY first actions (once at Phase 2 entry, before any cycle)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note.

2. **Branch setup (inline, per `git-workflow.md`):**
   - Detect default branch (canonical two-step):
     ```bash
     DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
     ```
   - **Anchor to remote truth (mandatory before reading any `.dreamers/` files):** `git fetch origin && git log origin/$DEFAULT --oneline -5`.
   - `git checkout $DEFAULT && git pull origin $DEFAULT` — never build off a stale local default branch.
   - Cut `feat/<slug>` from `$DEFAULT`.
   - Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edits.

3. **Branch identity check** — `git log --oneline -3`. Confirm branch + recent commits match the expected feature.

### Sequential plan loop

For each plan in the approved list (argument order from Mode 2, plan sequence from Mode 1 or Mode 3 manifest):

1. **Mark "Phase 2 cycle N — implement plan N" in_progress.**

2. **Read `implementation-procedure.md` in full** (already loaded in pre-flight; confirm).

3. **Follow `implementation-procedure.md` Steps 1–8 inline** with this plan's path as the input. When manifest-mode is in effect (Mode 3 OR Mode 1 where planning produced a manifest), pass the captured **shared context payload** into Step 5's reviewer prompts under a "Feature context" header — this is the hierarchical-AI-context lever.

4. **Mark "Phase 2 cycle N" completed** once the cycle's commit lands (Step 8).

5. **If strategy is INCREMENTAL AND more plans remain:**
   - Read `close-out-procedure.md` in full (already loaded).
   - Follow `close-out-procedure.md` in LIGHT mode (Steps 2 + 4 + 5 + 6 only) for THIS plan: docs if applicable + final commit + user gate + push + PR.
   - After Step 6's PR URL is returned, call `request_information`:
     ```
     Plan {n} of {N} shipped as PR {url}.
     Next: wait for that PR to merge, then re-cut the feature branch and start the implementation cycle for plan {n+1} ({next-path}).

     Options:
     - label: Continue — wait for merge then start next cycle
     - label: Halt for now — stop here; I will resume manually
     - label: Other — freeform redirect
     ```
   - On `Halt for now`: stop with resume command.
   - On `Continue`: wait for explicit user confirmation that PR has merged (do NOT poll). Then switch to default branch + pull + re-cut feature branch for the next plan.

6. **If strategy is INCREMENTAL AND this is the LAST plan:**
   - Skip the light close-out. Fall through to Phase 3 (full close-out) — the final plan's commit is the last thing on the current branch and gets the milestone retro + improvements + PR.

7. **If strategy is ATOMIC:** do NOT push, do NOT close out per plan. The commit stays on the current branch. If more plans remain, proceed to drift check.

8. **Drift check (if more plans remain, ATOMIC strategy or pre-merge in INCREMENTAL):**
   - Run inline drift check against the next plan path: read the next plan, verify cited file paths still exist, signatures still match, etc. (Per `feature-decomposition.md`-style verification.)
   - If drift: surface specific drift items to the user; user may revise the next plan, skip it, or halt.
   - If no drift: call `request_information` with `["Continue", "Halt for now", "Other"]`. On Continue, loop to step 1 with the next plan.

### Push discipline

- **ATOMIC strategy:** no push during Phase 2. Single push at Phase 3 covering all plans.
- **INCREMENTAL strategy:** ONE push per plan during Phase 2 (via close-out's LIGHT mode at each plan). The FINAL plan's push happens at Phase 3 (full close-out).

---

## Phase 3 — Close-out (follow close-out-procedure.md inline)

1. Mark "Phase 3 — close-out" in_progress.
2. Read `close-out-procedure.md` in full (already loaded; confirm).
3. Follow the procedure in FULL mode (Steps 1–8) with these inputs:
   - **Plan file paths** — full list shipped this milestone.
   - **Branch name** — current feature branch.
   - **Default branch name** — `$DEFAULT`.
   - **Sentinel summary string** — concatenated chat outputs from Sentinel + Probe + Hone across all Phase 2 cycles.
   - **Issue reference** — if the originating user task referenced a GitHub issue number / URL.
4. At Step 6, the close-out procedure directs you to read `pr-procedure.md` in full and follow it inline. Capture the PR URL.
5. At Step 8 (post-PR discipline), surface the project-state scan findings to the user — do not auto-apply.
6. Mark "Phase 3 — close-out" completed once the PR URL is captured and post-PR scan is done.

---

## Exit behavior

Return in chat output:
- PR URL.
- Plan files shipped (in order).
- Per-plan commits (hashes + summaries).
- Final reviewer summary (concatenated across cycles).
- Open improvements surfaced by close-out Step 8 post-PR scan.

No further work after Phase 3 completes. Post-PR changes (review comments, CI fixes) are user-driven — the pipeline does not auto-commit per `close-out-procedure.md` Step 8.

---

## Failure handling

If a subagent returns a `Blocked` status or fails: surface the block to the user with the subagent's chat output. Do not proceed to subsequent phases until the block is resolved.

Common failure cases:
- Planning Phase 1f quality check failure (plan revision needed).
- Implementation Step 5 reviewer `Blocked` (plan AC missing or ambiguous).
- pr-procedure Step 1 push rejected (non-fast-forward).

The pipeline does not auto-retry; it relies on the procedure refs' own recovery paths or user input.

If a subagent (Sentinel / Probe / Hone / Echo) crashes mid-run, follow `agent-recovery.md`. The orchestrator does not intervene unless recovery itself fails.

---

## Subagent inventory (in this skill)

**Subagent allowlist (hard rule from `delegation.md`):** the only `agent_type` values that appear anywhere in this skill's pipeline are:

- `sentinel`, `probe`, `hone` — parallel review in implementation-procedure Step 5 (3 spawns per cycle = 3 × N for N plans)
- `echo` — docs in close-out-procedure Step 2 (1–N spawns depending on strategy: ATOMIC = 1 final; INCREMENTAL = up to N per-plan plus final)

**NEVER** `general-purpose`, `claude`, `forge`, `nova`, `bolt`, or any other agent_type. Implementation, git ops, file edits, test runs, and PR creation are done INLINE by the orchestrator (this skill, running in your context) using its own Edit / Write / Bash tools. If you find yourself about to invoke a non-allowlist agent for any reason, STOP and re-read `delegation.md` § "Subagent allowlist."

**Subagent prompt rule (every spawn):** include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in each subagent's prompt. Per `orchestration-flow.md` § "Single-owner todo."

---

## What this skill does NOT do

- Does NOT invoke `/dreamers-plan`, `/dreamers-implement`, `/dreamers-close-out`, `/dreamers-docs`, or `/dreamers-pr` as sub-skills. Every phase runs inline by following the procedure refs.
- Does NOT manage multiple todo lists. ONE todo, owned by this skill.
- Does NOT spawn agents outside the 5-item allowlist.
- Does NOT auto-push between cycles in ATOMIC mode. Single push at PR creation only.
