# /dreamers-full — flow

Visual map of every decision point in the end-to-end pipeline. Source of truth is `SKILL.md`; this is the picture.

```mermaid
flowchart TD
    Start([/dreamers-full $ARGUMENTS]) --> ModeCheck{$ARGUMENTS<br/>type?}

    ModeCheck -->|Task description| Mode1[Mode 1]
    ModeCheck -->|Plan path s| Mode2[Mode 2]
    ModeCheck -->|manifest.md| Mode3[Mode 3 + shared context]

    Mode1 --> P1[Phase 1 — Planning]
    Mode2 --> P15
    Mode3 --> P15

    P1 --> InvokePlan[/dreamers-plan]
    InvokePlan --> PlanResult{Plan result}
    PlanResult -->|Halt| HaltA([Halt + resume cmd])
    PlanResult -->|Plan paths| P15

    P15{Multi-plan?} -->|Yes| Strategy{INCREMENTAL<br/>or ATOMIC?}
    P15 -->|No| BranchSetup
    Strategy -->|INCREMENTAL| BranchSetup
    Strategy -->|ATOMIC| BranchSetup
    Strategy -->|Halt| HaltB([Halt + resume cmd])

    BranchSetup[Branch setup<br/>cut feat slug + check improvements.md] --> Cycle

    Cycle[Phase 2 — cycle N] --> S1[Step 1<br/>Read plan + write failing tests]
    S1 --> S2[Step 2<br/>Implement inline]
    S2 --> S3[Step 3<br/>Type-check + run tests]

    S3 --> S3Check{Tests green<br/>within 3 attempts?}
    S3Check -->|No| HaltC([Halt + surface])
    S3Check -->|Yes| S4

    S4[Step 4<br/>Invoke /dreamers-review] --> ReviewResult{Review<br/>result}
    ReviewResult -->|Blocked| HaltD([Halt + surface])
    ReviewResult -->|Findings| S5

    S5[Step 5 — Apply findings] --> Gate{Major-refactor<br/>gate fires?}
    Gate -->|No| ApplyFixes
    Gate -->|Yes| GateChoice{User decides}
    GateChoice -->|Apply now| ApplyFixes
    GateChoice -->|Defer| CreateStub[Create stub plan file]
    CreateStub --> ApplyFixes
    GateChoice -->|Other| GateChoice

    ApplyFixes[Apply non-deferred fixes<br/>re-run tests] --> S6
    S6[Step 6<br/>User testing gate] --> UserTest{User response}
    UserTest -->|Bug| BugFix[Fix inline + re-test]
    BugFix --> S6
    UserTest -->|Halt| HaltE([Halt])
    UserTest -->|Approved| MorePlans{More plans<br/>remain?}

    MorePlans -->|No| P3
    MorePlans -->|Yes| Between{Strategy?}

    Between -->|INCREMENTAL| Light[Drift check<br/>/dreamers-docs if applicable<br/>commit<br/>/dreamers-pr]
    Between -->|ATOMIC| AtomicCommit[Drift check<br/>commit]

    Light --> ContIncr{Continue?}
    AtomicCommit --> ContAtomic{Continue?}

    ContIncr -->|Continue| ReCut[Wait for merge<br/>re-cut feature branch]
    ContIncr -->|Halt| HaltF([Halt])
    ContAtomic -->|Continue| Cycle
    ContAtomic -->|Halt| HaltG([Halt])
    ReCut --> Cycle

    P3[Phase 3 — Close-out FULL] --> Improvements[Append .dreamers/improvements.md]
    Improvements --> InvokeDocs[/dreamers-docs]
    InvokeDocs --> Retro[Write retro]
    Retro --> FinalCommit[Final commit if staged]
    FinalCommit --> Approval{User approval}
    Approval -->|Halt| HaltH([Halt])
    Approval -->|Approved| InvokePR[/dreamers-pr]
    InvokePR --> Archive[Plan archive — merged features only]
    Archive --> PostScan[Post-PR scan<br/>surface improvements + drift]
    PostScan --> End([PR URL + summary])

    classDef skill fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff

    class InvokePlan,S4,InvokeDocs,InvokePR skill
    class ModeCheck,PlanResult,P15,Strategy,S3Check,ReviewResult,Gate,GateChoice,UserTest,MorePlans,Between,ContIncr,ContAtomic,Approval gate
    class HaltA,HaltB,HaltC,HaltD,HaltE,HaltF,HaltG,HaltH halt
    class P1,Cycle,P3,BranchSetup,Light,AtomicCommit,Improvements,Retro,FinalCommit,Archive,PostScan phase
```

## Legend

- **Blue nodes** — invoke another skill (`/dreamers-plan`, `/dreamers-review`, `/dreamers-docs`, `/dreamers-pr`).
- **Orange diamonds** — decision points (most call `request_information` and surface options to the user).
- **Red nodes** — halt points (skill exits with a resume command).
- **Green nodes** — phase / step / inline action.

## Key invariants

- Step 6 (user-testing gate) fires at the end of **every** plan, not just plans that declare `User-testing-required: yes`.
- `/dreamers-review` is **report-only** — Step 5 (apply findings + major-refactor gate) lives in this skill, not in `/dreamers-review`.
- All `request_information` calls include an **Other** freeform option.
- INCREMENTAL ships a PR per plan (between cycles). ATOMIC accumulates commits and ships one PR at Phase 3.
