---
name: dreamers-docs
description: 'Docs skill — spawns Echo to update Echo-owned sections of .github/copilot-instructions.md plus other project docs (README, CHANGELOG) affected by recent changes. Echo stages edits; does not commit. Triggers: /dreamers-docs, update docs, echo docs update.'
---

- Run from the target worktree. Standalone runs, delivery close-out, and PR follow-up use this same handoff.
- Start a fresh Echo with `task(agent_type: "echo", mode: "sync")` and no inherited conversation. Its entire prompt is:

  > Update the documentation for all changes in this worktree and branch since it diverged from main.

- Wait for Echo and report its staged documentation changes, any open questions, or that no updates were needed. Resolve questions that affect accuracy with the user before close-out. Apply approved documentation clarifications in the caller.

## Exit
- Files Echo touched. The caller commits (this skill does NOT commit, push, or open a PR).

## Dreamers Kernel
<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Echo uses the sole prompt defined in `/dreamers-docs`. All other `task()` invocations MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>
