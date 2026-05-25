---
name: dreamers-close-out
description: 'Close-out entry point. Runs the canonical close-out procedure (`close-out-procedure.md`). Two modes: FULL (default) and LIGHT (`--light <plan-path>`). Includes push + PR via `pr-procedure.md` at Step 6. Triggers: /dreamers-close-out, close out the milestone, ship the feature.'
argument-hint: '[--light <plan-path>] [--issue <#|url>]  (omit flags for full milestone close-out with no issue close)'
---

## What this skill does

Standalone entry point for the close-out phase. The user invokes this when they have completed implementation (manually or via `/dreamers-implement`) and want to ship — push + PR + docs + retro + archive.

This skill follows `~/.copilot/dreamers/refs/close-out-procedure.md` end-to-end. Echo is spawned as a subagent inline at Step 2 for project-doc updates. `pr-procedure.md` is followed inline at Step 6 for push + PR creation.

This skill does NOT invoke any other skill. Echo is spawned as a subagent inline (per close-out-procedure Step 2). PR creation is handled inline (per pr-procedure.md).

---

## Two modes

| Mode | When | Run |
|---|---|---|
| **FULL** (default) | Milestone end — all plans in the feature are implemented. Includes the case where INCREMENTAL ship-strategy is in play: the FINAL plan's close-out is always FULL. | All of close-out-procedure (Steps 1–8). |
| **LIGHT** (`--light <plan-path>`) | Mid-sequence in INCREMENTAL ship mode — one plan complete, more remain. Used by `/dreamers-full` between plans. | Steps 2 + 4 + 5 + 6 only (docs if applicable + final commit + user gate + push + PR). NO retro, NO improvements append, NO plan archive, NO post-PR discipline. |

If `$ARGUMENTS` includes `--light` followed by a plan path, run LIGHT mode. Otherwise run FULL mode.

If `$ARGUMENTS` includes `--issue <#|url>` (bare issue number or GitHub issue URL), capture it as the issue reference for `pr-procedure.md` Step 4. Do NOT prompt the user for an issue reference.

---

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + logging + test-writing + git rules
- `~/.copilot/dreamers/refs/delegation.md` — subagent allowlist + Echo invocation protocol
- `~/.copilot/dreamers/refs/git-workflow.md` — commit + push discipline
- `~/.copilot/dreamers/refs/close-out-procedure.md` — the procedure this skill follows (FULL or LIGHT)
- `~/.copilot/dreamers/refs/pr-procedure.md` — the PR-creation sub-procedure read by close-out Step 6

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions.

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`.

**FULL mode:**
- [ ] Read close-out-procedure.md + pr-procedure.md
- [ ] Step 1 — improvements.md milestone-close append
- [ ] Step 2 — docs update (Echo subagent)
- [ ] Step 3 — retro write
- [ ] Step 4 — final commit (if needed)
- [ ] Step 5 — user approval gate
- [ ] Step 6 — push + PR (follow pr-procedure.md inline)
- [ ] Step 7 — plan archive (whole feature directory)
- [ ] Step 8 — post-PR discipline

**LIGHT mode:**
- [ ] Read close-out-procedure.md + pr-procedure.md
- [ ] Step 2 — docs update (if applicable)
- [ ] Step 4 — final commit (if needed)
- [ ] Step 5 — user approval gate
- [ ] Step 6 — push + PR (follow pr-procedure.md inline)

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**Subagent prompt rule:** when this skill spawns Echo in Step 2, include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in Echo's prompt. Per `orchestration-flow.md` § "Single-owner todo."

---

## Standalone-input auto-detection

Auto-detect when running standalone:

- **Branch name + default branch**: canonical two-step `git symbolic-ref` + `gh repo view`.
- **Plan paths**: extract via `git log origin/<DEFAULT>..HEAD --format=%B | grep -E "^Plan:"` and resolve each value to `.dreamers/plans/<value>.md`. The commit body format produced by `implementation-procedure.md` Step 8 is `Plan: feature-<slug>/plan-NN-<name>` — repo-relative, no `.md`, no `.dreamers/plans/` prefix. Skip lines that don't resolve to an existing file (these may be stale commits or merge artifacts).
- **Sentinel summary**: not available — pass placeholder "Standalone close-out — no Sentinel summary captured."
- **Issue reference**: parse from `$ARGUMENTS` only — accepts `--issue <#|url>` flag or a bare issue number / GitHub issue URL. If not provided, skip the issue close entirely. **Do not prompt the user.**

---

## Procedure

Follow `~/.copilot/dreamers/refs/close-out-procedure.md` in the appropriate mode (FULL or LIGHT). The procedure includes its own user approval gate at Step 5 and reads `pr-procedure.md` in full at Step 6 for the push + PR creation.

Update this skill's todo as each step completes.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (yes/no/N/A).
- Retro file path (FULL mode).
- Improvements surfaced for user follow-up (FULL mode).
- Project state scan summary (FULL mode).

For LIGHT mode, exit with the per-plan PR URL and a one-line status block per close-out-procedure's LIGHT mode exit format.

---

## What this skill does NOT do

- Does NOT invoke any other skill. Echo is spawned as a subagent inline at Step 2; PR creation runs inline at Step 6 per `pr-procedure.md`.
- Does NOT spawn agents outside the 5-item allowlist. Only Echo is used in this skill.
