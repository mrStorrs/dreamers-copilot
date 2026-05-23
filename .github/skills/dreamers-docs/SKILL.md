---
name: dreamers-docs
description: 'Docs-update phase of the Dreamers pipeline. Spawns Echo to update Echo-owned sections of `.github/copilot-instructions.md` plus any other project docs affected by the change. Invokable standalone (--branch or --staged scope) or composed from `/dreamers-close-out`. Triggers: /dreamers-docs, update docs, echo docs update.'
argument-hint: '[--branch | --staged] (composed mode passes full inputs)'
---

## What this skill does

Wraps the Echo subagent for project-documentation updates. Echo audits the changed files for the cycle, updates Echo-owned sections of the project-level `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands), and surfaces any other project docs that need updates (README, CHANGELOG, project-specific docs).

Echo stages its edits with `git add` but does NOT commit. The caller (orchestrator `/dreamers-close-out` or the user) handles the final commit.

## Pre-flight reads

Read these refs once at startup:

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — for the closeout-discipline section's framing of Echo's role.
- `~/.copilot/dreamers/refs/close-out.md` — Echo's contract within the close-out flow.

Echo agent reads its own startup files internally — this skill does not duplicate them here.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Spawn Echo with changed-files context
- [ ] Capture doc changes and open questions from Echo output
- [ ] Report completion (doc-changes log + open questions) to caller

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-close-out`, do NOT declare a new list — update the parent's matching Step 2 item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## Invocation modes

### Composed mode (called by `/dreamers-close-out`)

The orchestrator passes a full prompt to this skill including:
- Plan file paths (list of plans shipped in this milestone)
- Changed-files list (output of `git diff --name-only origin/<DEFAULT>...HEAD`)
- Diff base (`origin/<DEFAULT_BRANCH>`)
- Sentinel summary string (concatenated chat outputs from Sentinel across all cycles)

The skill forwards these to Echo's invocation prompt.

### Standalone mode (user invokes directly)

Argument parsing:
- `--branch` (default if no args) — scope to feature-branch diff vs default. Echo runs `git diff --name-only origin/<DEFAULT>...HEAD` to discover changed files.
- `--staged` — scope to staged + unstaged changes. Echo runs `git diff --cached --name-only` + `git diff --name-only`.

For standalone mode, this skill:
1. Detects the default branch (canonical two-step):
   ```bash
   DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
2. Resolves the changed-files list per the arg flag.
3. Looks at `.dreamers/plans/` for plan files that correspond to the changed files (best-effort match — if uncertain, asks Echo to discover).
4. There is no orchestrator-provided Sentinel summary in standalone mode; this skill passes `"Standalone invocation — no Sentinel summary available"` instead. Echo's prompt already directs it to use the changed-files list as its primary signal.

---

## Spawn Echo

Invoke Echo via the runtime's subagent-spawn mechanism:

```
agent_type: "echo"
mode: "sync"
prompt:
  Context: pipeline docs update. The orchestrator did the implementation inline.
  Plan file(s): <absolute paths to the plan(s) shipped this milestone; or "none — standalone invocation, discover from .dreamers/plans/" in standalone mode>
  Changed files: <output of the resolved git diff per scope>
  Diff base: origin/<DEFAULT_BRANCH>
  Sentinel summary: <one-paragraph concatenation of Sentinel chat outputs across all cycles; or "Standalone invocation — no Sentinel summary available" in standalone mode>
  When no Sentinel summary is available, use the changed-files list as the primary signal for what shipped.
  Scope: update Echo-owned sections of `.github/copilot-instructions.md` (Tech stack, Repo structure, Conventions, Key files, Test commands) plus any other project docs (README, CHANGELOG, TESTING.md, etc.) that need updates based on what shipped. Skip sections the change doesn't materially affect.
  Return: doc-changes log + open questions (use "none" if empty) in chat output.
```

Wait for Echo to signal completion. Read its chat output.

---

## Handle Echo output

- **`Docs updated — N files changed`** → skill complete. Pass Echo's chat output back to caller.
- **`No doc updates needed`** → skill complete. Caller can skip the final commit step for docs.
- **Open questions raised** → surface each question to the user before declaring complete. Capture user answers, then route by scope: if the answer changes what Echo should write (e.g., which docs to update, what wording to use) → re-invoke Echo with the clarification; if the answer is upstream policy or out-of-scope for docs (e.g., "should we add a deprecation flag in code") → note in the retro and report back to the caller without re-invoking Echo.

Echo's staged edits remain in the working tree for the caller to commit.

---

## Exit behavior

When called **standalone**, the user is expected to commit Echo's staged edits if they want them landed. Tell the user:
- Files Echo touched.
- Run `git status` + `git diff --cached` to review before `git commit`.

When called **from `/dreamers-close-out`**, the orchestrator handles the final commit. Return in chat output:
- Echo's doc-changes log (verbatim).
- Open questions (if any).
- Confirmation that staged edits are ready for the close-out's final commit step.

This skill does NOT push, does NOT open a PR, does NOT commit. Echo stages; the caller commits.
