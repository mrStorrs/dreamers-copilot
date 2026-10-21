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
    Tests -->|Yes| Review["/dreamers-review --vigil<br/>--branch initially; uncommitted diff for follow-ups"]
    Review --> Result{"Review result?"}
    Result -->|Blocked| Halt
    Result -->|Approved| UserTesting{"User testing required?"}
    Result -->|Findings| Major{"Major refactor?"}
    Major -->|No| Cap{"Fewer than 2<br/>review fix cycles?"}
    Major -->|Yes| Choice{"User direction"}
    Choice -->|Apply| Cap
    Choice -->|Defer| Deferred["Append root defered.md"]
    Choice -->|Other| Direction["Follow user direction"]
    Deferred --> Remaining{"Actionable findings remain?"}
    Remaining -->|Yes| Cap
    Remaining -->|No| UserTesting
    Cap -->|No| Halt
    Cap -->|Yes| Fix["/dreamers-implement<br/>findings or reported problem + task context"]
    Fix --> Tests
    UserTesting -->|No| Docs["/dreamers-docs --staged<br/>include uncommitted changes"]
    UserTesting -->|Yes| TestGate{"User-testing sign-off"}
    TestGate -->|Approved| Docs
    TestGate -->|Bug found| Cap
    TestGate -->|Other| Direction
    Docs --> Existing{"Updating an open PR?"}
    Existing -->|No| Commit["Stage explicit paths<br/>commit changes"]
    Existing -->|Yes| UpdateApproval{"Commit + push approved?"}
    UpdateApproval -->|Halt| Halt
    UpdateApproval -->|Other| Direction
    UpdateApproval -->|Approved| Update["Commit + push existing PR"]
    Update --> Done
    Commit --> Approval{"PR approved?"}
    Approval -->|Halt| Halt
    Approval -->|Other| Direction
    Approval -->|Approved| PR["/dreamers-pr"]
    PR --> Done(["Return PR URL"])
    Done -.->|Related bug or correction| Cap

    classDef skill fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    class Implement,Review,Fix,Docs,PR skill
    class Task,Tests,Result,Major,Choice,Remaining,Cap,UserTesting,TestGate,Existing,UpdateApproval,Approval gate
    class Halt halt
    class Branch,Scope,Deferred,Direction,Commit,Update phase
```

1. Create a fresh `fix/<slug>` branch. Inspect the task and raise ambiguities or critiques.
2. Pass the task and agreed scope to `/dreamers-implement`; it implements, type-checks, and tests.
3. Run `/dreamers-review --vigil --branch <task>`. Apply accepted findings through `/dreamers-implement`, then Vigil review, for at most 2 fix cycles. Ask before major refactors and record deferred findings in `defered.md`. Halt on blocked review or unresolved findings at the cap.
4. Complete any required user testing, then update docs with `/dreamers-docs --staged`, which includes uncommitted changes. Commit explicit paths, present the summary for approval, then invoke `/dreamers-pr` and return its URL.

`/dreamers-lite` invokes specialized phase skills only; it never invokes itself or `/dreamers` to continue delivery. Wrapped skills return control to the existing orchestrator without invoking either delivery skill. Questions leave the next phase pending; resume after answering unless the user requests discussion, pauses, or changes direction.

Related bug reports during user testing or after PR creation authorize fixes through `/dreamers-implement` with the current task/agreed scope, followed by capped Vigil review over staged + unstaged changes and any required user testing. For an open PR, reuse its branch and update docs from the uncommitted diff; ask approval before committing and pushing the update. Do not create a plan or repeat branch setup for that continuation.

Keep one delivery todo aligned with confirmed results, reopening affected stages after changes and reconciling stale entries after detours. New corrections after completed close-out start a new capped cycle; detours within a cycle keep its review count.

Implementation validation halts after 3 failed fix attempts. User instructions can override commit or PR steps.
