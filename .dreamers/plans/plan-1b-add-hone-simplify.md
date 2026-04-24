# Plan 1b — Add Hone Simplify

**Owner:** Dreamers
**Date:** 2026-04-16
**Scope:** repo-local
**Parent:** [plan-1-dreamers-system-cleanup.md](plan-1-dreamers-system-cleanup.md)
**Depends-on:** [plan-1a-align-workflow-contracts.md](plan-1a-align-workflow-contracts.md)
**Status:** Draft
**Branch:** feat/d1-dreamers-system-cleanup
**User-testing-required:** no
**Links:** `.github\skills\dreamers-implement\SKILL.md`, `.github\skills\dreamers-full\SKILL.md`, `.github\skills\dreamers-fix\SKILL.md`, `.github\skills\dreamers-atlas-choice\SKILL.md`, `.github\dreamers\refs\delegation.md`, `.github\agents\forge.agent.md`, `README.md`

---

## Summary

Replace the broken `/simplify` step with a first-class Dreamers simplification stage. This sub-plan adds a new `hone` agent and a new `dreamers-simplify` skill, then wires that stage into supported implementation routes as a post-completion holistic pass. Hone runs after all sub-plan cycles finish, operates on the full feature-branch diff vs the default branch, and is followed by a final Sentinel + Probe validation before close-out.

---

## Problem / Motivation

Dreamers currently depends on `/simplify`, which is not a shipped part of this system. The missing step leaves implementation close-out incomplete and encourages ad hoc cleanup instead of a defined, reviewable simplification pass.

---

## Scope / Non-goals

**In scope:**
- add `.github\agents\hone.agent.md`
- add `.github\skills\dreamers-simplify\SKILL.md`
- update pipeline/agent selection docs that need to know about Hone
- replace broken `/simplify` references in supported implementation flows
- define Hone's workspace contract and role boundaries

**Non-goals:**
- broad README/user-facing documentation cleanup beyond what is needed to support the new agent/skill references in agent-facing files
- turning Hone into a general code-review or bug-fix agent
- using Hone to bypass Sentinel or Probe

---

## Constraints

- Hone must optimize for simpler, easier-to-read, easier-to-maintain, low-redundancy code without intentionally changing behavior.
- Hone may edit code, but it must not own commits, pushes, or PR creation.
- The new simplify flow must be runnable on the active feature branch; it may not cut its own branch or open its own PR.
- Hone operates on the full feature-branch diff vs the default branch — not just the latest sub-plan's changes.
- Hone runs only after all sub-plan implementation cycles are complete, never mid-cycle.
- A final Sentinel review + Probe test pass must follow Hone before close-out.

---

## Design Decisions

**Decision:** Introduce Hone as a dedicated code-editing Dreamers agent focused on readability, maintainability, and redundancy reduction.  
**Rationale:** The simplification concern is valuable enough to deserve a dedicated role rather than a broken generic slash-command placeholder.  
**Rejected:** Keeping `/simplify`; folding the behavior into Sentinel; overloading Forge with a second unrelated persona.

**Decision:** Place Hone after all sub-plan cycles complete, operating on the full feature-branch diff vs the default branch, followed by a final Sentinel review + Probe test pass before close-out.  
**Rationale:** Hone needs the complete picture — simplifying piecemeal per sub-plan misses cross-cutting redundancy. Running Sentinel + Probe after Hone ensures the simplified code is still correct and reviewed. The pipeline becomes: `[sub-plan cycles (Forge → Sentinel → Probe) ...] → Hone (full branch diff) → Sentinel → Probe → Close-out`.  
**Rejected:** Running Hone per sub-plan (fragmented view, misses holistic simplification); running Hone before Forge (no code to simplify); skipping post-Hone validation (Hone edits code, correctness must be verified).

**Decision:** Give Hone its own repo-local workspace notes, centered on a `hone\simplification.md` artifact.  
**Rationale:** The simplification pass needs a bounded record of what was changed and why without overloading Forge's implementation notes.  
**Rejected:** Reusing Forge's artifact wholesale; running Hone with no persistent record.

**Decision:** Expose simplification through a `dreamers-simplify` skill that can be invoked directly and from parent workflows.  
**Rationale:** Dreamers already uses skills as the entry point for named workflows, and the new behavior should be discoverable and reusable.  
**Rejected:** Hidden implicit Hone delegation only; a one-off replacement string in `dreamers-implement`.

---

## Acceptance Criteria

1. The repository contains a `hone` agent definition with explicit role, constraints, tool access, workspace files, and completion/output rules focused on simplicity, readability, maintainability, and low redundancy.
2. The repository contains a `dreamers-simplify` skill that delegates to Hone on the current branch without creating a separate branch or PR.
3. No scoped workflow file still references `/simplify`; all supported simplification behavior is routed through Hone and/or `dreamers-simplify`.
4. Hone's agent definition and the `dreamers-simplify` skill specify that Hone operates on the full feature-branch diff vs the default branch, not per-sub-plan changes.
5. The primary code-changing implementation routes that adopt simplification place Hone after all sub-plan cycles complete, followed by a final Sentinel + Probe validation pass before close-out.
6. Delegation and agent-selection docs in scope describe Hone accurately enough for the orchestrator to route work without inventing behavior.

---

## Test Cases for Probe

**TC-1 (unit — Hone artifact contract):**  
Given the new `hone.agent.md` file /  
When Probe reads its required workspace files, role rules, and completion contract /  
Then Hone has a bounded simplification-focused scope and does not claim commit, push, or review authority.

**TC-2 (unit — simplify replacement):**  
Given all files in scope /  
When Probe searches for `/simplify` and Dreamers simplify-stage references /  
Then no broken `/simplify` dependency remains and all supported references point to Hone or `dreamers-simplify`.

**TC-3 (integration — pipeline ordering):**  
Given the updated implementation-route skills in scope /  
When Probe traces the documented stage ordering for each supported code-changing pipeline /  
Then Hone runs after all sub-plan cycles complete and before close-out, with a final Sentinel + Probe validation pass between Hone and close-out.

**TC-4 (integration — full branch diff scope):**  
Given a feature branch with changes from multiple sub-plan cycles /  
When Hone's agent definition and skill instructions describe the input scope /  
Then Hone is instructed to operate on all changes on the feature branch vs the default branch, not just the latest sub-plan's delta.

**TC-4 (UI / E2E — skill discoverability):**  
Given the shipped Dreamers skill files /  
When a human reviews the available Dreamers skills and the implementation-flow instructions /  
Then `dreamers-simplify` is a clearly named, current-branch simplification pass and its use in the pipeline is understandable without improvisation.

**TC-5 (regression risk — behavior-preserving simplification):**  
Given Hone's instructions and parent-pipeline expectations /  
When Probe checks the role boundaries /  
Then Hone is constrained to simplification work and does not implicitly expand into bug triage, architecture redesign, or review-signoff duties.

---

## Rollback Boundary

This sub-plan is bounded to the new Hone agent/skill files plus the workflow files that route into them. Reverting those files removes the simplification feature without undoing the broader workflow-contract cleanup.

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| Hone duplicates Forge or Sentinel responsibilities instead of owning a distinct niche. | Define Hone narrowly around simplification and make downstream review/test stages explicit. |
| The new skill is wired into too many workflows at once. | Limit adoption to clearly supported code-changing routes in this sub-plan and leave other routes unchanged unless explicitly justified. |
| Hone over-refactors behavior-critical code. | Constrain the agent to behavior-preserving simplification and require post-Hone Sentinel review + Probe test validation. |
| Post-Hone Sentinel/Probe pass adds pipeline time. | Hone runs once at the end (not per sub-plan), and post-Hone validation catches any correctness regressions before the PR ships. |
