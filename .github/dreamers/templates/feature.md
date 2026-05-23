# Feature — [Short Name]

**Owner:** [Owner]
**Date:** YYYY-MM-DD
**Status:** Draft *(Draft / Active / Completed / Superseded)*
**Links:** *(GitHub issue, design doc, related PRs, or omit if none)*

---

## Summary

[2–4 sentences: what this feature delivers end-to-end and why. The manifest exists because the work spans multiple plans AND there's shared context that benefits every plan in the sequence.]

---

## Plan sequence

| Order | Plan file | Summary |
|---|---|---|
| 1 | [plan-{slug-a}.md](plan-{slug-a}.md) | [one line] |
| 2 | [plan-{slug-b}.md](plan-{slug-b}.md) | [one line] |
| 3 | [plan-{slug-c}.md](plan-{slug-c}.md) | [one line] |

Plans run in this order via `/dreamers-full feature-{slug}.md` (or equivalently `/dreamers-full <plan-a> <plan-b> <plan-c>` if invoked variadically — same result).

Each plan above is independently shippable. If a single plan is invoked alone (`/dreamers-implement <plan>`), the manifest content is NOT loaded; the plan must stand on its own. Use the manifest invocation when you want the full sequence with shared context.

---

## Shared constraints

[Hard rules that apply across ALL plans in this feature. Things like:
- "All plans must preserve API X's backward compatibility until plan-{c} ships."
- "All new database tables follow naming convention Y."
- "No plan may introduce dependencies on package Z."]

Skip this section if there are no genuine cross-plan constraints — that's a signal the manifest may not be needed.

---

## Shared design decisions

[Architectural / structural choices that apply across all plans. Format same as a single plan's Design Decisions:

**Decision:** [what was chosen]
**Rationale:** [why — one sentence]
**Rejected:** [alternatives considered]]

Example: "Decision: state machines for all auth flows. Rationale: makes login/logout/reset/MFA share the same abstraction. Rejected: per-flow ad-hoc handlers (duplicates state-transition logic across plans)."

---

## Shared data models

[Data shapes / interface contracts referenced by multiple plans. Critical for AI context: when plan B references `UserSession`, the reviewer running on plan B benefits from seeing the definition here. Inline the interface — no implementation.

```typescript
interface UserSession {
  userId: string
  expiresAt: Date
  // ...
}
```]

Skip if no shared data models cross plan boundaries.

---

## End-to-end Acceptance Criteria

*(Verified only after ALL plans in the sequence ship. Different from per-plan ACs — those verify a single plan; these verify the whole feature.)*

1. [Numbered, measurable, verifiable AT THE FEATURE LEVEL — e.g., "User completes the full login → reset password → re-login flow without errors."]
2. ...

---

## Risks / Mitigations (cross-plan)

[Risks that span plans. A risk specific to one plan belongs in that plan's Risks section. Examples:
- "Plan-A's schema migration must complete before plan-B's writes start. Mitigation: deploy plan-A first; verify migration; only then start plan-B."]

| Risk | Mitigation |
|---|---|
| [cross-plan risk] | [mitigation] |

---

## Rollback strategy (cross-plan)

[How the system behaves if one plan is rolled back mid-sequence. Which plans can be reverted independently; which require coordinated revert.]
