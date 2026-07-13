---
name: dreamers
description: 'Adaptive end-to-end Dreamers delivery orchestrator. Accepts a task description, approved plan path(s), or a feature manifest; routes empty/help input to read-only guidance; invokes the specialized planning, implementation, review, documentation, and PR skills; applies artifact-backed findings; runs triggered user testing and retrospectives; then opens a reviewed PR. Use for /dreamers, plan and implement, ship a feature, or deliver an existing Dreamers plan.'
argument-hint: '<task description> | [--no-grill] | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Route input

Normalize whitespace before routing.

- Empty or whitespace-only input, help, --help, or -h: invoke /dreamers-help as a read-only delegation and halt this delivery workflow. Do not inspect or mutate repository, git, mailbox, or external state first.
- Task description: use planning mode.
- Resolved plan path or paths: use plan mode.
- A resolved manifest.md: use manifest mode.
- Otherwise halt and ask for a task, plan path, or manifest.

Plan paths must resolve under .dreamers/plans/ and be named plan-*.md. A manifest must resolve under .dreamers/plans/ and be named manifest.md. Reject missing or escaping paths.

## Own the delivery workflow

Declare the complete parent todo at entry. Invoked Dreamers skills run in this same orchestrator context, complete their owned phase, and return control without replacing the parent todo. Explicit handoffs are required only for spawned agents.

After help routing, load and apply the catalog `dreamers/refs/git-workflow.md` contract (installed at `~/.copilot/dreamers/refs/git-workflow.md`). Run its startup verification before reading .dreamers files, and retain its branch, commit, and push invariants through close-out.

### Planning mode

- Invoke /dreamers-plan with the task description. Task descriptions run Grill by default.
- Pass through --no-grill or unmistakable natural-language direction such as "do not grill" or "skip the interview"; strip control syntax from the actual task.
- Capture the approved plan paths and optional manifest returned by /dreamers-plan.
- Plan approval authorizes implementation. Do not add an implementation-start gate.
- If planning halts without approval, halt this workflow.

### Plan and manifest modes

- Plan path and manifest artifact modes skip Grill, replanning, plan rewriting, and implementation-start approval.
- Preserve supplied plan order. For a manifest, carry its shared constraints, decisions, contracts, and end-to-end ACs into every cycle and reviewer call.
- Read each plan, detect Plan-type, read plan-guide-selector.md, then only the matching plan-guide-lite.md, plan-guide-standard.md, or plan-guide-complex.md.
- Reject missing required sections, placeholders, invalid AC Layer annotations, unresolved open questions, and unverifiable citations presented as facts.
- A missing Plan-type is legacy input; warn and continue only with explicit user approval.
- Every supplied plan reaches the single verification call at cycle entry before implementation. Drift detected there halts the workflow until the user revises, accepts, skips, or abandons the plan.

### Independent adaptive decisions

Decide independently: ship strategy, reviewer rerun, documentation need, and retrospective need. State each selected value and a one-sentence rationale. Honor explicit user overrides and ask only when classification is genuinely ambiguous.

- Select INCREMENTAL for independent plans, different repositories or subsystems, or standalone value that should ship first.
- Select ATOMIC for overlapping files, ordered contract or migration work, or plans that require joint verification. Conflicting signals default to ATOMIC.
- Never add a routine strategy confirmation gate.

### Branch setup

After artifact checks pass, execute git-workflow branch setup once per repository: checkout the detected default branch, pull it from origin, cut the planned feature branch, confirm branch identity with the recent log, and verify .dreamers/ is ignored. Before the first implementation edit, read open .dreamers/improvements.md items and action, defer with a reason, or close each relevant item. For a cross-repository INCREMENTAL sequence, repeat startup verification and branch setup only after the prior transfer gate is approved.

## Run each plan through the specialized skills

For every plan in sequence:

1. Invoke /dreamers-plan-verify exactly once for this plan against the current branch state and shared manifest context. This is the executable verification point for task, plan, and manifest routes.
2. Invoke /dreamers-implement with the absolute plan path and shared manifest context. Require green automated validation, an AC coverage matrix, changed-file scope, and validation commands/results before continuing.
3. Select the initial reviewer lane through review-selection below, then invoke /dreamers-review with that lane, the plan path, shared manifest context, branch scope, and validation results.
4. Read every reviewer artifact returned by /dreamers-review. Blocked halts the cycle with the artifact path; ask each open question before applying findings.
5. Apply or defer findings, revalidate, and decide reviewer reruns through the rules below.
6. Run the triggered user-testing/fix loop when required.
7. Complete the plan cycle and either continue, ship incrementally, or enter milestone close-out.

<review-selection>
# Review Selection

Use this contract for the initial review and any reviewer rerun in a PR-bearing Dreamers workflow.

## Initial lane

- A complex plan selects Sentinel + Probe + Hone through the full /dreamers-review lane.
- A low-risk lite or standard plan selects Vigil.
- Any danger or high-risk trigger overrides a smaller plan type and selects the triad:
  - Security, authentication, authorization, privacy, payment, secret, or permission changes.
  - Schema, migration, persistence, destructive-data, concurrency, or irreversible-side-effect changes.
  - Public or breaking API, dependency, build, distribution, or cross-subsystem changes.
  - Rollback that requires operator action or data recovery instead of reverting the feature commit.
- PR-bearing work receives at least Vigil unless the user explicitly requests that review be skipped.

## Decision behavior

- State the selected reviewer lane and a one-sentence rationale, then proceed without a routine confirmation gate.
- An explicit user override wins and remains authoritative. Before a requested downshift, surface the concrete risk being accepted.
- If classification is genuinely ambiguous, ask once before review. Do not silently promote or downshift.
- Record the selected lane, rationale, trigger or plan type, and any user override in the cycle summary.

## Invocation

- The caller selects the lane; /dreamers-review only executes it and reports artifact-backed results.
- For Vigil, invoke /dreamers-review --vigil --branch with the plan path, changed-file scope, branch and default names, validation commands/results, shared manifest context when present, and prior review artifacts when applicable.
- For the triad, invoke /dreamers-review --branch with the same context.
- For a selected rerun, invoke /dreamers-review with --lens or --lenses and the same context.
- Read every reviewer artifact before reporting or applying findings. Blocked halts the cycle; open questions return to the user.

## Reruns

- Decide reviewer reruns independently from plan type, ship strategy, documentation, and retrospective decisions.
- Skip a rerun when fixes are small and automated validation directly covers them; record the reason.
- Use the /dreamers-review Vigil lane for a normal rerun after targeted fixes.
- Escalate a rerun to the triad only when the new change set itself meets a danger/high-risk trigger. A selected /dreamers-review lane is valid when one specific lens is sufficient.
- State the rerun choice and rationale and proceed without a routine gate. Ask only when the new risk is genuinely ambiguous; explicit user overrides remain authoritative.
</review-selection>

### Apply findings

Sort findings critical to low. Resolve conflicts by correctness/security, then test coverage, then simplicity. Ask when ambiguity remains.

Apply targeted fixes inline using the implementation rules already loaded from /dreamers-implement unless a suggested fix triggers the major scope expansion gate through any of:

- A new module or top-level directory outside planned scope.
- A schema or data-model change.
- A cross-subsystem refactor or broad rewrite.
- A new public API, exported symbol, dependency, or persistence behavior not specified by the plan.
- Files outside plan scope.
- Full-refactor language from Hone or Vigil.

For a gate-triggering finding, present reviewer, severity, lens, location, finding, suggested fix, triggered criterion, rationale, and breadth estimate. Offer Apply now / Defer - create follow-up plan / Other. Apply now fixes and revalidates. Defer writes a right-sized stub plan under .dreamers/plans/ and continues. Never silently apply or defer.

After applied fixes, rerun the project validation commands with the existing three-attempt limit. Invoke /dreamers-review again only when review-selection requires a rerun, and route every returned artifact through this same finding process.

### User-testing and fix loop

Trigger user testing when the plan requires manual verification, the change is user-facing, build or distribution verification is required, a reviewer requests it, or the user asked to test the area. Otherwise record the skip.

Read .github/dreamers/templates/user-testing-gate.md and present its numbered Testing steps and Notes exactly. Offer exactly Approved / Bug found (enter text) / Other (enter text). A bug is fixed inline by the orchestrator, revalidated, reviewed again when warranted, and returned to the same gate. Neither /dreamers-review nor its reviewers apply the fix.

## Complete a cycle

- Commit exactly once per plan after review findings, validation, and required user testing are complete. Follow the project conventional-commit style with an explicit Plan: feature-.../plan-... line and the Dreamers co-author trailer.
- Before the next plan, carry forward the landed diff and shared manifest context so its cycle-entry verification checks the updated branch state.
- INCREMENTAL: decide documentation need, invoke /dreamers-docs --branch when documentable, include its staged edits in the cycle commit, present the mandatory pre-PR approval gate, invoke /dreamers-pr, and halt until the user confirms merge. Start the next repository or cycle from a fresh default branch.
- ATOMIC: commit without pushing and continue. Push exactly once at final PR creation.

## Close out

- Decide documentation need from the landed diff. Invoke /dreamers-docs --branch when user-facing or documentable; otherwise record the skip.
- Write a retro and append .dreamers/improvements.md only when triggered by multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or explicit user request. Otherwise record that retrospective and improvements were skipped.
- Include an AC coverage matrix and testing bugs in any retro; include regression analysis only for an originating bug fix.
- Stage explicit paths and create the final commit only when staged work remains.
- Present the mandatory pre-PR approval gate with milestone summary, validation, review artifacts, user-testing status, commits, and PR scope. Offer Approved / Halt / Other.
- On approval invoke /dreamers-pr, passing any referenced issue. Capture the PR URL.
- After PR creation, surface open retro improvements and project-state drift only. Do not auto-commit.
