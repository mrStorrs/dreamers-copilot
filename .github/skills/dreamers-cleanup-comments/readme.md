# /dreamers-cleanup-comments — flow

Visual map of the project-wide comment cleanup. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-cleanup-comments [--scope path]"]) --> P1

    P1["Phase 1 — Audit"] --> Walk["Walk scope:<br/>default = source root<br/>or --scope path"]
    Walk --> Categorize["Categorize comment-rules violations:<br/>Redundant<br/>Separator<br/>Reference (plan/ticket/agent)<br/>Spec-rationalization<br/>Redundant docstring<br/>Excessive length (> 2 lines)"]
    Categorize --> CountReport["Count per category<br/>+ worst-offender paths"]
    CountReport --> P2

    P2["Phase 2 — Proposal + approval"] --> Propose["Present in chat:<br/>total removals<br/>per-category summary<br/>most-affected files"]
    Propose --> ApprovalGate{"request_information"}
    ApprovalGate -->|"Other freeform<br/>e.g. preserve license headers"| Revise["Revise proposal"]
    Revise --> Propose
    ApprovalGate -->|Halt for now| HaltA(["Audit complete<br/>no changes applied"])
    ApprovalGate -->|Approved — apply cleanup| P3

    P3["Phase 3 — Apply"] --> Apply["Edit files inline<br/>git add as you go<br/>only files in scope"]
    Apply --> TypeCheck["Run project's type-check<br/>comments shouldn't affect it<br/>but verify"]
    TypeCheck --> P4

    P4["Phase 4 — Optional Sentinel review"] --> ReviewGate{"request_information"}
    ReviewGate -->|Other| ReviewGate
    ReviewGate -->|No — skip review| P5
    ReviewGate -->|Yes — review before commit| SpawnSentinel["Spawn Sentinel<br/>scope = changed files<br/>maintainability lens"]
    SpawnSentinel --> ApplyFindings["Apply findings inline"]
    ApplyFindings --> P5

    P5["Phase 5 — Commit"] --> Status["git status"]
    Status --> Commit["git commit -m chore: comment cleanup<br/>per comment-rules.md"]
    Commit --> End(["Exit — do NOT push"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class ApprovalGate,ReviewGate gate
    class HaltA halt
    class SpawnSentinel agent
    class P1,P2,P3,P4,P5,Walk,Categorize,CountReport,Propose,Revise,Apply,TypeCheck,ApplyFindings,Status,Commit phase
```

## Key invariants

- **Audit-first.** Phase 1 only categorizes — no edits until Phase 3.
- **Categories are the worst offenders the audit looks for** — separator comments, plan/ticket references, redundant docstrings, spec-rationalization comments.
- **License headers and TODO/FIXME are preserved** by default; users can refine via `Other` (e.g., "preserve vendor headers").
- **No logic edits.** Phase 3 touches comments only — no while-I'm-here code refactors.
- **No push.** Exits at commit.

For branch-scoped cleanup (only files in the current feature-branch diff), use `/dreamers-cleanup-comments-branch`.
