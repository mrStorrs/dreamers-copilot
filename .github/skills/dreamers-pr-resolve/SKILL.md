---
name: dreamers-pr-resolve
description: "Apply justified PR feedback, verify it, run Vigil, then push with approval and resolve accepted threads."
argument-hint: "[pr-number]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Use the supplied PR, otherwise discover open PRs and ask if ambiguous. Query reviewThreads through gh api graphql; paginate all threads and comments. Collect unresolved thread IDs, paths, full discussion, and intended changes.
2. Accept or reject each suggestion with a reason. Apply accepted fixes inline within the feedback scope; leave rejected threads open. Run [verification](../../dreamers/refs/testing-mandate.md) after changes.
3. If fixes were applied, invoke /dreamers-review on the accepted-change diff with the feedback as intent and validation results. Vigil is the default. Read the artifact and follow [apply findings](../../dreamers/refs/apply-findings.md), including scope gates and deferred entries.
4. Commit accepted fixes and any deferred entries once. Present hash, scope, validation, and review result for the existing push gate: Push to PR, Hold, or freeform direction. Hold stops with the local commit intact.
5. After an approved successful push, resolve only accepted threads whose fix is present on the PR using the GraphQL resolveReviewThread mutation. If nothing changed, resolve only threads demonstrably already satisfied.
6. Report accepted/rejected decisions, remaining threads, review artifact, deferrals, commit, and push status. Do not change the PR description, close the PR, or re-request review.
