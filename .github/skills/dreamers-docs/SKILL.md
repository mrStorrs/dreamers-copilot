---
name: dreamers-docs
description: 'Standalone docs-update entry point. Spawns Echo to update Echo-owned sections of `.github/copilot-instructions.md` plus any other project docs affected by recent changes. Triggers: /dreamers-docs, update docs, echo docs update.'
argument-hint: '[--branch | --staged] (defaults to --branch: diff vs origin/<default>)'
---

## What this skill does

Standalone entry point for ad-hoc documentation updates. The user invokes this when they have made changes (manually or via another skill) and want Echo to update project docs without running a full close-out cycle.

The skill resolves the diff scope (feature-branch diff vs default, or staged-only) and spawns Echo as a subagent with that context. Echo audits the changed files, updates Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands), and surfaces any other project docs that need updates (README, CHANGELOG, project-specific docs).

Echo stages its edits with `git add` but does NOT commit. The user handles the commit after reviewing the diff.

---

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — git + comment discipline
- `~/.copilot/dreamers/refs/delegation.md` — Echo invocation protocol + subagent allowlist

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, Echo-owned section list, tech stack.

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Resolve diff scope (per `--branch` or `--staged` flag)
- [ ] Spawn Echo with changed-files context
- [ ] Capture doc changes + open questions from Echo output
- [ ] Surface result to the user

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

**Subagent prompt rule:** when spawning Echo below, include the line "Do NOT call `manage_todo_list`. The orchestrator owns the todo." in Echo's prompt. Per `orchestration-flow.md` § "Single-owner todo rule."

---

## Step 1 — Resolve diff scope

Parse `$ARGUMENTS`:

- `--branch` (default if no args) — scope to feature-branch diff vs default.
- `--staged` — scope to staged + unstaged changes on the current branch.

Detect the default branch (canonical two-step):

```bash
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
```

Resolve the changed-files list:

- `--branch` mode: `git diff --name-only origin/$DEFAULT...HEAD`
- `--staged` mode: union of `git diff --cached --name-only` and `git diff --name-only`

If the changed-files list is empty, output `No changes detected — nothing for Echo to document` and exit.

## Step 2 — Spawn Echo

Invoke Echo via the `task` tool:

- `agent_type: "echo"`, `mode: "sync"`

Pass in the prompt (per `delegation.md`):

- **Context:** ad-hoc documentation update; no plan binding. User wants project docs synced with recent changes.
- **Prior work:** changed-files list (from Step 1), diff base (`origin/$DEFAULT` for `--branch` mode, working tree for `--staged` mode).
- **What is needed:** review the changed files and update project docs as appropriate — Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands), plus README, CHANGELOG, or any project-specific docs the project conventions specify. Skip sections the change doesn't materially affect.
- **Constraints:** Echo edits docs ONLY — no production code, no tests. Stage edits with `git add` but do NOT commit (the user commits after review). **Do NOT call `manage_todo_list` — the orchestrator owns the todo.**
- **Definition of Done:** structured chat output per Echo's output discipline (status line + docs-changes log + instruction-file changes + comment audit + open questions).

Wait for Echo to signal completion. Capture the doc-changes log + any open questions.

## Step 3 — Handle Echo output

- **`Docs updated — N files changed`** → mark todo complete; proceed to Step 4 reporting.
- **`No doc updates needed`** → mark todo complete; tell the user no docs needed updating; exit.
- **Open questions raised** → surface each to the user via `request_information`. Capture answers. If an answer requires Echo to revise, re-spawn Echo with the clarification; if it's out-of-scope, note in the report and move on.

## Step 4 — Report

Tell the user:
- Files Echo touched (doc-changes log verbatim).
- Run `git status` + `git diff --cached` to review before committing.
- Suggested commit message: `docs: update for recent changes` (or appropriate).

This skill does NOT commit, does NOT push, does NOT open a PR. Echo's edits stay staged.

---

## What this skill does NOT do

- Does NOT commit Echo's edits — that's the user's call after review.
- Does NOT push or open a PR.
- Does NOT modify code or tests.
- Does NOT invoke any other skill. Echo is the only subagent spawned here.
- Does NOT spawn agents outside the 5-item allowlist (`sentinel`, `probe`, `hone`, `echo`, `sage`). In this skill, only Echo is used.
