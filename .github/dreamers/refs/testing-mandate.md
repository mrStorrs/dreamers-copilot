# Verification

## Coverage

Read the project's instructions and existing tests to identify validation commands and coverage for each required outcome. Reuse sufficient tests; add or improve a test only when it protects behavior or a likely regression. Prefer the narrowest layer that proves the requirement:

- Unit: logic, boundaries, invalid input, and failure states that can be proved in isolation.
- Integration: important contracts and side effects across services, storage, APIs, or other boundaries.
- E2E: user actions through to observable results. Navigation changes need an E2E check; if automation is unavailable, name a specific manual check and record the coverage gap.
- Bug fixes: preserve a verified reproduction in a meaningful regression test when feasible. Otherwise explain the limitation and the evidence used to verify the fix.

Test order is flexible. Do not add a test per function or checklist row. Tests must survive harmless refactors: no source/prompt wording assertions, implementation snapshots, duplicate coverage, or mocks that merely confirm themselves. Inspect docs/comment-only changes instead of manufacturing tests.

## Execution and evidence

Run relevant project type-check, build, lint, and test commands. Verify affected callers, required outcomes, meaningful edges, and failure behavior. A passing test count does not prove the whole requirement.

Map each required outcome to a named test, manual check, or inspection result. Identify unverified outcomes explicitly. After three unsuccessful fix-and-retry attempts, stop and report the failing command, failure, attempted fixes, and blocker. Do not report green while a required check is failing or blocked.

## Test timings

After every successful test command, create/update its row in root test-benchmarks.md, including post-fix runs. Record measured duration and date; preserve human Notes. Use max(last duration × 2, 30 seconds) for the next timeout. If no prior row exists, use the project's normal timeout until a measurement is available.

| Command | Last run | Updated | Recommended timeout | Notes |
| --- | --- | --- | --- | --- |

The main session runs validation and updates timings. Reviewers assess supplied evidence and report gaps; they do not run tests or edit benchmark records.
