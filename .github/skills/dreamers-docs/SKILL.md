---
name: dreamers-docs
description: 'Echo-backed documentation update with arg-flag invocation. Updates README, CHANGELOG, project .github/copilot-instructions.md (Echo-owned sections), and other project docs based on changes. Triggers: /dreamers-docs, update docs, document changes.'
argument-hint: '[--branch] [--staged]'
---

## What this skill does

Wraps the Echo agent for ergonomic standalone invocation. Echo updates project documentation based on the change scope.

$ARGUMENTS

---

## Argument parsing

Default scope (no flags): staged changes.

- `--staged` — explicit staged scope (same as default).
- `--branch` — scope to feature-branch diff vs default:
  ```bash
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
  ```

---

## Invocation modes

- **Standalone:** user invokes for ad-hoc doc updates.
- **From orchestrator:** `/dreamers-full` and `/dreamers-implement` invoke at end-of-session per `close-out.md`. Functionally identical.

---

## Spawn Echo

`task(agent_type: "echo", mode: "sync")` with prompt that includes:
- The scope (`--staged` or `--branch` resolved to a `git diff` range or `git diff --staged`)
- List of changed files (`git diff --name-only <range>`)
- The plan file path if available
- A one-paragraph summary of what was reviewed/fixed (if context available, else "ad-hoc doc update")

---

## Output

Chat output is Echo's chat output (passed through):
- Status line (`Docs updated — N files changed` or `No doc updates needed`)
- Doc-changes log: one bullet per doc file touched
- Comment audit results (or "no violations")
- Open questions (if any)
