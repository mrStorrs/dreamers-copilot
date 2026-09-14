---
name: dreamers-lite
description: "Fix a bounded bug with meaningful regression coverage and verification; stop before review or shipping."
argument-hint: "<bug>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Read [git workflow](../../dreamers/refs/git-workflow.md) and create/resume a fix branch. Inspect the failing behavior and affected callers.
2. If the fix needs unrelated subsystems, a new module, schema changes, or broader architecture, stop and recommend /dreamers with the expanded scope.
3. Fix within the identified surface. Apply [verification](../../dreamers/refs/testing-mandate.md) and [logging](../../dreamers/refs/logging-discipline.md). Add or improve a meaningful regression test where feasible; otherwise document the verified reproduction and coverage gap. Do not invent brittle text checks.
4. Stage changes and return scope, regression coverage, and validation/timing results. Stop at verified implementation. Suggest Vigil review and /dreamers-pr as separate next steps.
