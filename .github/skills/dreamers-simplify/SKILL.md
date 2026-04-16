---
name: dreamers-simplify
description: 'Run the Hone simplification pass on the current feature branch. Operates on the full feature-branch diff vs the default branch, followed by a Sentinel + Probe validation pass. Does not create branches or PRs. Triggers: /dreamers-simplify, run simplification, invoke hone.'
argument-hint: '(optional) path/to/plan.md'
---

### ⚠️ MANDATORY FIRST ACTIONS — do these before anything else, in this exact order

1. **Read ALL of the following refs** (no skipping):
   - `~/.copilot/dreamers/refs/delegation.md`
   - `~/.copilot/dreamers/refs/quality-gates.md`

2. **Confirm the active feature branch** — run `git branch --show-current`. If the working tree is on the default branch (typically `master` or `main`), stop and report: Hone must run on a feature branch, not the default branch.

3. **Detect the default branch** — run `git remote show origin | grep 'HEAD branch'` to resolve the default branch name dynamically. Never hardcode `main` or `master`.

---

## Invocation

This skill can be invoked:
- **Standalone:** `/dreamers-simplify` (optionally with a plan file path)
- **From a parent pipeline:** after all sub-plan cycles complete, before close-out

If a plan file path is provided in `$ARGUMENTS`, pass it to Hone as plan context.

---

## Pipeline

**This skill does NOT cut a new branch, push, or create a PR.**

### Step 1 — Delegate to Hone

Invoke Hone as a background subagent (`mode: "background"` + `read_agent(wait: true)`).

Pass Hone:
- Repo path (current working directory)
- Current branch name (from `git branch --show-current`)
- Default branch name (resolved above)
- Plan file path (if provided)

Hone will:
1. Run `git diff origin/<DEFAULT_BRANCH>...HEAD` to scope its work.
2. Edit only files that appear in that diff.
3. Make behavior-preserving simplifications only.
4. Stage all changes with `git add`.
5. Write `.dreamers/hone/simplification.md`.

Wait for Hone to complete and review its summary before proceeding.

### Step 2 — Sentinel validation pass

Invoke Sentinel as a background subagent (`mode: "background"` + `read_agent(wait: true)`).

Pass Sentinel:
- Path to `.dreamers/hone/simplification.md` (list of files Hone edited)
- Plan file path (if provided)
- Context: this is a post-Hone validation pass; review Hone's changes for correctness, security, and maintainability regressions

Wait for Sentinel to complete. If Sentinel blocks (critical/high findings), route to Forge before proceeding.

### Step 3 — Probe validation pass

Invoke Probe as a background subagent (`mode: "background"` + `read_agent(wait: true)`).

Pass Probe:
- Path to `.dreamers/hone/simplification.md`
- Plan file path (if provided)
- Context: this is a post-Hone validation pass; verify Hone's simplifications did not break existing behavior

Wait for Probe to complete.

---

## Completion

When all three steps complete and no blockers remain:

Report to the orchestrator:
- Hone complete: files edited, `simplification.md` path
- Sentinel: approved / approved with fixes / blocked (resolved)
- Probe: pass / fail (resolved)

The pipeline that invoked this skill may then proceed to close-out.
