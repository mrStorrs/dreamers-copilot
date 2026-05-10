---
applyTo: "**"
---

# Git Hygiene

Universal rules for all `git` operations performed by any agent or skill in this repo. Binds every agent (Forge, Sentinel, Probe, Hone, Bolt) and every skill.

## Staging

Stage files by explicit path. Never use `git add -A`, `git add --all`, `git add -a`, `git add .`, or any other "add everything" invocation — these capture unrelated working-tree changes from other agents' lanes, stray local files, or newly-tracked artifacts, silently widening the PR diff. Pass each path to `git add` directly: `git add path/a path/b`. Directory paths are fine when the directory genuinely is the unit of work; that scope is still bounded by what you typed, not "everything currently dirty."
