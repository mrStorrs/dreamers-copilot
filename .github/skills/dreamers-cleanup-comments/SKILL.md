---
name: dreamers-cleanup-comments
description: 'Code comment cleanup pass — remove redundant/stale comments, improve clarity. Triggers: /dreamers-cleanup-comments, clean up comments, comment cleanup.'
---

Run a code comment cleanup pass across the codebase.

Read these refs:
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

**Step 1 — Branch setup**
```
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
git checkout "$DEFAULT_BRANCH" && git pull origin "$DEFAULT_BRANCH"
git checkout -b chore/cleanup-comments
```

**Step 2 — Forge's task — comment cleanup rules (non-negotiable):**

Invoke Forge (follow delegation.md). Read `~/.copilot/dreamers/refs/comment-rules.md` — those are the authoritative rules. Scan and edit source files to enforce them. No other changes — do not touch logic, formatting, or structure.

**Step 3 — Single commit (Forge)**
```
style: remove plan refs, dividers, and noise comments
```

**Step 4 — PR (Bolt)**
Invoke **Bolt** to handle the mechanical close-out:
- Push the branch
- Open PR with title: `style: remove plan refs, dividers, and noise comments`
- Body: brief summary of what was cleaned up

Bolt reports the PR URL.

