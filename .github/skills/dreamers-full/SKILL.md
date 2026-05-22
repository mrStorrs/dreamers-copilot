---
name: dreamers-full
description: 'Full Dreamers TDD pipeline orchestrator. Delegates to `/dreamers-plan` (Phase 1), `/dreamers-implement` (Phase 2 per cycle), `/dreamers-close-out` (Phase 3). Owns branch setup, umbrella-vs-cohesive routing, and the per-sub-plan loop with inline drift check. Triggers: /dreamers-full, full pipeline, plan and implement, new feature, ship a feature.'
---

## What this skill does

A thin orchestrator that wires the three TDD-pipeline phases together. The orchestrator owns only cross-phase concerns: branch setup at Phase 2 entry, umbrella-vs-cohesive routing after Phase 1, the per-sub-plan loop with inline drift check between sub-plans (umbrella mode), and sequencing handoff from one sub-skill to the next.

Each phase delegates to a sub-skill that owns the actual work. The orchestrator does NOT embed implementation / test / docs / git rules — those live in the sub-skills, which cite `~/.copilot/dreamers/refs/tdd-orchestrator-discipline.md`.

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

## Phase 1 — Planning (delegated)

Invoke `/dreamers-plan` with the user's task description forwarded as the argument.

`/dreamers-plan` runs the three-phase requirements conversation (Hash-it-out → Approval → Decompose), writes plan files to `.dreamers/plans/`, and exits at the implementation-start approval gate (Phase 1g). It does NOT proceed to implementation.

From `/dreamers-plan`'s chat output, capture:
- **Plan shape decision** — cohesive or umbrella.
- **Plan file path(s)** — exact paths under `.dreamers/plans/`.
- **Approval status** — confirmed at Phase 1g.

If the user rejects at Phase 1c or 1g, `/dreamers-plan` loops until approved. The orchestrator does not bypass.

After `/dreamers-plan` exits successfully, proceed to Phase 2.

---

## Phase 2 — Implementation (orchestrated loop)

### MANDATORY first actions (once at Phase 2 entry, before any cycle)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note. (This is the orchestrator's responsibility — `/dreamers-implement` skips this when called from the orchestrator to avoid re-reading per sub-plan.)

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

### Per-cycle loop

The loop body is one invocation of `/dreamers-implement` per plan / sub-plan. The orchestrator does NOT run the per-cycle steps directly — `/dreamers-implement` owns the loop (failing tests → implement → run tests → coverage sweep → Sentinel review → optional user-test → commit).

**Cohesive mode (one cycle total):**
- Invoke `/dreamers-implement <path-to-plan>` once with the cohesive plan file path.
- Wait for it to complete (one commit lands on the branch).
- Proceed to Phase 3.

**Umbrella mode (one cycle per sub-plan):**
- For each sub-plan file in order (`plan-{slug}-a.md`, `plan-{slug}-b.md`, …):
  1. Invoke `/dreamers-implement <path-to-sub-plan>`.
  2. Wait for it to complete (one commit lands on the branch).
  3. **Inline drift check before next sub-plan.** Re-read the NEXT sub-plan file and ask explicitly:
     - Does it still apply against the codebase as it now stands?
     - Did anything in this just-completed sub-plan change file paths, function signatures, or data shapes the next sub-plan references?
     - Are the next sub-plan's Acceptance Criteria still measurable against the current code?
  4. **If yes to all three** → loop to step 1 with the next sub-plan.
  5. **If any drift detected** → surface drift items to the user. Either:
     - User revises the next sub-plan inline (then re-run Phase 1f quality check, then loop), OR
     - User halts the orchestrator for manual recovery.
- After the last sub-plan's cycle completes (and no remaining sub-plans), proceed to Phase 3.

### Push discipline (no push in Phase 2)

Neither the orchestrator nor `/dreamers-implement` pushes during Phase 2. Each sub-plan / cycle ends with a local commit. Push happens once in Phase 3 via `/dreamers-pr`.

---

## Phase 3 — Close-out (delegated)

Invoke `/dreamers-close-out` with the inputs captured from Phases 1 and 2:

- **Plan file paths** — list shipped this milestone (cohesive: 1 file; umbrella: umbrella + all sub-plans).
- **Branch name** — current feature branch (`git branch --show-current`).
- **Default branch name** — `$DEFAULT` from Phase 2 first actions.
- **Sentinel summary string** — concatenated chat outputs from Sentinel across all cycles. Pull from the orchestrator's captured per-cycle summaries.
- **Issue reference** — if the originating user task referenced a GitHub issue number / URL, pass it.

`/dreamers-close-out` runs the 8-step close-out sequence (improvements append → docs via `/dreamers-docs` → retro → final commit → user approval gate → push + PR via `/dreamers-pr` → plan archive → post-PR discipline).

The user approval gate inside `/dreamers-close-out` (Step 5) is the LAST point where the user can halt before the PR goes live. The orchestrator does not bypass it.

After `/dreamers-close-out` returns the PR URL, the milestone is complete.

---

## Exit behavior

Return in chat output:
- PR URL.
- Plan files shipped.
- Per-cycle commits (hashes + summaries) across all sub-plans.
- Final Sentinel summary (concatenated across cycles).
- Open improvements surfaced by `/dreamers-close-out`'s Step 8 post-PR scan.

No further work after Phase 3 completes. Post-PR changes (review comments, CI fixes) are user-driven — the orchestrator does not auto-commit per `close-out.md`.

---

## Failure handling

If any sub-skill returns a `Blocked` status or fails:
- Surface the block to the user with the sub-skill's chat output.
- Do not proceed to subsequent phases until the block is resolved.
- Common cases: `/dreamers-plan` Phase 1f quality check failure (plan revision needed); `/dreamers-implement` Sentinel `Blocked` (plan AC missing); `/dreamers-pr` push rejected (non-fast-forward).
- The orchestrator does not auto-retry; it relies on the sub-skill's own recovery path or user input.

If a subagent spawned by a sub-skill (Sentinel or Echo) crashes mid-run, the sub-skill handles recovery per `agent-recovery.md`. The orchestrator does not intervene unless the sub-skill itself fails.

---

## Subagent inventory (in this skill)

- **None directly.** The orchestrator does not spawn agents.
- `/dreamers-implement` spawns Sentinel (per cycle).
- `/dreamers-close-out` → `/dreamers-docs` spawns Echo (once per milestone).

Two agent spawns per milestone in cohesive mode; N+1 in umbrella mode where N = number of sub-plans (each sub-plan spawns Sentinel once, plus the single Echo at close-out).

## Push discipline (single source of truth)

`git push` happens EXACTLY ONCE per milestone — inside `/dreamers-pr` (invoked by `/dreamers-close-out` Step 6). Never between cycles, never in Phase 2.
