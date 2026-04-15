---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments via Forge and Probe pipeline. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
---

Resolve unresolved PR review comments. Route: Forge → Probe → resolve threads.

Read these refs:
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

**Step 1 — Discover open PRs**
Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in the arguments, use that one. If multiple are open and none is specified, ask the user which PR to target before proceeding.

$ARGUMENTS

**Step 2 — Pull unresolved review threads**
For the target PR, use GraphQL to get only the unresolved threads (the REST API `resolved` field is unreliable — always use GraphQL):
```
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 50) { nodes { isResolved id comments(first: 1) { nodes { path body } } } } } } }'
```
Extract only threads where `isResolved: false`. If there are none, report that back to the user and stop.

**Step 3 — Invoke Forge**
Pass all unresolved threads to Forge (follow delegation.md) with this framing:
- Forge is the implementation expert and has full authority to accept or reject each comment.
- For each thread: decide accept or reject, implement if accepted, leave a brief rationale for each decision in `implementation.md`.
- Forge should not feel obligated to accept every comment — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

**Step 4 — Invoke Probe**
After Forge completes, route to Probe to verify that accepted changes pass tests and nothing regressed.

**Step 5 — Resolve comments (Bolt)**
After Probe passes, invoke **Bolt** to resolve each accepted thread via the GitHub API:
```
gh api graphql -f query='mutation { resolveReviewThread(input: { threadId: "THREAD_ID" }) { thread { isResolved } } }'
```
Pass Bolt the list of thread IDs to resolve (accepted comments only). Leave rejected threads open — they represent active disagreements the reviewer should see.

Bolt reports back: threads resolved. Then report to the user: how many comments were accepted, how many rejected, and which threads remain open (with a one-line reason per rejection).

