---
name: dreamers-cleanup-comments-branch
description: 'Feature-branch comment cleanup pass — clean up comments in files changed on the current feature branch only. Does NOT checkout the default branch, cut a new branch, or open a PR. For use inside parent pipelines (e.g. dreamers-full). Triggers: /dreamers-cleanup-comments-branch.'
---

Run a comment cleanup pass scoped to the current feature branch. This skill is for in-pipeline use — it operates only on files changed on the current branch and leaves branch and PR ownership entirely with the parent pipeline.

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

**Step 1 — Identify changed files**

Fetch the latest remote refs, then determine which files have been changed on the current branch relative to the default branch:

```bash
git fetch origin 2>/dev/null || true
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
git diff --name-only "origin/$DEFAULT_BRANCH"...HEAD
```

If there are no changed files, report that and stop — nothing to clean.

**Step 2 — Forge's task — comment cleanup (non-negotiable)**

Invoke Forge (follow `~/.copilot/dreamers/refs/delegation.md`). Pass Forge:
- The list of changed files from Step 1
- The rule source: `~/.copilot/dreamers/refs/comment-rules.md` — those are the authoritative rules
- Constraint: scan and edit only the files in the changed-files list; do not touch logic, formatting, structure, or files not in the list

Forge stages any changes with `git add`. No commit — staging only.

**Step 3 — Report**

After Forge completes, report in chat:
- Files reviewed
- Files changed (with a one-line summary of what was cleaned per file)
- Files with no changes needed

Do not push, do not open a PR. The parent pipeline owns the branch and the eventual PR.
