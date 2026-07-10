---
name: dreamers-review
description: 'Review skill — spawns Sentinel / Probe / Hone in the selected lane, reads their `.dreamers/reviews/` artifacts, and reports structured findings. Read-only; does NOT apply fixes. The caller decides what to do with the findings. Supports full triad, selected-lens subsets, and single-lens audits. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[--lens sentinel|probe|hone | --lenses sentinel,probe[,hone]] [--paths <glob>] [--branch]'
---

$ARGUMENTS

## Modes
- (default) Full triad: Sentinel + Probe + Hone in parallel.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).
- `--lenses <csv>` Selected-lens audit (`sentinel`, `probe`, `hone` in any non-empty combination).

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry: Step 1 / Step 2.

## Step 1 — Spawn reviewers
- Determine the selected reviewers: default = `full`; `--lens` = one reviewer; `--lenses` = the explicit reviewer subset.
- Before spawning, record existing matching artifacts under `.dreamers/reviews/{sentinel,probe,hone}-*.md` so stale files are never mistaken for this run.
- For multiple selected reviewers, use one batched `task()` call with all selected sub-invocations, each `mode: "sync"`.
- Single-lens mode: spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Every reviewer prompt MUST require exactly one artifact under `.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md` and short chat output containing only status, counts, artifact path, blocked reason, and open questions.
- Per-lens prompt context:
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Artifact contains findings + plan-alignment summary.
  - **Probe** — test coverage (AC matrix, layer audit, edge cases, gaps). Artifact contains findings + AC coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Mandate verbatim: "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly so the caller can route it through their major-refactor gate."
- Wait for all spawned reviewers to return.

## Step 2 — Report
- For each selected reviewer, read the artifact path returned in chat. If the path is missing or unreadable, inspect only new matching artifacts created after Step 1; if exactly one exists for that reviewer, read it. Otherwise surface `Blocked — review artifact missing for <reviewer>` and stop.
- Return per-reviewer artifact contents verbatim to the caller, including artifact paths.
- Aggregate counts by severity + lens from the artifacts for a one-line summary.
- Surface any `Blocked` status from any artifact (caller handles).
- Surface any open questions raised by any artifact (caller handles).

## Exit
- Artifact-backed structured findings per `reviewer-findings-format` (Kernel). The caller applies (or defers) findings on its own terms.

## Lane policy

The caller selects initial and rerun review through the shared adaptive contract. This skill executes Sentinel, Probe, and Hone lanes; Vigil is spawned directly by the caller. Reviewer work is read-only except for its artifact.

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

- For Vigil, spawn vigil directly with the plan path, changed-file scope, branch and default names, validation commands/results, shared manifest context when present, and prior review artifacts when applicable.
- For the triad, invoke /dreamers-review --branch with the plan path and shared manifest context.
- Read every reviewer artifact before reporting or applying findings. Blocked halts the cycle; open questions return to the user.

## Reruns

- Decide reviewer reruns independently from plan type, ship strategy, documentation, and retrospective decisions.
- Skip a rerun when fixes are small and automated validation directly covers them; record the reason.
- Use Vigil for a normal rerun after targeted fixes.
- Escalate a rerun to the triad only when the new change set itself meets a danger/high-risk trigger. A selected /dreamers-review lane is valid when one specific lens is sufficient.
- State the rerun choice and rationale and proceed without a routine gate. Ask only when the new risk is genuinely ambiguous; explicit user overrides remain authoritative.
</review-selection>

Standalone lane choices:

| Lane | Reviewers | Use when |
| --- | --- | --- |
| sentinel | Sentinel | Correctness, security, or maintainability audit. |
| probe | Probe | Test coverage, AC layer, edge-case, or regression-risk audit. |
| hone | Hone | Simplicity, architecture, or over-engineering audit. |
| standard | Sentinel + Probe | Explicit combined correctness and coverage audit. |
| full | Sentinel + Probe + Hone | Adaptive triad selection or explicit full review. |

/dreamers-pr-resolve retains its own artifact-backed Vigil requirement for accepted fixes.

## Dreamers Kernel
<dreamers-kernel>
# Dreamers Kernel

## User overrides

Explicit user instructions can skip or alter phases/actions.

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

<reviewer-findings-format>
# Reviewer Findings Format

## Artifact contract

Each reviewer writes exactly one markdown artifact under `.dreamers/reviews/`:

`.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md`

Use the branch, plan slug, or task slug for `<slug>`. If unavailable, use `review`.

The artifact is the durable handoff. Chat output is only a short status pointer with the artifact path. The caller must read the artifact before reporting, applying, or deferring findings.

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

Reviewers are read-only / report-only for code, tests, docs, config, scripts, and git state. The only allowed write is the single review artifact. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

<logging-discipline>
# Logging Discipline

Rules for log calls — what to write, what to flag in review.

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, it is the binding spec.
2. **Else: match surrounding code.** Existing log calls in the same module and nearest neighbors define:
   - Logger library / import path (do not introduce a new logger where one already exists).
   - Level conventions in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).
3. **Never log:** secrets, tokens, PII, full request/response bodies. No exceptions.
4. **Neither rule yields a clear answer** → raise an open question via `request_information` rather than guessing.
</logging-discipline>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
