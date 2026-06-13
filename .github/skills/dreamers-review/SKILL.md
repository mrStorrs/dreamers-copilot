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

## Stats checkpoints
<stats-checkpoints>
- Generate one run ID at skill entry and reuse it for the whole run.
- Use the stats writer checkpoint subcommand for skill-side events; keep output empty unless a short event ID is explicitly needed.
- Record only safe categories, counts, reviewers, artifact paths, plan paths, commit hashes, PR URLs, and closed enum values.
- Do not record freeform user answers, blocker detail, prompts, tool outputs, diffs, or transcript text.
</stats-checkpoints>
- Record `skill_started` at entry with the selected lane and whether the run is standalone or called from another Dreamers skill.
- Record `review_pass_started` before spawning reviewers and `review_pass_completed` after artifacts are read, including lane, reviewer set, artifact paths, blocked status, open-question count, and `findings_by_severity` / `findings_by_lens`.
- Record `skill_halted` when review cannot continue because artifacts are missing or a reviewer reports `Blocked`.
- Record `skill_completed` when the report is returned.

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

Use the full lane for the initial `/dreamers-full` review for each plan. In `/dreamers-full`, routine follow-up reviewer reruns go through Vigil, not another triad or selected triad lane. Use `/dreamers-review` follow-up lanes only when the `/dreamers-full` major-change rerun gate asks the user and the user selects a triad or selected-lane rerun, or for standalone focused audits. Reviewer work is read-only except for review artifacts; the orchestrator applies or defers findings.

| Lane | Reviewers | Use when |
| --- | --- | --- |
| `sentinel` | Sentinel | Correctness/security/maintainability audit, lightweight bug fix, cleanup, logging/comment pass, or user explicitly asks for Sentinel only. |
| `probe` | Probe | Test coverage audit, AC/layer coverage check, regression-risk review, or user explicitly asks for Probe only. |
| `hone` | Hone | Simplicity/architecture/over-engineering audit, or user explicitly asks for Hone only. |
| `standard` | Sentinel + Probe | Standalone or user-selected follow-up check when both correctness and coverage need review but Hone is not warranted. |
| `full` | Sentinel + Probe + Hone | Initial `/dreamers-full` per-plan review. Invoke as `/dreamers-review` with no lens flags. After that, use only when the user selects it from the `/dreamers-full` major-change rerun gate or explicitly requests a full review. |

## Gate Rules

- `/dreamers-full` PR-bearing code changes require one `full` review per plan after orchestrator-run type-checks and tests pass.
- Do not use a narrower lane to bypass the initial full per-plan review.
- After the full review has passed, `/dreamers-full` follow-up review reruns use Vigil by default. It may invoke `/dreamers-review` again only after the major-change rerun gate asks the user and the user selects `full` or a selected lane.
- `/dreamers-pr-resolve` requires Sentinel for accepted fixes. Add Probe or Hone only when the accepted fixes touch coverage/regression risk or architecture/refactor risk.
- If the user asks for a narrower lane that conflicts with a required gate, surface the conflict before PR creation and ask whether to run the missing required lane or stop short of PR.

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
