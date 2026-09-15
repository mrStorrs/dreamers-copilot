## Plan selection

`Plan-type` labels complexity for review routing; all types use the same structure. Honor an explicit user choice, noting any mismatch in the proposal. Otherwise choose:

- **lite:** tiny localized work without new architecture, contracts, migration, public API, multi-step flows, or meaningful risk.
- **standard:** normal feature work and other changes that do not need complex coordination.
- **complex:** cross-module or multi-plan work; data/API changes; security/privacy/payment risk; non-trivial state, async, or UI flows; high rollback cost.

Use `feature-<slug>/manifest.md` when multiple plans share context, constraints, contracts, or feature-level ACs. Backfill a missing manifest when adding a second plan. Each plan must remain usable alone; `/dreamers <manifest>` passes shared context through the sequence, while direct plan invocations do not.
