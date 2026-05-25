# Feature: [short name]

**Date:** YYYY-MM-DD
**Status:** Draft *(Draft / Active / Completed / Superseded)*

---

## Summary

[2–4 sentences: what this feature delivers end-to-end and why. The manifest exists because the work spans multiple plans AND there's shared context that benefits every plan in the sequence.]

---

## Plan sequence

| Order | Plan file | Summary |
|---|---|---|
| 1 | [plan-01-<name>.md](plan-01-<name>.md) | [one line] |
| 2 | [plan-02-<name>.md](plan-02-<name>.md) | [one line] |
| 3 | [plan-03-<name>.md](plan-03-<name>.md) | [one line] |

Plans run in this order via `/dreamers-full feature-<slug>/manifest.md` (or equivalently `/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md ...` if invoked variadically — same result, no shared context threading in variadic mode).

Each plan above is independently shippable. If a single plan is invoked alone (`/dreamers-implement feature-<slug>/plan-NN-<name>.md`), the manifest content is NOT loaded; the plan must stand on its own. Use the manifest invocation when you want the full sequence with shared context.

---

## Shared constraints

<shared_constraints>
- [Hard rules that apply across ALL plans in this feature.]
- [Example: "All plans must preserve API X's backward compatibility until plan-03 ships."]
- [Example: "All new database tables follow naming convention Y."]
- [Cross-plan rollback rules belong here, NOT in a separate rollback section: "If plan-02 must be reverted, plan-01's schema must also revert because Z."]
</shared_constraints>

Skip this section if there are no genuine cross-plan constraints — that's a signal the manifest may not be needed.

---

## Shared design decisions

**Decision:** [what was chosen — applies across multiple plans]
**Rationale:** [why — one sentence]
**Rejected:** [alternatives considered]

[Example: "Decision: state machines for all auth flows. Rationale: makes login/logout/reset/MFA share the same abstraction. Rejected: per-flow ad-hoc handlers (duplicates state-transition logic across plans)."]

---

## Shared data models  (only if 2+ plans produce or consume the same interface)

[Data shapes / interface contracts referenced by multiple plans. Critical for AI context: when plan-02 references `UserSession`, the reviewer running on plan-02 benefits from seeing the definition here. Inline the interface — no implementation.]

```typescript
interface UserSession {
  userId: string
  expiresAt: Date
  // ...
}
```

Skip if no shared data models cross plan boundaries.

---

## End-to-end Acceptance Criteria

*(Verified only after ALL plans in the sequence ship. Different from per-plan ACs — those verify a single plan; these verify the whole feature.)*

<acceptance_criteria>
1. Given [feature-level state], when [whole-feature trigger], then [observable outcome AT FEATURE LEVEL — e.g., "User completes the full login → reset password → re-login flow without errors."].
   *Layer: E2E.*
2. ...
</acceptance_criteria>

---

## Sections NOT to include in a manifest

- **Risks / Mitigations (cross-plan)** — real cross-plan risks belong in Shared constraints as hard rules with rationale. Decorative risk enumeration adds no execution value.
- **Rollback strategy (cross-plan)** — cross-plan rollback rules belong in Shared constraints, with the conditions and order spelled out as hard rules. No separate prose section.
