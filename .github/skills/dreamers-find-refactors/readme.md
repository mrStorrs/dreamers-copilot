# dreamers-find-refactors - flow

Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-find-refactors"]) --> Lens["Ask for refactor lenses"]
    Lens --> Section["Map repo into sections"]
    Section --> Manifest["Write sections.md"]
    Manifest --> Hone["Spawn section-scoped Hone audits"]
    Hone --> Artifacts["Read hone-refactor artifacts"]
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
- Hone writes section-named `.dreamers/reviews/hone-refactor-*.md` artifacts.
- The orchestrator groups findings into coherent plan files instead of one plan per finding.
- Generated plans follow `plan-writing-guide.md`.
- No branch, implementation, commit, push, or PR.
