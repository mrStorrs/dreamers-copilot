# Verification

Read the project's validation commands and run those relevant to the change, including applicable type-check, build, lint, and tests. Verify required outcomes, failures, edge cases, and affected callers.

Add or improve tests only when they protect meaningful behavior. Prefer the narrowest layer that proves the requirement: unit for logic, integration for boundaries, E2E for user journeys. Navigation behavior needs an E2E check; if automation is unavailable, record a specific manual check and coverage gap. Do not add a test per function or per checklist row.

Bug fixes need meaningful regression coverage when feasible. Test order is flexible. Tests must survive harmless refactors: no source/prompt wording assertions, implementation snapshots, redundant coverage, or mocks that merely confirm themselves. Inspect docs/comment-only changes instead of manufacturing tests.

After each successful test command, create/update its measured duration and date in root test-benchmarks.md using [the template](../templates/test-benchmarks.md). Preserve human Notes. Use max(last duration × 2, 30 seconds) for its next timeout.

Map required outcomes to actual verification results, including manual or uncovered outcomes. Green tests alone do not prove every requirement. Fix failures; after three unsuccessful attempts, report the blocker and evidence.
