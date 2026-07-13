---
name: dreamers-review
description: 'Review skill — executes the caller-selected Vigil, Sentinel, Probe, Hone, selected-subset, or full-triad lane; reads reviewer-written `.dreamers/reviews/` artifacts; and reports structured findings. Read-only for project files and git state; does NOT apply fixes. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[--vigil | --lens sentinel|probe|hone | --lenses sentinel,probe[,hone]] [--paths <glob>] [--branch]'
---

$ARGUMENTS

## Modes
- (default) Full triad: Sentinel + Probe + Hone in parallel.
- `--vigil` Single-agent combined review through Vigil.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).
- `--lenses <csv>` Selected-lens audit (`sentinel`, `probe`, `hone` in any non-empty combination).

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

## Todo - Before you begin.
- When standalone, declare a todo list for Step 1 / Step 2. When invoked by an outer delivery skill, complete these steps under its existing todo.

## Step 1 — Spawn reviewers
- Determine the selected reviewers: default = `full`; `--vigil` = Vigil; `--lens` = one reviewer; `--lenses` = the explicit reviewer subset. The caller selects the lane; this skill only executes it.
- Before spawning, record existing matching artifacts under `.dreamers/reviews/{vigil,sentinel,probe,hone}-*.md` so stale files are never mistaken for this run.
- For multiple selected reviewers, use one batched `task()` call with all selected sub-invocations, each `mode: "sync"`.
- Vigil and single-lens modes spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Every reviewer prompt MUST require exactly one artifact under `.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md` and short chat output containing only status, counts, artifact path, blocked reason, and open questions.
- Per-lens prompt context:
  - **Vigil** — combined correctness, security, maintainability, test coverage, and simplicity review with the required architecture audit. Artifact contains findings, plan alignment, AC coverage, and architecture audit sections.
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

The caller owns adaptive lane selection and all finding disposition. This skill executes the requested lane, reads its artifacts, and reports without modifying project code, tests, docs, config, dependencies, or git state. Each spawned reviewer is read-only for those same project files; its sole write is exactly one `.dreamers/reviews/` artifact.

Standalone lane choices:

| Lane | Reviewers | Use when |
| --- | --- | --- |
| vigil | Vigil | Combined proportional review selected by a delivery caller or explicit user request. |
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
