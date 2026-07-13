# /dreamers-implement — flow

Visual map of the initial-change implementation skill. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-implement $ARGUMENTS"]) --> ArgCheck{"Plan path<br/>provided?"}
    ArgCheck -->|No| HaltA(["Halt + ask<br/>do not invent a plan"])
    ArgCheck -->|Yes| S1

    S1["Step 1 — Read plan + write failing tests"] --> ReadPlan["Read the plan file"]
    ReadPlan --> WriteTests["For each AC G/W/T + Layer:<br/>write at least one failing test<br/>at the annotated layer"]
    WriteTests --> Stage1["git add"]
    Stage1 --> S2

    S2["Step 2 — Implement"] --> EditFiles["Edit production files<br/>per comment-rules + testing-mandate"]
    EditFiles --> Stage2["git add as you go"]
    Stage2 --> S3

    S3["Step 3 — Complete automated validation"] --> Validate["Run every project-required<br/>type-check, test, build, and lint command<br/>record commands + results"]
    Validate --> TestResult{"Validation green?"}
    TestResult -->|Yes| Benchmarks["Update relevant ./test-benchmarks.md rows<br/>if project uses them"]
    TestResult -->|No| AttemptCheck{"Attempts < 3?"}
    AttemptCheck -->|Yes| FixInline["Fix inline"]
    FixInline --> Validate
    AttemptCheck -->|No| HaltB(["Halt + surface"])
    Benchmarks --> End(["Return AC coverage matrix<br/>changed-file scope<br/>validation commands + results"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff

    class ArgCheck,TestResult,AttemptCheck gate
    class HaltA,HaltB halt
    class S1,S2,S3,ReadPlan,WriteTests,Stage1,EditFiles,Stage2,Validate,FixInline,Benchmarks phase
```

## Key invariants

- **Tests-first.** Step 1 writes failing tests BEFORE Step 2's implementation. Stage but don't run yet — they should fail.
- **Layer annotation drives test layer.** Each plan AC has a `*Layer: ...*` annotation; the test goes at that layer.
- **Complete validation.** Step 3 runs every type-check, test, build, and lint command required by project instructions and records each result.
- **3-attempt fix loop in Step 3.** If automated validation is not green after 3 fix attempts, halt and surface to the user.
- **Phase boundary.** This skill returns after the initial change reaches green validation. It does not review, apply review findings, run user testing, commit, push, or open a PR.
- **Same-context composition.** When /dreamers invokes this skill, it keeps the outer todo and immediately invokes /dreamers-review after a successful return. Standalone use owns its own three-step todo.
