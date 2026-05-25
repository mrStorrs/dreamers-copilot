# Close-out Procedure (canonical — read in full, no skipping)

This ref is the SOLE source of truth for the Dreamers close-out phase. Both `/dreamers-close-out` (standalone) and `/dreamers-full` (end-to-end pipeline) follow this procedure. Echo is spawned inline at Step 2 for project-doc updates.

**MUST-READ rule:** any skill citing this ref in its pre-flight reads MUST load this file in full using the `view` tool from top to bottom — no `grep`, no `head`, no pattern-matching shortcut. Read every line before starting the procedure.

The PR-creation half of close-out lives in `pr-procedure.md`. Step 6 below directs the orchestrator to follow that ref inline.

---

## Two modes

| Mode | When | Steps |
|---|---|---|
| **FULL** (default) | Milestone end — all plans in the feature are implemented. Includes the case where INCREMENTAL ship-strategy is in play: the FINAL plan's close-out is always FULL. | Steps 1–8. |
| **LIGHT** (`--light <plan-path>`) | Mid-sequence in INCREMENTAL ship mode — one plan complete, more remain. Used by `/dreamers-full` between plans. | Steps 2 + 4 + 5 + 6 only (docs if applicable + final commit + user gate + push + PR). NO retro, NO improvements append, NO plan archive, NO post-PR discipline. |

The light mode is intentionally minimal: per-plan retros would spam history, and milestone-level scan / improvements / plan-archive belong to the END of the sequence.

If the procedure is invoked with a `--light <plan-path>` argument, run LIGHT mode against that plan. Otherwise run FULL mode.

---

## Inputs

- **Plan file paths** (list shipped this milestone — one or many, all under the same `feature-<slug>/` directory).
- **Branch name** + **default branch name**.
- **Sentinel summary string** (concatenated across cycles in the milestone for FULL mode; just this plan's reviewer summary for LIGHT mode).
- **Issue reference** (number or URL, if applicable).
- **Final commit hash** (if any docs/retro/improvements were committed during this procedure).

## Outputs

- Updated docs (Echo edits committed) — if applicable.
- Retro file at `.dreamers/retros/retro-d<N>-<name>.md` (FULL mode only).
- One PR opened against the default branch.
- Plan directory archived to `.dreamers/plans/archive/feature-<slug>/` (FULL mode only, at milestone-final PR merge — actually performed in Step 7).

The orchestrator's todo (a single list owned by the top-level skill) records step completion.

---

## Step 1 — improvements.md milestone-close (FULL only)

Append any new improvement suggestions from this milestone to `.dreamers/improvements.md`. Format: dated entry, one sentence each, references the retro file path written in Step 3.

If `.dreamers/improvements.md` doesn't exist, skip — Step 3 will note this in the retro for future reference.

LIGHT mode skips this step.

## Step 2 — Docs update (Echo subagent invocation)

The orchestrator spawns Echo as a subagent here for project-doc updates.

**When to invoke Echo:**

- FULL mode: always invoke (docs are evaluated at milestone end).
- LIGHT mode: invoke only when the just-completed plan's diff has user-facing or documentable changes. Judgment criteria: user-visible behavior changed, public API changed, config/setup steps changed, test commands changed, or significant new exported symbol.

When invoking, spawn Echo via the `task` tool:

- `agent_type: "echo"`, `mode: "sync"`
- Pass in the prompt (per `delegation.md`):
  - **Context:** brief description of the milestone or plan being documented.
  - **Prior work:** plan file paths (or "n/a (bug fix)" if no plan), changed files (output of `git diff --name-only origin/<DEFAULT>...HEAD`), diff base (`origin/<DEFAULT>`), Sentinel summary string.
  - **What is needed:** review the changed files vs the plan(s) and update project docs as appropriate (README, CHANGELOG, Echo-owned sections of `.github/copilot-instructions.md`, project-specific docs the project conventions call out).
  - **Constraints:** Echo edits docs ONLY — no production code, no tests. Echo writes to its own scope per `echo.agent.md`. **Do NOT call `manage_todo_list` — the orchestrator owns the todo.**
  - **Definition of Done:** structured chat output per Echo's output discipline (status line + docs-changes log + instruction-file changes + comment audit + open questions).

Wait for Echo to signal completion. Capture the doc-changes log + open questions from chat output. If open questions are raised, resolve them with the user before proceeding.

Stage any new doc edits with `git add`.

## Step 3 — Retro (FULL only)

Write `.dreamers/retros/retro-d<N>-<name>.md`. Required sections:

- **What worked well** — clean handoffs, inline phases that held up.
- **Friction points** — weak output, rework, places the inline discipline slipped.
- **Proposed improvements** — specific, actionable edits to the skill set, agent files, or refs. Reference the exact section to change and why.

Additionally, write inline summaries:
- **AC coverage matrix** — which test covers which AC across all cycles. Roll up from each cycle's chat output.
- **Bugs found during user-testing** (if any) — what was found and how it was fixed.
- **Regression analysis** (if the originating task was a user-reported bug) — three questions per `orchestrator-discipline.md`: why wasn't it caught, what test was added, what else might be missing.

LIGHT mode skips this step.

## Step 4 — Final commit (if needed)

If Steps 1, 2, or 3 wrote any uncommitted changes (Echo's doc edits, improvements.md, retro file), create a final commit:

```bash
git status                                  # confirm uncommitted state
git add <files>                             # explicit, no `-A`
git commit -m "docs: final cleanup before PR"  # or appropriate message
```

If no uncommitted changes, skip — never create empty commits.

## Step 5 — User approval gate (MANDATORY)

Before invoking the PR-creation procedure, present this block:

```
**Milestone ready to ship.**

Plan(s) shipped:
- .dreamers/plans/feature-<slug>/plan-NN-<name>.md — one-line summary

AC coverage: <N>/<N> ACs covered (or list any uncovered with reason)

Sentinel summary: <one-paragraph from chat outputs across cycles>

Echo docs result: <status line + N files touched, or "No doc updates needed">

Retro: .dreamers/retros/retro-d<N>-<name>.md   (FULL only)

Final commit: <hash + message, or "no final commit — nothing pending">

Issue reference: <number/URL, or "none">
```

Call `request_information` with choices `["Approved — push + PR", "Halt for now", "Other"]`. Freeform corrections are accepted via Other.

- **Approved → push + PR** → proceed to Step 6.
- **Halt for now** → output "Resume by re-invoking `/dreamers-close-out`. Branch state is preserved on `<branch-name>`." and stop. No push.
- **Other / corrections** → apply inline, re-run any affected steps (e.g. re-invoke Echo if docs missed something), and re-present this gate. Loop until approved.

This is the LAST point where the user can halt before the PR goes live.

## Step 6 — Push + PR (follow `pr-procedure.md` inline)

Read `pr-procedure.md` in full (must-read rule) and execute its procedure inline with the following inputs:

- Branch name + default branch name (from procedure inputs).
- Plan file paths (from procedure inputs).
- Retro file path (from Step 3 if FULL; omitted in LIGHT).
- Sentinel summary string (from procedure inputs).
- Issue reference (from procedure inputs, if applicable).
- Final commit hash (from Step 4, if any).

Capture the PR URL returned by `pr-procedure.md`.

## Step 7 — Plan archive (FULL only, whole-feature-directory)

The archive unit is the **whole feature directory** (`.dreamers/plans/feature-<slug>/`), not individual plan files. Mid-feature archiving (file-by-file) is NOT allowed.

**Trigger:** the feature is complete when ALL plans in `feature-<slug>/` have shipped (their PRs merged to main). For single-plan features this is one PR; for multi-plan features this is the last plan's PR.

**Procedure:**

1. Identify any feature directories at `.dreamers/plans/feature-<slug>/` whose plans are all referenced by merged PRs (excluding the PR just opened in Step 6, which is unmerged).
2. For each such complete feature, verify every plan's PR is merged via `gh pr view <number> --json state -q .state` returning `MERGED`. If ANY plan's PR is still open or in-flight, skip this feature — it is not yet ready to archive.
3. Move the entire feature directory: `mv .dreamers/plans/feature-<slug>/ .dreamers/plans/archive/` (create the archive dir if needed). Never delete files.

Skip silently if no complete feature directories are ready to archive.

LIGHT mode skips this step.

## Step 8 — Post-PR discipline (FULL only)

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

LIGHT mode skips this step.

---

## What happens after this procedure ends

- **`/dreamers-full`** (end-to-end pipeline): the milestone is complete. The orchestrator's todo records final phase complete. The skill exits with the PR URL.
- **`/dreamers-close-out`** (standalone, FULL or LIGHT mode): exit with success. Surface the PR URL + summary to the user.

This procedure does not touch the todo. The consuming skill maintains it.
