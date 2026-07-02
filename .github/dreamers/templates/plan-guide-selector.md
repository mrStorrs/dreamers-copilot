# Plan Guide Selector

Read this first. Then read only the selected guide:

- `plan-guide-lite.md`
- `plan-guide-standard.md`
- `plan-guide-complex.md`

## User override

If the user explicitly asks for `lite`, `standard`, or `complex`, use that plan type. If the override appears mismatched, state the mismatch in the proposal, then follow the requested guide.

## Default selection

Use the smallest guide that preserves quality.

- **Lite:** one-file or tiny localized change; no new architecture, data contract, migration, public API, multi-step UI/process flow, or meaningful risk.
- **Standard:** default for normal feature work, bug fixes touching several files, or any change needing architecture/context but not complex coordination.
- **Complex:** cross-module or multi-plan work; schema/data migration; public API/contract changes; auth/security/privacy/payment risk; non-trivial state machine, async flow, or multi-step UI/process; high rollback cost.

## Mandatory checks

Every plan must:

- Include `**Plan-type:** lite / standard / complex`.
- Have measurable ACs with layer annotations.
- Have no open questions.
- Avoid placeholders: no "relevant files", "handle edge cases", "follow existing pattern" without exact details.
- Verify cited code artifacts by reading them in the planning session.

## Manifest trigger

Create `feature-<slug>/manifest.md` only when multiple plans share constraints, decisions, contracts, data models, or end-to-end ACs. When adding a second plan to an existing feature directory without a manifest, backfill one.

## Ship strategy

When `/dreamers-full` runs multiple plans:

- Recommend **INCREMENTAL** when there are 4+ independent plans, different subsystems, or plan A has standalone user value.
- Recommend **ATOMIC** when plans overlap files, depend on ordering, include schema/migration/API contract work, or require all plans to verify.
- If signals conflict, default to **ATOMIC**.
