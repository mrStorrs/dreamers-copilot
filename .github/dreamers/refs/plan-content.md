# Plan Content Rules

Use `~/.copilot/dreamers/templates/plan-sub.md` as the starting structure for every sub-plan and standalone plan. Copy it, fill in the sections, remove any that don't apply.

## Umbrella plan (`plan-{n}`) must include:
- `# Plan {n} — {Short Title} (Umbrella)`
- Metadata: Owner, Date, Scope (repo/global), Status, Links
- Sections: Summary, Problem/Motivation, Scope/Non-goals (shared), Sub-plans (ordered table: ID | File | Summary | Status), Constraints (shared), End-to-end Acceptance Criteria (verified after all sub-plans ship), Rollback/Observability strategy
- Status field: Draft / Active / Completed / Superseded

## Sub-plan (`plan-{n}a`, `plan-{n}b`, …) must include:
- `# Plan {n}{letter} — {Short Title}`
- Metadata: Owner, Date, Scope, Parent (link to umbrella), Depends-on (prior sub-plans if any), Status, User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases for Probe, Rollback boundary, Risks/Mitigations
- **User testing required:** `yes` if a human must manually verify before next sub-plan begins (UI flows, push notifications, payments, camera, permissions). `no` for purely backend, data-layer, or non-visible changes. When in doubt, default to `yes`.
- Status field: Draft / Active / Completed / Superseded

### Design Decisions format (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

## Standalone plan (atomic change, no decomposition needed):
- `# Plan {n} — {Short Title}`
- Sections: Summary, Problem/Motivation, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases for Probe, Risks/Mitigations, Rollback/Observability
- Status field: Draft / Active / Completed / Superseded

## Code in plans (mandatory)
Plans must **not** include code snippets. Implementation is Forge's domain.

**One exception:** interface and type contracts where the signature itself is the design decision (e.g., a new public API shape). In this case:
- Include the interface/type signature only — no implementation bodies
- State the file path and package where it will live
- Keep it minimal: the contract, not the code
