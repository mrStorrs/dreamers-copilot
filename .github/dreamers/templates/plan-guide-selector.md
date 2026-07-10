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

+## Downstream review signal

Plan type is the baseline initial-review signal:

- Complex selects Sentinel + Probe + Hone.
- Low-risk lite and standard select Vigil.
- A danger or high-risk trigger overrides plan type.
- The delivery orchestrator states its lane and rationale, honors explicit user overrides, and asks only when classification is genuinely ambiguous.


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

When /dreamers runs multiple plans:

- Select **INCREMENTAL** for independent plans, different repositories or subsystems, or standalone value that should ship first.
- Select **ATOMIC** when plans overlap files, depend on ordering, include schema, migration, or API contract work, or require joint verification.
- If signals conflict, default to **ATOMIC**.
- State the selection and rationale without a routine confirmation gate. Explicit user overrides remain authoritative.
