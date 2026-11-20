# /dreamers-pr-resolve — flow

How the skill attempts to resolve PR merge conflicts and addresses review comments. See [SKILL.md](SKILL.md) for the full workflow.

```mermaid
flowchart TD
    Start(["/dreamers-pr-resolve #PR"]) --> S1["Step 1 · Select an open PR and check mergeability"]
    S1 --> S2["Step 2 · Fetch unresolved review threads via GraphQL"]
    S2 --> Work{"Known conflicts or<br/>review comments to handle?"}
    Work -->|No| Report
    Work -->|Yes| Checkout{"Clean checkout of the<br/>verified PR head?"}
    Checkout -->|No| BlockedReplies
    Checkout -->|Yes| Conflicts{"GitHub reports conflicts?"}

    Conflicts -->|No| Comments
    Conflicts -->|Yes| Merge["Step 3 · Fetch and merge the PR's actual base.<br/>Resolve conflicts inline."]
    Merge --> MergeResult{"Merge ready for validation?"}
    MergeResult -->|Yes| Comments
    MergeResult -->|No| Abort["Report the obstacle.<br/>Abort the merge if this run started it."]
    Abort --> Restored{"Checkout safe to continue?"}
    Restored -->|Yes| Comments
    Restored -->|No| BlockedReplies
    Comments["Evaluate any retrieved review comments<br/>and apply accepted fixes inline."] --> Changes{"Pending merge or<br/>local fixes?"}
    Changes -->|No| Replies
    Changes -->|Yes| Tests["Step 4 · Run type checks and tests"]
    Tests -->|Failed| BlockedReplies
    Tests -->|Passed| Review["Step 5 · Run Vigil review"]
    Review -->|Blocked| BlockedReplies
    Review -->|Approved or findings addressed| Commit["Step 6 · Commit validated changes"]

    Commit --> PushGate{"Push approved?"}
    PushGate -->|No| BlockedReplies
    PushGate -->|Yes| Push["Recheck PR refs and push to the verified head.<br/>Confirm mergeability after a merge push."]
    Push -->|Push failed or PR changed| BlockedReplies
    Push -->|Pushed| Replies
    BlockedReplies["Step 7 · Reply-only mode when comments exist.<br/>Leave threads open."] --> Report
    Replies["Step 7 · Reply when comments exist.<br/>Resolve only fully fixed threads."] --> Report
    Report(["Step 8 · Report conflict status and review outcomes"])

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class Work,Checkout,Conflicts,MergeResult,Restored,Changes,PushGate gate
    class Review agent
    class S1,S2,Merge,Abort,Comments,Tests,Commit,Push,Replies,BlockedReplies,Report phase
```

## Key invariants

- **Merge conflicts can be handled independently.** If review threads are empty or unavailable, a known conflict still gets an attempt. Report an unavailable thread lookup or unverified mergeability.
- **Merge the PR's actual base into its verified head.** Abort an unresolved merge started during this run. After a push, report conflicts as cleared once GitHub confirms mergeability.
- **Use GraphQL for unresolved threads.** Paginate threads and comments and read the full discussion.
- **Reject is OK.** Don't feel obligated to accept every comment. If a suggestion conflicts with the plan, architecture, or is simply wrong, reject with rationale.
- **Every handled reviewer comment gets a GitHub reply:** `fixed: in commit <SHA>`, `blocked: <reason>`, or `no-action: <reason>`. Identify the source comment when replying to multiple comments in one thread; reuse identical replies on resume.
- **Fixed requires delivery.** Validate and review the fix, then reference its actual commit on the remote PR branch. Never claim an unpushed local fix is fixed.
- **Blocked means needed but unable to fix.** State the obstacle; reply before halting, including failed validation, blocked review, or held/failed pushes.
- **No-action means decided not to act.** State why; do not use it for an accepted issue that could not be fixed.
- **Only fully fixed threads resolve.** Every comment must be fixed and every reply successful. Blocked, no-action, and reply failures leave threads open.
- **Vigil reviews pending merges and accepted fixes.** Include conflict paths and relevant coverage or architecture risks in the review, then read the artifact before applying findings.
- **Deferred Vigil findings persist.** Append them to project-root `defered.md` without overwriting prior entries; do not create follow-up plans automatically.
- **Push requires explicit approval.** Post-PR changes never auto-push.
- **Hold is a valid exit** — the commit stays on the branch for the user to push manually later.
