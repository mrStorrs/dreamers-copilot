# Review Lanes

Choose the narrowest reviewer set that satisfies the workflow gate. Reviewer work is read-only; the orchestrator applies or defers findings.

| Lane | Reviewers | Use when |
| --- | --- | --- |
| `sentinel` | Sentinel | Correctness/security/maintainability audit, lightweight bug fix, cleanup, logging/comment pass, or user explicitly asks for Sentinel only. |
| `probe` | Probe | Test coverage audit, AC/layer coverage check, regression-risk review, or user explicitly asks for Probe only. |
| `hone` | Hone | Simplicity/architecture/over-engineering audit, or user explicitly asks for Hone only. |
| `standard` | Sentinel + Probe | Default for PR-bearing full-pipeline code changes after orchestrator-run tests pass. |
| `full` | Sentinel + Probe + Hone | Architectural/refactor risk: new abstractions, public API/schema/data model changes, dependency changes, persistence changes, cross-module rewrites, broad subsystem movement, conflicting reviewer feedback, or explicit user request for full review. |

## Gate Rules

- Full-pipeline PR-bearing code changes require `standard` at minimum: Sentinel review + Probe coverage audit after the orchestrator has run type-checks and tests.
- Hone is not a default full-pipeline gate. Add Hone only when a `full` trigger fires.
- Single-lens lanes are valid for focused audit-only work and Tier 1/lightweight workflows. Do not use a single-lens lane to bypass the `standard` gate before opening a full-pipeline PR.
- If the user asks for a narrower lane that conflicts with a required gate, surface the conflict before PR creation and ask whether to run the missing required lens or stop short of PR.
- When uncertain between `standard` and `full`, choose `standard` and state why Hone was not triggered.
