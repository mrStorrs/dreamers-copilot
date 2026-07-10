# Dreamers

One adaptive delivery pipeline handles task descriptions, approved plans, and feature manifests. Planning depth, reviewer lane, ship strategy, documentation, and retrospective decisions remain independent.

~~~mermaid
flowchart TD
    I[/dreamers input/] --> R{Input kind}
    R -->|empty or help flags| H[/dreamers-help read-only guide/]
    R -->|task| P[/dreamers-plan with default Grill/]
    R -->|plan or manifest| Q[Artifact quality and drift checks]
    P --> A[Approved plans]
    Q --> A
    A --> T[Tests-first implementation and validation]
    T --> S{Plan type or danger}
    S -->|complex or high risk| F[Sentinel + Probe + Hone]
    S -->|low-risk lite or standard| V[Vigil]
    F --> X[Apply findings and revalidate]
    V --> X
    X --> U{User-testing trigger}
    U -->|yes| G[User-testing gate]
    U -->|no| C[Adaptive close-out]
    G --> C
    C --> D[Triggered docs and retro decisions]
    D --> PR[Mandatory pre-PR approval then /dreamers-pr]
~~~

Empty or whitespace-only input, help, --help, and -h route directly to /dreamers-help without inspecting or mutating repository or external state. Task descriptions run Grill unless the user supplies --no-grill or unmistakable natural-language direction to skip the interview. Supplied plan paths and manifests preserve their sequence and skip Grill, replanning, rewriting, and implementation-start approval while retaining quality and drift checks.

The selected reviewer lane and rationale are surfaced without a routine confirmation gate. Explicit user overrides win; ambiguous risk is returned to the user.

The closed danger rubric escalates security, authentication, authorization, privacy, payment, secret, and permission changes; schema, migration, persistence, destructive-data, concurrency, and irreversible-side-effect changes; public or breaking API, dependency, build, distribution, and cross-subsystem changes; and rollback that requires operator action or data recovery. Anything outside the rubric is not silently promoted.

The only mandatory gates are task-mode plan approval, major scope expansion, triggered user testing, and final pre-PR approval. Documentation runs for a user-facing or otherwise documentable landed diff. Retro and improvements run only for multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or an explicit request; otherwise each skip is recorded.
