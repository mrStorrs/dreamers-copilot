---
name: dreamers-cleanup-comments-branch
description: 'Branch-scoped comment cleanup. Same as /dreamers-cleanup-comments but scoped to the current feature-branch diff. Standalone pre-PR comment sweep. Triggers: /dreamers-cleanup-comments-branch, comment cleanup branch scope, pre-PR comment sweep.'
argument-hint: '(no args; scope is automatic from the current branch diff)'
---

## What this skill does

Branch-scoped variant of `/dreamers-cleanup-comments`. Audits and cleans comment-rules violations on the feature-branch diff only (files in `git diff origin/<DEFAULT>...HEAD --name-only`). Identical phase structure: audit → propose → user approval → apply inline → optional Sentinel review → commit.

Standalone utility — invoke directly when you want a comment sweep limited to the changes this branch introduced (typical use: pre-PR polish on a feature branch).

## Pre-flight reads

- `~/.copilot/dreamers/refs/comment-rules.md`
- `~/.copilot/dreamers/refs/orchestrator-discipline.md`

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
