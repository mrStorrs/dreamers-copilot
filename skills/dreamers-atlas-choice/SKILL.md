---
name: dreamers-atlas-choice
description: 'Route to the correct Dreamers pipeline based on task type. Use when unsure whether to plan or implement. Triggers: /dreamers-atlas-choice, which pipeline, route this task.'
argument-hint: '$ARGUMENTS'
---

Evaluate the following task and choose the correct pipeline:

$ARGUMENTS

## How to choose

**Use Tier 1 if ALL four conditions are true:**
1. The feature it belongs to is fully shipped (PR merged)
2. The bug is directly and obviously caused by the just-shipped feature
3. The fix is clearly scoped — describable in one sentence
4. No new logic, no new files, no data model changes — purely corrective

**Use Tier 2 for everything else:** new features, non-trivial bugs, anything with ambiguity, any data model or API change, any fix that doesn't meet all four Tier 1 conditions.

---

## Tier 1 — Simple fix

Read these refs:
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

Route: Forge → Bolt (run tests) → Close-out (Bolt handles push + PR). Skip Probe and Sentinel.

## Tier 2 — Full pipeline

### Phase 1 — Planning

Read these refs:
- `~/.copilot/dreamers/refs/planning-protocol.md`
- `~/.copilot/dreamers/refs/plan-rules.md`
- `~/.copilot/dreamers/refs/feature-decomposition.md`
- `~/.copilot/dreamers/refs/plan-content.md`
- `~/.copilot/dreamers/refs/testing-mandate.md`
- `~/.copilot/dreamers/refs/citation-accuracy.md`

Run the full requirements conversation with the user. Wait for explicit approval.

### Phase 2 — Implementation

Read these refs:
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/quality-gates.md`
- `~/.copilot/dreamers/refs/delegation.md`
- `~/.copilot/dreamers/refs/close-out.md`
- `~/.copilot/dreamers/refs/agent-recovery.md`

If the plan has sub-plans, also read:
- `~/.copilot/dreamers/refs/sub-plan-loop.md`

Route: Forge → Sentinel → Probe → Close-out (Bolt handles push + PR)

---

## Rules for both tiers

- If the change touches `mobile/` runtime files, distribute a Firebase preview build before opening the PR per the project CLAUDE.md Distribution section.
- If the prompt references a GitHub issue number or URL, close that issue once the PR is created: `gh issue close <number> --comment "Resolved in <PR URL>"`.
- Follow git-workflow.md for branching, commits, and push discipline.

State your choice and reasoning in one sentence, then proceed immediately.

