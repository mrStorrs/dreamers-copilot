# Plan — Dreamers Approval UX and Orchestrator Terminology Cleanup

**Owner:** Copilot CLI
**Date:** 2026-04-20
**Scope:** repo-local
**Status:** Active
**Branch:** feat/dreamers-full-approval-orchestrator-cleanup
**Links:** `.github\skills\dreamers-full\SKILL.md`, `.github\copilot-instructions.dreamers.md`, `.github\agents\echo.agent.md`, `.github\agents\forge.agent.md`, `.github\agents\hone.agent.md`, `.github\agents\probe.agent.md`, `.github\agents\sage.agent.md`, `.github\agents\sentinel.agent.md`

---

## Summary

Tighten the `dreamers-full` approval gate so the user can approve quickly or type corrections inline in one `ask_user` interaction, and normalize committed Dreamers `.github` docs so the orchestrator is described consistently without the legacy `Atlas` label.

---

## Problem / Motivation

`dreamers-full` currently documents a two-step approval flow: choose approval or corrections, then provide the corrections separately. That adds friction to the planning loop. Separately, committed Dreamers docs still mix `Atlas` and `orchestrator` for the same role. Repo history shows `Atlas` was explicitly clarified, but later simplification notes flagged the dual naming as unresolved. The result is needless operator ambiguity in the shipped instructions.

---

## Scope / Non-goals

**In scope:**
- `.github\skills\dreamers-full\SKILL.md` — change the approval-gate wording to keep a quick approval option while allowing inline corrections in the same `ask_user` interaction.
- `.github\copilot-instructions.dreamers.md` — define the main Copilot CLI context only as the orchestrator.
- `.github\agents\echo.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.
- `.github\agents\forge.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.
- `.github\agents\hone.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.
- `.github\agents\probe.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.
- `.github\agents\sage.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.
- `.github\agents\sentinel.agent.md` — replace orchestrator-role `Atlas` wording with consistent terminology.

**Non-goals:**
- Changing the `ask_user` tool itself.
- Editing local `.dreamers\` workspace artifacts that mention prior terminology.
- Changing Dreamers behavior beyond wording and instruction clarity.

---

## Constraints

- Preserve an explicit quick approval path in `dreamers-full`; inline corrections must be additive, not a replacement for approval.
- Treat non-approval freeform input as corrections to revise and re-present, not as a separate follow-up branch in the flow.
- Limit terminology cleanup to committed `.github` Dreamers files that describe the active pipeline.
- Keep role ownership and handoff semantics unchanged while renaming the orchestrator label.
- Record in implementation notes that the feature branch was based on local `master` by user-approved fallback because no `origin` remote was configured.

---

## Design Decisions

**Decision:** Keep `ask_user` in the approval gate with a single explicit `Approved` option and freeform input enabled for inline corrections.
**Rationale:** This preserves the one-click happy path while removing the extra correction round-trip.
**Rejected:** Keeping `["Approved", "Corrections needed"]`; removing the explicit approval option and relying on freeform only.

**Decision:** Use `orchestrator` as the canonical term in committed Dreamers `.github` instructions and agent definitions.
**Rationale:** The user expects `Atlas` to be retired, and the current dual naming is already flagged as unresolved ambiguity.
**Rejected:** Retaining `Atlas` as an alias; changing only one or two files and leaving the rest mixed.

**Decision:** Exclude local `.dreamers\` artifacts from the terminology sweep.
**Rationale:** They are workspace outputs rather than shipped instructions, and changing them would expand scope without improving the live contract.
**Rejected:** Sweeping every file in the repo regardless of whether it ships or is local-only.

---

## Acceptance Criteria

1. `.github\skills\dreamers-full\SKILL.md` instructs the approval gate to use `ask_user` with an explicit approval option and inline freeform corrections in the same interaction.
2. `.github\skills\dreamers-full\SKILL.md` no longer instructs a separate `"Corrections needed"` choice.
3. The committed Dreamers instruction/agent files listed in scope no longer use `Atlas` to name the orchestrator role.
4. The changed wording still makes it unambiguous that the main Copilot CLI context passes prompts, reads workspace outputs, and routes agents.
5. The implementation notes capture that branch setup used local `master` as a user-approved fallback because remote truth was unavailable.

---

## Test Cases for Probe

**TC-1 (Approval gate inline corrections):**
Given `.github\skills\dreamers-full\SKILL.md` /
When Probe inspects the Phase 1 approval-gate instructions /
Then it finds one explicit approval option plus inline freeform correction handling and no separate correction-choice branch.

**TC-2 (No committed Atlas orchestrator label in scope):**
Given the committed `.github` Dreamers files listed in scope /
When Probe greps them for whole-word `Atlas` /
Then no matches remain in those scoped files.

**TC-3 (Role clarity after rename):**
Given the changed instruction and agent files /
When Probe reads the handoff and routing lines in each changed file /
Then the orchestrator responsibilities are still explicit and consistent after the terminology cleanup.

**TC-4 (Branch provenance recorded):**
Given `.dreamers\forge\implementation.md` /
When Probe reviews the implementation notes /
Then it finds a note that the feature branch was based on local `master` by user-approved fallback because no `origin` remote was configured.

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| A scoped `.github` file still contains `Atlas` after the cleanup | Run a whole-word grep over the scoped committed files before handing to Probe |
| Approval-gate wording accidentally removes the quick approval path | Keep an explicit `Approved` choice in the documented `ask_user` flow |
| Terminology edits blur agent handoff ownership | Limit edits to role labels and verify the surrounding sentences still describe the same responsibilities |

---

## Rollback / Observability

Rollback is a straight revert of the changed `.github` skill, instruction, and agent files. No runtime code, data model, or external integration behavior changes. Observability is file-content based: grep for `Atlas` in the scoped committed files and inspect the `dreamers-full` approval-gate wording.
