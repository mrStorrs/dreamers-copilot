# /dreamers-retro — flow

Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start[Review current session] --> Evidence{Observed blocker,<br/>AI mistake, or<br/>developer correction?}
    Evidence -->|No| Skip[No retrospective warranted<br/>no file changes]
    Evidence -->|Yes| Fit{Specific repo-local<br/>scaffolding gap?}
    Fit -->|No| Skip
    Fit -->|Dreamers core| Skip
    Fit -->|Yes| Verify[Inspect exact target<br/>confirm rule is not clear]
    Verify --> Qualified{High-confidence<br/>minimal change?}
    Qualified -->|No| Skip
    Qualified -->|Yes| Record[Write retro and append<br/>deduplicated improvement]
    Record --> Report[Report up to three suggestions<br/>apply none]
```

## Invariants

- `/dreamers` and `/dreamers-lite` invoke this skill exactly once before a terminal response.
- Evidence comes from the current session; no speculative repository audit.
- Suggestions target current-repo AI scaffolding only.
- Dreamers core is never a target.
- No evidence means no retro file and no improvement entry.
- Scaffolding changes are never applied by this skill.
