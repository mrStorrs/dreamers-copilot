---
name: dreamers-review
description: 'Sentinel-backed code review with arg-flag invocation. Reviews through correctness/security/maintainability lenses and fixes issues on sight in production-code lane. Triggers: /dreamers-review, review my code, review staged changes, review the branch.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Wraps the Sentinel agent for ergonomic standalone invocation. Sentinel reviews through three lenses (correctness, security, maintainability), fixes issues directly in production code, and reports a severity-graded fixes-applied list in chat.

Test files are Probe's domain — Sentinel only edits test-file comments to enforce comment-rules.

$ARGUMENTS

---

## Argument parsing

Default scope (no flags): staged + unstaged changes.

- `--branch` — scope to feature-branch diff vs default branch:
  ```bash
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
  # scope = files in `git diff origin/$DEFAULT...HEAD --name-only`
  ```
- `--paths <glob>` — scope to files matching the glob (e.g. `--paths "src/**/*.ts"`).
- `--all` — entire codebase. Emit a chat warning before invoking; rare.

---

## Invocation modes

- **Standalone:** user invokes directly with arg flags; this skill runs in the main thread and spawns Sentinel.
- **From orchestrator:** `/dreamers-full` and `/dreamers-implement` may call this in lieu of a direct `task(agent_type: "sentinel", ...)` call. Functionally identical.

---

## Spawn Sentinel

`task(agent_type: "sentinel", mode: "sync")` with prompt that includes:
- The scope (file list or diff range derived from arg flags)
- The plan file path if available in the calling context (else "no plan; review against general standards in `comment-rules.md`, `logging-standards.md`, and the three review lenses")
- Any additional context from the orchestrator

---

## Output

Chat output is Sentinel's chat output (passed through):
- Status line — `Approved — no fixes needed`, `Fixed and approved — N fixes applied`, or `Blocked — <reason>`
- Severity-graded fixes-applied list (if any) — `[SEVERITY] file:line — what was wrong → what was fixed`
- Plan-alignment summary
- Risk notes (if any)
