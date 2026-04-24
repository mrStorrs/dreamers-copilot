# Plan 1 — Dreamers System Cleanup (Umbrella)

**Owner:** Dreamers
**Date:** 2026-04-16
**Scope:** repo-local
**Status:** Draft
**Links:** 2026-04-16 review conversation covering CLI fit, workflow drift, and `simplify` replacement

---

## Summary

Clean up the Dreamers system so its shipped agents, skills, refs, templates, and docs describe one coherent harness-native workflow. The work also introduces a new `hone` agent and `dreamers-simplify` skill to replace the broken `/simplify` path with a supported simplification stage, while preserving `dreamers-cleanup-comments` as the whole-project cleanup flow and adding a separate feature-branch comment-cleanup skill for in-pipeline use.

---

## Problem / Motivation

The current system has multiple classes of drift:
- core workflow contradictions across refs, agents, skills, and templates
- missing support for the current `/simplify` close-out step
- planning/template inconsistencies that make Dreamers' own planning rules impossible to satisfy
- path, platform, and bootstrap guidance that does not consistently match the actual repository layout or Windows-targeted Copilot CLI usage

These issues make the system harder to trust, harder to extend, and harder to use without improvisation.

---

## Scope / Non-goals

**In scope:**
- align the canonical workflow contract for commits, findings, gates, cleanup passes, comment-cleanup skill boundaries, and improvement tracking
- add `hone` and `dreamers-simplify`, then wire that flow into the supported implementation pipelines
- normalize planning artifacts, templates, and Nova's role so Dreamers' planning rules are internally coherent
- correct path/platform/bootstrap/doc guidance so shipped docs describe the system that actually exists

**Non-goals:**
- redesign Dreamers into a generic non-harness orchestration system
- rewrite unrelated skills or agents that are not implicated by the confirmed audit findings
- commit or ship the cleanup without explicit user review after implementation

---

## Sub-plans

| ID | File | Summary | Status |
|---|---|---|---|
| 1a | `plan-1a-align-workflow-contracts.md` | Canonicalize commit authority, findings format, quality-gate scope, nested cleanup behavior, and improvement tracking. | Draft |
| 1b | `plan-1b-add-hone-simplify.md` | Add the `hone` agent and `dreamers-simplify` skill, then replace the broken `/simplify` path in supported pipelines. | Draft |
| 1c | `plan-1c-normalize-planning-artifacts.md` | Align plan templates, shell-plan behavior, bootstrap planning flow, and Nova's role. | Draft |
| 1d | `plan-1d-align-paths-platform-and-docs.md` | Normalize path/platform guidance, bootstrap references, and user-facing documentation. | Draft |

---

## Constraints

- Preserve Dreamers as a harness-native Copilot CLI system; do not remove valid internal-harness tool usage from agent-facing instructions.
- Keep changes surgical and grounded in confirmed contradictions or gaps from the 2026-04-16 audit.
- Do not create git commits as part of this cleanup cycle; the user will review all changes before any commit happens.
- Prefer one canonical rule source per concern rather than repeating the same workflow rules in many places.
- Keep sub-plans independently testable and mergeable in sequence.

---

## End-to-end Acceptance Criteria

1. Dreamers ships a supported simplification flow built on `hone` and `dreamers-simplify`, and no shipped pipeline still depends on `/simplify`.
2. Core workflow files define one consistent contract for commit ownership, findings output, review/test gates, cleanup passes, and PR behavior.
3. Planning artifacts are internally coherent: umbrella plans, sub-plans, shell plans, and Nova responsibilities all align with the updated rules and templates.
4. User-facing docs and bootstrap guidance point to real files, describe the harness-native model accurately, and no longer rely on conflicting path or platform assumptions.
5. Dreamers distinguishes between whole-project comment cleanup and feature-branch comment cleanup, and no in-pipeline cleanup flow opens a nested branch or PR from inside another active feature pipeline.
6. The cleanup can be reviewed locally without any commit being created.

---

## Rollback / Observability strategy

- Roll back by sub-plan file group: workflow-contract files, Hone/simplify files, planning/template files, and docs/bootstrap files can each be reverted independently.
- Observe completion through static consistency checks across refs, agents, skills, and templates plus manual verification of the updated Dreamers CLI flows.
- No production data or runtime persistence is involved; the blast radius is limited to repository content and local workflow behavior.
