---
name: dreamers-find-refactors
description: "Find refactor opportunities with section-scoped Vigil audits and write candidate plans; no implementation."
argument-hint: "[scope or directive]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Resolve the requested refactor lenses: simplicity, duplication, boundaries/coupling, state/data flow, contracts, error handling, dead code, testability, or a custom directive. Ask for selection unless already clear.
2. Map source and relevant tests by ownership boundary, excluding generated/vendor/cache files. Use one section for a small repo; split only for meaningful independent audits. Write .dreamers/refactor-audits/<slug>/sections.md with selected lenses, section files, purpose, and exclusions.
3. Spawn Vigil per section with existing behavior/contracts as the review basis, selected lenses, section scope, and a unique artifact path per [review format](../../dreamers/refs/reviewer-findings-format.md). Alternatives require explicit user direction. Independent sections may run in parallel, at most six at once.
4. Read each artifact; mark missing/blocked sections rather than treating stale files as new results. Deduplicate findings and group useful candidates by coherent implementation boundary. Write summary.md beside sections.md with evidence links, affected files, rationale, rejected candidates, and blockers. Ask unresolved questions that affect plan scope.
5. Read [the plan selector](../../dreamers/templates/plan-guide-selector.md) and the chosen guide. Write a small set of actionable plans under .dreamers/plans/feature-refactor-<slug>/, linking verified files, summary, and review artifacts. Add a manifest for shared context. Do not make one plan per finding.
6. Present the reports and plans for approval, revision, or halt. Revise only these artifacts; stop after approval.

Allowed writes: these audit reports, review artifacts, and candidate plans. No project edits, tests, git mutations, implementation, or shipping.
