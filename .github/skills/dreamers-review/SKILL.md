---
name: dreamers-review
description: 'Review skill — spawns Sentinel + Probe + Hone in parallel and reports their structured findings. Read-only; does NOT apply fixes. The caller decides what to do with the findings. Standalone --lens flag for single-lens audits. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[--lens sentinel|probe|hone] [--paths <glob>] [--branch]'
---

$ARGUMENTS

## Modes
- (default) Triad: Sentinel + Probe + Hone in parallel.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry: Step 1 / Step 2.

## Step 1 — Spawn reviewers
- Triad mode: one batched `task()` call with three sub-invocations (Sentinel + Probe + Hone, all `mode: "sync"`).
- Single-lens mode: spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Per-lens prompt context:
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Return findings + plan-alignment summary.
  - **Probe** — test coverage (AC matrix, layer audit, edge cases, gaps). Return findings + AC coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Mandate verbatim: "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly so the caller can route it through their major-refactor gate."
- Wait for all spawned reviewers to return.

## Step 2 — Report
- Return per-reviewer chat output verbatim to the caller.
- Aggregate counts by severity + lens for a one-line summary.
- Surface any `Blocked` status from any reviewer (caller handles).
- Surface any open questions raised by any reviewer (caller handles).

## Exit
- Structured findings per `reviewer-findings-format` (Kernel). The caller applies (or defers) findings on its own terms.

## Dreamers Kernel
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

## Continuation principle

At every natural pause between phases — where the skill has produced a meaningful result and the user could redirect — call `request_information` with three choices: `Continue` / `Halt for now` / `Other` (freeform). Never silently advance; never silently stop. On `Halt`, emit a one-line resume command and stop.

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

Reviewers are read-only / report-only. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

<logging-discipline-review>
# Logging Discipline (reviewer lens)

When Sentinel reviews log calls in the diff:

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, treat it as the binding spec. Flag any log call that violates it.
2. **Else: surrounding-code conformity.** Compare added/changed log calls to existing calls in the same module and nearest neighbors. Flag mismatches in:
   - Logger library / import path (introduces a new logger where one already exists).
   - Level usage (e.g., ERROR for recoverable issues, INFO with full bodies).
   - Message format (structured fields vs interpolated strings, key naming, casing) that breaks local convention.
3. **Never-log violations are `security` severity.** Secrets, tokens, PII, or full request/response bodies in any log call → flag at `security` regardless of lens.

Severity mapping: never-log violation → `security`; library/format/level deviation → `maintainability`. Findings follow the format in `reviewer-findings-format` (Kernel).
</logging-discipline-review>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
