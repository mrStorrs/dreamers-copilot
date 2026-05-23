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

Read these refs once at startup (use the `view` tool, full file):

- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, push discipline (orchestrator handles branch setup; sub-skills handle commits)
- `~/.copilot/dreamers/refs/close-out.md` — the close-out flow `/dreamers-close-out` runs

Sub-skills cite the discipline ref themselves. The orchestrator does not duplicate that read.

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, test commands.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

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

After Phase 1 (or its skip), proceed to Phase 2.

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

For each plan in the approved list (argument order from Mode 2, plan sequence from Mode 1 or Mode 3 manifest):

1. **Invoke `/dreamers-implement <path-to-plan>`.**
   - When a manifest is available (Mode 3, or Mode 1 where `/dreamers-plan` produced a manifest), ALSO pass the captured **shared context payload** from the manifest. The shared context is threaded into the per-cycle reviewer prompts (Sentinel + Probe + Hone) so they reason with full feature context, not just the single plan's contents. This is the hierarchical AI-context lever.
   - When no manifest exists (Mode 2 variadic, or Mode 1 where no manifest was produced), no shared context is passed — plans run in isolation.
2. Wait for it to complete (one commit lands on the branch).
3. **If more plans remain — inline drift check before the next plan.** Re-read the next plan and ask explicitly:
   - Does it still apply against the codebase as it now stands?
   - Did anything in the just-completed plan change file paths, function signatures, or data shapes the next plan references?
   - Are the next plan's Acceptance Criteria still measurable against the current code?
   - (Manifest modes) Does the manifest's shared context still hold given the just-completed cycle? If a shared constraint or end-to-end AC is now invalid, surface to user.
4. **If yes to all three (or four)** → loop to step 1 with the next plan.
5. **If any drift detected** → surface drift items to the user. Options:
   - User revises the next plan or the manifest inline (re-run quality self-check from `/dreamers-plan` Phase 1f mentally, then continue).
   - User skips the affected plan (proceed without it; the user accepts the consequences).
   - User halts the orchestrator entirely for manual recovery.

After the last plan's cycle completes, proceed to Phase 3.

### Single-plan mode

If only one plan path was provided (Mode 2 with one path, or Mode 1 producing one plan), the sequential loop runs exactly once. No drift check (no next plan). Proceed to Phase 3.

### Push discipline (no push in Phase 2)

Neither the orchestrator nor `/dreamers-implement` pushes during Phase 2. Each plan's cycle ends with a local commit. Push happens once in Phase 3 via `/dreamers-pr`.

---

## Phase 3 — Close-out (delegated)

Invoke `/dreamers-close-out` with the inputs captured from Phases 1 and 2:

- **Plan file paths** — full list of plans shipped this milestone.
- **Branch name** — current feature branch (`git branch --show-current`).
- **Default branch name** — `$DEFAULT` from Phase 2 first actions.
- **Sentinel summary string** — concatenated chat outputs from Sentinel + Probe + Hone across all cycles. Pull from the orchestrator's captured per-cycle summaries.
- **Issue reference** — if the originating user task referenced a GitHub issue number / URL, pass it.

`/dreamers-close-out` runs the 8-step close-out sequence (improvements append → docs via `/dreamers-docs` → retro → final commit → user approval gate → push + PR via `/dreamers-pr` → plan archive → post-PR discipline).

The user approval gate inside `/dreamers-close-out` (Step 5) is the LAST point where the user can halt before the PR goes live. The orchestrator does not bypass it.

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
- `/dreamers-implement` spawns Sentinel + Probe + Hone in parallel (per cycle).
- `/dreamers-close-out` → `/dreamers-docs` spawns Echo (once per milestone).

Per milestone: (3 × N) reviewer spawns + 1 Echo spawn, where N = number of plans in the sequence.

## Push discipline (single source of truth)

`git push` happens EXACTLY ONCE per milestone — inside `/dreamers-pr` (invoked by `/dreamers-close-out` Step 6). Never between cycles, never in Phase 2.
