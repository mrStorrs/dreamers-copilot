# Plan N[letter] — [Short Description]

**Owner:** [Owner]
**Date:** YYYY-MM-DD
**Scope:** repo-local
**Parent:** [plan-N-short-name.md](plan-N-short-name.md)
**Depends-on:** [plan-Na-prior-sub-plan.md](plan-Na-prior-sub-plan.md) *(or "none")*
**Status:** Draft
**Branch:** feat/d<N>-<name>
**User-testing-required:** yes/no
**Links:** *(list any key refs or related files, or omit if none)*

---

## Summary

[1-2 sentences: what this sub-plan delivers and why it is needed]

---

## Scope / Non-goals

**In scope:**
- [file or component being changed, with one-line reason]

**Non-goals:**
- [what this deliberately does NOT cover]

---

## Constraints

- [hard rules Forge must not violate]

---

## Design Decisions

**Decision:** [what was chosen]
**Rationale:** [why — the specific trade-off or constraint that drove it]
**Rejected:** [alternatives considered and why they lost]

### Race conditions and ordering
*(Required when the data flow involves async operations, shared mutable state, or concurrent writes — e.g., seq counters, catch-up protocols, event replay, optimistic UI updates. Omit only if the sub-plan has no async flows with shared state.)*

| Scenario | Risk | Resolution |
|---|---|---|
| [concurrent operation A and B] | [what can go wrong] | [how the design prevents it] |

---

## Acceptance Criteria

1. [Numbered, measurable, Forge-verifiable — not vague]
2. ...

---

## Post-merge gates

*(Remove this section if all ACs are verifiable before PR merge. Use it only for ACs that require the branch to be merged to main first — e.g., auto-deploy triggers, production DNS propagation, webhook callbacks from external services.)*

| AC | Verification step | Who verifies |
|---|---|---|
| [AC number] | [exact check to perform after merge] | [human / automated] |

---

## Test Cases for Probe

**TC-1 ([short name]):**
Given [precondition] /
When [action] /
Then [expected outcome]

**TC-2 ([short name]):**
Given ... / When ... / Then ...

---

## § Deferred Items

[Any known defects or scope items punted from this plan]

| Item | Why deferred | Target milestone |
|---|---|---|
| — | — | — |

*(Remove this section entirely if there are no deferred items.)*

---

## Rollback Boundary

[Which files can be reverted, and whether rollback affects other sub-plans or features]

---

## Risks / Mitigations

| Risk | Mitigation |
|---|---|
| [risk] | [mitigation] |
