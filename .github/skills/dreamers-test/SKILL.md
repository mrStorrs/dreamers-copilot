---
name: dreamers-test
description: 'Standalone Probe review (test coverage audit). Read-only — returns structured findings on AC coverage, layer audit, edge cases, regression risks. No auto-fix. Triggers: /dreamers-test, test coverage audit, audit tests, check test gaps.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Spawns just Probe (one of the three pipeline reviewers) for a standalone test-coverage audit. Read-only — Probe reads the code and tests in scope, identifies coverage gaps + edge case misses + regression risks, returns structured findings. No orchestrator-as-fixer step. If you want missing tests written, take the findings and run `/dreamers-implement` with a plan that adds them.

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — for the structured findings format spec Probe uses.
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations.

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
- `--all` — entire codebase. Emit a chat warning before invoking; rare.

---

## Spawn Probe

Invoke via the runtime's subagent-spawn mechanism:

```
agent_type: "probe"
mode: "sync"
prompt:
  Context: Standalone test-coverage audit via /dreamers-test. No plan binding (ad-hoc audit).
  Scope: <list of files from arg parsing above>
  Branch: <current feature branch>
  Default branch: <detected default>
  Lens: test coverage (AC matrix is N/A here — no plan binding; focus on layer audit + edge cases + regression risks for the scope).
  Return: status line + severity-graded findings + observations + open questions.
```

## Output

Pass Probe's chat output through to the user verbatim. Do NOT write any tests — this is a read-only audit. Surface any `Blocked` status or open questions for user follow-up.

If the user wants missing tests written from the findings, suggest: "Run `/dreamers-implement` with a plan that addresses these coverage gaps."
