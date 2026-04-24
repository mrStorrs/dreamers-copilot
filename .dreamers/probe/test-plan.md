# Probe Test Plan — dreamers-full approval/orchestrator cleanup

## Scope
- Plan: `C:\projects-gh\dreamers-copilot\.dreamers\plans\plan-dreamers-full-approval-orchestrator-cleanup.md`
- Implementation notes: `C:\projects-gh\dreamers-copilot\.dreamers\forge\implementation.md`
- Change type: docs/instructions only
- Test method: deterministic file-content inspection; no runtime behavior invented

## Test Inventory

| Test ID | Type | Covers | Method |
|---|---|---|---|
| TC-1 | Happy path | AC1 | Inspect `SKILL.md` approval-gate text for `ask_user`, explicit `["Approved"]`, and inline freeform corrections in the same interaction. |
| TC-1b | Negative | AC2 | Confirm `SKILL.md` no longer contains `Corrections needed`. |
| TC-2 | Regression | AC3 | Whole-word `Atlas` scan across committed scoped `.github` Dreamers files. |
| TC-3 | Happy path / regression | AC4 | Inspect changed `.github` docs for explicit orchestrator prompt/handoff/output/routing wording. |
| TC-4 | Edge / provenance | AC5 | Inspect `forge/implementation.md` for the local-`master` user-approved fallback note caused by missing `origin`. |
| TC-5 | Edge | AC3 scope note | Confirm `.github/agents/hone.agent.md` is absent, so the plan's listed file is not an applicable committed target. |

## Acceptance Criteria Coverage Matrix

| AC | Requirement | Covering tests | Status |
|---|---|---|---|
| AC1 | `SKILL.md` uses `ask_user` with explicit approval option and inline freeform corrections in one interaction | TC-1 | PASS |
| AC2 | `SKILL.md` no longer instructs a separate `"Corrections needed"` choice | TC-1b | PASS |
| AC3 | Scoped committed `.github` Dreamers files no longer use `Atlas` for the orchestrator role | TC-2, TC-5 | PASS |
| AC4 | Wording still makes orchestrator prompt passing, workspace reading, and routing explicit | TC-3 | PASS |
| AC5 | Implementation notes capture local `master` fallback because `origin` was unavailable | TC-4 | PASS |

## Results
- TC-1 PASS: `SKILL.md:24` documents `ask_user` with choice `["Approved"]`, inline freeform corrections, and the revise/re-present loop.
- TC-1b PASS: no `Corrections needed` match remains in `SKILL.md`.
- TC-2 PASS: no whole-word `Atlas` matches remain in the scoped committed `.github` files checked.
- TC-3 PASS: orchestrator ownership remains explicit in `.github/copilot-instructions.dreamers.md` and the changed agent files.
- TC-4 PASS: `forge/implementation.md:35` records the local-`master` fallback because no `origin` remote was configured.
- TC-5 PASS: `.github/agents/hone.agent.md` does not exist, so there is no committed file there that could still carry stale terminology.

## Coverage Expansion

### Layer audit
- **Unit:** No code paths changed. No unit-testable logic introduced.
- **Integration:** The only integration-like contract here is cross-file documentation consistency between the skill, shared instructions, and agent handoff docs; TC-2 and TC-3 cover that.
- **UI / E2E:** The user-facing approval interaction changed only as documented instructions. The highest-fidelity applicable test is direct inspection of the shipped wording in `SKILL.md`; no runtime `ask_user` behavior changed and no runtime test is applicable.

### Gap triage
- Added TC-1b because AC2 needed an explicit negative assertion, not just a happy-path wording check.
- Added TC-5 because the plan scope listed `hone.agent.md`, but the file is absent; this had to be documented instead of hand-waved.
- No additional genuine test opportunity remains inside the changed docs beyond these deterministic checks.

### Deferred / Untestable
- Runtime approval-loop behavior is out of scope: the plan changes wording only and explicitly does not change the `ask_user` tool itself.
- Local `.dreamers/` files that still mention `Atlas` are intentionally out of scope per the task context and plan.

### Final missed-AC check
- Re-read all five ACs after the coverage expansion pass.
- Every AC has at least one green covering test above.

## Verdict
- PASS — all plan acceptance criteria are covered and verified by deterministic file-content checks.
