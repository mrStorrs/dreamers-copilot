---
name: dreamers-close-out
description: 'Close-out phase of the Dreamers pipeline. Wraps `/dreamers-docs` (Echo) + `/dreamers-pr` (push + PR) with the inline retro, improvements.md milestone-close append, final commit, post-PR discipline, and plan archive. Invokable standalone (commits-on-branch state) or composed from `/dreamers-full` Phase 3. Triggers: /dreamers-close-out, close out the milestone, ship the feature.'
argument-hint: '(inputs auto-detected; orchestrator passes via composed mode)'
---

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
- Plan paths: scan `.dreamers/plans/` for non-archived files referenced by `git log origin/<DEFAULT>..HEAD --format=%B | grep -E "^Plan:"`.
- Sentinel summary: not available — pass placeholder.
- Issue reference: ask the user (one-time).

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

Additionally, write inline summaries (these replace the Probe-era artifacts):
- **AC coverage matrix** — which test covers which AC across all cycles.
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
- path/to/plan-{slug}.md — one-line summary

AC coverage: <N>/<N> ACs covered (or list any uncovered with reason)

Sentinel summary: <one-paragraph from chat outputs across cycles>

Echo docs result: <status line + N files touched, or "No doc updates needed">

Retro: .dreamers/retros/retro-d<N>-<name>.md

Final commit: <hash + message, or "no final commit — nothing pending">

Issue reference: <number/URL, or "none">

Reply "Approved — push + PR" to proceed, or describe corrections needed.
```

Call `ask_user` with choice `["Approved — push + PR"]` and allow inline freeform corrections.

- Approval → proceed to Step 6.
- Corrections → apply the corrections inline, re-run any affected steps (e.g. re-invoke `/dreamers-docs` if Echo missed something), and re-present this gate. Loop until approved.

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

## Step 7 — Plan archive

For any merged prior PR's plan file in `.dreamers/plans/` (NOT the current cycle's plan — that stays until ITS PR merges):

- Verify the prior PR is merged: `gh pr view <number> --json state -q .state` returns `MERGED`.
- `mv` the plan file to `.dreamers/plans/archive/` (create dir if needed). Never delete.

Skip silently if no merged prior plan files exist.

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

## Push discipline (single source of truth)

`git push` happens EXACTLY ONCE per milestone — Step 6 (`/dreamers-pr`'s push). Step 8.4 push only fires if the user explicitly approves a post-PR commit; that is a SEPARATE event from the milestone's single push.
