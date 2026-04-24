# Plan 1d — Align Paths Platform And Docs

**Owner:** Dreamers
**Date:** 2026-04-16
**Scope:** repo-local
**Parent:** [plan-1-dreamers-system-cleanup.md](plan-1-dreamers-system-cleanup.md)
**Depends-on:** [plan-1a-align-workflow-contracts.md](plan-1a-align-workflow-contracts.md), [plan-1b-add-hone-simplify.md](plan-1b-add-hone-simplify.md), [plan-1c-normalize-planning-artifacts.md](plan-1c-normalize-planning-artifacts.md)
**Status:** Draft
**Branch:** feat/d1-dreamers-system-cleanup
**User-testing-required:** no
**Links:** `README.md`, `Install-Dreamers.ps1`, `Remove-Dreamers.ps1`, `.github\copilot-instructions.dreamers.md`, `.github\dreamers\refs\project-bootstrap.md`, `.github\dreamers\refs\sub-plan-loop.md`, `.github\dreamers\templates\pr-description.md`, scoped skills/refs with path or platform guidance

---

## Summary

Normalize the shipped docs and guidance so they describe the actual Dreamers system accurately for this Copilot CLI environment. This sub-plan resolves confirmed path/platform drift, incorrect bootstrap references, and stale Claude Code wording.

---

## Problem / Motivation

The repository currently mixes valid harness-native concepts with conflicting user-facing guidance: ambiguous `~/.copilot/...` read instructions in contexts that need exact paths, POSIX-only "mandatory" command snippets despite Windows-targeted usage, a bootstrap reference to a file location that is not installed there, and stale Claude Code branding.

---

## Scope / Non-goals

**In scope:**
- `README.md` and any shipped user-facing Dreamers descriptions
- path/platform guidance in scoped refs and skills that was confirmed to conflict with the active environment or repo layout
- `project-bootstrap.md` and any file-location references it currently gets wrong
- stale product-branding residue in scoped templates and docs
- any user-facing mention needed to explain Hone and `dreamers-simplify` after sub-plan 1b lands
- `sub-plan-loop.md`: add the `dreamers-simplify` step between `[all sub-plans done]` and `PR opened` so the loop diagram matches what the calling skills actually do

**Non-goals:**
- redesigning installer behavior unless documentation cannot be corrected without a real file move
- removing harness-native tool language from agent-facing instructions where it is valid
- broad copy-editing unrelated to confirmed fit or accuracy issues

---

## Constraints

- Distinguish clearly between agent-facing harness instructions and user-facing CLI workflow guidance.
- Where a file read truly requires an exact path, document it in OS-native terms rather than relying on ambiguous shorthand.
- Replace POSIX-only mandatory snippets with tool-agnostic or Windows-safe guidance in this repository's shipped docs.
- Keep the documentation accurate to the repo that actually ships after sub-plans 1a through 1c.

---

## Design Decisions

**Decision:** Keep harness-native tool usage in agent-facing files, but rewrite user-facing docs to talk in normal Dreamers/Copilot CLI workflow terms.  
**Rationale:** The system is intentionally harness-native, but user docs should not read like raw internal tool API notes.  
**Rejected:** Removing harness-native instructions entirely; leaving user docs mixed with internal orchestration jargon.

**Decision:** Replace ambiguous path wording with explicit guidance to resolve Copilot home and use OS-native absolute paths where exact file reads matter.  
**Rationale:** The current mix of `~/.copilot/...` and "full path" language is not reliable in this Windows-targeted environment.  
**Rejected:** Keeping shorthand everywhere; forcing every file to embed one hard-coded absolute path.

**Decision:** Correct the bootstrap/reference docs before changing installer behavior.  
**Rationale:** The confirmed bootstrap error is currently a documentation mismatch, not necessarily an installer defect.  
**Rejected:** Expanding installer scope first; leaving broken file-location guidance in place.

**Decision:** Remove stale Claude Code language from Dreamers docs and templates.  
**Rationale:** The shipped repository should accurately represent the system users are working with today.  
**Rejected:** Leaving the residue because it is "only wording."

---

## Acceptance Criteria

1. User-facing Dreamers docs in scope describe the system as a harness-native Copilot CLI workflow without mixing in unsupported or misleading slash-command guidance.
2. Path guidance in scope no longer relies on ambiguous shorthand when the underlying instruction requires an exact file path or OS-native path form.
3. Scoped path/platform guidance no longer uses POSIX-only mandatory command snippets where Windows-safe or tool-agnostic wording is required.
4. `project-bootstrap.md` and related docs in scope point to real file locations that exist in the repository or installed Dreamers layout they describe.
5. Scoped docs and templates no longer contain stale Claude Code naming, and user-facing descriptions include the shipped Hone/`dreamers-simplify` additions plus the split between whole-project and feature-branch comment-cleanup skills where relevant.

---

## Test Cases for Probe

**TC-1 (unit — path guidance accuracy):**  
Given the updated docs and refs in scope /  
When Probe checks every exact-path or file-location instruction that was flagged in the audit /  
Then each instruction points to a real file or clearly tells the reader how to resolve the correct OS-native path.

**TC-2 (unit — branding and simplify references):**  
Given the updated scoped docs and templates /  
When Probe searches for stale Claude Code wording and the broken `/simplify` guidance /  
Then neither remains in scope after the cleanup lands.

**TC-3 (integration — bootstrap/readme consistency):**  
Given the updated `README.md`, `project-bootstrap.md`, and any related installer/bootstrap references /  
When Probe compares the described file locations and setup steps /  
Then the docs agree on where Dreamers-managed files live and how they should be copied or installed.

**TC-4 (UI / E2E — Windows doc usability):**  
Given a human following the updated README/bootstrap guidance from this repository on Windows /  
When they step through the documented setup and workflow instructions /  
Then they do not hit a mandatory POSIX-only command or an unresolved path reference in the scoped docs.

**TC-5 (regression risk — harness-native model preserved):**  
Given the updated user-facing and agent-facing files in scope /  
When Probe compares the two layers of guidance /  
Then harness-native tool usage is still present where Dreamers needs it, while user-facing docs stay readable and accurate.

---

## Rollback Boundary

This sub-plan is bounded to README, bootstrap refs, path/platform wording, and related templates/docs. Reverting those files removes the documentation/path cleanup without undoing the underlying workflow or planning changes from the earlier sub-plans.

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| A documentation-only fix hides a real installer/layout issue. | Verify each referenced file location against the actual repository and installed Dreamers layout before final wording is locked. |
| Path wording becomes too Windows-specific and less portable. | Use OS-native "resolve to an absolute path" language with Windows-safe examples for this repo instead of hard-coding one non-portable path style everywhere. |
| User-facing docs drift again from agent-facing behavior. | Update user-facing docs only after workflow and planning sub-plans land so they describe the final shipped behavior. |
