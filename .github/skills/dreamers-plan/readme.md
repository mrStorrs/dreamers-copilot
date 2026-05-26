# /dreamers-plan — flow

Visual map of the 3-phase planning conversation. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-plan $ARGUMENTS"]) --> ArgCheck{"Task description<br/>provided?"}
    ArgCheck -->|No| HaltA(["Halt + ask"])
    ArgCheck -->|Yes| S1

    S1["Step 1 — Hash out"] --> Summary["Write 1-paragraph<br/>understanding summary"]
    Summary --> Questions["Identify ambiguities<br/>ask all clarifying Qs<br/>in ONE request_information"]
    Questions --> Proposal["Present proposal +<br/>request approval"]
    Proposal --> ApprovalGate{"User response"}
    ApprovalGate -->|Corrections| Proposal
    ApprovalGate -->|Approved| Decide["Decide plan count + manifest<br/>backfill check on existing feature dir"]
    Decide --> S2

    S2["Step 2 — Write plans"] --> ReadGuide["Read plan-writing-guide.md<br/>in full via view"]
    ReadGuide --> Mkdir["mkdir -p .dreamers/plans/feature-slug/"]
    Mkdir --> WritePlans["Write each plan-NN-name.md<br/>+ manifest if multi-plan"]
    WritePlans --> Component["Component-usage check<br/>grep callers for shared components"]
    Component --> Citation["Citation accuracy<br/>verify every cited artifact exists"]
    Citation --> SelfCheck{"Self-check<br/>against guide?"}
    SelfCheck -->|Fail| FixPlan["Fix violations"]
    FixPlan --> SelfCheck
    SelfCheck -->|Pass| S3

    S3["Step 3 — Review gate"] --> Present["Present plan paths<br/>via request_information"]
    Present --> Review{"User response"}
    Review -->|Minor edit| MinorFix["Apply inline +<br/>re-run Step 2 self-check"]
    MinorFix --> Present
    Review -->|Major rewrite| S1
    Review -->|Halt| HaltB(["Halt + surface paths"])
    Review -->|Other| Review
    Review -->|Approved| End(["Surface plan paths<br/>HARD STOP"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff

    class ArgCheck,ApprovalGate,SelfCheck,Review gate
    class HaltA,HaltB halt
    class S1,S2,S3,Summary,Questions,Proposal,Decide,ReadGuide,Mkdir,WritePlans,Component,Citation,FixPlan,Present,MinorFix phase
```

## Key invariants

- **Hard stop at Step 3.** The skill never invokes implementation — surfaces plan paths and exits.
- **One round of clarifying questions** in Step 1. No trickling questions across turns.
- **Manifest backfill check** in Step 1 — existing `feature-<slug>/` + `plan-01-*.md` + no `manifest.md` → manifest MUST be produced in Step 2.
- **Major rewrite loops back to Step 1**, not Step 2 — the proposal/scope needs to be re-agreed first.
