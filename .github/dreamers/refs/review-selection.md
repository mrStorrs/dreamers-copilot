# Review Selection

Use this contract for the initial review and any reviewer rerun in a PR-bearing Dreamers workflow.

## Initial lane

- A complex plan selects Sentinel + Probe + Hone through the full /dreamers-review lane.
- A low-risk lite or standard plan selects Vigil.
- Any danger or high-risk trigger overrides a smaller plan type and selects the triad:
  - Security, authentication, authorization, privacy, payment, secret, or permission changes.
  - Schema, migration, persistence, destructive-data, concurrency, or irreversible-side-effect changes.
  - Public or breaking API, dependency, build, distribution, or cross-subsystem changes.
  - Rollback that requires operator action or data recovery instead of reverting the feature commit.
- PR-bearing work receives at least Vigil unless the user explicitly requests that review be skipped.

## Decision behavior

- State the selected reviewer lane and a one-sentence rationale, then proceed without a routine confirmation gate.
- An explicit user override wins and remains authoritative. Before a requested downshift, surface the concrete risk being accepted.
- If classification is genuinely ambiguous, ask once before review. Do not silently promote or downshift.
- Record the selected lane, rationale, trigger or plan type, and any user override in the cycle summary.

## Invocation

- For Vigil, spawn vigil directly with the plan path, changed-file scope, branch and default names, validation commands/results, shared manifest context when present, and prior review artifacts when applicable.
- For the triad, invoke /dreamers-review --branch with the plan path and shared manifest context.
- Read every reviewer artifact before reporting or applying findings. Blocked halts the cycle; open questions return to the user.

## Reruns

- Decide reviewer reruns independently from plan type, ship strategy, documentation, and retrospective decisions.
- Skip a rerun when fixes are small and automated validation directly covers them; record the reason.
- Use Vigil for a normal rerun after targeted fixes.
- Escalate a rerun to the triad only when the new change set itself meets a danger/high-risk trigger. A selected /dreamers-review lane is valid when one specific lens is sufficient.
- State the rerun choice and rationale and proceed without a routine gate. Ask only when the new risk is genuinely ambiguous; explicit user overrides remain authoritative.
