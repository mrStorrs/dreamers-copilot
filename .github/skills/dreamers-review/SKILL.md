---
name: dreamers-review
description: 'Review skill — selects reviewers from plan complexity or explicit direction, includes a linked verbatim Grill transcript when present, or infers intent without a plan. Reports artifact-backed findings; read-only for project files and git state. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[plan-path] [--vigil | --full | --lens sentinel|probe|hone | --lenses sentinel,probe[,hone]] [--paths <glob>] [--branch]'
---

$ARGUMENTS

## Modes
- `--full` Full triad: Sentinel + Probe + Hone in parallel.
- `--vigil` Single-agent combined review through Vigil.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).
- `--lenses <csv>` Selected-lens audit (`sentinel`, `probe`, `hone` in any non-empty combination).
- With a plan and no lane flag: select from the plan as described below.
- Without a plan or lane flag: infer a review basis, then default to the full triad.

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

## Todo - Before you begin.
- When standalone, declare a todo list for Steps 1–3. When invoked by an outer delivery skill, complete these steps under its existing todo.

## Step 1 — Establish the review basis
- If a readable plan is supplied, use it as the review basis. A user-supplied path that cannot be read remains a blocking error; do not silently replace it with an inferred basis.
- For a supplied plan, resolve `**Grilling transcript:**` relative to the plan. If the metadata is absent, check for sibling `grilling-transcript.md` for compatibility. When a readable transcript exists, read it in full and bind its absolute path + verbatim contents alongside the plan as authoritative user-intent context. If the plan references a transcript that is missing or unreadable, block instead of silently dropping it. If no transcript exists or is referenced, continue with the plan alone.
- If no plan is supplied or no plan is available, infer the intended behavior from, in order: explicit user direction; PR title/body and branch name; commits and diff in the selected scope; changed tests; changed code and its callers; then nearby conventions and public interfaces.
- Write a concise inferred-intent summary with the observable behavior, invariants, likely regression risks, evidence paths, and confidence. Treat that summary as the review basis, not as a replacement plan.
- If the evidence does not support one reliable interpretation of the change, ask the user one concise question before spawning reviewers. Do not guess or use the full triad to decide the requirement.

## Step 2 — Spawn reviewers
- Determine the selected reviewers in this order:
  1. Honor an explicit lane flag or explicit user direction.
  2. Honor an explicit reviewer requirement written in the plan.
  3. Otherwise read `**Plan-type:**`: `lite` = Vigil; `standard` = Sentinel + Probe; `complex` = Sentinel + Probe + Hone.
  4. If no plan or Plan-type is available, use Sentinel + Probe + Hone.
- Before spawning, record existing matching artifacts under `.dreamers/reviews/{vigil,sentinel,probe,hone}-*.md` so stale files are never mistaken for this run.
- For multiple selected reviewers, launch every reviewer in parallel through the runtime's batched-spawn mechanism, each with `mode: "sync"`. Never spawn or await reviewers sequentially.
- Vigil and single-lens modes spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Every reviewer prompt MUST include the review basis: either the absolute plan path or the inferred-intent summary with its evidence and confidence. For a plan-bound review with a resolved Grill transcript, include its absolute path and full verbatim contents; require the reviewer to use it when checking intent alignment and to report any plan/transcript conflict rather than silently choosing one. Explicitly say `no plan binding` for inferred-intent reviews.
- Every reviewer prompt MUST require exactly one artifact under `.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md` and short chat output containing only status, counts, artifact path, blocked reason, and open questions.
- Per-lens prompt context:
  - **Vigil** — combined correctness, security, maintainability, test coverage, and simplicity review with the required architecture audit. Artifact contains findings, intent alignment, requirement coverage, and architecture audit sections.
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Artifact contains findings + intent-alignment summary.
  - **Probe** — test coverage (requirement matrix, layer audit, edge cases, gaps). Artifact contains findings + requirement coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Mandate verbatim: "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly so the caller can route it through their major-refactor gate."
- Wait for all spawned reviewers to return.

## Step 3 — Report
- For each selected reviewer, read the artifact path returned in chat. If the path is missing or unreadable, inspect only new matching artifacts created for this review; if exactly one exists for that reviewer, read it. Otherwise surface `Blocked — review artifact missing for <reviewer>` and stop.
- Return per-reviewer artifact contents verbatim to the caller, including artifact paths.
- Aggregate counts by severity + lens from the artifacts for a one-line summary.
- Surface any `Blocked` status from any artifact (caller handles).
- Surface any open questions raised by any artifact (caller handles).

## Exit
- Artifact-backed structured findings per `reviewer-findings-format` (Kernel). The caller applies (or defers) findings on its own terms.

## Lane policy

This skill owns reviewer selection and execution. The caller owns all finding disposition, gates, fixes, revalidation, and user testing. This skill does not modify project code, tests, docs, config, dependencies, or git state. Each spawned reviewer is read-only for those same project files; its sole write is exactly one `.dreamers/reviews/` artifact.

Lane choices:

| Lane | Reviewers | Use when |
| --- | --- | --- |
| vigil | Vigil | Lite plan or explicit request. |
| sentinel | Sentinel | Correctness, security, or maintainability audit. |
| probe | Probe | Test coverage, AC layer, edge-case, or regression-risk audit. |
| hone | Hone | Simplicity, architecture, or over-engineering audit. |
| standard | Sentinel + Probe | Standard plan or explicit combined correctness and coverage audit. |
| full | Sentinel + Probe + Hone | Complex plan, explicit full review, or the standalone default. |

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
