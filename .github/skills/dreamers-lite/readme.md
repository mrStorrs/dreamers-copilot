# /dreamers-lite

Deliver a task without creating a plan. Delivery order: `SKILL.md`. Shared phase mechanics: XML-synced workflow blocks embedded in this skill, with all required standards. No skill calls or runtime ref-file reads.

The Required workflow checklist drives setup, the implementation/test/review loop, conditional user testing, docs, and close-out. Implementation, review, documentation, and publishing bodies sit directly in their corresponding sections. This skill supplies their inputs and owns the todo, review loop, approval, and final exit. Shared rules and formats are grouped once at the end.

```mermaid
flowchart TD
    Start(["/dreamers-lite $ARGUMENTS"]) --> Task{"Task provided?"}
    Task -->|No| Halt(["Halt + report"])
    Task -->|Yes| Branch["Create fresh fix/slug branch"]
    Branch --> Scope["Inspect scope<br/>raise ambiguities or critiques"]
    Scope --> Implement["Embedded implementation workflow<br/>task + agreed scope"]
    Implement --> Tests{"Available checks pass<br/>within 3 fix attempts?"}
    Tests -->|No| Halt
    Tests -->|Yes| Review["Embedded review workflow --vigil<br/>branch initially; uncommitted fixes after testing/PR"]
    Review --> Result{"Review result?"}
    Result -->|Blocked| Halt
    Result -->|Approved| UserTesting{"User verification still needed?"}
    UserTesting -->|No| Docs["Embedded documentation workflow --staged<br/>include uncommitted changes"]
    UserTesting -->|Yes| TestGate{"Targeted user-testing gate"}
    TestGate -->|Approved| Docs
    TestGate -->|Bug found| Implement
    TestGate -->|Other| Direction
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
    Cap -->|Yes| Implement
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
    Approval -->|Approved| PR["Embedded pr workflow"]
    PR --> Done(["Return PR URL"])
    Done -.->|Related bug or correction| Implement

    classDef workflow fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    class Implement,Review,Docs,PR workflow
    class Task,Tests,Result,Major,Choice,Remaining,Cap,UserTesting,TestGate,Existing,UpdateApproval,Approval gate
    class Halt halt
    class Branch,Scope,Deferred,Direction,Commit,Update phase
```

1. Create a fresh `fix/<slug>` branch. Inspect the task and raise ambiguities or critiques.
2. Pass the task and agreed scope to `implementation-workflow.md`; execute it inline to implement, type-check, and test.
3. Run `review-workflow.md` with `--vigil --branch` and the task context (no plan binding). Apply findings through at most 2 implementation/review fix cycles. Ask before major refactors and record deferred findings in `defered.md`. Halt on blocked review or unresolved findings at the cap.
4. Perform available automated and agent-operated verification. Ask the user only for remaining checks you cannot complete or explicit personal testing. Bugs return to step 1 of Implement and review loop, retaining the active cap.
5. Update docs with `documentation-workflow.md --staged`, which includes uncommitted changes. Commit explicit paths, present the summary for approval, then execute the embedded PR block and return its URL.

Questions leave the next phase pending; resume after answering unless the user requests discussion, pauses, or changes direction. Related bug reports resume the existing `Implement and review loop` at step 1; do not invoke the delivery skill again. For an open PR, reuse its branch and repeat implementation/tests, capped Vigil review, user testing only when needed, and docs; ask approval before committing and pushing the update.

Keep one delivery todo aligned with confirmed results, reopening affected stages after changes and reconciling stale entries after detours. New corrections after completed close-out start a new capped cycle; detours within a cycle keep its review count.

Implementation validation halts after 3 failed fix attempts. User instructions can override commit or PR steps.
