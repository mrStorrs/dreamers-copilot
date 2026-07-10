# /dreamers-plan — flow

Visual map of the 3-phase planning conversation. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-plan $ARGUMENTS"]) --> ArgCheck{"Task description<br/>provided?"}
    ArgCheck -->|No| HaltA(["Halt + ask"])
    ArgCheck -->|Yes| OptOut{"Explicit Grill<br/>opt-out?"}
    OptOut -->|No| S1
    OptOut -->|Yes| Skip["Strip control syntax<br/>record skip reason"]
    Skip --> S1

    S1["Step 1 — Hash out"] --> Summary["Write 1-paragraph<br/>understanding summary"]
    Summary --> GrillChoice{"Grill enabled?"}
    GrillChoice -->|Yes| Grill["Phase 1A — Grill<br/>one request_information question at a time"]
    GrillChoice -->|No| Draft
    Grill --> Shared{"Shared<br/>understanding?"}
    Shared -->|No| Grill
    Shared -->|Yes| Draft["Phase 1B — Proposal review"]
    Draft --> ReviewPhase["Proposal review<br/>critique + user questions"]
    ReviewPhase --> ApprovalGate{"User response"}
    ApprovalGate -->|"Questions / challenges / corrections"| Answer["Fully review + answer<br/>update proposal + critique"]
    Answer --> ReviewPhase
    ApprovalGate -->|Approved| Decide["Select plan type<br/>user override wins<br/>decide manifest"]
    Decide --> S2

    S2["Step 2 — Write plans"] --> ReadGuide["Read selected guide only<br/>lite / standard / complex"]
    ReadGuide --> Mkdir["mkdir -p .dreamers/plans/feature-slug/"]
    Mkdir --> WritePlans["Write plan-NN-name.md<br/>with Plan-type metadata"]
    WritePlans --> Component["Component-usage check<br/>grep callers for shared components"]
    Component --> Citation["Citation accuracy<br/>verify every cited artifact exists"]
    Citation --> SelfCheck{"Self-check<br/>against guide?"}
    SelfCheck -->|Fail| FixPlan["Fix violations"]
    FixPlan --> SelfCheck
    SelfCheck -->|Pass| Coverage{"Coverage review<br/>proposal + user discussion?"}
    Coverage -->|Fail| FixCoverage["Fix missing / weak items"]
    FixCoverage --> Citation
    Coverage -->|Pass| S3

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

    class ArgCheck,OptOut,GrillChoice,Shared,ApprovalGate,SelfCheck,Coverage,Review gate
    class HaltA,HaltB halt
    class S1,S2,S3,Summary,Grill,Draft,ReviewPhase,Answer,Decide,ReadGuide,Mkdir,WritePlans,Component,Citation,FixPlan,FixCoverage,Present,MinorFix phase
```

## Key invariants

- **Hard stop at Step 3.** The skill never invokes implementation — surfaces plan paths and exits.
- **Phase 1A — Grill is default-on.** Skip it only for --no-grill or unmistakable natural-language direction such as "do not grill" or "skip the interview." Record the reason and strip control syntax. When Grill runs, ask one blocking question at a time through `request_information`; option 1 is the recommendation, option 2 is the strongest alternate, and option 3 is `Other`.
- **Proposal review is mandatory and interactive.** Approval is valid only after the proposal is stress-tested for pitfalls, weak spots, tradeoffs, hidden assumptions, likely failure modes, scope risks, and simpler counter-proposals. User questions, challenges, and partial answers are handled inside the same loop with substantive reasoning, implications, and a recommended next move.
- **Plan type is selected before writing.** User override wins; otherwise use the smallest guide that preserves quality: lite / standard / complex.
- **Plans are right-sized specs.** Each plan follows only its selected guide and includes enough detail that implementation does not infer missing design.
- **Plan coverage review is mandatory after writing.** Before Step 3, compare the written plan(s) against the approved proposal, proposal critique, and all user-discussed questions, corrections, decisions, and constraints. Fix any missing, ambiguous, contradicted, or weakened item before presenting paths.
- **Manifest backfill check** in Step 1 — existing `feature-<slug>/` + `plan-01-*.md` + no `manifest.md` → manifest MUST be produced in Step 2.
- **Major rewrite loops back to Step 1**, not Step 2 — the proposal/scope needs to be re-agreed first.
