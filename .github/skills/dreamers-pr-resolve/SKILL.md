---
name: dreamers-pr-resolve
description: 'Attempt to resolve PR merge conflicts and unresolved review comments inline. Apply accepted fixes, run artifact-backed Vigil review, record deferred Vigil findings in project-root defered.md, reply to each comment with fixed / blocked / no-action, and resolve fixed threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback, resolve PR merge conflicts.'
argument-hint: '[<pr-number>] (auto-discovers from open PRs if omitted)'
---

Attempt to resolve merge conflicts and address unresolved review comments on the selected PR. Apply changes inline and use Vigil for artifact-backed review.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Select the PR and check mergeability
- [ ] Read unresolved review comments via GraphQL
- [ ] Attempt merge conflict resolution if needed
- [ ] Categorize comments (accept/reject decision + outcome per comment)
- [ ] Apply accepted fixes inline + validate all changes
- [ ] Spawn Vigil review of all changes
- [ ] Commit + approved push, reply to each comment, resolve fixed threads + report

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Discover open PRs

Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in `$ARGUMENTS`, use that one. If multiple are open and none is specified, call `request_information` with each open PR as a choice (format: `#NUM — <title>`) plus `"Other"` for freeform input. If exactly one is open, use it without prompting.

Confirm that the selected PR is open. Read its mergeability, base repository and branch, and head repository, branch, and commit from GitHub. For example, with `REPO` set to the base repository and `PR` set to the PR number:

```bash
gh pr view "$PR" --repo "$REPO" --json state,mergeable,baseRefName,headRefName,headRefOid,headRepository,headRepositoryOwner
```

If mergeability is `UNKNOWN`, retry the lookup briefly. Report a persistent unknown as unverified and continue with independent review comments. If GitHub reports `MERGEABLE`, skip the merge attempt even if the branch is behind the base.

## Step 2 — Pull unresolved review threads (GraphQL only)

For the target PR, use GraphQL to get only the unresolved threads (the REST API `resolved` field is unreliable — always use GraphQL):

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 100) { pageInfo { hasNextPage endCursor } nodes { isResolved id comments(first: 100) { pageInfo { hasNextPage endCursor } nodes { id url path body author { login } } } } } } } }'
```

Paginate both `reviewThreads` and each thread's `comments` using `after: endCursor` until `hasNextPage` is false. Extract only threads where `isResolved: false`. Capture each thread ID and every comment's ID, URL, path, body, and author. An empty thread list skips comment handling. When the list is empty and mergeability is `MERGEABLE`, report that there is no work and stop. For an unverified status, report that mergeability could not be determined before stopping. If the lookup fails or pagination is incomplete, report that failure and skip comment handling. Continue with a known merge conflict when the PR metadata is verified.

Read the full discussion. Handle every reviewer comment, including follow-ups; prior outcome replies are context, not new requests. Reuse an existing identical outcome reply when resuming; post an updated reply only if the outcome changed.

## Step 3 — Resolve merge conflicts, then decide accept / reject per comment (inline)

Before any merge or comment edits, use a clean checkout of the selected PR head branch with no Git operation in progress. Confirm the branch and commit against the PR head and identify the exact head repository and ref for the eventual push, including for a fork. If no safe checkout is available, report the blocker and leave existing work intact. Evaluate any retrieved comments without editing and use Step 7 in reply-only mode, with accepted fixes marked **blocked**.

If GitHub reports `CONFLICTING`, attempt the merge even when there are no unresolved threads:

1. Fetch the PR's actual base branch from the base repository. Merge the fetched commit into the PR head with `git merge --no-ff --no-commit <base-commit>`. Use the PR's base metadata even when the target branch differs from the default. Keep this as a merge so the existing PR commits can be pushed normally. If Git reports the base is already integrated and leaves no merge in progress, refresh GitHub status and report any discrepancy.
2. Inspect unmerged paths, resolve each conflict inline using both sides and the PR's intent, and stage the resolutions. Check that no unmerged entries or newly introduced conflict markers remain. If the correct resolution needs user input or the merge cannot be completed, report the affected paths and why. Abort only the merge started by this run with `git merge --abort`. Verify the original head and clean checkout were restored before continuing with independent review comments. If restoration fails, report the checkout state and continue only in reply-only mode.
3. Keep a successful merge pending while applying accepted comment fixes. Validate and review the combined result before committing or pushing. For the merge review, inspect the reconciled paths and compare the staged result with the pre-merge PR head and fetched base so intentional upstream changes and PR behavior can both be checked.

For review comments:

**HARD STOP — fix application is inline.** The orchestrator (this skill) edits files directly using Edit / Write / Bash tools to apply accepted PR-feedback fixes. **Do NOT spawn any subagent to write the fix code.** Specifically:
- ❌ `agent_type: "general-purpose"` → FORBIDDEN. There is no general-purpose fallback for implementation.
- ❌ `agent_type: "claude"` or any other host-runtime agent → FORBIDDEN.
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `dreamers-kernel.md` § "Subagent allowlist").
- ✅ The only `agent_type` value you may spawn from this skill is `vigil` in Step 5 (review of the applied fixes). Nothing else.

For each reviewer comment in an unresolved thread, judge whether to accept or reject it. You are the implementation expert and have full authority. **Do not feel obligated to accept every comment** — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

For each comment, record:
- Thread ID + comment ID / URL
- Path + comment body (one-line summary)
- Decision: **accept** or **reject**
- Rationale: one sentence
- Final outcome: **fixed**, **blocked**, or **no-action**; fixing commit SHA or concrete reason (finalize after the checks below)

If **accept** → apply the fix inline (Edit the file). Stage with `git add`. Follow the comment + implementation discipline from `dreamers-kernel.md` and `comment-rules.md`.

If **reject** → no edit; outcome **no-action** with the reason we decided not to act.

If an accepted fix cannot be completed → outcome **blocked** with the reason. It should be fixed, but this run could not fix it. Continue independent fixes where possible. Acceptance alone never means **fixed**; that outcome requires validation, Vigil review, and a fixing commit available on the PR branch after push.

Before stopping because of an unfixable issue, failed validation, blocked Vigil review, or a held/failed push, use Step 7 in reply-only mode: reply **blocked** for each affected accepted comment and **no-action** for rejected comments; leave threads open. Report any reply API failure with the affected comment URLs; never claim an unposted reply succeeded.

## Step 4 — Validate local changes

If a merge is pending or any accepted fixes changed files:
- Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before proceeding.
- Run the project's test command. Fix any regressions inline. Up to 3 attempts.

If no merge is pending and no accepted fixes changed files, skip to Step 6. For an already-fixed comment, verify the existing PR commit, relevant validation, and prior required Vigil review before assigning **fixed**; otherwise report **blocked** pending verification.

## Step 5 — Vigil review of local changes

Run Vigil for the pending merge and accepted PR-feedback fixes. Scope the review to conflict resolutions, their integration with the PR and base, and files touched by accepted threads.

Use `agent_type: "vigil"`, `mode: "sync"` for the required review. Do not spawn Sentinel, Probe, or Hone from this skill; selected reviewer lanes belong to `/dreamers-review`.

Common prompt context for Vigil (subagent prompt rule — include verbatim):
- **Todo discipline:** "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `dreamers-kernel.md` § "Single-owner todo")
- Plan file: none (ad-hoc PR-feedback work, no plan binding) — mark plan-alignment summary as N/A
- Scope: list of conflict paths, if any, and files changed by accepted threads
- Branch + default branch names
- What the orchestrator has done: summarize the merge resolution and accepted comment fixes, and list passing checks.
- Risk notes: call out whether accepted fixes changed tests/test harnesses/AC-covered behavior/validation/regression-sensitive behavior, or introduced/reshaped abstractions/module boundaries/APIs/schemas/data models/persistence/dependencies/refactors.
- Review lenses: correctness, security, maintainability, test coverage, and simplicity. Treat the risk notes as focus areas, not as permission to skip the other lenses.
- Write exactly one `.dreamers/reviews/vigil-*.md` artifact.
- Return only status, counts, artifact path, blocked reason, and open questions.

Read the returned artifact before applying findings. Apply findings from the artifact inline per the shared /dreamers apply-findings rules:

1. Sort findings by severity.
2. Resolve conflicts per the rule (correctness/security > test-coverage > simplicity).
3. **Evaluate each finding against the Major-refactor finding gate** per `dreamers-review.md` § "Major-refactor finding gate." If ANY criterion fires for a finding (new module / schema change / cross-cutting refactor / new exported symbols / files outside the PR-feedback surface / Vigil full-refactor scope language), call `request_information` with the 3-choice template (`Apply now — refactor in this cycle` / `Defer — save to defered.md` / `Other`) and route per the user's answer. On `Defer`, do NOT apply the finding or create a follow-up plan. Append a Markdown entry to `defered.md` in the project root; create it with `# Deferred Suggestions` if absent, and never overwrite existing entries. Record the date, PR + branch, Vigil artifact path, severity / lens / location, finding, suggested fix, triggered criterion, and deferral rationale. Stage `defered.md` and surface its path.
4. Apply each (non-deferred) fix inline; stage with `git add`.
5. Re-run type-check + tests; fix regressions inline (up to 3 attempts).

Handle non-finding outputs:
- The artifact reports `Blocked` → halt; surface the artifact path and reason; resolve; re-spawn Vigil.
- Open questions in the artifact → present to user before proceeding.
- The artifact reports `Approved — no findings` → proceed to Step 6 directly.

## Step 6 — Commit local changes and approve push

If a merge is pending, commit it after validation and review, including accepted comment fixes and any deferred entries staged for this run. Use a descriptive merge subject. If any fixes landed or Step 5 added deferred entries and there is no pending merge:

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit for this run and include the Dreamers co-author trailer.

If there is no new commit to push, skip the push gate and proceed to Step 7.

**Do not push yet.** Call `request_information` with `["Push to PR", "Hold — don't push yet", "Other"]` and summarize the local commit (hash, files touched, accepted thread count, and merge conflict outcome). Post-PR changes always require explicit user approval before pushing.

Only push after explicit `Push to PR` approval. Reread the PR and confirm it is still open and its base repository and branch and head repository, branch, and SHA match the starting metadata. Then push normally to the verified head repository and ref. If the PR changed or the push fails, preserve the local commit, report the blockage, and use Step 7 in reply-only mode. After a successful merge push, recheck the PR head and mergeability. Retry a briefly unknown status and report conflicts as cleared only when GitHub confirms the new head is mergeable. On `Hold` → use Step 7 in reply-only mode with **blocked** reasons stating that the fix is committed locally but awaiting push approval, then stop; the commit stays on the branch for the user to push manually. A held or failed push never earns a **fixed** reply.

## Step 7 — Reply to each comment, then resolve fixed threads

Skip this step when there are no handled review comments. Otherwise, post a reply in the original GitHub review thread for every handled reviewer comment, including when all comments are rejected or blocked. Use exactly one of these outcome lines:

- `fixed: in commit <SHA>` — the fix passed validation and required Vigil review, and the referenced commit is available on the remote PR branch. Use the actual fixing commit SHA, never a placeholder or an unpushed local commit.
- `blocked: <reason>` — the issue should be fixed, but we were unable to complete it. State the concrete obstacle and any remaining work.
- `no-action: <reason>` — we decided not to take action. Explain that decision; do not use this for an accepted issue we could not fix.

Use GraphQL variables for the reply body so quotes and newlines remain data:

```bash
gh api graphql -f query='mutation($thread: ID!, $body: String!) { addPullRequestReviewThreadReply(input: { pullRequestReviewThreadId: $thread, body: $body }) { comment { id url } } }' -f thread="$THREAD_ID" -f body="$REPLY_BODY"
```

When a thread contains multiple reviewer comments, post a separate outcome reply for each and append its source comment URL on a separate line. Confirm each reply succeeded and record its URL before resolving anything. On API failure, leave the affected thread open and report the failure.

Resolve a thread only when every handled reviewer comment in it is **fixed** and every required reply succeeded. In reply-only mode, do not resolve any threads.

```bash
gh api graphql -f query='mutation { resolveReviewThread(input: { threadId: "THREAD_ID" }) { thread { isResolved } } }'
```

Leave threads with **blocked** or **no-action** outcomes open so the reviewer can see the remaining issue or decision.

## Step 8 — Report

Report to the user:
- Merge conflict outcome separately, including affected paths, local or pushed status, and any blockage or unverified GitHub state
- Counts of **fixed**, **blocked**, and **no-action** comments, with path + fixing SHA or reason per comment
- Posted reply URLs and any reply failures
- Deferred Vigil findings recorded in `defered.md` (one line each)
- Threads resolved and remaining open, including blocked and no-action outcomes
- Commit hash + push status
- Vigil artifact path and result

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.
