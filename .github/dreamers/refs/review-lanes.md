# Review Lanes

Use the full lane for the initial `/dreamers-full` review for each plan. Use narrower lanes only for follow-up review gates after that full review has already happened, or for standalone focused audits. Reviewer work is read-only; the orchestrator applies or defers findings.

| Lane | Reviewers | Use when |
| --- | --- | --- |
| `sentinel` | Sentinel | Correctness/security/maintainability audit, lightweight bug fix, cleanup, logging/comment pass, or user explicitly asks for Sentinel only. |
| `probe` | Probe | Test coverage audit, AC/layer coverage check, regression-risk review, or user explicitly asks for Probe only. |
| `hone` | Hone | Simplicity/architecture/over-engineering audit, or user explicitly asks for Hone only. |
| `standard` | Sentinel + Probe | Follow-up check when both correctness and coverage need review but Hone is not warranted. |
| `full` | Sentinel + Probe + Hone | Initial `/dreamers-full` per-plan review. Invoke as `/dreamers-review` with no lens flags. Also use for follow-up architectural/refactor risk: new abstractions, public API/schema/data model changes, dependency changes, persistence changes, cross-module rewrites, broad subsystem movement, conflicting reviewer feedback, or explicit user request for full review. |

## Gate Rules

- `/dreamers-full` PR-bearing code changes require one `full` review per plan after orchestrator-run type-checks and tests pass.
- Do not use a narrower lane to bypass the initial full per-plan review.
- After the full review has passed, follow-up fix loops may use a narrower lane. User-testing bug fixes may skip reviewer re-run when the fix is small and automated validation covers it; otherwise run Sentinel by default. Add Probe or Hone only when the follow-up change touches their lenses.
- `/dreamers-pr-resolve` requires Sentinel for accepted fixes. Add Probe or Hone only when the accepted fixes touch coverage/regression risk or architecture/refactor risk.
- If the user asks for a narrower lane that conflicts with a required gate, surface the conflict before PR creation and ask whether to run the missing required lane or stop short of PR.
