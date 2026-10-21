---
name: dreamers-cleanup-comments-branch
description: 'Branch-scoped comment cleanup. Same as /dreamers-cleanup-comments but scoped to the current feature-branch diff. Standalone pre-PR comment sweep. Triggers: /dreamers-cleanup-comments-branch, comment cleanup branch scope, pre-PR comment sweep.'
argument-hint: '(no args; scope is automatic from the current branch diff)'
---

$ARGUMENTS

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

## Cleanup

Read [comment-cleanup-workflow](../../dreamers/refs/comment-cleanup-workflow.md), resolving the link relative to this file, and execute it inline with the explicit branch-diff file list and commit message `chore: comment cleanup on feature branch`. Keep this skill's scope and todo throughout; an empty diff means no cleanup.
