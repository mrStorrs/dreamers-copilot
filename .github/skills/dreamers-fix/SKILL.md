---
name: dreamers-fix
description: 'Bug-fix entry point. Routes to /dreamers-full with bug-fix framing in the planning conversation. The planning phase produces a minimal plan for trivial bugs, a fuller plan for complex ones. Triggers: /dreamers-fix, fix this bug, there is a bug, bug fix, address the bug.'
argument-hint: '<bug description>'
---

## What this skill does

Thin entry-point wrapper for bug fixes. Forwards the bug description to `/dreamers-full` with framing that tells the planning phase "this is a bug fix, not new functionality."

The planning conversation handles the rest:
- Trivial bug (single-file edit, no new logic) → minimal plan, one cycle, ship quickly.
- Complex bug (touches multiple components, may need new tests or refactor) → fuller plan, possibly multiple plans if scope warrants (per the multi-plan model).

Every bug goes through plan → implement → close-out, with planning scaled to the bug's complexity. There is no separate fast-track for trivial bugs — the planning conversation itself decides how much plan is warranted.

## Pre-flight reads

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + git rules (relevant for the eventual implementation step).

$ARGUMENTS

---

## Routing

Invoke `/dreamers-full` with a prompt that includes:

- The bug description (user's `$ARGUMENTS`).
- Framing: "This is a bug fix. Planning should focus on reproducing the bug, identifying the root cause, and specifying the corrective change. If the bug touches existing behavior, the plan must include regression-analysis questions: (1) why wasn't this caught? (2) what test will prevent recurrence? (3) what adjacent cases might be similarly broken?"
- If the user referenced a GitHub issue number / URL in `$ARGUMENTS`, forward it so `/dreamers-close-out`'s issue-close step fires at PR creation.

## Output

This skill produces no output of its own — it hands off to `/dreamers-full`. The user interacts with `/dreamers-full`'s phases (planning conversation, approval gates, implementation cycle, close-out, PR).

## When this skill is NOT the right tool

- Multi-feature scope masquerading as a "bug" → use `/dreamers-full` directly with the feature framing.
- Question about existing behavior (not a real bug) → answer in chat; no pipeline needed.
- Trivial typo fix in a doc → just edit the doc directly. Don't spin up a planning conversation.
