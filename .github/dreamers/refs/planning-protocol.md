# Requirements Clarification Protocol (MANDATORY)

Never write a plan file until the user has explicitly approved the goal and acceptance criteria. Three phases — in order, no skipping.

## Phase 1 — Hash it out

On receiving a new task:
1. Write a concise **understanding summary** — one paragraph stating what you believe the goal, scope, and done-state to be.
2. Identify all ambiguities, gaps, and open decisions.
3. Ask every clarifying question in a **single numbered list** — one round only. Do not trickle questions across multiple messages.
4. Wait for the user's response before proceeding.

If the task is fully unambiguous and there are no questions, skip directly to Phase 2 with a brief "I understand the goal as: …" confirmation.

## Phase 2 — Explicit approval

After Phase 1 (or immediately if no questions), present this proposal block and wait — no plan file is written until the user explicitly approves:

---
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous or there's real risk of over-building — omit by default]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…

*Reply "approved" or provide corrections.*

---

If corrections are given, revise the proposal and re-present it. Repeat until approved.

## Phase 3 — Decompose

Only after explicit user approval: write the plan file(s) per the naming rules in `refs/plan-rules.md`, content rules in `refs/plan-content.md`, and multi-plan rules in `refs/feature-decomposition.md`.

Use the template at `~/.copilot/dreamers/templates/plan.md` as the starting structure for every plan. Plans live at `.dreamers/plans/feature-<slug>/plan-NN-<name>.md`. If the work warrants multiple plans, produce multiple files inside the same feature directory; the user sequences them via `/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md ...`.

**Component usage check (mandatory):** When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's actual source root from `.github/copilot-instructions.md`) before finalizing the Context file list — include all callers in the plan's Context so the implementer knows what else changes.

## All-questions-resolved rule (mandatory, non-negotiable)

A plan must NEVER contain an "Open Questions" section. All open questions must be resolved during Phase 1 (Hash it out) BEFORE plan generation.

If during Phase 3 plan-writing the orchestrator discovers a new question that didn't surface in Phase 1, the orchestrator MUST:

1. Pause plan-writing.
2. Surface the question to the user via `request_information`.
3. Wait for the answer.
4. Resume plan-writing with the answer incorporated.

Never write a plan that says "TBD" or "open question:" anywhere. The plan must be the answer, not a record of what's unanswered.

## Manifest backfill rule (multi-plan, mandatory)

A feature directory may start with a single plan (no manifest). When the planning conversation produces a SECOND plan for an existing feature directory, the orchestrator must:

1. Detect: feature dir exists, contains `plan-01-*.md`, no `manifest.md` is present, current work is producing `plan-02-*.md`.
2. Create `manifest.md` in that same Phase 3 step, using plan-01 as seed context.
3. Verify the manifest captures the shared constraints / design decisions / data models / end-to-end ACs that span both plans.
4. Only then write plan-02.

See `refs/feature-decomposition.md` § "Manifest backfill" for the full rule.

## Output discipline during planning

**During Phase 1:** Understanding summary (one paragraph) + numbered clarifying questions (one round only).
**During Phase 2:** The proposal block only. Nothing else until user approves.
**After Phase 3:** Brief summary + plan file path(s) created/updated + any deferred items flagged in the PR description (NOT in the plan).

Never output plan content in chat — write it to the plan file only.
