# /dreamers-lite

Deliver a task without creating a plan. Source of truth: `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-lite $ARGUMENTS"]) --> Task{"Task provided?"}
    Task -->|No| Halt(["Halt + report"])
    Task -->|Yes| Branch["Create fresh fix/slug branch"]
    Branch --> Scope["Inspect scope<br/>raise ambiguities or critiques"]
    Scope --> Implement["/dreamers-implement<br/>task + agreed scope"]
    Implement --> Tests{"Validation green<br/>within 3 fix attempts?"}
    Tests -->|No| Halt
    Tests -->|Yes| Review["/dreamers-review --vigil --branch"]
    Review --> Result{"Review result?"}
    Result -->|Blocked| Halt
    Result -->|Approved| Docs["/dreamers-docs --staged<br/>include uncommitted changes"]
    Result -->|Findings| Major{"Major refactor?"}
    Major -->|No| Cap{"Fewer than 2<br/>review fix cycles?"}
    Major -->|Yes| Choice{"User direction"}
    Choice -->|Apply| Cap
    Choice -->|Defer| Deferred["Append root defered.md"]
    Choice -->|Other| Direction["Follow user direction"]
    Deferred --> Remaining{"Actionable findings remain?"}
    Remaining -->|Yes| Cap
    Remaining -->|No| Docs
    Cap -->|No| Halt
    Cap -->|Yes| Fix["Pass findings to /dreamers-implement<br/>apply fixes + validate"]
    Fix --> Tests
    Docs --> Commit["Stage explicit paths<br/>commit changes"]
    Commit --> Approval{"PR approved?"}
    Approval -->|Halt| Halt
    Approval -->|Other| Direction
    Approval -->|Approved| PR["/dreamers-pr"]
    PR --> Done(["Return PR URL"])

    classDef skill fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    class Implement,Review,Fix,Docs,PR skill
    class Task,Tests,Result,Major,Choice,Remaining,Cap,Approval gate
    class Halt halt
    class Branch,Scope,Deferred,Direction,Commit phase
```

1. Create a fresh `fix/<slug>` branch. Inspect the task and raise ambiguities or critiques.
2. Pass the task and agreed scope to `/dreamers-implement`; it implements, type-checks, and tests.
3. Run `/dreamers-review --vigil --branch <task>`. Apply findings through at most 2 implementation/review fix cycles. Ask before major refactors and record deferred findings in `defered.md`. Halt on blocked review or unresolved findings at the cap.
4. Update docs with `/dreamers-docs --staged`, which includes uncommitted changes. Commit explicit paths, present the summary for approval, then invoke `/dreamers-pr` and return its URL.

Implementation validation halts after 3 failed fix attempts. User instructions can override commit or PR steps.
