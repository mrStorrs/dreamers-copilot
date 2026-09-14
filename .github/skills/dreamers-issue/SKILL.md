---
name: dreamers-issue
description: "Create a GitHub issue with outcome-based acceptance criteria; # prefix enables discussion first."
argument-hint: "[#]<task>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. A # prefix selects discussion: clarify scope and outcomes before drafting. Otherwise create directly from the request, marking inferred criteria [potential].
2. Confirm the target repository with gh repo view; ask if unavailable. Read existing labels and choose applicable ones. Limit code inspection to what the issue needs.
3. Use [the issue template](../../dreamers/templates/github-issue.md). Describe observable user outcomes, not prescribed implementation.
4. Create with gh issue create and --body-file, preserving literal Markdown. Return the URL.
