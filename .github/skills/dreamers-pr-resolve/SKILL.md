---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments inline. Orchestrator decides accept/reject per thread, applies fixes, spawns the narrowest required review lane for accepted changes, then resolves accepted threads via `gh api`. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
argument-hint: '[<pr-number>] (auto-discovers from open PRs if omitted)'
---

Resolve unresolved PR review comments. All work inline except required Sentinel review over accepted changes; add Probe/Hone only when situationally needed.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

<review-lanes>
# Review Lanes

Use the full lane for the initial `/dreamers-full` review for each plan. Use narrower lanes only for follow-up review gates after that full review has already happened, or for standalone focused audits. Reviewer work is read-only; the orchestrator applies or defers findings.

| Lane | Reviewers | Use when |
| --- | --- | --- |
| `sentinel` | Sentinel | Correctness/security/maintainability audit, lightweight bug fix, cleanup, logging/comment pass, or user explicitly asks for Sentinel only. |
| `probe` | Probe | Test coverage audit, AC/layer coverage check, regression-risk review, or user explicitly asks for Probe only. |
| `hone` | Hone | Simplicity/architecture/over-engineering audit, or user explicitly asks for Hone only. |
| `standard` | Sentinel + Probe | Follow-up check when both correctness and coverage need review but Hone is not warranted. |
| `full` | Sentinel + Probe + Hone | Initial `/dreamers-full` per-plan review. Invoke as `/dreamers-review` with no lens flags. Also use for follow-up architectural/refactor risk: new abstractions, public API/schema/data model changes, dependency changes, persistence changes, cross-module rewrites, broad subsystem movement, conflicting reviewer feedback, or explicit user request for full review. |

## Gate Rules

- `/dreamers-full` PR-bearing code changes require one `full` review per plan after orchestrator-run type-checks and tests pass.
- Do not use a narrower lane to bypass the initial full per-plan review.
- After the full review has passed, follow-up fix loops may use a narrower lane. User-testing bug fixes may skip reviewer re-run when the fix is small and automated validation covers it; otherwise run Sentinel by default. Add Probe or Hone only when the follow-up change touches their lenses.
- `/dreamers-pr-resolve` requires Sentinel for accepted fixes. Add Probe or Hone only when the accepted fixes touch coverage/regression risk or architecture/refactor risk.
- If the user asks for a narrower lane that conflicts with a required gate, surface the conflict before PR creation and ask whether to run the missing required lane or stop short of PR.
</review-lanes>

<dreamers-kernel>
# Dreamers Kernel

## Subagent allowlist (HARD RULE)

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

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
- [ ] Categorize threads (accept/reject decision per thread)
- [ ] Apply accepted fixes inline + run tests
- [ ] Spawn Sentinel review of accepted changes; add Probe/Hone only when situationally required
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
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `dreamers-kernel.md` § "Subagent allowlist").
- ✅ The only `agent_type` values you may spawn from this skill are `sentinel`, `probe`, `hone` in Step 5 (selected-lane review of the applied fixes). Nothing else.

For each unresolved thread, judge whether to accept or reject the comment. You are the implementation expert and have full authority. **Do not feel obligated to accept every comment** — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

For each thread, record:
- Thread ID
- Path + comment body (one-line summary)
- Decision: **accept** or **reject**
- Rationale: one sentence

If **accept** → apply the fix inline (Edit the file). Stage with `git add`. Follow the comment + implementation discipline from `dreamers-kernel.md` and `comment-rules.md`.

If **reject** → no edit. Note in chat for the final report.

## Step 4 — Run tests after accepted changes

If any threads were accepted:
- Run the project's type-check command (from project `.github/copilot-instructions.md`). Fix any errors before proceeding.
- Run the project's test command. Fix any regressions inline. Up to 3 attempts.

If no threads were accepted, skip to Step 6.

## Step 5 — Sentinel review of accepted changes

Run Sentinel for accepted PR-feedback fixes. This pass stays light because Probe and Hone already ran during the main pipeline review. Scope is restricted to ONLY the files touched by accepted threads.

Use `agent_type: "sentinel"`, `mode: "sync"` for the required review.

Add Probe only when accepted fixes changed tests, test harnesses, AC-covered behavior, validation logic, regression-sensitive behavior, or user/reviewer feedback asks for a coverage audit.

Add Hone only when accepted fixes introduce or reshape abstractions, module boundaries, public APIs, schemas, data models, persistence, dependencies, or broad refactors.

If Probe or Hone is added, spawn all selected reviewers in one batched tool call. All reviewers are read-only / report-only; each returns structured findings in the format from `reviewer-findings-format.md`.

Common prompt context for each selected reviewer (subagent prompt rule — include verbatim):
- **Todo discipline:** "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `dreamers-kernel.md` § "Single-owner todo")
- Plan file: none (ad-hoc PR-feedback work, no plan binding) — mark plan-alignment summary as N/A
- Scope: list of files changed by accepted threads from `git status`
- Branch + default branch names
- What the orchestrator has done: addressed N accepted PR review comments via inline edits; type-checked + tests green.

Per-reviewer prompt addition:

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`) — correctness, security, maintainability lenses.

**Probe** (`agent_type: "probe"`, `mode: "sync"`) — test coverage lens (did the PR-feedback fixes break or weaken test coverage?).

**Hone** (`agent_type: "hone"`, `mode: "sync"`) — simplicity lens (did the fixes introduce over-engineering or redundancy?).
- **Mandate reinforcement (include in Hone's prompt verbatim):** "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor — do not soften, hedge, or omit findings because the fix is big. When the suggested fix has architectural scope (touches files outside the PR-feedback surface, requires a new module, requires schema or symbol changes, or amounts to a full refactor of a subsystem), state the scope explicitly in the suggested-fix text. The orchestrator's major-refactor finding gate (per `dreamers-review.md`) routes those findings through the user for apply-now vs defer decisions. Your job is to surface; the gate handles disposition."

Apply findings inline per the full-pipeline apply-findings rules:

1. Sort findings by severity.
2. Resolve conflicts per the rule (correctness/security > test-coverage > simplicity).
3. **Evaluate each finding against the Major-refactor finding gate** per `dreamers-review.md` § "Major-refactor finding gate." If ANY criterion fires for a finding (new module / schema change / cross-cutting refactor / new exported symbols / files outside the PR-feedback surface / Hone-style "tear out X" scope language), call `request_information` with the 3-choice template (`Apply now — refactor in this cycle` / `Defer — create follow-up plan` / `Other`) and route per the user's answer. On `Defer`, create the stub plan file per the canonical template; do NOT apply the deferred fix.
4. Apply each (non-deferred) fix inline; stage with `git add`.
5. Re-run type-check + tests; fix regressions inline (up to 3 attempts).

Handle non-finding outputs:
- Any reviewer returns `Blocked` → halt; surface; resolve; re-spawn that reviewer.
- Open questions → present to user before proceeding.
- All spawned reviewers return `Approved — no findings` → proceed to Step 6 directly.

## Step 6 — Commit accepted fixes (if any)

If any fixes landed (Step 3 accepted + Step 5 reviewer findings applied):

```bash
git status                # confirm staged content
git commit -m "fix: address PR feedback"
```

Use a single commit covering all the PR-feedback fixes. Commit message per `.github/instructions/git.instructions.md` if present.

**Do not push yet.** Call `request_information` with `["Push to PR", "Hold — don't push yet", "Other"]` and a summary of the staged commit (hash, files touched, accepted thread count). Post-PR changes always require explicit user approval before pushing.

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
- Reviewer results (selected lane)

This skill does NOT update the PR description, does NOT re-request review, does NOT close the PR. Those are user actions.
