# /dreamers-lite - flow

Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-lite task"]) --> Context["Read project context"]
    Context --> Questions{"Clarification needed?"}
    Questions -->|Yes| Ask["Ask one batch"]
    Questions -->|No| Proposal
    Ask --> Proposal["Proposal + critique"]
    Proposal --> Approval{"Approved?"}
    Approval -->|Revise| Proposal
    Approval -->|Halt| Halt(["Halt"])
    Approval -->|Approved| Plan["Write compact plan file"]
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
- Vigil writes one `.dreamers/reviews/` artifact; chat output stays short.
- Full-refactor findings are always surfaced. User may apply, defer, or continue lite scope.
- No pre-PR approval gate.
