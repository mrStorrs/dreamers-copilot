# /dreamers-implement — flow

One approved plan, implemented inline. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    P[Approved plan] --> I[Implement code and tests; stage changes]
    I --> V[Run project type-check and tests]
    V --> R{Validation passes?}
    R -->|yes| B[Update test benchmarks]
    R -->|no| A{Fewer than 3 fix attempts?}
    A -->|yes| F[Fix inline]
    F --> V
    A -->|no| H[Halt and surface failure]
    B --> E[Return AC coverage matrix]
```

- Tests cover the plan's annotated AC layers; tests-first ordering is not required.
- Standalone runs own a two-step todo. Calls from `/dreamers` use its existing todo.
- The skill exits at green validation. `/dreamers` invokes `/dreamers-review` next.
