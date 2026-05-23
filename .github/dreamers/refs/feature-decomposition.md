# When to write multiple plans (mandatory)

Default to one plan. Split into multiple plans only when one plan's scope is genuinely too large to land cleanly in a single cycle.

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

Multiple related plans run sequentially on the same branch via:

```
/dreamers-full <plan-a> <plan-b> <plan-c>
```

The orchestrator runs cycle-A → inline drift check → cycle-B → inline drift check → cycle-C → close-out + single PR.

If plan-B references state that plan-A modified (paths, signatures, data shapes), the inline drift check between cycles surfaces any mismatch before cycle-B starts. The user can revise plan-B and continue, or halt.

## When NOT to split

Truly atomic changes (a single model field, a single bug fix, a single screen tweak) stay as one plan. Splitting an atomic change adds ceremony without benefit.

## Grouping related plans (optional)

If multiple plans cover the same feature area, you may share a slug prefix purely for visual grouping:

- `plan-auth-login.md`
- `plan-auth-logout.md`
- `plan-auth-reset.md`

This is cosmetic. Each plan still stands alone; the prefix doesn't create semantics.

## Manifest pattern (optional, for multi-plan with shared context)

When multiple plans share genuine cross-plan context — constraints, design decisions, data models, or end-to-end ACs that span all plans — produce a **feature manifest** alongside the plan files: `feature-{slug}.md`.

**Why:** research on AI coding agents shows hierarchical task decomposition is significantly more effective than flat plan lists (58% faster on complex tasks; ~2× success rate on long-horizon work in published benchmarks). The manifest carries the cross-plan context into each cycle's reviewer prompts so the AI reasons with full-feature awareness, not just the single plan in isolation.

**Produce a manifest if ANY hold:**
- ≥ 2 shared constraints apply across all plans.
- Shared design decisions span plans (e.g., a common abstraction every plan uses).
- Shared data models / interface contracts referenced by multiple plans.
- End-to-end ACs only verifiable after ALL plans ship.
- Cross-plan risks (ordering dependencies, rollback coordination).

**Skip the manifest if:** the multiple plans are independent (e.g., 3 unrelated bug fixes shipped together). A manifest with all sections empty is decorative — either populate it or skip it.

**Naming:** `feature-{slug}.md`. Slug should match the prefix shared by the related plans (e.g., `feature-auth.md` for `plan-auth-login.md` + `plan-auth-logout.md` + `plan-auth-reset.md`).

**Template:** `~/.copilot/dreamers/templates/feature.md`.

**Invocation:**
- Variadic plans (no manifest): `/dreamers-full <plan-a> <plan-b> <plan-c>` — plans run in argument order; no shared context.
- Manifest mode: `/dreamers-full feature-{slug}.md` — orchestrator reads the manifest, extracts the plan sequence, threads shared context into reviewer prompts at each cycle.
