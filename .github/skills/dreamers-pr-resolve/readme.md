# /dreamers-pr-resolve — flow

Visual map of the merge conflict and review resolution workflow. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-pr-resolve $ARGUMENTS"]) --> S1

    S1["Step 1 — Select an open PR and check mergeability"] --> PRCheck{"PR target?"}
    PRCheck -->|$ARGUMENTS specified| UseSpecified["Use specified PR"]
    PRCheck -->|"Multiple open<br/>none specified"| PickPR["request_information<br/>list open PRs + Other"]
    PRCheck -->|Exactly one open| UseOne["Use it without prompting"]
    PickPR --> UseSpecified
    UseSpecified --> S2
    UseOne --> S2

    S2["Step 2 — Pull unresolved threads<br/>via GraphQL only"] --> Query["gh api graphql<br/>filter isResolved: false"]
    Query --> Conflicts{"Merge conflicts?"}
    Conflicts -->|Yes| Merge["Attempt to resolve conflicts"]
    Conflicts -->|No| HasThreads{"Unresolved<br/>threads?"}
    HasThreads -->|None| EarlyExit(["Report + stop"])
    HasThreads -->|Yes| S3
    Merge -->|Resolved| S3
    Merge -->|Blocked, checkout restored| S3
    Merge -->|Unsafe checkout| BlockedReplies

    S3["Step 3 — Decide accept / reject for any comments"] --> PerThread["For each reviewer comment:<br/>record decision + rationale<br/>track fixed / blocked / no-action"]
    PerThread --> AcceptedAny{"Pending merge or<br/>local fixes?"}
    AcceptedAny -->|No| S6
    AcceptedAny -->|Yes| ApplyFixes["Stage accepted fixes<br/>and conflict resolutions"]
    ApplyFixes --> S4

    S4["Step 4 — Type-check + run tests"] --> TestResult{"Tests pass<br/>within 3 attempts?"}
    TestResult -->|No| BlockedReplies["Step 7 — Reply-only mode<br/>blocked: reason for affected fixes<br/>no-action: reason for rejections<br/>leave threads open"]
    TestResult -->|Yes| S5

    S5["Step 5 — Vigil review"] --> SpawnVigil["Spawn Vigil<br/>write review artifact"]
    SpawnVigil --> ReadArtifacts["Read Vigil artifact"]
    ReadArtifacts --> ReviewResult{"Reviewer<br/>statuses?"}
    ReviewResult -->|Blocked| BlockedReplies
    ReviewResult -->|Findings| ApplyReviewer["Apply or defer Vigil findings<br/>deferred → append root defered.md<br/>re-run tests after applied findings"]
    ReviewResult -->|Approved no findings| S6
    ApplyReviewer --> S6

    S6["Step 6 — Commit a resolved merge or accepted fixes"] --> NewCommit{"New commit<br/>to push?"}
    NewCommit -->|No| S7
    NewCommit -->|Yes| CommitFixes["Commit local changes"]
    CommitFixes --> PushGate{"Push gate"}
    PushGate -->|Hold| BlockedReplies
    PushGate -->|Push to PR| Push["Recheck PR refs for a merge.<br/>Push to the PR head."]
    PushGate -->|Other| PushGate
    Push --> PushResult{"Push succeeded?"}
    PushResult -->|Yes| S7
    PushResult -->|No| BlockedReplies
    BlockedReplies --> HaltA(["Report obstacle + stop<br/>retain local commit on Hold"])

    S7["Step 7 — Reply to any handled comments<br/>fixed: in commit SHA<br/>blocked: reason<br/>no-action: reason"] --> ResolveGQL["Resolve only threads where<br/>every comment is fixed<br/>and every reply succeeded"]
    ResolveGQL --> S8

    S8["Step 8 — Report"] --> End(["merge outcome + GitHub mergeability after push<br/>fixed / blocked / no-action counts<br/>fixing SHAs or reasons + reply URLs<br/>commit hash + push status<br/>reviewer results + open threads"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef halt fill:#7f1d1d,stroke:#991b1b,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class PRCheck,Conflicts,HasThreads,AcceptedAny,TestResult,ReviewResult,NewCommit,PushGate,PushResult gate
    class HaltA halt
    class SpawnVigil agent
    class S1,S2,S3,S4,S5,S6,S7,S8,UseSpecified,PickPR,UseOne,Query,Merge,PerThread,ApplyFixes,ReadArtifacts,ApplyReviewer,CommitFixes,Push,ResolveGQL,BlockedReplies phase
```

## Key invariants

- **GraphQL only** for unresolved-thread discovery. Paginate threads and comments; read the full discussion.
- **Reject is OK.** Don't feel obligated to accept every comment. If a suggestion conflicts with the plan, architecture, or is simply wrong, reject with rationale.
- **Every handled reviewer comment gets a GitHub reply:** `fixed: in commit <SHA>`, `blocked: <reason>`, or `no-action: <reason>`. Identify the source comment when replying to multiple comments in one thread; reuse identical replies on resume.
- **Fixed requires delivery.** Validate and review the fix, then reference its actual commit on the remote PR branch. Never claim an unpushed local fix is fixed.
- **Blocked means needed but unable to fix.** State the obstacle; reply before halting, including failed validation, blocked review, or held/failed pushes.
- **No-action means decided not to act.** State why; do not use it for an accepted issue that could not be fixed.
- **Only fully fixed threads resolve.** Every comment must be fixed and every reply successful. Blocked, no-action, and reply failures leave threads open.
- **Vigil is required for conflict resolutions and accepted fixes.** Keep PR-feedback review to one artifact-backed Vigil pass. Pass coverage/regression or architecture/refactor risk notes into Vigil's prompt, then read the artifact before applying findings.
- **Deferred Vigil findings persist.** Append them to project-root `defered.md` without overwriting prior entries; do not create follow-up plans automatically.
- **Push requires explicit approval.** Post-PR changes never auto-push.
- **Hold is a valid exit** — the commit stays on the branch for the user to push manually later.
