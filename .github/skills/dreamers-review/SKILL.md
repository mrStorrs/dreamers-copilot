---
name: dreamers-review
description: 'Standalone Sentinel review (correctness / security / maintainability). Read-only — returns structured findings without applying fixes. For ad-hoc audits outside the full pipeline. Triggers: /dreamers-review, review my code, audit correctness, audit security.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Spawns just Sentinel (one of the three pipeline reviewers) for a standalone correctness / security / maintainability audit. Read-only — Sentinel returns structured findings; no orchestrator-as-fixer step. If you want fixes applied, take the findings and run `/dreamers-implement` with a fix plan, or invoke `/dreamers-full` for a full cycle.

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — for the structured findings format spec Sentinel uses.

$ARGUMENTS

---

## Argument parsing

Default scope (no flags): staged + unstaged changes.

- `--branch` — scope to feature-branch diff vs default:
  ```bash
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
  # scope = files in `git diff origin/$DEFAULT...HEAD --name-only`
  ```
- `--paths <glob>` — scope to files matching the glob.
- `--all` — entire codebase. Emit a chat warning before invoking; rare.

---

## Spawn Sentinel

Invoke via the Agent tool:

```
agent_type: "sentinel"
mode: "sync"
prompt:
  Context: Standalone review via /dreamers-review. No plan binding (ad-hoc audit).
  Scope: <list of files from arg parsing above>
  Branch: <current feature branch>
  Default branch: <detected default>
  Lenses: correctness, security, maintainability (the three canonical Sentinel lenses).
  Plan-alignment summary: mark N/A — no plan binding.
  Return: status line + severity-graded lane-labelled findings + open questions.
```

Wait for Sentinel to signal completion. Read its chat output.

## Output

Pass Sentinel's chat output through to the user verbatim. Do NOT apply fixes — this is a read-only audit. Surface any `Blocked` status or open questions for user follow-up.

If the user wants fixes applied from the findings, suggest: "Run `/dreamers-implement` with a plan that addresses these findings, or `/dreamers-full` for a full cycle."
