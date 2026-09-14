## Plan quality

Before branch setup, read every plan and check the following. Reject missing requirements, unresolved questions, missing AC layers, or unverifiable citations presented as facts. Reject placeholders such as "relevant files", "handle edge cases", or "follow existing pattern" without exact details. A missing `Plan-type` is legacy: warn and require explicit user approval to continue.

### Common requirements

- Metadata: `# Plan-NN: {short-title}`, `**Date:**` YYYY-MM-DD, `**Status:**` Draft / Active / Completed / Superseded, `**Plan-type:**` lite / standard / complex, `**Branch:**` feat/{slug} or fix/{slug}, and `**User-testing-required:**` yes/no.
- When the sibling transcript exists: `**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)`.
- `Files Touched`: exact paths in a `Path | Action | Required change | Verification` table. No vague rows. Add adjacent required files only when discovered during implementation, justified by the same goal, and recorded before continuing.
- `Acceptance Criteria`: measurable Given/When/Then outcomes inside `<acceptance_criteria>`, each with `*Layer: ...*`. Labels: `unit`, `integration`, `E2E`, `perf`; compounds only when one assertion serves both purposes. No separate Test Cases section.
- `Verification` is last: project test and type-check commands, exact files to inspect, and specific smoke checks (one for lite; one or two for standard/complex).

### Required sections by type

| Type | Sections, in order | Additional requirements |
|---|---|---|
| lite | Goal, Files Touched, Acceptance Criteria, Verification | One-paragraph Goal. Context / Out of Scope only when useful. No code snippets except a minimal public interface contract. |
| standard | Goal, Context, Architecture, Files Touched, Acceptance Criteria, Out of Scope, Constraints, Verification | Design Decisions for non-obvious architecture/API/data/persistence/UI choices; UI for user-visible surfaces. |
| complex | Goal, Context, Architecture, Decision Log, Files Touched, Acceptance Criteria, Traceability, Out of Scope, Constraints, Quality Attributes, Risk / Mitigation, Verification | UI for user-visible surfaces. |

For standard/complex:
- Architecture covers current/target flow, boundary ownership, contracts (or `No contract changes.`), and failure/edge states. Include Mermaid for non-trivial flows, processes, state machines, lifecycles, async handoffs, branching, or multi-step workflows.
- Constraints use `<constraints>` with Technical (stack/perf/libraries), Process (gates/review/tests), and Hard rules (never-do constraints with rationale).

For complex:
- Context uses `Artifact | Verified fact` evidence; keep prose short.
- Architecture also covers data shapes, schema/API changes, retry, rollback, and migration behavior.
- Decision Log: `Decision | Recommended answer | User choice | Rationale | Rejected`.
- Traceability: `Decision / requirement | AC | Verification`.
- Quality Attributes: one line each, or `N/A - <reason>`, for security, privacy, accessibility, performance, migration, and observability.
- Risk / Mitigation: at most three `Risk | Mitigation | Verification` rows.

## Multi-plan ship strategy

Recommend INCREMENTAL for 4+ independent plans, different subsystems, or standalone user value from plan A. Recommend ATOMIC for overlapping files, ordering dependencies, schema/migration/API contracts, or verification requiring all plans. Conflicting signals default to ATOMIC.
