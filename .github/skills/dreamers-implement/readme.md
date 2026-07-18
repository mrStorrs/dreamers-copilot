# /dreamers-implement — flow

Visual map of the one-cycle implementation skill. Source of truth is `SKILL.md`.

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

    S3["Step 3 — Type-check + run tests"] --> TypeCheck["Run project's type-check"]
    TypeCheck --> RunTests["Run project's test command"]
    RunTests --> TestResult{"Tests pass?"}
    TestResult -->|Yes| Benchmarks["Update ./test-benchmarks.md<br/>if project uses one"]
    TestResult -->|No| AttemptCheck{"Attempts < 3?"}
    AttemptCheck -->|Yes| FixInline["Fix inline"]
    FixInline --> RunTests
    AttemptCheck -->|No| HaltB(["Halt + surface"])
    Benchmarks --> End(["Return AC coverage matrix<br/>/dreamers invokes /dreamers-review next"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff

    class ArgCheck,TestResult,AttemptCheck gate
    class HaltA,HaltB halt
    class S1,S2,S3,ReadPlan,WriteTests,Stage1,EditFiles,Stage2,TypeCheck,RunTests,FixInline,Benchmarks phase
```

## Key invariants

- **Tests-first.** Step 1 writes failing tests BEFORE Step 2's implementation. Stage but don't run yet — they should fail.
- **Layer annotation drives test layer.** Each plan AC has a `*Layer: ...*` annotation; the test goes at that layer.
- **3-attempt fix loop in Step 3.** If tests still fail after 3 fix attempts, halt and surface to the user.
- **Phase boundary.** This skill returns after the initial change reaches green validation. It does not review, apply review findings, run user testing, commit, push, or open a PR.
- **Pipeline order.** When `/dreamers` invokes this skill, `/dreamers-review` runs immediately after a successful return.
