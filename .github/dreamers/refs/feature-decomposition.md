# When to write multiple plans (mandatory)

Default to one plan inside a feature directory. Split into multiple plans only when one plan's scope is genuinely too large to land cleanly in a single cycle.

## What counts as "too large"

- More than ~300 lines of new/changed code across all touched files.
- Touches more than one data-layer change PLUS more than one UI surface in the same cycle.
- Crosses natural seams (model → repository → viewmodel → screen → cloud function) in ways that make one cycle's review hard to scope.

## Splitting rules

When you do split into multiple plans, each plan MUST satisfy:

- **Independently shippable.** Each plan can be merged to main on its own. No plan depends on a later plan to land.
- **Testability in isolation.** Each plan has at least one machine-verifiable assertion the orchestrator can declare pass/fail before the next plan starts.
- **Coherent scope.** Each plan touches at most one data-layer change + one UI surface (loose guideline, not absolute).
- **Natural seam.** Split boundaries fall at model → repository → viewmodel → screen → cloud function joints, not arbitrary line-count cuts.

## Sequencing

Multiple plans within a feature directory run sequentially via:

```
/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md feature-<slug>/plan-03-<name>.md
```

OR, when a manifest exists:

```
/dreamers-full feature-<slug>/manifest.md
```

The orchestrator runs cycle-A → inline drift check → cycle-B → inline drift check → cycle-C → close-out + single PR (or per-plan PRs in INCREMENTAL ship strategy).

If plan-02 references state that plan-01 modified (paths, signatures, data shapes), the inline drift check between cycles surfaces any mismatch before cycle-02 starts.

## When NOT to split

Truly atomic changes (a single model field, a single bug fix, a single screen tweak) stay as one plan inside a single-plan feature directory. Splitting an atomic change adds ceremony without benefit.

## Manifest pattern (optional, for multi-plan with shared context)

When multiple plans share genuine cross-plan context — constraints, design decisions, data models, or end-to-end ACs that span all plans — produce a **manifest** at the feature directory's root: `feature-<slug>/manifest.md`.

**Why:** research on AI coding agents shows hierarchical task decomposition is significantly more effective than flat plan lists (58% faster on complex tasks; ~2× success rate on long-horizon work in published benchmarks). The manifest carries the cross-plan context into each cycle's reviewer prompts so the AI reasons with full-feature awareness, not just the single plan in isolation.

**Produce a manifest if ANY hold:**
- ≥ 2 shared constraints apply across all plans.
- Shared design decisions span plans (e.g., a common abstraction every plan uses).
- Shared data models / interface contracts referenced by multiple plans.
- End-to-end ACs only verifiable after ALL plans ship.
- Cross-plan rollback rules (folded into shared constraints — separate rollback section is retired).

**Skip the manifest if:** the multiple plans are independent (e.g., 3 unrelated changes shipped together). A manifest with all sections empty is decorative — either populate it or skip it.

**Path:** `feature-<slug>/manifest.md` (lives inside the feature directory, not at the plans/ root).

**Template:** `~/.copilot/dreamers/templates/manifest.md`.

**Invocation:**
- Variadic plans (no manifest): `/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md ...` — plans run in argument order; no shared context.
- Manifest mode: `/dreamers-full feature-<slug>/manifest.md` — orchestrator reads the manifest, extracts the plan sequence, threads shared context into reviewer prompts at each cycle.

## Manifest backfill (mandatory)

A feature directory may start with a single plan and no manifest. When a SECOND plan is added to the same feature directory (because work grew beyond one plan's scope), the manifest is created during the planning conversation that produces plan-02:

- **Trigger:** `/dreamers-plan` Phase 1d.1 detects: feature dir already exists, contains `plan-01-*.md`, no `manifest.md` present, and the current conversation is producing what will become `plan-02-*.md` for the same feature.
- **Responsibility:** `/dreamers-plan` creates `manifest.md` in that same Phase 1d.1 step. Uses the existing plan-01 as seed context for the manifest's shared sections.
- **Timing:** before plan-02 implementation starts.

This avoids the edge case where a feature has multiple plans but no manifest, and reviewer agents can't see the cross-plan shared context.

## Ship strategy (multi-plan invocations)

When `/dreamers-full` runs ≥ 2 plans, it presents a **Phase 1.5 ship-strategy gate** asking how to ship:

- **INCREMENTAL** — each plan's cycle ends with its own push + PR; main advances incrementally; the final plan's close-out runs the milestone retro + improvements + plan-archive (whole feature dir moves to archive at that point).
- **ATOMIC** — plans land as commits on one branch; ONE close-out + ONE PR at the end covering all plans; whole feature dir moves to archive after the single PR merges.

The orchestrator RECOMMENDS a strategy based on heuristics; the user picks at the gate. Single-plan invocations skip this gate.

### Recommendation heuristics

The orchestrator reads the manifest (if any) and plan files; the strongest signal cited as the reasoning.

**Recommend INCREMENTAL when ANY hold:**
- ≥ 4 plans in the sequence (review burden of one big PR is high).
- Plans touch significantly different file subsystems (low overlap in plan Context file lists).
- Manifest's shared constraints do NOT mention "ordering dependency," "breaking change," or "coordinated revert."
- Plans are substantial (≥ 5 ACs each, or test cases spanning multiple layers).
- Plan A's value is observable to users without plans B+ (incremental value delivery).

**Recommend ATOMIC when ANY hold:**
- 2–3 plans only (small feature).
- Plans touch overlapping files (same files edited by multiple plans).
- Manifest's shared constraints mention "ordering dependency," "breaking change requiring shim," or "coordinated revert."
- DB migrations or schema changes gated on prior plans.
- End-to-end ACs require ALL plans to verify (no piecewise testability).
- Feature-flag protected work where partial deployment leaves the system in a half-state.

If signals conflict, default to ATOMIC (safer) and cite the conflicting signals.

### Strategy is a runtime decision, not a manifest field

The manifest itself does NOT declare a strategy. The decision happens at invocation time, at the Phase 1.5 gate, where the user can weigh current capacity, review bandwidth, and post-incident risk against the recommendation. Same manifest may ship atomically one cycle and incrementally the next.
