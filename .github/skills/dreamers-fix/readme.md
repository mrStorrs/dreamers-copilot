# /dreamers-fix — flow

Visual map of the lightweight bug-fix pipeline. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-fix $ARGUMENTS"]) --> ArgCheck{"Bug description<br/>provided?"}
    ArgCheck -->|No| HaltA(["Halt + ask"])
    ArgCheck -->|Yes| S1

    S1["Step 1 — Branch setup"] --> Branch["fetch + checkout default + pull<br/>cut fix/slug branch"]
    Branch --> S2

    S2["Step 2 — Scope survey + escalation"] --> Survey["Read the bug surface<br/>identify affected files"]
    Survey --> ScopeCheck{"Bug-fix scope<br/>or scope blowup?"}
    ScopeCheck -->|"Scope blowup<br/>multi-subsystem / new module / schema"| HaltB(["Halt + recommend<br/>/dreamers-full instead"])
    ScopeCheck -->|"In scope<br/>single file or tight cluster"| S3

    S3["Step 3 — Regression test + implement + run"] --> WriteTest["Write failing test that<br/>captures the buggy behavior"]
    WriteTest --> Implement["Implement the fix<br/>per comment-rules + testing-mandate<br/>edit only files in bug-fix surface"]
    Implement --> Stage["git add"]
    Stage --> RunTests["Type-check + run tests"]
    RunTests --> TestResult{"Tests pass?"}
    TestResult -->|Yes| End(["Surface:<br/>bug-fix surface<br/>regression test name<br/>test status<br/><br/>Next: Vigil review<br/>then commit + /dreamers-pr"])
    TestResult -->|No| AttemptCheck{"Attempts < 3?"}
    AttemptCheck -->|Yes| FixInline["Fix inline"]
    FixInline --> RunTests
    AttemptCheck -->|No| HaltC(["Halt + surface"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff

    class ArgCheck,ScopeCheck,TestResult,AttemptCheck gate
    class HaltA,HaltB,HaltC halt
    class S1,S2,S3,Branch,Survey,WriteTest,Implement,Stage,RunTests,FixInline phase
```

## Key invariants

- **Escalation check in Step 2.** Multi-subsystem changes, new modules, or schema changes are NOT in bug-fix scope — halt and recommend `/dreamers-full` instead.
- **Regression test first.** Step 3 writes the failing test BEFORE implementing the fix. If no test infra exists for the affected surface, note the absence.
- **Files in the bug-fix surface only.** No while-I'm-here cleanup, no unrelated refactors.
- **3-attempt fix loop.** Same as `/dreamers-implement`. Halt and surface after 3 failed attempts.
- **No review, no commit, no push.** This skill exits at green tests. The user runs Vigil for the audit, then commits + `/dreamers-pr` to ship.
