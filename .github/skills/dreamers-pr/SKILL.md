---
name: dreamers-pr
description: "Push the prepared branch, open a PR, and archive shipped plan artifacts."
argument-hint: "[--issue <number|url>]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Read [git workflow](../../dreamers/refs/git-workflow.md). Verify branch, commits, clean working tree, and available validation/review results. Resolve missing preparation before pushing. In /dreamers, use its existing pre-PR approval; do not ask again.
2. Draft the PR from [the template](../../dreamers/templates/pr-description.md). Push the branch normally, then use gh pr create with explicit base/head and --body-file. For a rejected non-fast-forward push, fetch and reconcile before retrying. Return an existing matching PR instead of creating a duplicate.
3. With --issue, post the resolution link to that issue; leave closing until merge.
4. After PR creation, archive shipped plans under .dreamers/plans/archive/feature-<slug>/. For partial delivery, move only shipped plans and copy their linked transcript so archived links resolve. Keep the live transcript/manifest with unfinished plans. On final delivery, move remaining feature context without overwriting prior archive files. Report conflicts instead of discarding artifacts.
5. Return PR URL and archive paths. No post-PR edits or commits.
