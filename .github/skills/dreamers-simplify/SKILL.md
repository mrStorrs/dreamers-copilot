---
name: dreamers-simplify
description: 'Run Hone simplification (fix-on-sight) on the current feature branch + a single project-defined test/lint pass. Operates on the full feature-branch diff vs the default branch. Does not create branches or PRs. Triggers: /dreamers-simplify, run simplification, invoke hone.'
argument-hint: '(optional) [--paths <glob>] [--all]'
---

## MANDATORY first actions (in order)

1. **Confirm the active feature branch** — run `git branch --show-current`. If the working tree is on the default branch (typically `master` or `main`), stop and report: Hone must run on a feature branch, not the default branch.

2. **Detect the default branch** — canonical two-step (never hardcode):
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```

---

## Invocation modes

This skill can be invoked:
- **Standalone:** `/dreamers-simplify` (default scope: full feature-branch diff vs default — Hone's natural scope), `/dreamers-simplify --paths "src/**/*.ts"` (subset of branch diff), `/dreamers-simplify --all` (entire codebase — use sparingly; emit a chat warning before invoking).
- **From a parent pipeline:** `/dreamers-full` and `/dreamers-implement` invoke this at end-of-session, before close-out. The default branch-diff scope is what the orchestrator wants.

Pass any provided plan file path to Hone as plan context.

---

## Pipeline

**This skill does NOT cut a new branch, push, or create a PR.**

### Step 1 — Hone fix-on-sight

Invoke Hone via `task(agent_type: "hone", mode: "sync")`.

Pass Hone:
- Repo path (current working directory)
- Current branch name (from `git branch --show-current`)
- Default branch name (resolved above)
- Scope: branch diff (default), `--paths <glob>`, or `--all` per arguments
- Plan file path (if provided)

Hone will:
1. Run `git diff origin/<DEFAULT_BRANCH>...HEAD` (or scoped equivalent).
2. Edit files fix-on-sight (behavior-preserving simplifications only).
3. Stage edits with `git add`.
4. Report files-edited list, simplifications-not-made, and observations in chat output.

Wait for Hone to complete and review its summary before proceeding.

### Step 2 — Project-defined test/lint pass (delegate to Bolt)

Look up the project's test/lint command(s) from the project-level `.github/copilot-instructions.md` (look for "Build", "Test", "Lint", or equivalent sections).

Invoke **Bolt** via `task(agent_type: "bolt", mode: "sync")` to run the commands and report results. Do not run the commands inline — Bolt is the mechanical executor.

- If the project defines both `test` and `lint`: have Bolt run them sequentially. Report combined pass/fail.
- If only one is defined: have Bolt run that one.
- If neither is defined: skip with a chat warning. Hone's fix-on-sight scope is behavior-preserving by definition, so the absence of an automated check is degraded but not broken.

### Step 3 — Handle failures

If the test/lint pass fails:
- Surface the failure in chat output.
- Route to Forge (or Sentinel for production-code regressions caused by simplifications) for fix.
- Do NOT silently ship a failing branch.

If the test/lint pass succeeds (or is skipped per above): signal completion.

---

## Completion

Report to the orchestrator (or to chat if standalone):
- **Hone status:** files edited count, observations (if any)
- **Test/lint status:** pass / fail / skipped (with reason)
- **Next step:** if invoked from a parent pipeline, the parent proceeds to Echo + close-out. If standalone, the user reviews the diff.

The pipeline that invoked this skill may then proceed to close-out.
