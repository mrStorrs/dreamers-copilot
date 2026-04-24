# Plan 1c — Normalize Planning Artifacts

**Owner:** Dreamers
**Date:** 2026-04-16
**Scope:** repo-local
**Parent:** [plan-1-dreamers-system-cleanup.md](plan-1-dreamers-system-cleanup.md)
**Depends-on:** [plan-1a-align-workflow-contracts.md](plan-1a-align-workflow-contracts.md)
**Status:** Draft
**Branch:** feat/d1-dreamers-system-cleanup
**User-testing-required:** no
**Links:** `.github\dreamers\refs\planning-protocol.md`, `.github\dreamers\refs\plan-content.md`, `.github\dreamers\refs\feature-decomposition.md`, `.github\dreamers\templates\plan-sub.md`, `.github\dreamers\templates\shell-plan.md`, `.github\agents\nova.agent.md`, `.github\skills\dreamers-new-project\SKILL.md`, `.github\skills\dreamers-plan\SKILL.md`

---

## Summary

Bring Dreamers' planning artifacts into alignment with their own rules. This sub-plan fixes the mismatch between required plan structures, shipped templates, shell-plan behavior, and Nova's documented role.

---

## Problem / Motivation

Dreamers currently requires umbrella plans and structured sub-plans, but only ships a partial sub-plan template, treats shell plans as if Nova owns initial refinement, and assigns Nova responsibilities that conflict with other planning docs. That makes the planning system impossible to follow literally.

---

## Scope / Non-goals

**In scope:**
- `plan-content.md`, `planning-protocol.md`, and any related planning-rule references that currently contradict the shipped templates
- `plan-sub.md` and any new template needed for umbrella-plan support
- `shell-plan.md` semantics and the planning flow described in `dreamers-new-project`
- Nova's documented role wherever it currently conflicts with initial planning/refinement

**Non-goals:**
- rewriting historical plans
- changing plan numbering rules unless a contradiction requires a wording fix
- broad workflow-contract or user-facing docs cleanup outside planning/bootstrap paths

---

## Constraints

- Keep shell plans lightweight and clearly distinct from approved implementation plans if they remain part of the system.
- Reserve Nova for post-sub-plan revalidation unless the updated rules explicitly redefine that role.
- Ensure each required artifact type has either a matching template or a clear documented reason why no template is needed.
- Do not add code snippets to planning templates beyond already-permitted interface/type-contract exceptions.

---

## Design Decisions

**Decision:** Ship a dedicated umbrella-plan template instead of overloading `plan-sub.md` for every plan type.  
**Rationale:** The current rules require umbrella plans with sections that `plan-sub.md` does not provide.  
**Rejected:** Pretending `plan-sub.md` is enough for all cases; removing umbrella plans from the system entirely.

**Decision:** Update `plan-sub.md` so it matches the required metadata and section set for sub-plans.  
**Rationale:** A required template that cannot satisfy its own content rules invites repeated planning drift.  
**Rejected:** Leaving the mismatch in place; relying on planners to remember unwritten required fields.

**Decision:** Keep `shell-plan.md` as a distinct pre-plan artifact, but remove wording that frames Nova as the initial refinement owner.  
**Rationale:** The current shell-plan flow can still be useful for new-project scoping, but it should route into planning skills rather than contradict Nova's bounded role.  
**Rejected:** Treating shell plans as full approved plans; keeping the current "awaiting Nova refinement" wording.

**Decision:** Route initial plan-quality corrections back to the planning flow, not to Nova.  
**Rationale:** Nova is explicitly bounded to revalidation between sub-plans, and the docs should reflect that.  
**Rejected:** Using Nova as a catch-all planning repair agent.

---

## Acceptance Criteria

1. Every plan artifact type Dreamers requires in scope has a matching template or an explicit documented distinction, and the templates match the updated rules.
2. `plan-sub.md` includes the required sub-plan metadata and section structure defined by the updated plan-content rules.
3. If umbrella plans remain required, the repository ships a dedicated umbrella-plan template and the planning docs point to it correctly.
4. `shell-plan.md`, `dreamers-new-project`, and the planning refs describe one coherent path from shell planning to approved implementation planning.
5. Nova's role in agent docs, templates, and planning refs is limited to post-sub-plan revalidation rather than initial planning ownership.

---

## Test Cases for Probe

**TC-1 (unit — template-to-rule alignment):**  
Given the updated planning refs and templates /  
When Probe compares required sections and metadata for each plan type /  
Then every required field in scope is represented correctly in the matching template.

**TC-2 (integration — shell-plan to full-plan flow):**  
Given the updated `dreamers-new-project`, `shell-plan.md`, and planning refs /  
When Probe traces the documented flow from milestone shell plan to approved implementation plan /  
Then the flow is coherent and does not require Nova to do initial planning work.

**TC-3 (integration — Nova role alignment):**  
Given the updated Nova agent file and planning refs /  
When Probe inspects every scoped reference to Nova /  
Then Nova is only assigned post-sub-plan revalidation duties unless an explicitly updated rule says otherwise.

**TC-4 (UI / E2E — planner usability):**  
Given the updated plan templates and planning skills /  
When a human planner follows the documented process to create shell plans, umbrella plans, and sub-plans /  
Then the required artifact type and template are obvious at each step without relying on unwritten convention.

**TC-5 (regression risk — plan decomposition behavior):**  
Given the updated planning artifacts /  
When Probe checks the decomposition rules against the shipped templates /  
Then non-trivial work still decomposes into umbrella and sub-plan artifacts rather than collapsing back into one monolithic template.

---

## Rollback Boundary

This sub-plan is limited to planning refs, planning templates, Nova-role wording, and the new-project/planning skill docs that depend on them. Reverting those files returns Dreamers to its prior planning model without affecting Hone or the core workflow-contract cleanup.

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| Template changes accidentally force more process than the system needs. | Keep artifact types explicit and minimal: shell plan, umbrella plan, sub-plan. |
| Nova remains implied as an initial planner in a stray file. | Update every confirmed Nova reference in scope as part of the same sub-plan. |
| Planning docs become correct but harder to use. | Add explicit file-role distinctions and keep templates lean enough for direct adoption. |
