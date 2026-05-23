---
name: dreamers-simplify
description: 'Standalone Hone review (architectural quality). Read-only — returns structured findings on over-engineering, premature abstractions, redundancy, and bad architecture. May recommend full refactors. No auto-fix. Triggers: /dreamers-simplify, simplify this, audit for over-engineering, architectural review.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Spawns just Hone (one of the three pipeline reviewers) for a standalone architectural-quality audit. Read-only — Hone hunts over-engineering, premature abstractions, redundancy, dead code, and bad architecture. May recommend full refactors when implementation is poor. Returns structured findings. No orchestrator-as-fixer step. If you want findings applied, take them to `/dreamers-implement`.

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — for the structured findings format spec Hone uses.

$ARGUMENTS

---

## Argument parsing

Default scope (no flags): staged + unstaged changes.

- `--branch` — scope to feature-branch diff vs default:
  ```bash
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
  ```
- `--paths <glob>` — scope to files matching the glob.
- `--all` — entire codebase. Hone's lens (over-engineering, architectural quality) is well-suited to full-codebase audits; less of a warning here than for review / test.

---

## Spawn Hone

Invoke via the runtime's subagent-spawn mechanism:

```
agent_type: "hone"
mode: "sync"
prompt:
  Context: Standalone architectural-quality audit via /dreamers-simplify. No plan binding (ad-hoc audit).
  Scope: <list of files from arg parsing above>
  Branch: <current feature branch>
  Default branch: <detected default>
  Lens: simplicity / over-engineering / redundancy / bad architecture. Recommend full refactors when warranted.
  Return: status line + severity-graded findings + observations + open questions.
```

## Output

Pass Hone's chat output through to the user verbatim. Do NOT apply any of the suggested fixes / refactors — this is a read-only audit. Surface any `Blocked` status or open questions for user follow-up.

If Hone recommends a large refactor, suggest: "Run `/dreamers-plan` to scope the refactor, then `/dreamers-full` to execute it."
