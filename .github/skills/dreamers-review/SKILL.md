---
name: dreamers-review
description: 'Review skill — selects reviewers from plan complexity or explicit direction, includes a linked verbatim Grill transcript when present, or infers intent without a plan. Reports structured findings; read-only for project files and git state. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[plan-path] [--vigil | --full | --lens sentinel|probe|hone | --lenses sentinel,probe[,hone]] [--paths <glob>] [--branch]'
---

Follow YAGNI principles when reviewing.

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
- When standalone, a todo is optional. When invoked by an outer delivery skill, complete these steps under its existing todo.

## Step 1 — Establish the review basis
- If a readable plan is supplied, use it as the review basis. A user-supplied path that cannot be read remains a blocking error; do not silently replace it with an inferred basis.
- For a supplied plan, resolve `**Grilling transcript:**` relative to the plan. If the metadata is absent, check for sibling `grilling-transcript.md` for compatibility. When a readable transcript exists, read it in full and bind its absolute path + verbatim contents alongside the plan as authoritative user-intent context. If the plan references a transcript that is missing or unreadable, block instead of silently dropping it. If no transcript exists or is referenced, continue with the plan alone.
- If no plan is supplied or no plan is available, infer the intended behavior from, in order: explicit user direction; PR title/body and branch name; commits and diff in the selected scope; changed tests; changed code and its callers; then nearby conventions and public interfaces.
- Distinguish agreed requirements from behavior inferred from the implementation. Changed code and tests are evidence of implemented behavior, not authorization for additional scope. Surface uncertain scope explicitly and pass that distinction to reviewers.
- Write a concise inferred-intent summary with the observable behavior, invariants, likely regression risks, evidence paths, and confidence. Treat that summary as the review basis, not as a replacement plan.
- If the evidence does not support one reliable interpretation of the change, ask the user one concise question before spawning reviewers. Do not guess or use the full triad to decide the requirement.

## Step 2 — Spawn reviewers
- Determine the selected reviewers in this order:
  1. Honor an explicit lane flag or explicit user direction.
  2. Honor an explicit reviewer requirement written in the plan.
  3. Otherwise read `**Plan-type:**`: `lite` = Vigil; `standard` = Sentinel + Probe; `complex` = Sentinel + Probe + Hone.
  4. If no plan or Plan-type is available, use Sentinel + Probe + Hone.
- Before spawning, assign a fresh handoff path to each selected reviewer using the review handoff contract below.
- For multiple selected reviewers, launch every reviewer in parallel through the runtime's batched-spawn mechanism, each with `mode: "sync"`. Never spawn or await reviewers sequentially.
- Vigil and single-lens modes spawn only the chosen reviewer.
- Every reviewer prompt MUST include the review basis: either the absolute plan path or the inferred-intent summary with its evidence and confidence. For a plan-bound review with a resolved Grill transcript, include its absolute path and full verbatim contents; require the reviewer to use it when checking intent alignment and to report any plan/transcript conflict rather than silently choosing one. Explicitly say `no plan binding` for inferred-intent reviews.
- Give each reviewer its assigned path and request the complete report in both copies.
- Per-lens prompt context:
  - **Vigil** — combined correctness, security, maintainability, test coverage, and simplicity review against each acceptance criterion or agreed task requirement. Use the report format in Vigil’s instructions.
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Artifact contains findings + intent-alignment summary.
  - **Probe** — test coverage (requirement matrix, layer audit, edge cases, gaps). Artifact contains findings + requirement coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Check scope necessity before architectural quality using the shared MVP assessment; require concrete evidence for retained complexity and explicit scope for necessary refactors.
- Wait for all spawned reviewers to return.

## Step 3 — Report
- Require the shared MVP assessment in completed Hone and Vigil reports, including clean approvals. A completed report missing that assessment is an incomplete handoff.
- Collect one complete report per selected reviewer using the review handoff contract. For each missing handoff, report `Blocked — missing handoff for <reviewer>`. Report the results that did arrive.
- Return each accepted report verbatim to the caller. Include its source and path when using a file.
- Aggregate counts by severity and lens from the accepted reports. Surface all blocked statuses and open questions.

## Exit
- Structured findings per `reviewer-findings-format` (Kernel). The caller applies (or defers) findings on its own terms.

## Lane policy

This skill owns reviewer selection and execution. The caller owns all finding disposition, gates, fixes, revalidation, and user testing. This skill does not modify project code, tests, docs, config, dependencies, or git state. The reviewers deliver findings for the caller.

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
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Echo uses the sole prompt defined in `/dreamers-docs`. All other `task()` invocations MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

<reviewer-findings-format>
# Reviewer Findings Format

## Review handoff

The caller assigns an unused absolute path under the target worktree's `.dreamers/reviews/` for each invocation. Use `<reviewer>-<scope>-<unique-id>.md` with the section in the scope for section audits. Pass the exact path and this handoff requirement in the agent prompt.

The reviewer prepares one complete report in its assigned format, ending with `End of handoff` on its own line. Create the parent directory if needed, attempt to write the report at the assigned path, and return the same complete report in the final reply, even if the write fails.

For each expected reviewer invocation, check the assigned file and the final reply from that invocation. A complete report has a valid status, the required sections for the reported outcome, the stated number of findings, and the closing line. A blocked report needs the blocker and any open questions in addition to the closing line. Use the complete file if available, otherwise use the complete reply. Process one copy per invocation. If neither copy is complete, report the missing handoff for that reviewer and scope. Preserve blocked status, findings, and open questions from the accepted report and apply the caller's existing gates.

**Status line** (one of the following, allowing the reviewer format's `Status:` prefix and hyphen separator):
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

Reviewers are report-only for code, tests, docs, config, scripts, and git state. The caller applies fixes per its own orchestrator-as-fixer behavior.

## MVP assessment (Hone and Vigil)

For change reviews, establish the minimum implementation that satisfies the agreed acceptance criteria while preserving required security, data integrity, performance constraints, and existing contracts. For each distinct addition, identify the requirement or evidenced constraint it serves. Ask what would fail if it were removed or replaced with the simplest existing mechanism. If nothing required would fail, report the addition as unnecessary and name what to delete. Apply this check to behavior, abstractions, configuration, dependencies, tests, and supporting changes. Future usefulness and tests added by the change do not establish necessity.

Prefer deletion, reuse, or a local simplification. Recommend a broader refactor only with a concrete explanation of why it is needed to correct the changed implementation; separate unrelated architectural improvements from required fixes. Refactor cost alone does not justify suppressing a necessary finding. State the affected files, modules, call sites, and deletions where known.

Every completed Hone or Vigil change review, including approval, must include a brief **MVP assessment** identifying the minimum approach and any non-obvious additions retained, with their requirement or constraint justification. Cite concrete paths or symbols; a claim that the code is minimal is insufficient. Report removable additions as findings, not optional observations. If scope is uncertain, surface the uncertainty instead of treating implemented behavior as an agreed requirement. For an audit without a proposed change, use its stated audit objective rather than inventing feature ACs.
</reviewer-findings-format>

<logging-discipline>
1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, it is the binding spec.
2. **Else: match surrounding code.** Existing log calls in the same module and nearest neighbors define:
   - Logger library / import path (do not introduce a new logger where one already exists).
   - Level conventions in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).
</logging-discipline>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Check for a complete reviewer handoff using the review handoff contract. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
