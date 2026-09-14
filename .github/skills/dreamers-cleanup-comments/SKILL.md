---
name: dreamers-cleanup-comments
description: "Audit comment rules, approve cleanup, apply it, optionally review with Vigil, and commit."
argument-hint: "[--scope <path>]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Read [comment rules](../../instructions/dreamers.comment-rules.instructions.md). Audit the requested files, defaulting to project source. Count redundant comments/docstrings, separators, plan/ticket references, spec arguments, and excessive inline length.
2. Present proposed removals/edits and affected files for approval. Preserve necessary API docs, licenses, and actionable TODOs. Revise corrections before applying.
3. Apply the approved comment edits without changing behavior. Stage and run relevant checks per [verification](../../dreamers/refs/testing-mandate.md); do not manufacture tests for prose.
4. Offer Vigil review before commit. If selected, call /dreamers-review on the changed scope with comment/maintainability focus, then follow [apply findings](../../dreamers/refs/apply-findings.md).
5. Commit per [git workflow](../../dreamers/refs/git-workflow.md). Return changes and verification; do not push.
