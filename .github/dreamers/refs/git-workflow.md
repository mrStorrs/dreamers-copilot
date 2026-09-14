# Git workflow

1. Before reading local plans as current project state, identify the default branch from origin/HEAD or gh repo view and fetch origin. Inspect recent default-branch commits.
2. For new delivery work, branch from the updated default branch as feat/<slug> or fix/<slug>. Preserve existing work; resume an authorized feature branch instead of recutting it. Worktrees require user direction. Keep .dreamers/ gitignored.
3. Stage explicit paths. Commit once per plan/cycle after review fixes, green validation, and required user testing; include final docs/close-out edits before the PR. Use the project's conventional commit style, a Plan: feature-<slug>/plan-NN-<name> body line when applicable, and this trailer:

    Co-authored-by: The Dreamers System

4. Push at PR close-out, after its approval gate, then create the PR. Intermediate ATOMIC cycles stay local; INCREMENTAL cycles each have their own approved PR.
5. After a PR opens, further commits and pushes require user authorization. /dreamers-pr-resolve authorizes its fix commit and retains its explicit push gate.
