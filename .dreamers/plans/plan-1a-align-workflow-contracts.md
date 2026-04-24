# Plan 1a — Align Workflow Contracts

**Owner:** Dreamers
**Date:** 2026-04-16
**Scope:** repo-local
**Parent:** [plan-1-dreamers-system-cleanup.md](plan-1-dreamers-system-cleanup.md)
**Depends-on:** None
**Status:** Draft
**Branch:** feat/d1-dreamers-system-cleanup
**User-testing-required:** no
**Links:** `.github\copilot-instructions.dreamers.md`, `.github\dreamers\refs\delegation.md`, `.github\dreamers\refs\quality-gates.md`, `.github\dreamers\refs\git-workflow.md`, `.github\dreamers\refs\close-out.md`, `.github\dreamers\refs\sub-plan-loop.md`, `.github\agents\forge.agent.md`, `.github\agents\sentinel.agent.md`, `.github\agents\probe.agent.md`, `.github\skills\dreamers-full\SKILL.md`, `.github\skills\dreamers-fix\SKILL.md`, `.github\skills\dreamers-atlas-choice\SKILL.md`, `.github\skills\dreamers-clean-work\SKILL.md`, `.github\skills\dreamers-cleanup-comments\SKILL.md`

---

## Summary

Make the Dreamers workflow contract internally consistent before adding new capability. This sub-plan resolves the confirmed contradictions around findings format, commit ownership, review/test gate scope, the split between whole-project and feature-branch comment-cleanup behavior, and improvement tracking.

---

## Problem / Motivation

Dreamers currently gives different answers to basic workflow questions depending on which file is read: who commits, what `findings.md` looks like, when Sentinel and Probe are required, whether comment cleanup is a project-wide maintenance flow or an in-pipeline branch-local pass, whether cleanup passes may create their own PRs, and where improvement tracking lives. Until those contracts align, later changes will keep compounding drift.

---

## Scope / Non-goals

**In scope:**
- `.github\dreamers\refs\quality-gates.md` and all producers/consumers of `findings.md`
- `.github\dreamers\refs\git-workflow.md`, `.github\dreamers\refs\sub-plan-loop.md`, and commit-related agent/skill wording
- `.github\copilot-instructions.dreamers.md` plus quality-gate language in primary workflow skills
- `.github\skills\dreamers-cleanup-comments\SKILL.md`, the new feature-branch comment-cleanup skill, and `.github\skills\dreamers-clean-work\SKILL.md` where they conflict with the main branch/PR model
- the canonical path and policy for Dreamers improvements tracking

**Non-goals:**
- adding the new `hone` agent or `dreamers-simplify` skill
- planning-template or Nova-role cleanup
- broad user-facing doc polish beyond wording required to remove workflow contradictions

---

## Constraints

- Keep valid harness-native tool guidance intact for agent-facing instructions.
- Choose one canonical contract per concern and align all dependent files to it.
- Do not introduce any branch or PR creation step inside a cleanup substep that can be invoked from another active pipeline.
- Do not create commits during the cleanup cycle; the user wants review before any commit.

---

## Design Decisions

**Decision:** Treat `.github\dreamers\refs\quality-gates.md` as the canonical `findings.md` contract and align Sentinel, Nova, and PR-template references to that schema.  
**Rationale:** The gate document is already the natural contract source for downstream routing and validation.  
**Rejected:** Keeping narrative `findings.md` output in Sentinel; allowing mixed JSON and prose formats.

**Decision:** Standardize Bolt as the sole committer in Dreamers workflows.  
**Rationale:** The existing core refs already center commit/push/PR work in Bolt, and one committer keeps stage ownership simple.  
**Rejected:** Letting Forge or Probe commit conditionally; leaving skill-specific exceptions in place.

**Decision:** Scope the "Sentinel must review / Probe must test" rule to PR-bearing code-change workflows, with any exceptions documented explicitly and consistently.  
**Rationale:** The current absolute wording is contradicted by shipped Tier 1 and maintenance flows.  
**Rejected:** Pretending no exceptions exist; leaving each skill to define its own ad hoc interpretation.

**Decision:** Keep `dreamers-cleanup-comments` as the whole-project cleanup skill and introduce a second feature-branch comment-cleanup skill for in-pipeline use.  
**Rationale:** The existing skill has value as a repo-wide cleanup pass, but in-pipeline workflows like `dreamers-full` need a branch-local cleanup step that does not hijack branch or PR ownership.  
**Rejected:** Converting `dreamers-cleanup-comments` itself into a branch-local pass; continuing to invoke the whole-project cleanup skill from inside feature pipelines.

**Decision:** Use one repo-local improvements path and one governance policy.  
**Rationale:** Split paths and mixed "edit now" versus "propose only" rules create silent drift.  
**Rejected:** Keeping both `.dreamers\improvements.md` and `.dreamers\atlas\improvements.md`; mixing auto-edit and proposal-only modes.

---

## Acceptance Criteria

1. `findings.md` format, empty-state behavior, ID scheme, and allowed severities match across quality gates, Sentinel instructions, Nova expectations, and any template references.
2. Every commit-related file in scope assigns commit creation to Bolt only, and no scoped file tells Forge or Probe to commit.
3. Global and skill-level review/test gate wording agree on when Sentinel and Probe are mandatory and where exceptions exist.
4. Dreamers clearly distinguishes whole-project and feature-branch comment-cleanup behavior, and the feature-branch cleanup flow used by parent pipelines does not create a nested branch or PR.
5. Dreamers improvements tracking uses one path and one consistent policy across close-out and maintenance flows.

---

## Test Cases for Probe

**TC-1 (unit — findings schema alignment):**  
Given the updated workflow files /  
When Probe compares every `findings.md` producer, consumer, and template reference in scope /  
Then the schema, ID format, allowed severities, and no-findings state match exactly.

**TC-2 (unit — commit authority alignment):**  
Given the updated agent, ref, and skill files /  
When Probe inspects commit-related instructions in scope /  
Then Bolt is the only role authorized to create commits and no scoped file instructs Forge or Probe to commit.

**TC-3 (integration — gate policy consistency):**  
Given the full, Tier 1, Tier 2, and maintenance workflow docs in scope /  
When Probe traces each documented PR-bearing path end to end /  
Then the review/test gate policy is internally consistent and any exceptions are explicitly documented rather than implied.

**TC-4 (UI / E2E — split cleanup behavior):**  
Given the updated `dreamers-full`, `dreamers-cleanup-comments`, and feature-branch comment-cleanup instructions /  
When a human reads the documented flows for repo-wide cleanup versus in-pipeline cleanup /  
Then the whole-project skill is clearly separate from the branch-local skill, and the in-pipeline cleanup flow does not instruct them to cut a second branch or open a second PR from inside the parent pipeline.

**TC-5 (regression risk — improvement tracking path):**  
Given the updated close-out and clean-work files /  
When Probe checks the improvement-tracking path and behavior references /  
Then all scoped files refer to the same path and the same governance model.

---

## Rollback Boundary

This sub-plan is limited to workflow-contract files in `.github\copilot-instructions.dreamers.md`, `.github\dreamers\refs\`, `.github\agents\`, and selected `.github\skills\` files. Reverting those files restores the prior Dreamers workflow contract without affecting later sub-plans.

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| Fixing one contradiction accidentally introduces a new one in a less-visible skill or template. | Update the canonical source first, then sweep every confirmed producer/consumer in the same sub-plan. |
| Tightening gate wording breaks legitimate lightweight maintenance flows. | Scope the mandatory-gate language explicitly and document any retained exceptions in one place. |
| The distinction between whole-project cleanup and feature-branch cleanup remains muddy after the rewrite. | Give each cleanup mode a distinct documented purpose and ensure parent workflows call only the branch-local variant. |
