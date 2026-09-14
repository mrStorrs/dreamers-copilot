---
name: dreamers-simplify
description: "Audit code simplicity through Vigil without applying refactors."
argument-hint: "[--branch|--paths <glob>|--all]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

Invoke /dreamers-review --vigil with the supplied scope flags. Focus on [simplicity](../../dreamers/refs/hone-architecture-rubric.md), retaining correctness and reporting broader refactors with their scope.

Read and summarize the returned artifact, including its final simplicity answer. Stop without fixes.
