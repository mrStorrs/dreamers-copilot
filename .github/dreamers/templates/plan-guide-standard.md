# Standard Plan Guide

Default for normal feature work.

## Required metadata

- `# Plan-NN: {short-title}`
- `**Date:**` YYYY-MM-DD
- `**Status:**` Draft / Active / Completed / Superseded
- `**Plan-type:** standard`
- `**Branch:** feat/{slug}` or `**Branch:** fix/{slug}`
- `**User-testing-required:** yes/no`

## Required sections

1. **Goal**
2. **Context**
3. **Architecture**
4. **Files Touched**
5. **Acceptance Criteria**
6. **Out of Scope**
7. **Constraints**
8. **Verification**

Triggered sections:

- **Design Decisions:** required for non-obvious architecture, API, data, persistence, or UI choices.
- **UI:** required for user-visible surfaces.
- **Mermaid:** required for non-trivial flow, process, state machine, lifecycle, async handoff, branching path, or multi-step workflow.

## Architecture

Cover only what matters:

- Current flow / target flow.
- Boundary ownership.
- Contracts, or `No contract changes.`
- Failure and edge states.
- Mermaid diagram when triggered.

## Files Touched

| Path | Action | Required change | Verification |
|---|---|---|---|
| `path/file.ext` | modify | Exact change. | Test or inspection. |

Adjacent files may be added only when discovered during implementation and justified by the same goal.

## Acceptance Criteria

<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
</acceptance_criteria>

Layer labels: `unit` / `integration` / `E2E` / `perf`.

## Constraints

<constraints>
- **Technical:** stack / perf / libraries.
- **Process:** gates / review / tests.
- **Hard rules:** never-do constraints with rationale.
</constraints>

## Verification

- **Test command:** command from project instructions.
- **Type-check command:** command from project instructions.
- **Files to inspect after implementation:** exact paths.
- **Smoke check:** one or two specific checks.

Verification stays last.
