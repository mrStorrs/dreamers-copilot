# /dreamers-plan — flow

Planning only. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    I[Investigate current code] --> Q[Clarify as needed]
    Q --> P[Propose plans, concerns, and acceptance criteria]
    P --> A{Approved?}
    A -->|revise| P
    A -->|yes| W[Save approved plans and any question transcript]
    W --> C[Check artifacts against the approved proposal]
    C --> E[Return plan paths]
```

Every plan uses **Goal** and **Acceptance criteria**, matching GitHub issue proposals. Delivery metadata remains for downstream routing.

- Investigate code before proposing; report concerns with suggested acceptance criteria.
- Ask questions when needed and preserve any questions and answers verbatim in a linked transcript.
- Obtain proposal approval before writing; revisions require approval of the revised proposal.
- `Plan-type` labels lite / standard / complex for downstream reviewer selection.
- Split work only into independently shippable plans; use a manifest for their order and shared context.
- Planning formats are embedded through XML sync; no Dreamers rule-file reads are required.
- This skill returns paths to its caller or stops when standalone. It never implements or changes project files or git state.
