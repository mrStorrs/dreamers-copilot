---
name: dreamers-fix
description: 'Bug triage and fix pipeline. Routes to quick-fix (Forge only) or full pipeline based on bug scope. Triggers: /dreamers-fix, fix this bug, there is a bug, bug fix.'
argument-hint: '$ARGUMENTS'
---

Evaluate the following bug and choose the correct tier:

$ARGUMENTS

---

## How to choose

**Use Tier 1 if ALL four conditions are true:**
1. The feature it belongs to is fully shipped (PR merged)
2. The bug is directly and obviously caused by the just-shipped feature
3. The fix is clearly scoped — describable in one sentence
4. No new logic, no new files, no data model changes — purely corrective

**Use Tier 2 for everything else.**

State your choice and reasoning in one sentence, then proceed immediately.

---

## Tier 1 — Simple fix

Read `~/.copilot/dreamers/refs/git-workflow.md` once at startup.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

**Route:** Branch setup (Bolt) → Forge → Bolt (run tests) → Bolt commit + PR

1. **Bolt** — branch setup per `git-workflow.md` (canonical default detection, `feat/d<N>-fix-<slug>` from default).
2. **Forge** — `task(agent_type: "forge", mode: "sync")` — apply the fix; type-check; stage with `git add`. Mark task `trivial` in the prompt to skip the strict plan requirement.
3. **Bolt** — `task(agent_type: "bolt", mode: "sync")` — run the project's test suite (from project `.github/copilot-instructions.md`).
4. If tests pass: **Bolt** commits + pushes + opens PR with body from `pr-description.md` template. If the original prompt referenced a GitHub issue: `gh issue close <number> --comment "Resolved in <PR URL>"`.

Skip Sentinel and Probe for Tier 1 — this is a simple corrective fix on a shipped feature.

---

## Tier 2 — Full pipeline

Tier 2 routes through the same body as `/dreamers-full`. Either:

- Invoke `/dreamers-full` with the bug description as input, OR
- Inline the same flow: Phase 1 (planning + approval) → Phase 2 (per-sub-plan Forge → Sentinel → Probe → plan-verify loop) → Phase 3 (simplify + Echo + close-out).

**Tier 2 specifics:**
- Plan must include a regression analysis section (why this bug existed; what tests will prevent recurrence). This satisfies Probe's `regression-analysis.md` requirement at completion.
- Probe must write `regression-analysis.md` for any user-reported bug — three questions: why wasn't it caught, what was added, what else might be missing.

Follow `git-workflow.md` for branching, commits, and push discipline. Follow `close-out.md` for retro and PR.

---

## Rules for both tiers

- If the prompt references a GitHub issue number or URL, close that issue once the PR is created: `gh issue close <number> --comment "Resolved in <PR URL>"`.
- Push exactly once at PR close-out.
