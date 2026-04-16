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

Read these refs:
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

Route: Forge → Bolt (run tests) → Close-out

After Forge stages the fix (`git add`), invoke **Bolt** to run the project's test suite. If tests pass, proceed to close-out (Bolt commits and handles push + PR). Skip Probe and Sentinel — this is a simple fix.

---

## Tier 2 — Full pipeline

### Phase 1 — Planning

Read these refs:
- `~/.copilot/dreamers/refs/planning-protocol.md`
- `~/.copilot/dreamers/refs/plan-rules.md`
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

Route: Forge → Sentinel → Probe → Close-out (Bolt handles push + PR)

Include regression analysis from Probe — not just "fixed", but "here is why testing missed it and what we've added to prevent recurrence."

---

## Rules for both tiers

- If the change touches `mobile/` runtime files, distribute a Firebase preview build before opening the PR per the project CLAUDE.md Distribution section.
- If the prompt references a GitHub issue number or URL, close that issue once the PR is created: `gh issue close <number> --comment "Resolved in <PR URL>"`.
- Follow git-workflow.md for branching, commits, and push discipline.

