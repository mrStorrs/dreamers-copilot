# /dreamers-implement — flow

One task or approved plan, implemented inline. Shared workflow: [implementation-workflow](../../dreamers/refs/implementation-workflow.md). `SKILL.md` embeds this ref and its required standards through XML sync.

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
- Standalone todos are optional. Delivery skills execute the same embedded workflow under their existing todo.
- The skill exits at green validation. `/dreamers` executes its embedded review workflow next.
