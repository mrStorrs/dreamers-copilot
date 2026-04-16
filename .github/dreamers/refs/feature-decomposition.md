# Feature Decomposition (MANDATORY)

Every non-trivial feature must be broken into the smallest possible independently shippable sub-plans.

**Rule:** When planning any feature, always ask: *"Can this be split into pieces where Forge can implement each one in a single session and Probe can test it in isolation?"* If yes, split it.

## Naming convention
- `plan-{n}-{feature-name}.md` — the **umbrella plan**: describes the full feature goal, lists all sub-plans, defines the rollback/observability strategy. Contains NO milestones Forge implements directly — those live in sub-plans.
- `plan-{n}a-{first-chunk}.md`, `plan-{n}b-{second-chunk}.md`, `plan-{n}c-…` — **sub-plans**: each is a complete, independently shippable unit of work with its own acceptance criteria, its own Forge cycle, its own review.
- If a feature is large enough to span multiple major areas, use a new parent number: `plan-{n}` + `plan-{n}a/b/c` for the first area, `plan-{n+1}` + `plan-{n+1}a/b/c` for the next.

## What makes a good sub-plan split
- Each sub-plan can be merged to main independently (no sub-plan depends on an un-merged sibling).
- A sub-plan touches at most one data layer change + one UI surface.
- A new sub-plan starts when crossing a natural seam: model → repository → viewmodel → screen → cloud function — these are common split points.
- If a sub-plan would take Forge more than ~300 lines of new/changed code, split it further.
- **Testability gate:** A sub-plan must have at least one machine-verifiable assertion that Probe can declare pass/fail on in isolation, before the next sub-plan starts. If testability requires a sibling sub-plan not yet shipped, the split boundary is wrong — reslice.

## When NOT to decompose
Truly atomic changes (a single model field, a single bug fix, a single screen tweak) stay as a single standalone plan with no sub-plans.
