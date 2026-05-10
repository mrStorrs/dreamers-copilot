---
name: dreamers-plan
description: 'Planning only — produce a plan file from a task description without implementing anything. Use when you want a plan before committing to implementation. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '$ARGUMENTS'
---

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

Produce a plan only for the following task. Do not proceed to implementation.

$ARGUMENTS

---

## Three-phase planning conversation

### Phase 1 — Hash it out
1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question — use the `ask_user` tool one question at a time within a single round. Do not trickle questions across multiple message turns.
4. Wait for the user's responses before proceeding.

If the task is fully unambiguous, skip to Phase 2 with a brief "I understand the goal as: …" confirmation.

### Phase 1.5 — User Input Audit (gate)
Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it.

### Phase 2 — Approval gate
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

### Phase 3 — Write plan file(s)

Plan filenames follow `plan-{slug}.md` (umbrella or standalone) and `plan-{slug}-a.md`, `plan-{slug}-b.md`, … (sub-plans). No numeric prefix. Slug rules: lowercase, replace non-alphanumerics with single hyphen, trim, collapse repeats; if empty use `misc`. Plans live in `./.dreamers/plans/`.

Use templates as starting structure:
- `~/.copilot/dreamers/templates/plan-sub.md` — sub-plans and standalone plans
- `~/.copilot/dreamers/templates/plan-umbrella.md` — umbrella plans (only when decomposing)

**Each sub-plan must include:**
- `# Plan — {Short Title} ({Letter})`
- Metadata: Owner, Date, Scope, Parent (link to umbrella), Depends-on, Status (Draft/Active/Completed/Superseded), User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases for Probe (Given/When/Then for non-trivial), Rollback boundary, Risks/Mitigations

**Design Decisions format** (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User testing required:** `yes` if a human must manually verify before next sub-plan begins (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Umbrella plans (`plan-{slug}.md`) include:** Summary, Problem/Motivation, Scope/Non-goals (shared), Sub-plans (ordered table: ID | File | Summary | Status), Constraints (shared), End-to-end Acceptance Criteria, Rollback/Observability strategy.

**Standalone plans** (atomic change, no decomposition): include the same metadata block as a sub-plan (Owner, Date, Scope, Status — Draft/Active/Completed/Superseded, User-testing-required, Links). Sections: Summary, Problem/Motivation, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases for Probe, Risks/Mitigations, Rollback/Observability.

**Plans MUST NOT include code snippets.** One exception: interface and type contracts where the signature itself is the design decision.

### Phase 3 sub-step — Component usage check (mandatory, before finalizing scope)
When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's actual source root from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 3 sub-step — Citation accuracy (during plan writing)
Before citing the behavior of any existing artifact in the plan, read and verify the source. Do not cite from memory.

### Phase 3.5 — Plan quality self-check (MANDATORY, replaces former Gate 2)

Before presenting the plan path(s) to the user, verify against:
- [ ] Filenames follow `plan-{slug}[-a..n].md`
- [ ] Non-trivial features have an umbrella + sub-plans (not monolithic)
- [ ] Every sub-plan / standalone has measurable Acceptance Criteria
- [ ] Every sub-plan / standalone has Test Cases (Given/When/Then) for non-trivial cases
- [ ] Every sub-plan / standalone has Design Decisions in the structured format
- [ ] Every sub-plan / standalone has a Rollback Boundary
- [ ] Every sub-plan / standalone has a Status field (Draft / Active / Completed / Superseded)
- [ ] Plans reference only files/paths that exist (no invented paths)
- [ ] Sub-plan splits at natural seams
- [ ] No sub-plan's testability depends on a sibling not yet shipped
- [ ] No code snippets (exception: interface/type contracts only)

Any failure → halt and prompt the user with the specific item(s) that failed before presenting the plan paths.

---

## HARD STOP after Phase 3

When plan files are written and file paths are presented:
- Do NOT proceed to implementation
- Do NOT mark todos `in_progress`
- Do NOT delegate to Forge, Probe, Sentinel, or any other agent
- Do NOT query SQL todo tables for "ready" work

Tell the user to run `/dreamers-implement` when they are ready to build.
