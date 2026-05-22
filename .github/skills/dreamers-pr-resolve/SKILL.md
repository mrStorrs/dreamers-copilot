---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments inline. Orchestrator decides accept/reject per thread, applies fixes, spawns Sentinel for review of accepted changes, then resolves accepted threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
---

Resolve unresolved PR review comments. All work inline except a single Sentinel review pass over the accepted changes.

## Pre-flight reads

- `~/.copilot/dreamers/refs/tdd-orchestrator-discipline.md` — implementation + comment + git discipline (orchestrator applies these to the inline fixes)

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Step 1 — Discover open PRs

Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in the arguments, use that one. If multiple are open and none is specified, ask the user which PR to target before proceeding.

## Step 2 — Pull unresolved review threads (GraphQL only)

For the target PR, use GraphQL to get only the unresolved threads (the REST API `resolved` field is unreliable — always use GraphQL):

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 50) { nodes { isResolved id comments(first: 1) { nodes { path body } } } } } } }'
```

Extract only threads where `isResolved: false`. Capture each thread's `id`, `path`, and `body`. If there are none, report that back to the user and stop.

## Step 3 — Decide accept / reject per thread (inline)

For each unresolved thread, judge whether to accept or reject the comment. You are the implementation expert and have full authority. **Do not feel obligated to accept every comment** — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

For each thread, record:
- Thread ID
- Path + comment body (one-line summary)
- Decision: **accept** or **reject**
- Rationale: one sentence

If **accept** → apply the fix inline (Edit the file). Stage with `git add`. Follow the comment + implementation discipline from `tdd-orchestrator-discipline.md`.

If **reject** → no edit. Note in chat for the final report.

## Step 4 — Run tests after accepted changes

If any threads were accepted:
- Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before proceeding.
- Run the project's test command. Fix any regressions inline. Up to 3 attempts.

If no threads were accepted, skip to Step 6.

## Step 5 — Sentinel review of accepted changes

Invoke Sentinel via the Agent tool, scoped to ONLY the files touched by accepted threads:

```
agent_type: "sentinel"
mode: "sync"
prompt:
  Context: PR-comment-fix pass via /dreamers-pr-resolve.
  Plan file: none (ad-hoc PR-feedback work, no plan binding)
  Scope: <list of files changed by accepted threads from git status>
  Branch: <current feature branch>
  Default branch: <detected default>
  What the orchestrator has done: addressed N accepted PR review comments via inline edits; type-checked + tests green.
  Five lenses to apply: correctness, security, maintainability, simplicity / over-engineering, test coverage gaps.
  Fix-on-sight in BOTH production and test files. Type-check + re-run tests after fixes.
  Return: status line + severity-graded lane-labelled fixes-applied list + plan-alignment summary (mark as N/A here — no plan) + simplifications-not-made + design questions.
```

Wait for Sentinel. If `Blocked`, halt; surface to user. If `Fixed and approved`, proceed.

## Step 6 — Commit accepted fixes (if any)

If any fixes landed (Step 3 accepted + Step 5 Sentinel edits):

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit covering all the PR-feedback fixes. Commit message per `.github/instructions/git.instructions.md` if present.

Per `close-out.md` post-PR discipline: **do not push yet.** Ask the user before pushing:

> *I have a commit ready addressing the accepted PR comments. Should I push it to the PR?*

Only push after explicit user approval: `git push`.

## Step 7 — Resolve accepted threads via gh api

For each thread marked **accept** in Step 3, resolve it:

```bash
gh api graphql -f query='mutation { resolveReviewThread(input: { threadId: "THREAD_ID" }) { thread { isResolved } } }'
```

Leave rejected threads open — they represent active disagreements the reviewer should see.

## Step 8 — Report

Report to the user:
- N comments accepted (with one-line path + decision rationale per accept)
- M comments rejected (with one-line path + rejection rationale per reject)
- Threads remaining open (the M rejected ones)
- Commit hash + push status
- Sentinel result

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.
