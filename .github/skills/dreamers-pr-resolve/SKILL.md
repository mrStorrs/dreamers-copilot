---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments inline. Apply accepted fixes, run artifact-backed Vigil review, record deferred Vigil findings in project-root defered.md, reply to each comment with fixed / blocked / no-action, and resolve fixed threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
argument-hint: '[<pr-number>] (auto-discovers from open PRs if omitted)'
---

Resolve unresolved PR review comments. All work inline except required artifact-backed Vigil review over accepted changes.

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

- Follow YAGNI principles when writing or planning code. Build only what current requirements need; defer speculative features, abstractions, and configuration.
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
- [ ] Read review comments (discover PR + pull unresolved threads via GraphQL)
- [ ] Categorize comments (accept/reject decision + outcome per comment)
- [ ] Apply accepted fixes inline + run tests
- [ ] Spawn Vigil review of accepted changes
- [ ] Commit + approved push, reply to each comment, resolve fixed threads + report

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Discover open PRs

Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in `$ARGUMENTS`, use that one. If multiple are open and none is specified, call `request_information` with each open PR as a choice (format: `#NUM — <title>`) plus `"Other"` for freeform input. If exactly one is open, use it without prompting.

## Step 2 — Pull unresolved review threads (GraphQL only)

For the target PR, use GraphQL to get only the unresolved threads (the REST API `resolved` field is unreliable — always use GraphQL):

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 100) { pageInfo { hasNextPage endCursor } nodes { isResolved id comments(first: 100) { pageInfo { hasNextPage endCursor } nodes { id url path body author { login } } } } } } } }'
```

Paginate both `reviewThreads` and each thread's `comments` using `after: endCursor` until `hasNextPage` is false. Extract only threads where `isResolved: false`. Capture each thread ID and every comment's ID, URL, path, body, and author. If there are no unresolved threads, report that back to the user and stop.

Read the full discussion. Handle every reviewer comment, including follow-ups; prior outcome replies are context, not new requests. Reuse an existing identical outcome reply when resuming; post an updated reply only if the outcome changed.

## Step 3 — Decide accept / reject per comment (inline)

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

## Step 4 — Run tests after accepted changes

If any accepted fixes changed files:
- Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before proceeding.
- Run the project's test command. Fix any regressions inline. Up to 3 attempts.

If no accepted fixes changed files, skip to Step 6. For an already-fixed comment, verify the existing PR commit, relevant validation, and prior required Vigil review before assigning **fixed**; otherwise report **blocked** pending verification.

## Step 5 — Vigil review of accepted changes

Run Vigil for accepted PR-feedback fixes. Scope is restricted to ONLY the files touched by accepted threads.

Use `agent_type: "vigil"`, `mode: "sync"` for the required review. Do not spawn Sentinel, Probe, or Hone from this skill; selected reviewer lanes belong to `/dreamers-review`.

Common prompt context for Vigil (subagent prompt rule — include verbatim):
- **Todo discipline:** "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `dreamers-kernel.md` § "Single-owner todo")
- Plan file: none (ad-hoc PR-feedback work, no plan binding) — mark plan-alignment summary as N/A
- Scope: list of files changed by accepted threads from `git status`
- Branch + default branch names
- What the orchestrator has done: addressed N accepted PR review comments via inline edits; type-checked + tests green.
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

## Step 6 — Commit accepted fixes (if any)

If any fixes landed or Step 5 added deferred entries (Step 3 accepted + Step 5 reviewer findings applied or recorded):

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit covering all the PR-feedback fixes.

If there is no new commit to push, skip the push gate and proceed to Step 7.

**Do not push yet.** Call `request_information` with `["Push to PR", "Hold — don't push yet", "Other"]` and a summary of the staged commit (hash, files touched, accepted thread count). Post-PR changes always require explicit user approval before pushing.

Only push after explicit `Push to PR` approval: `git push`. On `Hold` → use Step 7 in reply-only mode with **blocked** reasons stating that the fix is committed locally but awaiting push approval, then stop; the commit stays on the branch for the user to push manually. A held or failed push never earns a **fixed** reply.

## Step 7 — Reply to each comment, then resolve fixed threads

Post a reply in the original GitHub review thread for every handled reviewer comment, including when all comments are rejected or blocked. Use exactly one of these outcome lines:

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
- Counts of **fixed**, **blocked**, and **no-action** comments, with path + fixing SHA or reason per comment
- Posted reply URLs and any reply failures
- Deferred Vigil findings recorded in `defered.md` (one line each)
- Threads resolved and remaining open, including blocked and no-action outcomes
- Commit hash + push status
- Vigil artifact path and result

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.
