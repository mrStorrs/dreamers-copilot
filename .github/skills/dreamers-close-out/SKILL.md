---
name: dreamers-close-out
description: 'Close-out phase of the Dreamers pipeline. Two modes — FULL (default): wraps docs + pr + retro + improvements append + plan archive + post-PR discipline (the milestone close-out). LIGHT (`--light`): docs (if applicable) + push + PR for ONE plan only; used by `/dreamers-full` between plans in incremental ship mode. Triggers: /dreamers-close-out, close out the milestone, ship the feature.'
argument-hint: '[--light <plan-path>] [--issue <#|url>]  (omit flags for full milestone close-out with no issue close)'
---

## Two modes

| Mode | When | Steps |
|---|---|---|
| **FULL** (default) | Milestone end — all plans in the sequence are implemented. This includes the case where `/dreamers-full` ran INCREMENTAL mode: the final plan's close-out is always FULL, covering the retro + improvements append + plan archive that the per-plan LIGHT close-outs skipped. | Steps 1–8 below. |
| **LIGHT** (`--light <plan-path>`) | Mid-sequence in INCREMENTAL ship mode — one plan complete, more remain. Invoked by `/dreamers-full` between plans. | Steps 2 + 4 + 5 + 6 only (docs if applicable + final commit + user gate + push + PR via `/dreamers-pr`). NO retro, NO improvements append, NO plan archive, NO post-PR discipline. |

The light mode is intentionally minimal: per-plan retros would spam the retro history, and the milestone-level scan / improvements / plan-archive belong to the END of the sequence, not the middle.

If `$ARGUMENTS` includes `--light` followed by a plan path, run LIGHT mode against that plan. Otherwise run FULL mode.

## What this skill does

The end-of-milestone wrapper. Sequences:

1. `improvements.md` milestone-close append.
2. `/dreamers-docs` invocation (Echo updates project docs).
3. Inline retro write.
4. Final commit if doc updates / retro / improvements landed uncommitted changes.
5. **User approval gate** — present summary before pushing.
6. `/dreamers-pr` invocation (push + PR creation + optional issue close).
7. Plan archive — `mv` merged-prior-PR plan files to `.dreamers/plans/archive/`.
8. Post-PR discipline (no auto-commit, surface improvements, project state scan).

The user approval gate sits between Echo (docs done) and the push (point of no return). Once `/dreamers-pr` runs, the PR is live.

## Pre-flight reads

Read these refs once at startup:

- `~/.copilot/dreamers/refs/close-out.md` — full retro + PR + post-PR procedure
- `~/.copilot/dreamers/refs/git-workflow.md` — commit + push discipline
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — closeout-discipline section

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions.

$ARGUMENTS

---

## Todo list

**FULL mode** — at skill entry, declare via `manage_todo_list`:
- [ ] Step 1 — improvements.md milestone-close append
- [ ] Step 2 — docs update (`/dreamers-docs`)
- [ ] Step 3 — retro write
- [ ] Step 4 — final commit (if needed)
- [ ] Step 5 — user approval gate
- [ ] Step 6 — push + PR (`/dreamers-pr`)
- [ ] Step 7 — plan archive
- [ ] Step 8 — post-PR discipline

**LIGHT mode** — at skill entry, declare via `manage_todo_list`:
- [ ] Docs update (if applicable)
- [ ] Final commit (if needed)
- [ ] User approval gate
- [ ] Push + PR via `/dreamers-pr`

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-full`, do NOT declare a new list — update the parent's matching Phase 3 item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## Invocation modes

### Composed mode (called by `/dreamers-full`)

The orchestrator passes:
- Plan file paths (list shipped this milestone).
- Branch name.
- Default branch name.
- Sentinel summary string (concatenated across cycles).
- Issue reference (if the originating task referenced one).

### Standalone mode (user invokes directly)

Auto-detect:
- Branch name + default branch (canonical two-step).
- Plan paths: extract via `git log origin/<DEFAULT>..HEAD --format=%B | grep -E "^Plan:"` and resolve each value to `.dreamers/plans/<value>.md`. The commit body format produced by `/dreamers-implement` Step 8 is `Plan: feature-<slug>/plan-NN-<name>` — repo-relative, no `.md`, no `.dreamers/plans/` prefix. Skip lines that don't resolve to an existing file (these may be stale commits or merge artifacts).
- Sentinel summary: not available — pass placeholder.
- Issue reference: parse from `$ARGUMENTS` only — accepts `--issue <#|url>` flag or a bare issue number / GitHub issue URL. If not provided, skip the issue close entirely. **Do not prompt the user.**

Use standalone mode when shipping a hand-rolled change or when the orchestrator wasn't used end-to-end.

---

## Step 1 — improvements.md milestone-close

Append any new improvement suggestions from this milestone to `.dreamers/improvements.md`. Format: dated entry, one sentence each, references the retro file path written in Step 3.

If `.dreamers/improvements.md` doesn't exist, skip — Step 3 will note this in the retro for future reference.

## Step 2 — `/dreamers-docs` (Echo invocation via the docs sub-skill)

Invoke `/dreamers-docs` in composed mode. Pass:
- Plan file paths.
- Changed files: output of `git diff --name-only origin/<DEFAULT>...HEAD`.
- Diff base: `origin/<DEFAULT>`.
- Sentinel summary string (composed mode) or placeholder (standalone mode).

Wait for `/dreamers-docs` to signal completion. Capture Echo's doc-changes log + open questions from chat output.

If open questions are raised, resolve them before proceeding to Step 3.

## Step 3 — Retro

Write `.dreamers/retros/retro-d<N>-<name>.md` per `close-out.md`. Required sections:

- **What worked well** — clean handoffs, inline phases that held up.
- **Friction points** — weak output, rework, places the inline discipline slipped.
- **Proposed improvements** — specific, actionable edits to the skill set, agent files, or refs. Reference the exact section to change and why.

Additionally, write inline summaries:
- **AC coverage matrix** — which test covers which AC across all cycles. Roll up from each cycle's `/dreamers-implement` chat output (captured by the orchestrator); concatenate per-cycle entries into one matrix.
- **Bugs found during user-testing** (if any) — what was found and how it was fixed.
- **Regression analysis** (if the originating task was a user-reported bug) — three questions per `orchestrator-discipline.md`: why wasn't it caught, what test was added, what else might be missing.

## Step 4 — Final commit (if needed)

If Steps 1, 2, or 3 wrote any uncommitted changes (Echo's doc edits, improvements.md, retro file), create a final commit:

```bash
git status                                  # confirm uncommitted state
git add <files>                             # explicit, no `-A`
git commit -m "docs: final cleanup before PR"  # or appropriate message
```

If no uncommitted changes, skip — never create empty commits.

## Step 5 — User approval gate (MANDATORY)

Before invoking `/dreamers-pr`, present this block:

```
**Milestone ready to ship.**

Plan(s) shipped:
- .dreamers/plans/feature-<slug>/plan-NN-<name>.md — one-line summary

AC coverage: <N>/<N> ACs covered (or list any uncovered with reason)

Sentinel summary: <one-paragraph from chat outputs across cycles>

Echo docs result: <status line + N files touched, or "No doc updates needed">

Retro: .dreamers/retros/retro-d<N>-<name>.md

Final commit: <hash + message, or "no final commit — nothing pending">

Issue reference: <number/URL, or "none">

Options:
- Approved — push + PR (proceed to Step 6)
- Halt for now (stop here; resume manually later — partial state preserved on the branch, no push)
- Freeform corrections (treated as not-yet-approved)
```

Call `request_information` with choices `["Approved — push + PR", "Halt for now", "Other"]`. Freeform corrections are accepted via Other.

- Approved → proceed to Step 6.
- Halt for now → output "Resume by re-invoking `/dreamers-close-out`. Branch state is preserved on `<branch-name>`." and stop. No push.
- Corrections → apply inline, re-run any affected steps (e.g. re-invoke `/dreamers-docs` if Echo missed something), and re-present this gate. Loop until approved.

This is the LAST point where the user can halt before the PR goes live.

## Step 6 — `/dreamers-pr` (push + PR via the pr sub-skill)

Invoke `/dreamers-pr` in composed mode. Pass:
- Branch name + default branch.
- Plan paths.
- Retro file path.
- Sentinel summary string.
- Issue reference (if applicable).
- Final commit hash (if Step 4 ran).

Wait for `/dreamers-pr` to signal completion. Capture the PR URL.

## Step 7 — Plan archive (whole feature directory)

The archive unit is the **whole feature directory** (`.dreamers/plans/feature-<slug>/`), not individual plan files. Mid-feature archiving (file-by-file) is NOT allowed — it would leave partially-emptied directories.

**Trigger:** the feature is complete when ALL plans in `feature-<slug>/` have shipped (their PRs merged to main). For single-plan features this is one PR; for multi-plan features this is the last plan's PR.

**Procedure:**

1. Identify any feature directories at `.dreamers/plans/feature-<slug>/` whose plans are all referenced by merged PRs (excluding the PR just opened in Step 6, which is unmerged).
2. For each such complete feature, verify every plan's PR is merged via `gh pr view <number> --json state -q .state` returning `MERGED`. If ANY plan's PR is still open or in-flight, skip this feature — it is not yet ready to archive.
3. Move the entire feature directory: `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/` (create the archive dir if needed). Never delete files.

Skip silently if no complete feature directories are ready to archive.

**Note:** this is the primary archive trigger. `git-workflow.md` Step 4 (run at the start of the next milestone in `/dreamers-implement` branch setup) is a fallback for prior features whose close-out never ran — if Step 7 already archived this feature, the source directory won't exist and Step 4 is a no-op.

**Legacy note:** legacy flat-format plan files (`.dreamers/plans/plan-<slug>.md` without a feature directory) created before the format overhaul are not auto-archived by this step — they stay where they are. If you need to archive a legacy plan, do it manually.

## Step 8 — Post-PR discipline (from `close-out.md`)

After `gh pr create` succeeds via Step 6:

1. **No auto-commit after PR is created.** If any further changes are needed (review comments, CI failures), do NOT auto-commit and push. Ask the user first: *"I have changes ready. Should I commit and push these to the PR?"* Only commit and push after explicit user approval. Commit message: `fix: address PR feedback` (or appropriate).

2. **Surface improvements from this cycle's retro** — list each as one sentence and ask: *"Should I address any of these?"* Do not apply without user go-ahead.

3. **Project state contradiction scan** (read durable surfaces, check for drift, surface — do NOT auto-apply):
   - The just-opened PR description vs the plan files shipped (verify the PR accurately describes what shipped).
   - `git log origin/$DEFAULT -10 --format=%s` — recent merged work.
   - Project-level `.github/copilot-instructions.md` Echo-owned sections — does the codebase still match?
   - `.dreamers/improvements.md` — open items still relevant?
   - `.dreamers/retros/` — any retro files for prior cycles that surface open improvements or stale items?

   Check for: tech stack drift, architecture pivots not reflected in instructions, milestone status drift, rule conflicts. **Propose all changes — do not auto-apply.** Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

4. **Post-PR push (if changes approved):** use plain `git push` (no force). The PR updates automatically.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (if applicable).
- Retro file path.
- Improvements surfaced for user follow-up.
- Project state scan summary (drift items found, or "none").

This is the terminal phase of the milestone. No further work after Step 8.

## LIGHT mode exit

After Step 6 completes (`/dreamers-pr` signals PR opened), return to the caller with this status block:

```
LIGHT close-out complete.
Plan: <plan-path>
PR: <PR URL>
```

The continuation prompt (whether to proceed to the next plan or halt) fires in `/dreamers-full`, not here. LIGHT mode's job is to return clean status.

## Push discipline (single source of truth)

- **FULL mode:** `git push` happens EXACTLY ONCE per close-out invocation — Step 6 (`/dreamers-pr`'s push). This applies whether FULL is running as a milestone-end close-out for an ATOMIC strategy OR as the FINAL plan's close-out in an INCREMENTAL strategy. Step 8.4 post-PR push only fires if the user explicitly approves a post-PR commit; that is a SEPARATE event from the close-out's single push.
- **LIGHT mode:** `git push` happens once per light close-out invocation — the equivalent of Step 6 for one plan. No Step 8 post-PR discipline runs in LIGHT mode.
