---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments inline. Orchestrator decides accept/reject per thread, applies fixes, spawns Sentinel + Probe + Hone in parallel for review of accepted changes, then resolves accepted threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
argument-hint: '[<pr-number>] (auto-discovers from open PRs if omitted)'
---

Resolve unresolved PR review comments. All work inline except a parallel review pass (Sentinel + Probe + Hone) over the accepted changes.

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + git discipline (orchestrator applies these to the inline fixes)

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Read review comments (discover PR + pull unresolved threads via GraphQL)
- [ ] Categorize threads (accept/reject decision per thread)
- [ ] Apply accepted fixes inline + run tests
- [ ] Spawn parallel review of accepted changes (Sentinel + Probe + Hone)
- [ ] Resolve accepted threads + commit + report

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Discover open PRs

Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in `$ARGUMENTS`, use that one. If multiple are open and none is specified, call `request_information` with each open PR as a choice (format: `#NUM — <title>`) plus `"Other"` for freeform input. If exactly one is open, use it without prompting.

## Step 2 — Pull unresolved review threads (GraphQL only)

For the target PR, use GraphQL to get only the unresolved threads (the REST API `resolved` field is unreliable — always use GraphQL):

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 50) { nodes { isResolved id comments(first: 1) { nodes { path body } } } } } } }'
```

Extract only threads where `isResolved: false`. Capture each thread's `id`, `path`, and `body`. If there are none, report that back to the user and stop.

## Step 3 — Decide accept / reject per thread (inline)

**HARD STOP — fix application is inline.** The orchestrator (this skill) edits files directly using Edit / Write / Bash tools to apply accepted PR-feedback fixes. **Do NOT spawn any subagent to write the fix code.** Specifically:
- ❌ `agent_type: "general-purpose"` → FORBIDDEN. There is no general-purpose fallback for implementation.
- ❌ `agent_type: "claude"` or any other host-runtime agent → FORBIDDEN.
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `delegation.md`).
- ✅ The only `agent_type` values you may spawn from this skill are `sentinel`, `probe`, `hone` in Step 5 (parallel review of the applied fixes). Nothing else.

For each unresolved thread, judge whether to accept or reject the comment. You are the implementation expert and have full authority. **Do not feel obligated to accept every comment** — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

For each thread, record:
- Thread ID
- Path + comment body (one-line summary)
- Decision: **accept** or **reject**
- Rationale: one sentence

If **accept** → apply the fix inline (Edit the file). Stage with `git add`. Follow the comment + implementation discipline from `orchestrator-discipline.md`.

If **reject** → no edit. Note in chat for the final report.

## Step 4 — Run tests after accepted changes

If any threads were accepted:
- Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before proceeding.
- Run the project's test command. Fix any regressions inline. Up to 3 attempts.

If no threads were accepted, skip to Step 6.

## Step 5 — Parallel review of accepted changes (Sentinel + Probe + Hone)

Spawn **three reviewers in parallel** in a single batched tool call (whatever the runtime surfaces for parallel agent spawning). All three are read-only / report-only; each returns structured findings in the format from `orchestrator-discipline.md`. Scope is restricted to ONLY the files touched by accepted threads.

Common prompt context for all three (subagent prompt rule — include verbatim):
- **Todo discipline:** "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `~/.copilot/dreamers/refs/orchestration-flow.md` § "Single-owner todo rule")
- Plan file: none (ad-hoc PR-feedback work, no plan binding) — mark plan-alignment summary as N/A
- Scope: list of files changed by accepted threads from `git status`
- Branch + default branch names
- What the orchestrator has done: addressed N accepted PR review comments via inline edits; type-checked + tests green.

Per-reviewer prompt addition:

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`) — correctness, security, maintainability lenses.

**Probe** (`agent_type: "probe"`, `mode: "sync"`) — test coverage lens (did the PR-feedback fixes break or weaken test coverage?).

**Hone** (`agent_type: "hone"`, `mode: "sync"`) — simplicity lens (did the fixes introduce over-engineering or redundancy?).

Apply findings inline per the orchestrator-as-fixer behavior:

1. Sort findings by severity.
2. Resolve conflicts per the rule (correctness > simplicity).
3. Apply each fix inline; stage with `git add`.
4. Re-run type-check + tests; fix regressions inline (up to 3 attempts).

Handle non-finding outputs:
- Any reviewer returns `Blocked` → halt; surface; resolve; re-spawn that reviewer.
- Open questions → present to user before proceeding.
- All three `Approved — no findings` → proceed to Step 6 directly.

## Step 6 — Commit accepted fixes (if any)

If any fixes landed (Step 3 accepted + Step 5 reviewer findings applied):

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit covering all the PR-feedback fixes. Commit message per `.github/instructions/git.instructions.md` if present.

Per `close-out-procedure.md` Step 8 post-PR discipline: **do not push yet.** Call `request_information` with `["Push to PR", "Hold — don't push yet", "Other"]` and a summary of the staged commit (hash, files touched, accepted thread count).

Only push after explicit `Push to PR` approval: `git push`. On `Hold` → stop with status; the commit stays on the branch for the user to push manually.

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
- Reviewer results (Sentinel + Probe + Hone)

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.
