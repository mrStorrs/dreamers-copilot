# Plan Content Rules

Every plan uses `~/.copilot/dreamers/templates/plan.md` as the starting structure. Copy it, fill in the sections, remove any that don't apply.

## Required fields

- `# Plan — {Short Title}`
- Metadata: Owner, Date, Scope, Status (Draft / Active / Completed / Superseded), Branch (if applicable), User-testing-required (yes/no), Links

## Required sections

- **Summary** — 1–2 sentences: what this plan delivers and why.
- **Scope / Non-goals** — in-scope file list with one-line reasons; explicit non-goals.
- **Constraints** — hard rules the implementation must not violate.
- **Design Decisions** — one entry per significant choice, structured (see below).
- **Acceptance Criteria** — numbered, measurable, verifiable.
- **Test Cases** — Given/When/Then for non-trivial cases; one-liners acceptable for simple assertions.
- **Rollback boundary** — which files can be reverted; cross-plan rollback implications if any.
- **Risks / Mitigations** — risks identified, mitigation per risk.

## Design Decisions format

One entry per significant choice:

- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

## User-testing required

- `yes` if a human must manually verify before the cycle completes (UI flows, push notifications, payments, camera, permissions).
- `no` for backend, data-layer, non-visible changes.
- Default to `yes` when in doubt.

## Code in plans (mandatory)

Plans must **not** include code snippets. Implementation is the orchestrator's domain.

**One exception:** interface and type contracts where the signature itself IS the design decision (e.g., a new public API shape). In this case:
- Include the interface/type signature only — no implementation bodies.
- State the file path and package where it will live.
- Keep it minimal: the contract, not the code.

## Multi-plan work

When the scope of a piece of work is too large for one plan, the planning phase produces **multiple separate plans**, each independently shippable. Sequencing is by argument order at invocation: `/dreamers-full <plan-a> <plan-b> <plan-c>` runs them in that order on one branch.

For multi-plan work with **shared cross-plan context** (shared constraints, shared design decisions, shared data models, end-to-end ACs that only verify after all plans ship), the planning phase may also produce an OPTIONAL **feature manifest**: `feature-{slug}.md`. The manifest is the AI-effectiveness anchor — it threads cross-plan context into per-cycle reviewer prompts.

See `feature-decomposition.md` § "Manifest pattern" for when to use a manifest and § "Splitting rules" for when to produce one plan vs many.
