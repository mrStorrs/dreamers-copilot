# /dreamers-add-logging — flow

Visual map of the 5-phase logging audit + apply pipeline. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-add-logging [--scope path]"]) --> P1

    P1["Phase 1 — Audit"] --> Walk["Walk scope:<br/>default = source root<br/>or --scope path"]
    Walk --> Identify["Identify issues:<br/>missing DEBUG entry/exit<br/>branch coverage gaps<br/>ERROR without stack trace<br/>NEVER-LOG violations<br/>wrong-level usage<br/>high-freq DEBUG"]
    Identify --> Summary["Audit summary in chat:<br/>file path → issues"]
    Summary --> P2

    P2["Phase 2 — Proposal + approval"] --> Propose["Present in chat:<br/>files to modify<br/>net adds vs net changes<br/>logger conventions detected"]
    Propose --> ApprovalGate{"request_information"}
    ApprovalGate -->|Other freeform| Revise["Revise proposal"]
    Revise --> Propose
    ApprovalGate -->|Halt for now| HaltA(["Audit complete<br/>no changes applied<br/>resume by re-invoking"])
    ApprovalGate -->|Approved — apply changes| P3

    P3["Phase 3 — Implement"] --> Apply["Apply changes inline<br/>git add as you go<br/>only files in scope"]
    Apply --> TypeCheck["Run project's type-check<br/>fix type errors"]
    TypeCheck --> P4

    P4["Phase 4 — Optional Sentinel review"] --> ReviewGate{"request_information"}
    ReviewGate -->|Other| ReviewGate
    ReviewGate -->|No — skip review| P5
    ReviewGate -->|Yes — review before commit| SpawnSentinel["Spawn Sentinel<br/>scope = changed files<br/>writes review artifact"]
    SpawnSentinel --> ReadArtifact["Read Sentinel artifact"]
    ReadArtifact --> ApplyFindings["Apply findings inline<br/>comment-rules + logging-standards"]
    ApplyFindings --> P5

    P5["Phase 5 — Commit"] --> Status["git status"]
    Status --> Commit["git commit -m chore: improve logging<br/>per logging-standards.md"]
    Commit --> End(["Exit — do NOT push<br/>user pushes or runs /dreamers-pr"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class ApprovalGate,ReviewGate gate
    class HaltA halt
    class SpawnSentinel agent
    class P1,P2,P3,P4,P5,Walk,Identify,Summary,Propose,Revise,Apply,TypeCheck,ReadArtifact,ApplyFindings,Status,Commit phase
```

## Key invariants

- **Audit-first, edit later.** Phase 1 is pure analysis; no files are touched until Phase 3.
- **Halt is a valid exit.** A user can `Halt for now` after the audit and get the audit summary with zero changes applied.
- **NEVER-LOG violations are high priority.** Secrets, PII, and full request bodies in INFO logs surface first.
- **Logger conventions are detected, not invented.** Phase 2 surfaces the existing library/format so additions stay consistent.
- **No push.** This skill exits at the commit. Push is the user's call or `/dreamers-pr`'s job.
- **Review artifacts are read before fixes.** Optional Sentinel review writes `.dreamers/reviews/sentinel-*.md`; Phase 4 applies findings from that artifact.
