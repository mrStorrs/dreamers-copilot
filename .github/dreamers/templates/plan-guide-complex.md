# Complex Plan Guide

Use for high-risk, cross-module, multi-plan, data/API, migration, security, or non-trivial process/state/UI work.

## Required metadata

- `# Plan-NN: {short-title}`
- `**Date:**` YYYY-MM-DD
- `**Status:**` Draft / Active / Completed / Superseded
- `**Plan-type:** complex`
- `**Branch:** feat/{slug}` or `**Branch:** fix/{slug}`
- `**User-testing-required:** yes/no`

## Required sections

1. **Goal**
2. **Context**
3. **Architecture**
4. **Decision Log**
5. **Files Touched**
6. **Acceptance Criteria**
7. **Traceability**
8. **Out of Scope**
9. **Constraints**
10. **Quality Attributes**
11. **Risk / Mitigation**
12. **Verification**

Triggered: **UI** for user-visible surfaces.

## Context

Use an evidence table. Keep prose short.

| Artifact | Verified fact |
|---|---|
| `path/file.ext` | What it proves. |

## Architecture

Must include:

- Current flow and target flow.
- Boundary ownership.
- Contracts, data shapes, schema/API changes, or `No contract changes.`
- Failure, edge, retry, rollback, and migration behavior.
- Mermaid diagram for each non-trivial flow/process/state machine.

## Decision Log

| Decision | Recommended answer | User choice | Rationale | Rejected |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Files Touched

| Path | Action | Required change | Verification |
|---|---|---|---|
| `path/file.ext` | modify | Exact change. | Test or inspection. |

Adjacent files may be added only when discovered during implementation and justified by the same goal.

## Acceptance Criteria

<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: E2E.*
</acceptance_criteria>

Layer labels: `unit` / `integration` / `E2E` / `perf`.

## Traceability

| Decision / requirement | AC | Verification |
|---|---|---|
| ... | AC-1 | Test / smoke check |

## Constraints

<constraints>
- **Technical:** stack / perf / libraries.
- **Process:** gates / review / tests.
- **Hard rules:** never-do constraints with rationale.
</constraints>

## Quality Attributes

One line each, or `N/A - <reason>`: security, privacy, accessibility, performance, migration, observability.

## Risk / Mitigation

Max 3 rows.

| Risk | Mitigation | Verification |
|---|---|---|
| ... | ... | ... |

## Verification

- **Test command:** command from project instructions.
- **Type-check command:** command from project instructions.
- **Files to inspect after implementation:** exact paths.
- **Smoke check:** one or two specific checks.

Verification stays last.
