---
applyTo: "**"
---

# Git Hygiene

Universal rules for all `git` operations performed by any agent or skill in this repo. Binds every agent (Forge, Sentinel, Probe, Hone, Bolt) and every skill.

## Staging

Stage files by explicit path. Never use `git add -A`, `git add --all`, `git add -a`, `git add .`, or any other "add everything" invocation — these capture unrelated working-tree changes from other agents' lanes, stray local files, or newly-tracked artifacts, silently widening the PR diff. Pass each path to `git add` directly: `git add path/a path/b`. Directory paths are fine when the directory genuinely is the unit of work; that scope is still bounded by what you typed, not "everything currently dirty."

## Commit messages

Use Conventional Commits (https://www.conventionalcommits.org/).

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`.

- Imperative mood ("add feature", not "added feature")
- Subject line ≤72 characters
- Breaking changes: `!` after the type/scope AND a `BREAKING CHANGE:` footer (e.g. `feat!: drop legacy auth`)

## Hooks and signing

Never bypass commit hooks or signing unless the user explicitly requested it this turn. No `--no-verify`, `--no-gpg-sign`, `-c commit.gpgsign=false`, or equivalent flags. If a hook fails, fix the underlying issue rather than skipping it.

## Destructive operations

Never run any of these without explicit user authorization in the current turn:

- `git push --force` / `git push --force-with-lease`
- `git reset --hard`
- `git checkout .` / `git checkout -- <path>` (when it would discard uncommitted work)
- `git restore .` / `git restore --staged .` (when it would discard work)
- `git clean -f` / `git clean -fd` / `git clean -fx`
- `git branch -D` (deleting unmerged branches)
- History rewrites: `git rebase -i`, `git commit --amend` on pushed commits, `git filter-branch`, `git filter-repo`, `git reflog expire`
- Tag deletion (`git tag -d`, `git push --delete`)

Authorization for one destructive op does not extend to others. Force-push to the default branch requires re-confirmation regardless of prior authorization. When in doubt, ask first.

## Git config

Never modify `git config` (`user.name`, `user.email`, hooks, signing, aliases, etc.). The user owns their git configuration and may have it intentionally tuned for cross-repo behavior; silent edits surprise the user and can break their other repos.
