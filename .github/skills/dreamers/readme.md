# /dreamers — flow

Visual map of the end-to-end pipeline. Source of truth is `SKILL.md`. The flow preserves the original full-pipeline gates and close-out while invoking the specialized skills for planning, implementation, review, docs, and PR creation.

~~~mermaid
flowchart TD
    I[/dreamers input/] --> R{Input kind}
    R -->|task| P[/dreamers-plan/]
    R -->|plan or manifest| Q[Artifact quality checks]
    P --> G[Plan review / implementation-start gate]
    G --> A[Approved plans]
    Q --> A
    A --> T[/dreamers-implement/]
    T --> V[/dreamers-review selects from plan complexity/]
    V --> X[Apply findings and revalidate]
    X --> U{User-testing trigger}
    U -->|yes| UT[User-testing gate and fix loop]
    U -->|no| C[Full close-out]
    UT --> C
    C --> D[/dreamers-docs, improvements, retro, final commit/]
    D --> PR[Mandatory pre-PR approval then /dreamers-pr]
~~~

## Key invariants

- Task mode invokes `/dreamers-plan`, then runs the original Phase 1.5 implementation-start gate. Plan path and manifest modes skip both phases and proceed after plan-quality checks.
- `/dreamers-implement` owns the tests-first implementation pass. `/dreamers-review` always runs after it succeeds.
- `/dreamers-review` selects Vigil for lite plans, Sentinel + Probe for standard plans, and Sentinel + Probe + Hone for complex plans unless the plan or user explicitly directs another lane.
- The review skill and reviewers are read-only for project files. Reviewers may write their required `.dreamers/reviews/` artifacts.
- `/dreamers` applies findings and owns the major-refactor gate, review-rerun gate, user-testing and fix loop, and revalidation.
- Major-refactor findings deferred at the user gate are appended to project-root `defered.md`; existing entries are preserved and no follow-up plan is created automatically.
- INCREMENTAL and ATOMIC behavior, improvements, docs, retro, commits, mandatory pre-PR approval, and PR creation remain the full pipeline behavior.
