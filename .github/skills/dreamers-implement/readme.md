# /dreamers-implement — flow

One task or approved plan, implemented inline. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    P[Task or approved plan] --> I[Implement code and tests; stage changes]
    I --> V[Run project type-check and tests]
    V --> R{Validation passes?}
    R -->|yes| B[Update test benchmarks]
    R -->|no| A{Fewer than 3 fix attempts?}
    A -->|yes| F[Fix inline]
    F --> V
    A -->|no| H[Halt and surface failure]
    B --> E[Return requirement or AC coverage and validation results]
```

- Tasks use their stated requirements as acceptance criteria, without a plan file. Plans use their annotated AC layers; tests-first ordering is not required.
- Standalone todos are optional. Calls from a delivery skill use its existing todo.
- The skill exits at green validation. `/dreamers` invokes `/dreamers-review` next.
