# dreamers-find-refactors - flow

Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-find-refactors"]) --> Lens["Ask for refactor lenses"]
    Lens --> Section["Map repo into sections"]
    Section --> Manifest["Write sections.md"]
    Manifest --> Hone["Spawn section-scoped Hone audits"]
    Hone --> Artifacts["Use one complete report per section<br/>from the file or final reply"]
    Artifacts --> Synthesis["Deduplicate + group findings"]
    Synthesis --> Summary["Write summary.md"]
    Summary --> Plans["Write Dreamers plan files"]
    Plans --> Gate{"Review gate"}
    Gate -->|Minor edit| Plans
    Gate -->|Major rewrite| Lens
    Gate -->|Approved| Stop(["Stop - no implementation"])
    Gate -->|Halt| Stop
```

## Invariants

- Read-only for project code.
- Hone attempts to save section-named reports under `.dreamers/reviews/` and returns the same reports in its final replies. The synthesis records missing handoffs, blockers, and open questions.
- The orchestrator groups findings into the smallest coherent shippable plans, with a manifest when there are multiple plans.
- Generated plans use the shared Goal and Acceptance criteria format.
- No branch, implementation, commit, push, or PR.
