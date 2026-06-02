# /dreamers-cleanup-comments-branch — flow

Visual map of the branch-scoped comment cleanup variant. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-cleanup-comments-branch"]) --> Detect

    Detect["Scope detection"] --> ResolveDefault["Resolve default branch:<br/>git symbolic-ref + gh fallback"]
    ResolveDefault --> Fetch["git fetch origin"]
    Fetch --> RevParse{"Can resolve<br/>origin/$DEFAULT?"}
    RevParse -->|No| HaltStale(["Halt — could not resolve<br/>origin/$DEFAULT<br/>check remote config"])
    RevParse -->|Yes| BranchCheck{"On default<br/>branch?"}
    BranchCheck -->|Yes| HaltOnDefault(["Halt — needs feature branch<br/>use /dreamers-cleanup-comments<br/>for project-wide"])
    BranchCheck -->|No, on feature branch| ComputeDiff["scope = git diff<br/>origin/$DEFAULT...HEAD --name-only"]
    ComputeDiff --> P1

    P1["Phase 1 — Audit (branch-diff scope)"] --> Categorize["Categorize violations:<br/>Redundant / Separator /<br/>Reference / Spec-rationalization /<br/>Redundant docstring /<br/>Excessive length"]
    Categorize --> CountReport["Count per category<br/>+ worst offenders"]
    CountReport --> P2

    P2["Phase 2 — Proposal + approval"] --> Propose["Present in chat"]
    Propose --> ApprovalGate{"request_information"}
    ApprovalGate -->|Other| Revise["Revise proposal"]
    Revise --> Propose
    ApprovalGate -->|Halt for now| HaltA(["Audit complete<br/>no changes applied"])
    ApprovalGate -->|Approved| P3

    P3["Phase 3 — Apply"] --> Apply["Edit files inline<br/>git add as you go"]
    Apply --> TypeCheck["Run project's type-check"]
    TypeCheck --> P4

    P4["Phase 4 — Optional Vigil review"] --> ReviewGate{"request_information"}
    ReviewGate -->|Other| ReviewGate
    ReviewGate -->|No — skip| P5
    ReviewGate -->|Yes — review| SpawnVigil["Spawn Vigil<br/>scope = changed files<br/>writes review artifact"]
    SpawnVigil --> ReadArtifact["Read Vigil artifact"]
    ReadArtifact --> ApplyFindings["Apply findings inline"]
    ApplyFindings --> P5

    P5["Phase 5 — Commit"] --> Commit["git commit -m<br/>chore: comment cleanup on feature branch"]
    Commit --> End(["Exit — do NOT push<br/>follow with /dreamers-pr"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class RevParse,BranchCheck,ApprovalGate,ReviewGate gate
    class HaltStale,HaltOnDefault,HaltA halt
    class SpawnVigil agent
    class Detect,P1,P2,P3,P4,P5,ResolveDefault,Fetch,ComputeDiff,Categorize,CountReport,Propose,Revise,Apply,TypeCheck,ReadArtifact,ApplyFindings,Commit phase
```

## Key invariants

- **Branch-only scope.** Files come from `git diff origin/$DEFAULT...HEAD --name-only` — nothing outside the branch diff is touched.
- **Refuses to run on the default branch.** Halt with a redirect to `/dreamers-cleanup-comments` for project-wide sweeps.
- **Fetch before diff.** Stale `origin/$DEFAULT` produces wrong scope — always fetch first.
- **Same phases as the project-wide variant** — only the scope source differs.
- **Review artifacts are read before fixes.** Optional Vigil review writes `.dreamers/reviews/vigil-*.md`; Phase 4 applies findings from that artifact.
- **Pre-PR positioning.** Designed to run before opening a PR; commit stays on branch for `/dreamers-pr` to push.
