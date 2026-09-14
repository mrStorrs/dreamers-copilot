---
name: dreamers-implement
description: "Implement an approved proposal or detailed plan and return verified outcomes. No review or shipping."
argument-hint: "<plan-path>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded. When standalone, also read [git workflow](../../dreamers/refs/git-workflow.md) and perform its startup verification.

1. Read the supplied plan and relevant manifest context. Missing or non-actionable input blocks implementation. An approved proposal is sufficient; no detailed plan or extra start approval is required.
2. When standalone, create/resume the feature branch per git workflow. Under /dreamers, reuse its established branch. Before edits, confirm the branch and recent commits match the approved scope; stop on an unexplained mismatch.
3. Implement the simplest correct solution within scope. Follow [verification](../../dreamers/refs/testing-mandate.md) and [logging](../../dreamers/refs/logging-discipline.md). Add meaningful behavior tests where warranted; tests-first is optional.
4. Run applicable checks and record successful test timings. Resolve failures within three attempts; report blocked checks and coverage gaps.
5. Stage explicit changes. Return outcome-to-verification coverage, results, and changed paths. The caller owns review, user testing, fixes from review, commits, and PRs.
