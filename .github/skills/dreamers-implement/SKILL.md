---
name: dreamers-implement
description: "Implement an approved proposal or plan inline, enforce scope and branch identity, and return verified outcomes. Stops before review or shipping."
argument-hint: "<plan-path>"
---

$ARGUMENTS

## Inputs and ownership

- Require a readable approved proposal/plan. If its path is missing, ask and stop; do not invent a replacement or require a detailed plan.
- Use the embedded Dreamers standards below. Read project instructions, source, tests, and work artifacts as needed; do not fetch Dreamers rule/template files.
- When standalone, track Resolve input / Branch / Implement / Verify / Return. When called by /dreamers, use its existing todo and return control after this phase.
- Work inline; do not spawn an implementer or reviewer.

## 1. Resolve input and branch

1. When standalone, perform the embedded git startup checks before treating local plans as current project state. Under /dreamers, use the startup evidence and branch it already established.
2. Read the plan and supplied manifest context. Identify the required outcomes, exact scope, constraints, and verification. Consult the linked Grill transcript only for an unclear decision or conflict.
3. Stop for missing files, shell drafts, placeholders, or unresolved requirements. Verify cited existing paths and affected callers; distinguish planned new files from stale references.
4. Create/resume the appropriate feature branch when standalone. Confirm branch identity and recent commits before the first edit; preserve work already present.

## 2. Implement within scope

Implement the smallest clear change that satisfies the approved outcomes and preserves existing contracts. Apply the embedded code, comment, logging, and verification standards. Reuse sufficient tests; add meaningful behavior coverage where needed. Test order is flexible.

For an unresolved decision, out-of-scope file, or broader behavior change, present the needed change and obtain direction before that work. Do not silently replace the plan or add unrelated cleanup.

## 3. Verify and inspect

1. Run applicable type-check, build, lint, and tests. After three unsuccessful fix attempts, stop with the command, failure, attempted fixes, and blocker.
2. Update root test-benchmarks.md after successful test commands using the embedded format. Record skipped or unavailable checks as coverage gaps.
3. Inspect the final diff against the approved outcomes and scope. Check callers, failure behavior, comment rules, and logging privacy; remove unnecessary complexity without weakening correctness.
4. Map each required outcome to its actual verification. A required failing or blocked check prevents a green result.

## Return to the caller

Stage explicit paths for this work, including verification records. Return:

- Status: verified implementation, or blocked with the reason.
- Changed paths and a concise behavior summary.
- Required outcome → named test/manual check/inspection → result, including gaps.
- Commands run, results, measured test durations, and remaining user-testing needs.

Stop here. The caller owns review/fixes, user testing, commits, docs/retros/improvements, and shipping. Under /dreamers, Vigil review is next.

## Embedded standards

<dreamers-kernel>
# Execution ownership

- The main session writes code/tests, validates, applies fixes, and performs git work. Never delegate implementation.
- Skills run in that same context. The outermost skill owns the todo, approvals, and phase transitions. Invoked skills complete their phase and return.
- Forge and Nova are user-entered personas, never spawned workers. Delegate only the role the active skill requires: Vigil for review, Echo for docs, Sage for research. Sentinel, Probe, and Hone require explicit user selection; never select them from plan complexity or generated plan text.
- Subagent prompts include task, scope, constraints, proposal/plan path or inferred intent, prior progress/artifact paths, validation evidence, output path, and completion criteria. Include: "Do NOT call manage_todo_list; the caller owns the todo." Use task mode: "sync".
- Read this invocation's returned artifact before acting. Resolve missing/blocked output. On failure, inspect partial artifacts and resume only unfinished steps inline or with the same allowed role.

# Scope and authorization

- The approved proposal/plan defines scope. Ask before unrelated cleanup, changing agreed behavior, or out-of-scope edits. Surface unresolved requirements instead of guessing.
- Proposal approval authorizes implementation. Detailed planning is opt-in; never add a second start gate.
- Dependency installs require user authorization. Honor permission already given; a missing dependency is not permission to install it.
- Explicit user direction can alter phases. Preserve remaining gates and record agreed scope changes in the proposal/plan.

# Work records

Keep plans, Grill transcripts, reviews, retros, and improvements in gitignored .dreamers/. Keep test-benchmarks.md and defered.md at the project root.

When the user explicitly defers a suggestion, append its date, source/artifact, suggestion, proposed action, and reason to defered.md. Create it with "# Deferred Suggestions" if absent; preserve previous entries and stage it with related work.
</dreamers-kernel>

<git-workflow>
# Git workflow

Apply the git steps owned by the active phase. Implementation-only work stops before commits, pushes, and PRs.

## Startup and branch

1. Run `git status --short --branch` and inspect existing changes. Preserve work already present; do not reset, discard, or silently include unrelated edits.
2. Resolve the default branch with `git symbolic-ref --short refs/remotes/origin/HEAD` and remove the leading `origin/`; if unavailable, use `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`. Do not assume main. Run `git fetch origin` and `git log --oneline -5 origin/<default>` before treating local plans as current project state. An unavailable base blocks new branch setup.
3. New work starts on feat/<slug> or fix/<slug> from updated `origin/<default>`. Resume an authorized feature branch when one already exists. When an outer delivery skill established the branch, reuse it.
4. Before the first edit, check `git branch --show-current` and `git log --oneline -3` against the intended feature. Stop on an unexplained mismatch; never implement directly on the default branch. Keep .dreamers/ gitignored. Use a worktree only on user direction.

## Delivery commits and PRs

- Stage explicit paths. The delivery owner commits once per plan/cycle after review fixes, green validation, and required user testing. Include final docs and close-out edits before the PR; skip an empty commit.
- Use the project's conventional commit style. Include `Plan: feature-<slug>/plan-NN-<name>` when applicable and this trailer:

    Co-authored-by: The Dreamers System

- ATOMIC intermediate cycles commit locally without pushing. INCREMENTAL cycles each have their own approved PR; wait for merge confirmation before starting the next branch from updated default.
- At PR close-out, obtain the existing pre-PR approval, then `git push -u origin <branch>` and create the PR. Never force-push or bypass hooks. Reconcile a rejected push before retrying.
- After a PR opens, further commits and pushes need user authorization. /dreamers-pr-resolve authorizes its fix commit and retains its push approval gate. Do not ask again for authorization already given.
</git-workflow>

<code-laws>
# Code laws

- Simplicity and correctness come first. Prefer the smallest clear design that meets current requirements. Preserve required behavior when simplifying.
- Reuse local patterns. Avoid speculative abstractions, pass-through layers, duplicate logic, dead code, and defensive paths for impossible states.
- Tests must protect observable behavior and remain stable through harmless refactors. Never test by matching source, prompt, or documentation wording, or snapshotting implementation details. No filler or duplicate tests.
- For a bug, add or improve a meaningful regression test when feasible; otherwise record the verification and coverage gap. Tests-first is optional.
- If a real constraint requires an exception to these laws, explain it. If missing scaffolding caused an avoidable mistake, record a concrete improvement.
</code-laws>

<comment-rules>
# Comment rules

Comments explain non-obvious reasons, constraints, or gotchas. Keep necessary public API docs, actionable TODO/FIXME notes, and license headers.

- No restating readable code or repeating signatures in docstrings.
- No source comments naming plans, tickets, milestones, or agents.
- No separators, blank-comment dividers, emojis, or arguments that the spec permits a pattern.
- Inline comments: one line where possible, at most two. Refactor code that needs longer explanation; this limit excludes necessary API documentation and licenses.
</comment-rules>

<testing-mandate>
# Verification

## Coverage

Read the project's instructions and existing tests to identify validation commands and coverage for each required outcome. Reuse sufficient tests; add or improve a test only when it protects behavior or a likely regression. Prefer the narrowest layer that proves the requirement:

- Unit: logic, boundaries, invalid input, and failure states that can be proved in isolation.
- Integration: important contracts and side effects across services, storage, APIs, or other boundaries.
- E2E: user actions through to observable results. Navigation changes need an E2E check; if automation is unavailable, name a specific manual check and record the coverage gap.
- Bug fixes: preserve a verified reproduction in a meaningful regression test when feasible. Otherwise explain the limitation and the evidence used to verify the fix.

Test order is flexible. Do not add a test per function or checklist row. Tests must survive harmless refactors: no source/prompt wording assertions, implementation snapshots, duplicate coverage, or mocks that merely confirm themselves. Inspect docs/comment-only changes instead of manufacturing tests.

## Execution and evidence

Run relevant project type-check, build, lint, and test commands. Verify affected callers, required outcomes, meaningful edges, and failure behavior. A passing test count does not prove the whole requirement.

Map each required outcome to a named test, manual check, or inspection result. Identify unverified outcomes explicitly. After three unsuccessful fix-and-retry attempts, stop and report the failing command, failure, attempted fixes, and blocker. Do not report green while a required check is failing or blocked.

## Test timings

After every successful test command, create/update its row in root test-benchmarks.md, including post-fix runs. Record measured duration and date; preserve human Notes. Use max(last duration × 2, 30 seconds) for the next timeout. If no prior row exists, use the project's normal timeout until a measurement is available.

| Command | Last run | Updated | Recommended timeout | Notes |
| --- | --- | --- | --- | --- |

The main session runs validation and updates timings. Reviewers assess supplied evidence and report gaps; they do not run tests or edit benchmark records.
</testing-mandate>

<logging-discipline>
# Logging

1. Use the consuming project's .github/instructions/logging.instructions.md when present. Otherwise match the logger library, levels, and message format in the same module or its nearest neighbors. Do not introduce a second logger alongside an existing one.
2. Never log secrets, credentials, tokens, PII, or complete request/response bodies. Sanitize arguments, configuration, URLs, return values, and errors before logging.
3. Record useful events at the project's established levels. Avoid noisy loop logging and redundant entry/exit calls that add no diagnostic value.
4. Keep logging changes within the approved scope. Leave unrelated logging alone unless an accepted finding requires a change.
5. If neither project instructions nor surrounding code provide a usable convention, ask one focused question before adding log calls.
</logging-discipline>
