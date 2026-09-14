---
name: dreamers-plan-verify
description: "Check an existing proposal or detailed plan for drift against current code; report without edits."
argument-hint: "<plan-path>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

Read the supplied plan and verify its cited existing paths, callers/signatures, data models, tests, observable outcomes, and constraints against current code. Distinguish intended new files from stale references. An approved proposal needs no detailed-plan conversion.

Return No change or Drift detected, with each discrepancy's plan location, expected fact, actual evidence, and impact. The user/caller decides revision or continuation. Do not edit files or start implementation.
