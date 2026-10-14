# /dreamers

Deliver tasks, approved plan paths, or a manifest. Source of truth: `SKILL.md`.

```mermaid
flowchart TD
    I["/dreamers input"] --> R{"Input kind?"}
    R -->|Empty or help| H["/dreamers-help"]
    H --> E(["Return guidance"])
    R -->|Task| P["/dreamers-plan"]
    P --> G{"Human plan review<br/>and start approval"}
    G -->|Revise| P
    G -->|Halt| Stop(["Halt + report"])
    G -->|Approved| A["Create feature branch"]
    R -->|Approved plans or manifest| A
    A --> T["/dreamers-implement<br/>implement + tests"]
    T --> V["/dreamers-review<br/>initial lane from plan or user direction"]
    T -->|Validation blocked| Stop
    V --> Result{"Review result?"}
    Result -->|Blocked| Stop
    Result -->|Actionable findings| Cap{"Fewer than 3<br/>review fix cycles?"}
    Cap -->|No| Stop
    Cap -->|Yes| X["Resolve major refactors with user<br/>apply fixes + validate"]
    X --> F["/dreamers-review --vigil"]
    X -->|Validation blocked| Stop
    F --> Result
    Result -->|Approved or findings deferred| U{"User testing triggered?"}
    U -->|Yes| UT["User-testing gate<br/>bug fixes + validation + review as needed"]
    U -->|No| More{"More plans?"}
    UT -->|Approved| More
    UT -->|Blocked or review cap reached| Stop
    More -->|Yes| Next["Check drift; commit plan<br/>INCREMENTAL: approved PR + merge<br/>ATOMIC: continue without pushing"]
    Next --> T
    More -->|No| D["/dreamers-docs<br/>commit remaining changes"]
    D --> Approval{"Final PR approved?"}
    Approval -->|Halt| Stop
    Approval -->|Approved| PR["/dreamers-pr"]
    PR --> Done(["Return PR URL"])
```

1. Empty/help input opens `/dreamers-help`. Task input invokes `/dreamers-plan`, then human plan review and start approval. Supplied plans/manifests are already implementation authorization.
2. Implement each plan with `/dreamers-implement`, then invoke `/dreamers-review`. Plan complexity selects the initial lane unless the plan or user specifies one.
3. Apply findings through at most 3 implementation/Vigil fix cycles. Ask before major refactors and record deferred findings in `defered.md`. Halt on blocked review or unresolved findings at the cap.
4. Complete triggered user testing. Between plans, check drift; ATOMIC commits and continues, while INCREMENTAL requests PR approval and waits for merge before continuing.
5. Update docs, commit remaining changes, request PR approval, and return the PR URL.

Reviewers only write review artifacts; the orchestrator applies fixes. Kernel, git workflow, and the user-testing gate are embedded through ref sync. User instructions can override workflow steps.
