---
name: dreamers-plan
description: 'Planning phase of the Dreamers pipeline. Three-phase requirements conversation → plan files in `.dreamers/plans/` → implementation-start approval gate. Invokable standalone (plan-only) or composed from `/dreamers-full` Phase 1. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '$ARGUMENTS'
---

## What this skill does

Drives the three-phase planning conversation (Hash-it-out → Approval → Decompose) and writes plan files to `.dreamers/plans/`. Exits at the implementation-start approval gate (Phase 1g). Does NOT proceed to implementation — that's `/dreamers-implement`'s job. When called from `/dreamers-full`, the orchestrator captures the approved plan paths from this skill's chat output and forwards them.

## Pre-flight reads

Read these refs once at startup (use the `view` tool, full file — never `cat`/`head`/`tail`/`Select-String`, which truncate):

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — the shared discipline cited by all pipeline sub-skills
- `~/.copilot/dreamers/refs/plan-content.md` — plan section requirements
- `~/.copilot/dreamers/refs/plan-rules.md` — plan naming + numbering
- `~/.copilot/dreamers/refs/planning-protocol.md` — three-phase conversation rules
- `~/.copilot/dreamers/refs/citation-accuracy.md` — verify before citing existing artifacts
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations the plan must capture
- `~/.copilot/dreamers/refs/feature-decomposition.md` — when to write multiple plans
- `~/.copilot/dreamers/templates/plan.md` — the single plan template
- `~/.copilot/dreamers/refs/orchestration-flow.md` — continuation principle, todo-list protocol, tool-name pseudonyms

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, test commands, source roots used by the component-usage check.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1a — hash it out (clarifying questions)
- [ ] Phase 1b — user input audit
- [ ] Phase 1c — approval gate
- [ ] Phase 1d — decide plan count (and manifest)
- [ ] Phase 1e — write plan file(s)
- [ ] Phase 1f — plan quality self-check
- [ ] Phase 1g — implementation-start approval gate

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-full`, do NOT declare a new list — update the parent's matching Phase 1 item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## Phase 1a — Hash it out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question — use the `request_information` tool one question at a time within a single round. Do not trickle questions across multiple message turns.
4. Wait for the user's responses before proceeding.

If the task is fully unambiguous, skip to Phase 1b with a brief "I understand the goal as: …" confirmation.

## Phase 1b — User Input Audit (gate)

Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it.

## Phase 1c — Approval gate

Present this proposal block in chat:

```
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…
```

Call `request_information` with choice `["Approved"]` and allow inline freeform corrections in the same interaction. Treat any non-approval freeform response as corrections; revise and re-present until explicit approval.

## Phase 1d — Decide plan count (one or multiple)

Default to ONE plan. If the work's scope is too large to land cleanly in a single cycle, produce MULTIPLE independent plans per `feature-decomposition.md` (each shippable on its own; sequenced via `/dreamers-full <plan-a> <plan-b> <plan-c>` at invocation time).

"Too large" thresholds:
- More than ~300 lines of new/changed code across the touched files.
- More than one data-layer change PLUS more than one UI surface in the same cycle.
- Crosses natural seams (model → repository → viewmodel → screen → cloud function) such that one cycle's review would be unwieldy.

When splitting, each plan MUST be:
- **Independently shippable** — can merge to main alone; no dependency on a later plan.
- **Testable in isolation** — at least one machine-verifiable assertion per plan.
- **Coherent scope** — touches at most one data-layer change + one UI surface (loose guideline).
- **At a natural seam** — split at model/repo/viewmodel/screen/function boundary, not arbitrary line cuts.

State your decision in chat: "Producing ONE plan: …" or "Producing N plans: …" with a one-sentence rationale.

### Phase 1d.1 — Decide whether to produce a feature manifest (multi-plan only)

If producing multiple plans, decide whether they warrant a `feature-{slug}.md` manifest. **Produce a manifest if ANY of these hold:**

- At least 2 shared constraints apply across all plans (e.g., "all plans must preserve API X's backward compat until plan-C ships")
- Shared design decisions span plans (e.g., "all auth flows use the same state-machine abstraction")
- Shared data models referenced by multiple plans (interface / type contracts)
- End-to-end Acceptance Criteria exist (only verifiable after ALL plans ship)
- Cross-plan risks (ordering dependencies, rollback coordination)

**Skip the manifest if:** the multiple plans are essentially unrelated (e.g., 3 bug fixes shipped together but touching different subsystems). No shared context → manifest would be decorative.

When produced, the manifest is the AI's hierarchical context anchor — research shows hierarchical task decomposition is significantly more effective for AI agents than flat plan lists. The manifest threads cross-plan context into each cycle's reviewer prompts.

State your manifest decision: "Manifest: yes (because …)" or "Manifest: no (plans are independent)."

## Phase 1e — Write plan file(s)

Plan filenames are `plan-{slug}.md` (no `-a`/`-b`/`-c` suffix — that convention is gone). Slug rules per `plan-rules.md`. Plans live in `./.dreamers/plans/`.

Use the templates as starting structure:
- `~/.copilot/dreamers/templates/plan.md` — every plan, one template.
- `~/.copilot/dreamers/templates/feature.md` — manifest template (only when multi-plan + Phase 1d.1 says manifest=yes). Manifest naming: `feature-{slug}.md`, lives in `.dreamers/plans/` alongside the plan files.

If producing multiple related plans, you may share a slug prefix purely for visual grouping (e.g., `plan-auth-login.md`, `plan-auth-logout.md`, `plan-auth-reset.md`). The shared prefix is cosmetic when there's no manifest. When a manifest is produced, its slug should match the shared prefix (e.g., `feature-auth.md` for the auth plans above).

**Each plan must include:**
- Metadata: Owner, Date, Scope, Status (Draft/Active/Completed/Superseded), Branch, User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases (Given/When/Then for non-trivial), Rollback boundary, Risks/Mitigations

**Design Decisions format** (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User-testing required:** `yes` if a human must manually verify before the cycle completes (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Plans MUST NOT include code snippets.** One exception: interface/type contracts where the signature itself is the design decision.

### Phase 1e.1 — Component usage check (mandatory)

When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's source root from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 1e.2 — Citation accuracy

Before citing the behavior, structure, content, or API of any existing artifact in the plan — test file, test method, repository method, ViewModel property, Maestro YAML, UI assertion pattern, or any other code artifact — read and verify the source during this planning session. Claiming "method X does Y" or "test Z asserts W" without reading the file is a planning error; the plan becomes a liability when implementation builds against a wrong assumption.

- **If the artifact cannot be read** (e.g., it belongs to a later plan in the same sequence and doesn't exist yet): state explicitly in the plan that the citation is an assumption pending verification. Do not present it as confirmed fact.
- **Maestro `assertVisible` / `assertNotVisible` collision check** (mobile UI tests): when a plan specifies asserting on visible text, read the target screen's Compose code (or equivalent) and verify no OTHER persistent UI element (filter tabs, headers, navigation labels, bottom-bar items) shares that text. If a collision exists, the plan must specify a more-specific assertion string that matches only the intended element.

## Phase 1f — Plan quality self-check (mandatory)

Before exiting Phase 1, verify each plan against:
- [ ] Filename follows `plan-{slug}.md`
- [ ] Has measurable Acceptance Criteria
- [ ] Has Test Cases (Given/When/Then) for non-trivial cases
- [ ] Has Design Decisions in the structured format
- [ ] Has a Rollback Boundary
- [ ] Has a Status field (Draft / Active / Completed / Superseded)
- [ ] References only files/paths that exist (no invented paths)
- [ ] No code snippets (exception: interface/type contracts only)

When multiple plans are produced, additionally verify:
- [ ] Each plan is independently shippable (no plan depends on a later sibling)
- [ ] Each plan has at least one machine-verifiable assertion testable in isolation
- [ ] Splits fall at natural seams (not arbitrary line-count cuts)

When a manifest is produced (from Phase 1d.1), additionally verify:
- [ ] `feature-{slug}.md` exists in `.dreamers/plans/`
- [ ] Manifest has a Plan sequence table listing all plans in the intended run order
- [ ] At least one of: shared constraints, shared design decisions, shared data models, end-to-end ACs, or cross-plan risks is populated (manifest with all sections empty = decorative; either populate or skip the manifest)

Any failure → halt and prompt the user with the specific item(s) that failed.

## Phase 1g — Implementation start approval gate (mandatory)

Phase 1c approved the high-level goal. Phase 1g approves the actual plan files before any implementation work begins.

Present this block:

```
**Plans written and ready for review:**

- `path/to/plan-{slug}.md` — [one-line summary from plan Summary]
- `path/to/plan-{related-slug}.md` — [one-line summary]  (if multiple plans were produced)
- ...

Please read the plan file(s) above. Reply "Approved — start implementation" to begin Phase 2, or describe any corrections needed.
```

Call `request_information` with choice `["Approved — start implementation"]` and allow inline freeform corrections.

- Approval → exit this skill with success status.
- Corrections → revise plan files, re-run Phase 1f, re-present this gate. Loop until approved.

---

## Exit behavior

When called **standalone**, exit on Phase 1g approval. Tell the user:
- The approved plan file path(s).
- If a manifest was produced: the manifest file path.
- Next step: invoke `/dreamers-implement <path-to-plan>` (one plan), `/dreamers-full <plan-a> <plan-b> ...` (multiple plans, no manifest), or `/dreamers-full feature-{slug}.md` (multiple plans via manifest — threads shared context into reviewer prompts).

When called **from `/dreamers-full`**, exit on Phase 1g approval. Return in chat output:
- Plan count (one or multiple) + sequence order if multiple.
- Plan file path(s).
- Manifest file path (if a manifest was produced; omit if none).
- Approval status.

The orchestrator reads this chat output and proceeds to Phase 2 (`/dreamers-implement` once for a single plan, or once per plan in the sequence).

## HARD STOP after Phase 1g

When plan files are written and the approval gate clears:
- Do NOT proceed to implementation.
- Do NOT delegate to any implementation agent or skill.
- Do NOT make any code edits beyond plan files.

If the user asks "start implementing" after approval, tell them to invoke `/dreamers-implement <plan>` (one plan) or `/dreamers-full <plan-a> <plan-b> ...` (multiple plans). This skill's lane is planning only.
