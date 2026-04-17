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

Only after explicit user approval: write the plan file(s) per the naming rules in `refs/plan-rules.md`, content rules in `refs/plan-content.md`, and decomposition rules in `refs/feature-decomposition.md`.

Use the template at `~/.copilot/dreamers/templates/plan-sub.md` as the starting structure for every sub-plan and standalone plan. Use the template at `~/.copilot/dreamers/templates/plan-umbrella.md` as the starting structure for every umbrella plan (`plan-{n}-…`).

**Component usage check (mandatory):** When a plan modifies a shared component, run `grep -r "ComponentName" app/` before finalizing the scope file list — include all callers in scope to avoid build failures from missing prop updates.

## Output discipline during planning

**During Phase 1:** Understanding summary (one paragraph) + numbered clarifying questions (one round only).
**During Phase 2:** The proposal block only. Nothing else until user approves.
**After Phase 3:** Brief summary + plan file path(s) created/updated + any open items flagged.

Never output plan content in chat — write it to the plan file only.
