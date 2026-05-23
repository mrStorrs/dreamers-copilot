---
name: dreamers-full
description: 'Full Dreamers pipeline orchestrator. Delegates to `/dreamers-plan` (Phase 1), `/dreamers-implement` (Phase 2, one cycle per plan), `/dreamers-close-out` (Phase 3). Accepts variadic plan paths OR a feature-manifest path to run multiple plans in sequence on one branch + one PR. Triggers: /dreamers-full, full pipeline, plan and implement, new feature, ship a feature.'
argument-hint: '<task description> | <plan-path> [more plan paths] | <feature-{slug}.md>'
---

## What this skill does

A thin orchestrator that wires the three pipeline phases together. Owns cross-phase concerns: branch setup, sequential plan loop, inline drift check between plans, sequencing handoff to sub-skills, and (in manifest mode) threading shared context into reviewer prompts.

Each phase delegates to a sub-skill that owns the actual work. The orchestrator does NOT embed implementation / test / docs / git rules — those live in the sub-skills, which cite `~/.copilot/dreamers/refs/orchestrator-discipline.md`.

## Invocation modes

**Mode 1 — no plan(s) yet:** `/dreamers-full <task description>` — orchestrator runs `/dreamers-plan` first; the planning conversation produces one or more plan files (and optionally a feature manifest); user approves; orchestrator then runs Phase 2.

**Mode 2 — plans already exist (variadic):** `/dreamers-full path/to/plan-a.md path/to/plan-b.md path/to/plan-c.md` — orchestrator skips Phase 1 planning and runs Phase 2 directly for each plan in argument order. One plan path = single-plan mode; multiple paths = sequential multi-plan mode. No shared-context manifest in this mode.

**Mode 3 — feature manifest:** `/dreamers-full path/to/feature-{slug}.md` — orchestrator reads the manifest, extracts the plan sequence from its "Plan sequence" table, and runs cycles in that order. The manifest's shared constraints / design decisions / data models / end-to-end ACs / cross-plan risks are loaded as **shared context** and threaded into each cycle's reviewer prompts. This is the hierarchical-AI-context mode, used when cross-plan context warrants it.

**Argument disambiguation:** the orchestrator checks the first argument:
- First argument filename matches `feature-*.md` → Mode 3 (manifest).
- First argument ends in `.md` but does NOT match `feature-*.md` → Mode 2 (variadic plan paths; remaining args are additional plan paths if provided).
- Otherwise → Mode 1 (task description).

## Pre-flight reads

Read these refs once at startup:

- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, push discipline (orchestrator handles branch setup; sub-skills handle commits)
- `~/.copilot/dreamers/refs/close-out.md` — the close-out flow `/dreamers-close-out` runs
- `~/.copilot/dreamers/refs/orchestration-flow.md` — continuation principle, todo-list protocol, tool-name pseudonyms

Sub-skills cite the discipline ref themselves. The orchestrator does not duplicate that read.

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, test commands.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1 — planning (`/dreamers-plan`)
- [ ] Phase 1.5 — ship strategy gate
- [ ] Phase 2 cycle 1 — implement plan 1 (`/dreamers-implement`)
- [ ] Phase 3 — close-out (`/dreamers-close-out`)

**Declaration point:** declare initial items at skill entry. In Mode 1, Phase 2 cycle items are added after Phase 1g produces the plan list. In Modes 2 and 3, all Phase 2 cycle items are declared upfront.

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

Directly composed sub-skills (`/dreamers-plan`, `/dreamers-implement`, `/dreamers-close-out`) MUST NOT declare their own todo lists when invoked by this orchestrator. They update this orchestrator's matching items instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`. Indirect children invoked by `/dreamers-close-out` (e.g. `/dreamers-docs`, `/dreamers-pr`) follow the same rule transitively — they update `/dreamers-close-out`'s items, which roll up to this orchestrator's Phase 3 item.

---

## Phase 1 — Planning (delegated; skipped in Modes 2 and 3)

If `$ARGUMENTS` contains a task description (Mode 1):

Invoke `/dreamers-plan` with the user's task description forwarded as the argument.

`/dreamers-plan` runs the three-phase requirements conversation (Hash-it-out → Approval → Decompose), writes one or more plan files to `.dreamers/plans/` (and optionally a `feature-{slug}.md` manifest if cross-plan context warrants), and exits at the implementation-start approval gate (Phase 1g). It does NOT proceed to implementation.

From `/dreamers-plan`'s chat output, capture:
- **Plan count + sequence order** — one plan or multiple.
- **Plan file path(s)** — exact paths under `.dreamers/plans/`.
- **Manifest path** — if a `feature-{slug}.md` was produced, capture its path.
- **Approval status** — confirmed at Phase 1g.

If the user rejects at Phase 1c or 1g, `/dreamers-plan` loops until approved. The orchestrator does not bypass.

If `$ARGUMENTS` contains plan paths directly (Mode 2): skip Phase 1; treat the paths as the approved plan list in the order given.

If `$ARGUMENTS` contains a manifest path (Mode 3): skip Phase 1; read the manifest's "Plan sequence" table to extract the ordered plan list. Capture the manifest content (shared constraints, design decisions, data models, end-to-end ACs, cross-plan risks) as the **shared context payload** for later use in Phase 2.

After Phase 1 (or its skip), proceed to Phase 1.5.

**Continuation prompt — post Phase 1g (Mode 1 only):**

After `/dreamers-plan` exits at Phase 1g approval (Mode 1), before entering Phase 1.5 or Phase 2, call `request_information`:

```
Phase 1 complete. Plan(s) approved and written.

Proceeding will enter Phase 1.5 (ship strategy gate, if multi-plan) then Phase 2 (implementation).

Options:
- label: Continue — proceed to Phase 1.5 / Phase 2
- label: Halt for now — stop here; I will resume later
- label: Other — freeform redirect
```

On `Halt for now`: output "Resume by re-invoking `/dreamers-full` with the approved plan paths: <paths>" and stop. Do not proceed.

Modes 2 and 3 skip Phase 1 entirely; no continuation prompt fires here for those modes.

---

## Phase 1.5 — Ship strategy gate (multi-plan only)

**If only one plan is in the sequence: skip Phase 1.5 entirely.** Single-plan = one cycle = one PR no matter the strategy.

**If two or more plans are in the sequence**, the orchestrator decides ship strategy:

- **Incremental** — each plan's cycle ends with a light close-out (docs if applicable + push + PR for that plan). Plans land on `main` incrementally; subsequent plans branch off the updated main as they go. Milestone-level retro + improvements append happens at the end of the LAST plan only.
- **Atomic** — current behavior. Plans land as commits on one branch; ONE full close-out at the end with retro + improvements + PR covering all plans.

### Recommend a strategy

Read the manifest (if any) and the plan files. Score against the heuristics below. Pick the strongest signal and form a one-sentence cited reason.

**Recommend INCREMENTAL when any hold:**
- ≥ 4 plans in the sequence (review burden of one big PR is high).
- Plans touch significantly different file subsystems (low overlap in plan §Scope file lists).
- Manifest's cross-plan Risks section does NOT mention "ordering dependency," "breaking change," or "coordinated revert."
- Plans are estimated as substantial (≥ 5 ACs each, or test cases spanning multiple layers).
- Plan A's value is observable to users without plans B+ (incremental value delivery).

**Recommend ATOMIC when any hold:**
- 2–3 plans only (small feature).
- Plans touch overlapping files (same files edited by multiple plans).
- Manifest's cross-plan Risks mentions "ordering dependency," "breaking change requiring shim," or "coordinated revert."
- DB migrations or schema changes gated on prior plans.
- End-to-end ACs require ALL plans to verify (no piecewise testability).
- Feature-flag protected work where partial deployment leaves the system in a half-state.

If signals point both ways, default to ATOMIC (safer) and cite the conflicting signals in the reasoning.

### Present the gate

```
**Phase 1.5 — Ship strategy**

Plans in sequence:
- path/to/plan-a.md — [one-line summary]
- path/to/plan-b.md — [one-line summary]
- path/to/plan-c.md — [one-line summary]

Manifest: [feature-{slug}.md path, or "none"]

**Recommended strategy:** [INCREMENTAL | ATOMIC]
**Reasoning:** [one sentence citing the strongest heuristic signal]

How do you want to ship?
- INCREMENTAL — PR per plan; main advances incrementally.
- ATOMIC — one PR at end; all plans ship together.
- Halt for now — stop here; I will resume later.
```

Call `request_information` with choices `["Incremental", "Atomic", "Halt for now", "Other"]`. Freeform corrections are allowed (e.g., "Atomic for plans A and B together; incremental for C"). On `Halt for now`: output "Resume by re-invoking `/dreamers-full` with the approved plan paths: <paths>" and stop.

Capture the user's choice as the **strategy** value for Phase 2.

---

## Phase 2 — Implementation (orchestrated sequential loop)

### MANDATORY first actions (once at Phase 2 entry, before any cycle)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note. (This is the orchestrator's responsibility — `/dreamers-implement` skips this when called from the orchestrator to avoid re-reading per plan.)

2. **Branch setup (inline, per `git-workflow.md`):**
   - Detect default branch (canonical two-step):
     ```bash
     DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
     ```
   - **Anchor to remote truth (mandatory before reading any `.dreamers/` files):** `git fetch origin && git log origin/$DEFAULT --oneline -5`. Workspace files in `.dreamers/` are local-only and may be stale; `origin/$DEFAULT` is the authoritative record of what is actually shipped.
   - `git checkout $DEFAULT && git pull origin $DEFAULT` — never build off a stale local default branch.
   - Cut `feat/d<N>-<name>` from `$DEFAULT`.
   - Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edits.

3. **Branch identity check** — `git log --oneline -3`. Confirm branch + recent commits match the expected feature.

### Sequential plan loop

The loop branches on the **strategy** captured in Phase 1.5 (single-plan invocations: strategy is irrelevant; loop runs once and proceeds to Phase 3).

For each plan in the approved list (argument order from Mode 2, plan sequence from Mode 1 or Mode 3 manifest):

1. **Invoke `/dreamers-implement <path-to-plan>`.**
   - When a manifest is available (Mode 3, or Mode 1 where `/dreamers-plan` produced a manifest), ALSO pass the captured **shared context payload** from the manifest. The shared context is threaded into the per-cycle reviewer prompts (Sentinel + Probe + Hone) so they reason with full feature context, not just the single plan's contents. This is the hierarchical AI-context lever.
   - When no manifest exists (Mode 2 variadic, or Mode 1 where no manifest was produced), no shared context is passed — plans run in isolation.
2. Wait for `/dreamers-implement` to complete (one commit lands on the branch).
3. **If strategy is INCREMENTAL** AND more plans remain:
   - Invoke `/dreamers-close-out --light <plan-path>` for the just-completed plan. The light close-out: docs update (if applicable) + push + PR for THIS plan only. NO retro, NO improvements append (those run at the final plan only).
   - After `/dreamers-close-out --light` returns the PR URL, call `request_information`:

     ```
     Plan {n} of {N} shipped as PR {url}.

     Next: wait for that PR to merge, then re-cut the feature branch and start the implementation cycle for plan {n+1} ({next-path}).

     Options:
     - label: Continue — wait for merge then start next cycle
     - label: Halt for now — stop here; I will resume manually
     - label: Other — freeform redirect
     ```

     On `Halt for now`: output "Resume by re-invoking `/dreamers-full` with the remaining plan paths: <paths>" and stop.
     On `Continue`: proceed to wait for merge (below).
   - **Wait for merge — explicit confirmation, not polling.** Ask the user: "Confirm PR <url> has merged before I start the next plan." When they confirm, run `git fetch origin && git log origin/$DEFAULT --oneline -5` to verify the squash commit is on the default branch. If the commit isn't visible, surface and ask again. (Do NOT poll in a loop; do NOT proceed without confirmation.)
   - After confirmed merge: switch to default branch + pull + re-cut feature branch for the next plan (light close-out's PR squashed main; need fresh branch for next plan).
4. **If strategy is INCREMENTAL** AND this is the LAST plan in the sequence:
   - Skip the light close-out. Fall through to Phase 3 (full close-out) — the final plan's commit is the last thing on the current branch and gets the milestone retro + improvements + PR.
5. **If strategy is ATOMIC**: do NOT push, do NOT close out per plan. The commit stays on the current branch. Proceed to drift check if more plans remain.
6. **If more plans remain — drift check before the next plan.** Invoke `/dreamers-plan-verify <next-plan-path>`. The skill returns `No change — proceed` or `Drift detected — halt` with specific drift items.
   - (Manifest modes only) Additionally check whether the manifest's shared context still holds given the just-completed cycle. If a shared constraint or end-to-end AC is now invalid, surface to user.
7. **If yes to all three (or four)** → call `request_information` (ATOMIC mode only, when more plans remain):

   **Precondition: if drift was detected in the prior step, skip this continuation prompt — surface drift items to the user per step 8 instead.**

   ```
   Plan {n} of {N} complete ({path}). Drift check passed.

   Next: start implementation cycle for plan {n+1} ({next-path}).

   Options:
   - label: Continue — start next cycle
   - label: Halt for now — stop here; I will resume later
   - label: Other — freeform redirect
   ```

   On `Halt for now`: output "Resume by re-invoking `/dreamers-full` with the remaining plan paths: <remaining paths>" and stop.
   On `Continue`: loop to step 1 with the next plan.
8. **If any drift detected** → surface drift items to the user. Options:
   - User revises the next plan or the manifest inline (re-run quality self-check from `/dreamers-plan` Phase 1f mentally, then continue).
   - User skips the affected plan (proceed without it; the user accepts the consequences).
   - User halts the orchestrator entirely for manual recovery.

After the last plan's cycle completes, proceed to Phase 3.

### Push discipline

- **ATOMIC strategy:** no push during Phase 2. Single push at Phase 3 via `/dreamers-pr` covering all plans.
- **INCREMENTAL strategy:** ONE push per plan via `/dreamers-close-out --light` (which invokes `/dreamers-pr` under the hood). The FINAL plan's push happens at Phase 3 (full close-out).

Net push count = ATOMIC: 1 per milestone | INCREMENTAL: N per milestone (one per plan).

---

## Phase 3 — Close-out (delegated)

Invoke `/dreamers-close-out` with the inputs captured from Phases 1 and 2:

- **Plan file paths** — full list of plans shipped this milestone.
- **Branch name** — current feature branch (`git branch --show-current`).
- **Default branch name** — `$DEFAULT` from Phase 2 first actions.
- **Sentinel summary string** — concatenated chat outputs from Sentinel + Probe + Hone across all cycles. Pull from the orchestrator's captured per-cycle summaries.
- **Issue reference** — if the originating user task referenced a GitHub issue number / URL, pass it.

`/dreamers-close-out` runs the 8-step close-out sequence (improvements append → docs via `/dreamers-docs` → retro → final commit → user approval gate → push + PR via `/dreamers-pr` → plan archive → post-PR discipline).

The user approval gate inside `/dreamers-close-out` is the LAST point where the user can halt before the PR goes live. The orchestrator does not bypass it.

After `/dreamers-close-out` returns the PR URL, the milestone is complete.

---

## Exit behavior

Return in chat output:
- PR URL.
- Plan files shipped (in order).
- Per-plan commits (hashes + summaries).
- Final reviewer summary (concatenated across cycles).
- Open improvements surfaced by `/dreamers-close-out`'s Step 8 post-PR scan.

No further work after Phase 3 completes. Post-PR changes (review comments, CI fixes) are user-driven — the orchestrator does not auto-commit per `close-out.md`.

---

## Failure handling

If any sub-skill returns a `Blocked` status or fails:
- Surface the block to the user with the sub-skill's chat output.
- Do not proceed to subsequent phases until the block is resolved.
- Common cases: `/dreamers-plan` Phase 1f quality check failure (plan revision needed); `/dreamers-implement` reviewer `Blocked` (plan AC missing); `/dreamers-pr` push rejected (non-fast-forward).
- The orchestrator does not auto-retry; it relies on the sub-skill's own recovery path or user input.

If a subagent spawned by a sub-skill (Sentinel / Probe / Hone / Echo) crashes mid-run, the sub-skill handles recovery per `agent-recovery.md`. The orchestrator does not intervene unless the sub-skill itself fails.

---

## Subagent inventory (in this skill)

- **None directly.** The orchestrator does not spawn agents.
- `/dreamers-implement` spawns Sentinel + Probe + Hone in parallel (per cycle): `3 × N` reviewer spawns where N = plans in the sequence.
- Echo (docs) spawns vary by strategy: ATOMIC = 1 (final close-out only); INCREMENTAL = up to N (each light close-out plus the final full close-out, when docs are applicable).
