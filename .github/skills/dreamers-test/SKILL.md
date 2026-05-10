---
name: dreamers-test
description: 'Probe-backed test pass with arg-flag invocation. Writes/runs tests, fixes test-file issues on sight, reports production bugs for Sentinel routing. Triggers: /dreamers-test, run tests, write tests, test coverage check.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Wraps the Probe agent for ergonomic standalone invocation. Probe writes tests against the AC coverage matrix, runs them, fixes test-file issues directly. Production code bugs are recorded in `.dreamers/probe/bugs.md` for orchestrator routing back to Sentinel.

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
- `--all` — entire codebase. Emit a chat warning before invoking.

---

## Invocation modes

- **Standalone:** user invokes directly; this skill runs in the main thread and spawns Probe.
- **From orchestrator:** `/dreamers-full` and `/dreamers-implement` may call this in lieu of a direct `task(agent_type: "probe", ...)` call. Functionally identical.

---

## Spawn Probe

`task(agent_type: "probe", mode: "sync")` with prompt that includes:
- The scope (file list or diff range derived from arg flags)
- The plan file path if available (else "ad-hoc test pass against general AC")
- User-bug flag if applicable (triggers Probe's `regression-analysis.md` output)

---

## Output

Chat output is Probe's chat output (passed through):
- Brief summary (pass / fail / partial)
- Paths to `test-plan.md`, `runbook.md`, `bugs.md` (and `regression-analysis.md` if user-bug)
- Bug count and severity (if any failures)
- Production bugs found (if any) flagged for orchestrator routing to Sentinel
