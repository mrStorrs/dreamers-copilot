---
name: dreamers-plan
description: "Clarify requirements and write detailed plans on request. Save the Grill transcript and stop after approval."
argument-hint: "<task> [lite|standard|complex]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Follow [the Grill](../../dreamers/refs/planning-grill.md). Resolve decisions and record the exchange verbatim. Read [the selector](../../dreamers/templates/plan-guide-selector.md), then only the selected guide.
2. Write .dreamers/plans/feature-<slug>/plan-NN-<name>.md in dependency order. Add manifest.md when multiple plans share context; backfill it when adding a dependent second plan. Link the sibling transcript when present.
3. Include all accepted decisions, scope, observable outcomes, constraints, relevant verification, and proposal critique. Verify cited files and affected callers. Check coverage against the conversation; consult the transcript for uncertainty. Fix missing decisions and unresolved questions before presenting.
4. Present the proposal and detailed plan paths together for one approval. Include ship strategy if invoked by /dreamers for multiple plans. Revise corrections before approval.
5. On approval mark plans Active and return paths. Standalone: stop without implementation. Under /dreamers: return to immediate implementation; no second approval gate. If the same scope was already approved, formatting it into a detailed plan does not require fresh start approval.
