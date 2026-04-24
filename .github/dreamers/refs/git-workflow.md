# Git Workflow (mandatory)

Every milestone uses a feature branch + PR — never work directly on the default branch.

## Startup verification (do this FIRST)
1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

## Branch setup (before invoking Forge)
1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Review all persistent workspace files across agents (`assumptions.md`, `decisions.md`, `questions.md`, `links.md`) — prune stale/resolved entries.
4. Wipe all live files across **all** agents — every file in this list must be reset to "No active work / No pending items":
   - `forge/status.md`, and any `forge/implementation*.md`
   - `probe/status.md`, `probe/bugs.md`, `probe/test-plan.md`, `probe/runbook.md`, and any `probe/*-test-plan.md`
   - `sentinel/status.md`, `sentinel/findings.md`, `sentinel/review.md`
   If any file still contains prior-milestone content after this step, it is a protocol failure.
   **Wipe mechanism:** Use Bash `printf 'content' > path` for each file — do NOT use the Write tool for wipes.
5. **Clean up prior feature's plan files** — check if the previous feature's PR is merged (`gh pr list --state merged` or `gh pr view <number>`):
   - **Merged:** delete all plan files for that feature from `.dreamers/plans/`. The PR description is the lasting record.
   - **Not merged:** leave plan files in place.
6. No init commit — Bolt's first commit for the milestone is the first thing in the PR diff.

## Commit discipline (non-negotiable)
1. **Commit at end of each sub-plan** — after Probe passes (and user sign-off if required).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

## Push discipline (non-negotiable)
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between sub-plans, or at any other point in the pipeline.

## Post-PR push discipline
If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

## Commit structure (one commit per sub-plan)
- Bolt makes exactly **one** commit per sub-plan, immediately after Probe passes and user testing (if required) is signed off.
- Forge and Probe stage their changes with `git add` throughout the pipeline but do **not** run `git commit`.
- Commit message format (Conventional Commits, imperative mood, under 72 chars):
  - `feat: <sub-plan-name>` — standard sub-plan
  - `feat!: <sub-plan-name>` + `BREAKING CHANGE:` footer — if the sub-plan introduces a breaking change
- Reference the plan file in the commit body: `Plan: plan-add-auth-a`.

One commit per sub-plan keeps each sub-plan's contribution atomic. Fix rounds (Sentinel → Forge) are staging work, not separate commits.

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
Forge works directly on the feature branch. Worktrees caused Sentinel/Probe to read stale default-branch code.

## Git history is the archive
No separate archive directories. `git log` and PR diffs are the record.
