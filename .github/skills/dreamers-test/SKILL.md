---
name: dreamers-test
description: "Audit meaningful test coverage through Vigil without writing tests."
argument-hint: "[--branch|--paths <glob>|--all]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

Invoke /dreamers-review --vigil with the supplied scope flags. Focus on observable requirement coverage, weak assertions, brittle implementation checks, edge/failure cases, and regression risks. Report other serious defects if found.

Read and summarize the returned artifact, including its final simplicity answer. Stop without fixes.
