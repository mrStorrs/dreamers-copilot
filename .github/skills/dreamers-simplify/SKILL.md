---
name: dreamers-simplify
description: 'Standalone focused Vigil review (architectural quality). Read-only — reads Vigil's `.dreamers/reviews/` artifact for over-engineering, premature abstractions, redundancy, and bad architecture. May recommend full refactors. No auto-fix. Triggers: /dreamers-simplify, simplify this, audit for over-engineering, architectural review.'
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

<dreamers-kernel>
# Dreamers Kernel

## User overrides

Explicit user instructions can skip or alter phases/actions.

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
- `--all` — entire codebase. Vigil's simplicity lens (over-engineering, architectural quality) is well-suited to full-codebase audits; less of a warning here than for review / test.

---

## Spawn Vigil

Invoke via the runtime's subagent-spawn mechanism:

```
agent_type: "vigil"
mode: "sync"
prompt:
  Context: Standalone focused Vigil audit via /dreamers-simplify. No plan binding (ad-hoc audit).
  Scope: <list of files from arg parsing above>
  Branch: <current feature branch>
  Default branch: <detected default>
  Focus: simplicity / over-engineering / redundancy / bad architecture. Recommend full refactors when warranted, while still reporting critical correctness/security/maintainability/test-coverage findings if they appear.
  Write: exactly one .dreamers/reviews/vigil-*.md artifact.
  Return: status + counts + artifact path + blocked reason + open questions only.
```

## Output

Read the artifact path returned by Vigil and pass the artifact contents through to the user verbatim. Do NOT apply any of the suggested fixes / refactors — this is a read-only audit. Surface any `Blocked` status or open questions for user follow-up.

If Vigil recommends a large refactor, suggest: "Run `/dreamers-plan` to scope the refactor, then `/dreamers-full` to execute it."
