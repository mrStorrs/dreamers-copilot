---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments inline. Apply accepted fixes, run a Vigil review, record deferred Vigil findings in project-root defered.md, reply to each comment with fixed / blocked / no-action, and resolve fixed threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
argument-hint: '[<pr-number>] (auto-discovers from open PRs if omitted)'
---

Resolve unresolved PR review comments. Apply fixes inline. Use Vigil to review accepted changes and `/dreamers-docs` to update affected documentation.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Echo uses the sole prompt defined in `/dreamers-docs`. All other `task()` invocations MUST include in the prompt:
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
- [ ] Read review comments (discover PR + pull unresolved threads via GraphQL)
- [ ] Categorize comments (accept/reject decision + outcome per comment)
- [ ] Apply accepted fixes inline + run tests
- [ ] Spawn Vigil review of accepted changes
- [ ] Update affected docs, commit + approved push, reply to each comment, resolve fixed threads + report

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Discover open PRs

Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in `$ARGUMENTS`, use that one. If multiple are open and none is specified, call `request_information` with each open PR as a choice (format: `#NUM — <title>`) plus `"Other"` for freeform input. If exactly one is open, use it without prompting.

If any merge conflicts exist, attempt to resolve them.

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
- Spawn only Vigil for review in Step 5. Use `/dreamers-docs` for the Echo handoff in Step 6.

Check each requested change against the governing plan or linked issue when available. Fixes needed to meet an acceptance criterion or correct a regression introduced by the PR are in scope even if the affected file was never named.

For each out-of-scope request, show the user the comment and explain why it is outside scope. Ask **Include in this PR** or **Decline**. Wait for the decision before applying that change or replying on GitHub. Continue independent in-scope feedback while waiting.

- **Include in this PR** → use the accepted-fix workflow below.
- **Decline** → leave the change unapplied, reply in the original thread with `blocked: outside the scope of <plan or issue>` and a brief reason, and leave the thread unresolved.

Judge in-scope requests on their merits. Reject incorrect or architecturally unsuitable suggestions with a reason.

For each comment, record:
- Thread ID + comment ID / URL
- Path + comment body (one-line summary)
- Decision and rationale per request: **accept**, **reject**, **pending scope decision**, or **declined scope expansion**
- Final outcome per comment: **fixed**, **blocked**, or **no-action**, with the fixing commit SHA or reason. Wait for all of its scope decisions before finalizing. Use the decline reply if any request was declined. Mark a comment **fixed** only if all its requests were fixed.

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

Assign Vigil a fresh path using the review handoff contract below. Include this context in the prompt:
- Plan file: none (ad-hoc PR-feedback work, no plan binding) — mark plan-alignment summary as N/A
- Scope: list of files changed by accepted threads from `git status`
- Branch + default branch names
- What the orchestrator has done: addressed N accepted PR review comments via inline edits; type-checked + tests green.
- Risk notes: call out whether accepted fixes changed tests/test harnesses/AC-covered behavior/validation/regression-sensitive behavior, or introduced/reshaped abstractions/module boundaries/APIs/schemas/data models/persistence/dependencies/refactors.
- Review lenses: correctness, security, maintainability, test coverage, and simplicity. Treat the risk notes as focus areas, not as permission to skip the other lenses.
- Handoff: <assigned path>. Attempt to save the full report there and return the same full report in your final reply.

Collect the review using the handoff contract below. Halt and report a missing handoff or the reason Vigil reported `Blocked`. Raise any open questions before proceeding. For an approval without findings, proceed to Step 6. Otherwise apply findings from the accepted report:

1. Sort findings by severity.
2. Resolve conflicts per the rule (correctness/security > test-coverage > simplicity).
3. **Evaluate each finding against the Major-refactor finding gate** per `dreamers-review.md` § "Major-refactor finding gate." If ANY criterion fires for a finding (new module / schema change / cross-cutting refactor / new exported symbols / files outside the PR-feedback surface / Vigil full-refactor scope language), call `request_information` with the 3-choice template (`Apply now — refactor in this cycle` / `Defer — save to defered.md` / `Other`) and route per the user's answer. On `Defer`, do NOT apply the finding or create a follow-up plan. Append a Markdown entry to `defered.md` in the project root; create it with `# Deferred Suggestions` if absent, and never overwrite existing entries. Record the date, PR + branch, Vigil handoff source (include the path for a file), severity / lens / location, finding, suggested fix, triggered criterion, and deferral rationale. Stage `defered.md` and surface its path.
4. Apply each (non-deferred) fix inline; stage with `git add`.
5. Re-run type-check + tests; fix regressions inline (up to 3 attempts).

## Step 6 — Commit accepted fixes (if any)

If any fixes landed or Step 5 added deferred entries, invoke `/dreamers-docs` before committing. Include its staged documentation edits in the commit.

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit covering all the PR-feedback fixes.

If there is no new commit to push, skip the push gate and proceed to Step 7.

**Do not push yet.** Call `request_information` with `["Push to PR", "Hold — don't push yet", "Other"]` and a summary of the staged commit (hash, files touched, accepted thread count). Post-PR changes always require explicit user approval before pushing.

Only push after explicit `Push to PR` approval: `git push`. On `Hold` → use Step 7 in reply-only mode with **blocked** reasons stating that the fix is committed locally but awaiting push approval, then stop; the commit stays on the branch for the user to push manually. A held or failed push never earns a **fixed** reply.

## Step 7 — Reply to each comment, then resolve fixed threads

Post a reply in the original GitHub review thread for each reviewer comment whose outcome is decided. Skip comments awaiting a scope decision, including in reply-only mode. Use exactly one of these outcome lines:

- `fixed: in commit <SHA>` — the fix passed validation and required Vigil review, and the referenced commit is available on the remote PR branch. Use the actual fixing commit SHA, never a placeholder or an unpushed local commit.
- `blocked: <reason>` — state the obstacle and remaining work, or use the Step 3 reply for a declined scope expansion.
- `no-action: <reason>` — we decided not to take action. Explain that decision; do not use this for an accepted issue we could not fix.

Use GraphQL variables for the reply body so quotes and newlines remain data:

```bash
gh api graphql -f query='mutation($thread: ID!, $body: String!) { addPullRequestReviewThreadReply(input: { pullRequestReviewThreadId: $thread, body: $body }) { comment { id url } } }' -f thread="$THREAD_ID" -f body="$REPLY_BODY"
```

When a thread contains multiple reviewer comments, post a separate outcome reply for each and append its source comment URL on a separate line. Confirm each reply succeeded and record its URL before resolving anything. On API failure, leave the affected thread open and report the failure.

Resolve a thread only when every reviewer comment in it is **fixed** and every required reply succeeded. In reply-only mode, do not resolve any threads.

```bash
gh api graphql -f query='mutation { resolveReviewThread(input: { threadId: "THREAD_ID" }) { thread { isResolved } } }'
```

Leave threads with **blocked** or **no-action** outcomes open so the reviewer can see the remaining issue or decision.

## Step 8 — Report

If scope decisions remain, wait for the user after processing independent feedback. Resume those requests at Step 3.

Report to the user:
- Counts of **fixed**, **blocked**, and **no-action** comments, with path + fixing SHA or reason per comment
- Posted reply URLs and any reply failures
- Deferred Vigil findings recorded in `defered.md` (one line each)
- Threads resolved and remaining open, including blocked and no-action outcomes
- Commit hash + push status
- Vigil handoff source and result

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.

<reviewer-findings-format>
# Reviewer Findings Format

## Review handoff

The caller assigns an unused absolute path under the target worktree's `.dreamers/reviews/` for each invocation. Use `<reviewer>-<scope>-<unique-id>.md` with the section in the scope for section audits. Pass the exact path and this handoff requirement in the agent prompt.

The reviewer prepares one complete report in its assigned format, ending with `End of handoff` on its own line. Create the parent directory if needed, attempt to write the report at the assigned path, and return the same complete report in the final reply, even if the write fails.

For each expected reviewer invocation, check the assigned file and the final reply from that invocation. A complete report has a valid status, the required sections for the reported outcome, the stated number of findings, and the closing line. A blocked report needs the blocker and any open questions in addition to the closing line. Use the complete file if available, otherwise use the complete reply. Process one copy per invocation. If neither copy is complete, report the missing handoff for that reviewer and scope. Preserve blocked status, findings, and open questions from the accepted report and apply the caller's existing gates.

**Status line** (one of):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:

```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

- `severity` ∈ `critical` / `high` / `medium` / `low`
- `lens-tag` ∈ `correctness` / `security` / `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` — absolute or repo-relative path + line number
- `what was wrong → suggested fix` — one-line description + targeted fix the caller can apply mechanically

**Observations** (optional) — out-of-scope notes that aren't findings. The caller may or may not act on them.

**Open questions** (optional) — items needing user judgment. Use "none" if no questions.

Reviewers deliver findings. The caller owns fix application and validation.
</reviewer-findings-format>
