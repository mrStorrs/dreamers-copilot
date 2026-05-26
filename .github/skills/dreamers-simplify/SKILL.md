---
name: dreamers-simplify
description: 'Standalone Hone review (architectural quality). Read-only — returns structured findings on over-engineering, premature abstractions, redundancy, and bad architecture. May recommend full refactors. No auto-fix. Triggers: /dreamers-simplify, simplify this, audit for over-engineering, architectural review.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

## What this skill does

Spawns just Hone (one of the three pipeline reviewers) for a standalone architectural-quality audit. Read-only — Hone hunts over-engineering, premature abstractions, redundancy, dead code, and bad architecture. May recommend full refactors when implementation is poor. Returns structured findings. No orchestrator-as-fixer step. If you want findings applied, take them to `/dreamers-implement`.

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


<dreamers-kernel>
# Dreamers Kernel

## Subagent allowlist (HARD RULE)

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Continuation principle

At every natural pause between phases — where the skill has produced a meaningful result and the user could redirect — call `request_information` with three choices: `Continue` / `Halt for now` / `Other` (freeform). Never silently advance; never silently stop. On `Halt`, emit a one-line resume command and stop.

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

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
