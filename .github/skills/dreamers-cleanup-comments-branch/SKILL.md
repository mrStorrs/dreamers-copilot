---
name: dreamers-cleanup-comments-branch
description: "Run comment cleanup on the current feature-branch diff."
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

Read [git workflow](../../dreamers/refs/git-workflow.md) to resolve/fetch the default branch. Require a feature branch and a usable remote base.

Compute changed source files from the merge-base through HEAD plus pending changes. Invoke /dreamers-cleanup-comments with exactly that file set. Its audit, proposal approval, optional Vigil review, verification, and local commit gates apply. Do not expand to unrelated project files.
