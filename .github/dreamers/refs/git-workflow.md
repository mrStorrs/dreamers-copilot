# Git workflow

Apply the git steps owned by the active phase. Implementation-only work stops before commits, pushes, and PRs.

## Startup and branch

1. Run `git status --short --branch` and inspect existing changes. Preserve work already present; do not reset, discard, or silently include unrelated edits.
2. Resolve the default branch with `git symbolic-ref --short refs/remotes/origin/HEAD` and remove the leading `origin/`; if unavailable, use `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`. Do not assume main. Run `git fetch origin` and `git log --oneline -5 origin/<default>` before treating local plans as current project state. An unavailable base blocks new branch setup.
3. New work starts on feat/<slug> or fix/<slug> from updated `origin/<default>`. Resume an authorized feature branch when one already exists. When an outer delivery skill established the branch, reuse it.
4. Before the first edit, check `git branch --show-current` and `git log --oneline -3` against the intended feature. Stop on an unexplained mismatch; never implement directly on the default branch. Keep .dreamers/ gitignored. Use a worktree only on user direction.

## Delivery commits and PRs

- Stage explicit paths. The delivery owner commits once per plan/cycle after review fixes, green validation, and required user testing. Include final docs and close-out edits before the PR; skip an empty commit.
- Use the project's conventional commit style. Include `Plan: feature-<slug>/plan-NN-<name>` when applicable and this trailer:

    Co-authored-by: The Dreamers System

- ATOMIC intermediate cycles commit locally without pushing. INCREMENTAL cycles each have their own approved PR; wait for merge confirmation before starting the next branch from updated default.
- At PR close-out, obtain the existing pre-PR approval, then `git push -u origin <branch>` and create the PR. Never force-push or bypass hooks. Reconcile a rejected push before retrying.
- After a PR opens, further commits and pushes need user authorization. /dreamers-pr-resolve authorizes its fix commit and retains its push approval gate. Do not ask again for authorization already given.
