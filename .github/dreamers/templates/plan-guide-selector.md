# Detailed plan selection

/dreamers uses an approved [proposal](proposal.md) by default. Read detailed guides only for an explicit planning request or when a plan-producing skill calls for them. Plan depth never selects reviewers.

Choose the smallest useful guide; honor the user's requested depth:
- [Lite](plan-guide-lite.md): small, localized change.
- [Standard](plan-guide-standard.md): normal feature or refactor needing context and boundaries.
- [Complex](plan-guide-complex.md): coupled modules, migrations, risky contracts, security, or intricate state/flows.

Use [plan metadata and fields](plan.md). Verify cited existing files/callers, measurable outcomes, relevant checks, and resolved decisions. No placeholders in an executable plan.

Create [a manifest](manifest.md) for multiple plans sharing constraints, contracts, or sequencing; backfill when adding a dependent second plan. ATOMIC suits coupled changes; INCREMENTAL suits independently useful plans. Include the strategy in the existing proposal approval, not a later start gate.
