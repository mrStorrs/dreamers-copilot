# /dreamers-plan — flow

Planning only. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    G[Understand the goal and Grill] --> P[Proposal and critique]
    P --> A{Approved?}
    A -->|revise| G
    A -->|yes| W[Save verbatim transcript and write plans]
    W --> C[Check scope, ACs, citations, and accepted decisions]
    C --> R{Plan review}
    R -->|minor edit| W
    R -->|major rewrite| G
    R -->|approved| E[Return plan paths; stop when standalone]
    R -->|halt| H[Stop and surface paths]
```

Every plan uses **Goal**, **Scope and context**, and **Acceptance Criteria**. Keep relevant decisions, constraints, contracts, UI details, and risks within scope; attach validation details to ACs when needed. There are no separate Approach or Verification sections.

- `Plan-type` still labels lite / standard / complex for reviewer selection; it does not select a document format.
- Grill one unresolved decision at a time. Save questions and responses verbatim and link the transcript from each plan when present.
- Proposal critique and plan approval remain mandatory. Written plans must preserve all accepted requirements and user decisions.
- Use a manifest for shared multi-plan context; backfill one when adding a second plan. Individual plans must remain usable alone.
- Planning rules and templates are embedded through XML sync; no Dreamers rule-file reads are required.
- The caller owns its todo. This skill never invokes implementation.
