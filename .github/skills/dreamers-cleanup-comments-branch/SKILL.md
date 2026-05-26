---
name: dreamers-cleanup-comments-branch
description: 'Branch-scoped comment cleanup. Same as /dreamers-cleanup-comments but scoped to the current feature-branch diff. Standalone pre-PR comment sweep. Triggers: /dreamers-cleanup-comments-branch, comment cleanup branch scope, pre-PR comment sweep.'
argument-hint: '(no args; scope is automatic from the current branch diff)'
---

## What this skill does

Branch-scoped variant of `/dreamers-cleanup-comments`. Audits and cleans comment-rules violations on the feature-branch diff only (files in `git diff origin/<DEFAULT>...HEAD --name-only`). Identical phase structure: audit → propose → user approval → apply inline → optional Sentinel review → commit.

Standalone utility — invoke directly when you want a comment sweep limited to the changes this branch introduced (typical use: pre-PR polish on a feature branch).

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


<comment-rules>
<!-- GENERATED from .github/dreamers/refs/comment-rules.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Comment Rules

## Core principle
Comments must add value that the code cannot express itself. Concise, no fluff, no separators — value only.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes
- License headers

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

## Strict prohibitions
- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words
</comment-rules>

<dreamers-kernel>
<!-- GENERATED from .github/dreamers/refs/dreamers-kernel.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Dreamers Kernel

Universal rules. Inlined at the bottom of every Dreamers skill + agent by `scripts/sync-refs.ps1`.

## Subagent allowlist (HARD RULE)

The only `agent_type` values a skill may pass to `task()`:
- `sentinel`, `probe`, `hone`, `echo`, `sage`

Forbidden: `general-purpose`, `claude`, `claude-code-guide`, `Explore`, `Plan`, `bolt`, or any non-Dreamers agent. Exception: only if the user explicitly authorizes a fallback in the current run.

## Single-owner todo

Each user-invoked skill owns its own todo for its run. When skills compose (e.g., `/dreamers-full` invokes `/dreamers-implement`), the called skill creates its own todo on entry and closes it on exit. Sub-skills do not touch the caller's todo.

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
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```
</dreamers-kernel>

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1 — audit branch-diff scope for comment-rules violations
- [ ] Phase 2 — proposal + user approval
- [ ] Phase 3 — apply cleanup inline
- [ ] Phase 4 — optional Sentinel review (if requested)
- [ ] Phase 5 — commit

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Scope detection

Detect default branch (canonical two-step):
```bash
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
```

Fetch the remote before computing the diff (otherwise a stale local `origin/$DEFAULT` will produce a wrong or empty file list):
```bash
git fetch origin
```

If `git rev-parse origin/$DEFAULT` fails after the fetch, halt with: "Could not resolve `origin/$DEFAULT`. Check your remote configuration."

Scope = files in `git diff origin/$DEFAULT...HEAD --name-only`.

If the working tree is on the default branch (no feature-branch diff), halt with an error: "This skill operates on a feature branch's diff. Use `/dreamers-cleanup-comments` for project-wide cleanup."

---

## Phases

Phases 1–5 are identical to `/dreamers-cleanup-comments`, scoped to the branch-diff file list:

1. **Audit** the branch-diff scope; categorize comment-rules violations.
2. **Propose** changes; `request_information` for approval.
3. **Apply** changes inline; stage with `git add`.
4. **Optional Sentinel review** of changed files.
5. **Commit** with message `chore: comment cleanup on feature branch`. Do NOT push.

## When this skill is the right tool

- Pre-PR polish — after a feature is done, before opening the PR, when you want the branch's comments inspected before they ship.
- Targeted clean-up scoped to the changes a single feature branch introduced, without auditing the entire project.

For project-wide cleanup (not branch-scoped), use `/dreamers-cleanup-comments`.
