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
- `~/.copilot/dreamers/refs/feature-decomposition.md` — load only if umbrella mode is selected
- `~/.copilot/dreamers/templates/plan-sub.md` — sub-plan / standalone template
- `~/.copilot/dreamers/templates/plan-umbrella.md` — umbrella template

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, test commands, source roots used by the component-usage check.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Phase 1a — Hash it out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question — use the `ask_user` tool one question at a time within a single round. Do not trickle questions across multiple message turns.
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

Call `ask_user` with choice `["Approved"]` and allow inline freeform corrections in the same interaction. Treat any non-approval freeform response as corrections; revise and re-present until explicit approval.

## Phase 1d — Decide plan shape

Single decision, default to cohesive:

- **Cohesive plan** (default) — one plan file, one PR. Use when the work can ship as a single coherent change.
- **Umbrella + sub-plans** — multi-cycle, still one PR at end. Use ONLY when the work genuinely needs to land in stages (e.g., risky migration with backfill, breaking change requiring shim period, multi-screen feature that needs sub-plan boundaries for git-history hygiene).

State your choice in chat with a one-sentence rationale before proceeding.

**If umbrella mode is selected, follow these decomposition criteria** (from `feature-decomposition.md`):

- Each sub-plan can be merged to main independently — no sub-plan depends on an un-merged sibling.
- A sub-plan touches at most one data-layer change + one UI surface.
- Split at natural seams: model → repository → viewmodel → screen → cloud function. These are common split points.
- If a sub-plan would take more than ~300 lines of new/changed code, split it further.
- **Testability gate:** each sub-plan must have at least one machine-verifiable assertion that can be declared pass/fail in isolation, before the next sub-plan starts. If testability requires a sibling sub-plan not yet shipped, the split boundary is wrong — reslice.
- **When NOT to decompose:** truly atomic changes (a single model field, a single bug fix, a single screen tweak) stay cohesive.

## Phase 1e — Write plan file(s)

Plan filenames follow `plan-{slug}.md` (umbrella or standalone) and `plan-{slug}-a.md`, `plan-{slug}-b.md`, … (sub-plans). Slug rules per `plan-rules.md`. Plans live in `./.dreamers/plans/`.

Use templates as starting structure:
- `~/.copilot/dreamers/templates/plan-sub.md` — sub-plans and standalone (cohesive) plans
- `~/.copilot/dreamers/templates/plan-umbrella.md` — umbrella plans only

**Each plan must include:**
- Metadata: Owner, Date, Scope, (Parent + Depends-on if sub-plan), Status (Draft/Active/Completed/Superseded), User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases (Given/When/Then for non-trivial), Rollback boundary, Risks/Mitigations

**Design Decisions format** (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User-testing required:** `yes` if a human must manually verify before the next cycle begins (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Plans MUST NOT include code snippets.** One exception: interface/type contracts where the signature itself is the design decision.

### Phase 1e.1 — Component usage check (mandatory)

When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's source root from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 1e.2 — Citation accuracy

Before citing the behavior, structure, content, or API of any existing artifact in the plan — test file, test method, repository method, ViewModel property, Maestro YAML, UI assertion pattern, or any other code artifact — read and verify the source during this planning session. Claiming "method X does Y" or "test Z asserts W" without reading the file is a planning error; the plan becomes a liability when implementation builds against a wrong assumption.

- **If the artifact cannot be read** (e.g., it belongs to a future sub-plan and doesn't exist yet): state explicitly in the plan that the citation is an assumption pending verification. Do not present it as confirmed fact.
- **Maestro `assertVisible` / `assertNotVisible` collision check** (mobile UI tests): when a plan specifies asserting on visible text, read the target screen's Compose code (or equivalent) and verify no OTHER persistent UI element (filter tabs, headers, navigation labels, bottom-bar items) shares that text. If a collision exists, the plan must specify a more-specific assertion string that matches only the intended element.

## Phase 1f — Plan quality self-check (mandatory)

Before exiting Phase 1, verify the plan(s) against:
- [ ] Filenames follow `plan-{slug}[-a..n].md`
- [ ] Non-trivial features have an umbrella + sub-plans (not monolithic)
- [ ] Every sub-plan / standalone has measurable Acceptance Criteria
- [ ] Every sub-plan / standalone has Test Cases (Given/When/Then) for non-trivial cases
- [ ] Every sub-plan / standalone has Design Decisions in the structured format
- [ ] Every sub-plan / standalone has a Rollback Boundary
- [ ] Every sub-plan / standalone has a Status field (Draft / Active / Completed / Superseded)
- [ ] Plans reference only files/paths that exist (no invented paths)
- [ ] Sub-plan splits at natural seams (not arbitrary line-count cuts)
- [ ] No sub-plan's testability depends on a sibling not yet shipped
- [ ] No code snippets (exception: interface/type contracts only)

Any failure → halt and prompt the user with the specific item(s) that failed.

## Phase 1g — Implementation start approval gate (mandatory)

Phase 1c approved the high-level goal. Phase 1g approves the actual plan files before any implementation work begins.

Present this block:

```
**Plans written and ready for review:**

- `path/to/plan-{slug}.md` — [one-line summary from plan Summary]
- `path/to/plan-{slug}-a.md` — [one-line summary]  (if umbrella)
- ...

Please read the plan file(s) above. Reply "Approved — start implementation" to begin Phase 2, or describe any corrections needed.
```

Call `ask_user` with choice `["Approved — start implementation"]` and allow inline freeform corrections.

- Approval → exit this skill with success status.
- Corrections → revise plan files, re-run Phase 1f, re-present this gate. Loop until approved.

---

## Exit behavior

When called **standalone**, exit on Phase 1g approval. Tell the user:
- The approved plan file path(s).
- Next step: invoke `/dreamers-implement <path-to-plan>` (cohesive) or `/dreamers-full` (umbrella — orchestrator handles the loop).

When called **from `/dreamers-full`**, exit on Phase 1g approval. Return in chat output:
- Plan shape decision (cohesive vs umbrella).
- Plan file path(s).
- Approval status.

The orchestrator reads this chat output and proceeds to Phase 2 (`/dreamers-implement` per cohesive or per sub-plan).

## HARD STOP after Phase 1g

When plan files are written and the approval gate clears:
- Do NOT proceed to implementation.
- Do NOT delegate to any implementation agent or skill.
- Do NOT make any code edits beyond plan files.

If the user asks "start implementing" after approval, tell them to invoke `/dreamers-implement` (cohesive) or `/dreamers-full` (umbrella). This skill's lane is planning only.
