# /dreamers-lite - flow

Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-lite $ARGUMENTS"]) --> ModeCheck{"$ARGUMENTS<br/>type?"}
    ModeCheck -->|Task description| Context["Read project context"]
    ModeCheck -->|Plan path(s)| ExistingPlan["Resolve supplied plan file(s)"]
    Context --> GrillChoice{"Would you like me<br/>to grill you on the plan?"}
    GrillChoice -->|Yes| Grill["Phase 1A Grill<br/>one request_information question at a time"]
    Grill --> Questions{"Clarification needed?"}
    GrillChoice -->|No / Other| Questions{"Clarification needed?"}
    Questions -->|Yes| Ask["Ask one batch"]
    Questions -->|No| Proposal
    Ask --> Proposal["Proposal + critique"]
    Proposal --> Approval{"Approved?"}
    Approval -->|Revise| Proposal
    Approval -->|Halt| Halt(["Halt"])
    Approval -->|Approved| Plan["Write compact plan file"]
    ExistingPlan --> Branch
    Plan --> Branch["Fresh feat branch"]
    Branch --> Cycle["Tests -> implement -> validate"]
    Cycle --> Vigil["Spawn Vigil"]
    Vigil --> Artifact["Read review artifact"]
    Artifact --> Findings{"Findings?"}
    Findings -->|Apply/defer/continue| Fix["Apply selected fixes + validate"]
    Findings -->|Blocked| Halt
    Fix --> UserTest{"User test trigger?"}
    UserTest -->|Yes| Gate["User testing gate"]
    Gate -->|Bug| Fix
    UserTest -->|No| Docs
    Gate -->|Approved| Docs{"Docs trigger?"}
    Docs -->|Yes| Echo["/dreamers-docs --branch"]
    Docs -->|No| Commit["Commit"]
    Echo --> Commit
    Commit --> PR["/dreamers-pr"]
```

## Invariants

- One approval gate covers plan approval and implementation start.
- Task mode asks whether to run optional Grill before the compact proposal. If accepted, Grill uses the shared one-question-at-a-time planning phase.
- Plan path mode skips planning, plan writing, and implementation-start approval; supplied plan files are used directly after path and structure checks.
- Vigil writes one `.dreamers/reviews/` artifact; chat output stays short.
- Full-refactor findings are always surfaced. User may apply, defer, or continue lite scope.
- No pre-PR approval gate.
