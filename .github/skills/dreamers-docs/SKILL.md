---
name: dreamers-docs
description: "Have Echo update affected documentation and project instruction sections; stage without committing."
argument-hint: "[--branch|--staged]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Resolve changed files, including pending edits: --branch (default) uses the merge-base with origin's default branch through the working tree; --staged uses staged plus unstaged changes. Include relevant untracked files. Empty scope exits.
2. Spawn Echo with scope, diff base, plan/proposal path when present, and review/validation results. Echo edits docs only and stages its changes.
3. Read its change summary. Resolve open questions with the user and return updated paths. The caller owns commits and shipping.
