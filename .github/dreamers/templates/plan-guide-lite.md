# Lite Plan Guide

Use for tiny localized work. If architecture, contracts, data, UI flow, or risk matters, use `standard` or `complex`.

## Required metadata

- `# Plan-NN: {short-title}`
- `**Date:**` YYYY-MM-DD
- `**Status:**` Draft / Active / Completed / Superseded
- `**Plan-type:** lite`
- `**Branch:** feat/{slug}` or `**Branch:** fix/{slug}`
- `**User-testing-required:** yes/no`
- `**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)` when the sibling artifact exists

## Required sections

1. **Goal** — one paragraph.
2. **Files Touched** — exact paths table.
3. **Acceptance Criteria** — XML-wrapped G/W/T with layer annotations.
4. **Verification** — commands and smoke check.

Optional: **Context** or **Out of Scope** if they prevent ambiguity.

## Files Touched

| Path | Action | Required change | Verification |
|---|---|---|---|
| `path/file.ext` | modify | Exact change. | Test or inspection. |

If implementation discovers adjacent required files, update this table before implementation continues.

## Acceptance Criteria

<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
</acceptance_criteria>

Layer labels: `unit` / `integration` / `E2E` / `perf`.

## Verification

- **Test command:** command from project instructions.
- **Type-check command:** command from project instructions.
- **Files to inspect after implementation:** exact paths.
- **Smoke check:** one specific check.

## Hard rules

- No vague file rows.
- No standalone Test Cases section.
- No code snippets unless a minimal public interface signature is the contract.
- Verification stays last.
