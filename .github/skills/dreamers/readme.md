# Dreamers

One thin adaptive orchestrator handles task descriptions, approved plans, and feature manifests by invoking the specialized planning, verification, implementation, review, documentation, and PR skills. Planning depth, reviewer lane, ship strategy, documentation, and retrospective decisions remain independent.

~~~mermaid
flowchart TD
    I[/dreamers input/] --> R{Input kind}
    R -->|empty or help flags| H[/dreamers-help read-only guide/]
    R -->|task| P[/dreamers-plan with default Grill/]
    R -->|plan or manifest| Q[Artifact quality checks]
    P --> A[Approved plans]
    Q --> A
    A --> PV[/dreamers-plan-verify once per plan/]
    PV --> T[/dreamers-implement tests-first change and validation/]
    T --> S{Plan type or danger}
    S -->|complex or high risk| F[/dreamers-review triad/]
    S -->|low-risk lite or standard| V[/dreamers-review --vigil/]
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

Invoked skills run in the same orchestrator context, complete their owned phase, and return control without replacing the outer todo. There are no composed modes or structured skill-to-skill handoffs. Explicit handoffs are limited to spawned agents.

The orchestrator surfaces the selected reviewer lane and rationale without a routine confirmation gate, then calls /dreamers-review for every lane. The review skill and reviewers are read-only for project files and git state; each reviewer may write exactly one .dreamers/reviews artifact. The orchestrator alone applies findings and owns user-testing, bug-fix, revalidation, and warranted review-rerun loops. Explicit user overrides win; ambiguous risk is returned to the user.

The closed danger rubric escalates security, authentication, authorization, privacy, payment, secret, and permission changes; schema, migration, persistence, destructive-data, concurrency, and irreversible-side-effect changes; public or breaking API, dependency, build, distribution, and cross-subsystem changes; and rollback that requires operator action or data recovery. Anything outside the rubric is not silently promoted.

The only mandatory gates are task-mode plan approval, major scope expansion, triggered user testing, and final pre-PR approval. Documentation runs for a user-facing or otherwise documentable landed diff. Retro and improvements run only for multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or an explicit request; otherwise each skip is recorded.
