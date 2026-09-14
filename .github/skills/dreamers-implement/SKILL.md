---
name: dreamers-implement
description: "Implement an approved proposal or detailed plan and return verified outcomes. No review or shipping."
argument-hint: "<plan-path>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Read the supplied plan and relevant manifest context. Missing or non-actionable input blocks implementation. An approved proposal is sufficient; no detailed plan or extra start approval is required.
2. Implement the simplest correct solution within scope. Follow [verification](../../dreamers/refs/testing-mandate.md) and [logging](../../dreamers/refs/logging-discipline.md). Add meaningful behavior tests where warranted; tests-first is optional.
3. Run applicable checks and record successful test timings. Resolve failures within three attempts; report blocked checks and coverage gaps.
4. Stage explicit changes. Return outcome-to-verification coverage, results, and changed paths. The caller owns review, user testing, fixes from review, commits, and PRs.
