---
name: dreamers-implement
description: 'Implementation-only entry point. Runs the canonical implementation procedure (`implementation-procedure.md`) for one plan. Exits at the cycle commit. Does NOT push or open a PR. Triggers: /dreamers-implement, implement this plan, execute the plan.'
argument-hint: 'feature-<slug>/plan-NN-<name>.md'
---

## What this skill does

Standalone entry point for implementing a single existing plan. The user invokes this when they want to run one implementation cycle and stop — to inspect the result before shipping, or to chain manually.

This skill follows `~/.copilot/dreamers/refs/implementation-procedure.md` end-to-end (Step 1 → Step 8) and exits cleanly at the commit. It does NOT push, does NOT open a PR, does NOT update docs. Those belong to close-out (`/dreamers-close-out` or `/dreamers-full`'s Phase 3).

This skill does NOT invoke any other skill. The user is in control of what runs next.

If the user wants the full pipeline (planning + implementation + close-out), they should run `/dreamers-full` instead.

---

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + logging + test-writing + git rules
- `~/.copilot/dreamers/refs/delegation.md` — subagent allowlist + forbidden list + protocol for invoking reviewers
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, staging, push discipline
- `~/.copilot/dreamers/refs/agent-recovery.md` — recovery if Sentinel/Probe/Hone crash mid-run
- `~/.copilot/dreamers/refs/implementation-procedure.md` — the procedure this skill follows
- `~/.copilot/dreamers/refs/plan-content.md` — plan structure (so the implementer knows what to expect)
- `~/.copilot/dreamers/refs/comment-rules.md` — comment discipline
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations
- `~/.copilot/dreamers/templates/logging-standards.md` — logging discipline

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, **test commands** (binding), build commands.
- `.github/instructions/build.instructions.md` (root, if present) — user-testing build/distribute playbook.
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.
- `./test-benchmarks.md` (root, if present) — test run-time benchmarks for timeout selection.

If no plan path is provided in `$ARGUMENTS`, halt and ask the user — do not invent or skip the plan.

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Read implementation-procedure.md
- [ ] Read plan file
- [ ] Step 1 — write failing tests
- [ ] Step 2 — implement (inline)
- [ ] Step 3 — type-check + run tests
- [ ] Step 4 — coverage sweep
- [ ] Step 5 — parallel review (Sentinel + Probe + Hone)
- [ ] Step 6 — apply reviewer findings + re-run tests
- [ ] Step 7 — user testing (if plan requires it)
- [ ] Step 8 — commit the cycle

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**Subagent prompt rule:** when this skill spawns Sentinel / Probe / Hone in Step 5, include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in each subagent's prompt. Per `orchestration-flow.md` § "Single-owner todo."

---

## MANDATORY first actions (in order, once at skill entry)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note.

2. **Branch setup (inline, per `git-workflow.md`):**
   - Detect default branch (canonical two-step):
     ```bash
     DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
     [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
     ```
   - **Anchor to remote truth (mandatory before reading any `.dreamers/` files):** `git fetch origin && git log origin/$DEFAULT --oneline -5`.
   - If currently on default branch: `git checkout $DEFAULT && git pull origin $DEFAULT`, then cut `feat/<slug>` from `$DEFAULT`.
   - If already on a feature branch: confirm via `git branch --show-current`. Stay on it.
   - Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edits.

3. **Branch identity check** — `git log --oneline -3`. Confirm branch + recent commits match the expected feature.

---

## Procedure

Follow `~/.copilot/dreamers/refs/implementation-procedure.md` Step 1 through Step 8, exactly as written. The procedure handles:

- Writing failing tests against the plan's ACs (Step 1)
- Inline implementation with the HARD STOP block on agent spawning (Step 2)
- Type-checking + running tests (Step 3)
- Coverage sweep (Step 4)
- Parallel Sentinel + Probe + Hone review (Step 5)
- Orchestrator-as-fixer applying findings (Step 6)
- User-testing pause if `User-testing-required: yes` in the plan (Step 7)
- Final commit with the `Plan: feature-<slug>/plan-NN-<name>` body line (Step 8)

Update this skill's todo as each step completes.

---

## Exit behavior

On Step 8 commit, exit with success. Tell the user:
- Commit hash + summary.
- AC coverage matrix.
- Reviewer status (Sentinel + Probe + Hone).
- Next step (their choice): more cycles (next plan, another `/dreamers-implement` invocation), OR `/dreamers-close-out` if all plans are shipped.

This skill does NOT proceed to close-out automatically. The user is in control.

---

## Push discipline

`git push` does NOT happen in this skill. Push happens exactly once at PR close-out via `pr-procedure.md` (invoked from `close-out-procedure.md` Step 6).

---

## What this skill does NOT do

- Does NOT push.
- Does NOT open a PR.
- Does NOT update docs (Echo is invoked at close-out, not here).
- Does NOT invoke `/dreamers-close-out` or any other skill. The user runs close-out themselves when ready.
- Does NOT spawn agents outside the 5-item allowlist (`sentinel`, `probe`, `hone`, `echo`, `sage`). In this skill, only Sentinel + Probe + Hone are used (in Step 5).
