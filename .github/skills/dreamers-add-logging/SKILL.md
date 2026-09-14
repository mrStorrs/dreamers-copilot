---
name: dreamers-add-logging
description: "Audit logging, approve a proposal, apply fixes, optionally review with Vigil, and commit."
argument-hint: "[--scope <path>]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Read [logging standards](../../dreamers/templates/logging-standards.md) and project logging conventions. Audit the requested scope, defaulting to project source: missing useful events, wrong levels, lost errors, sensitive data, and noisy loops.
2. Present files, proposed additions/changes/removals, and rationale for approval. Incorporate corrections before editing.
3. Apply approved changes inline and stage them. Run applicable [verification](../../dreamers/refs/testing-mandate.md).
4. Offer Vigil review before commit. If selected, call /dreamers-review with the exact changed scope and logging focus, then follow [apply findings](../../dreamers/refs/apply-findings.md).
5. Commit per [git workflow](../../dreamers/refs/git-workflow.md). Return scope and validation results; do not push.
