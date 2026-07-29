# Hone Architecture Rubric

## Core Position

End-state code quality is the only objective of the simplicity / architecture lens. Refactor cost is not a moderating factor. If the cleanest fix requires a full refactor, report it directly with explicit breadth so the orchestrator can route it through the major-refactor gate.

Bad architecture is a finding even when behavior is correct. Do not only flag broken code; flag code that is worse than it should be.

## Required Checks

For changed code in scope, look for and flag each applicable issue. Do not internally dismiss a finding because the fix is broad.

- **Over-engineering** - Code that exists for a hypothetical future case rather than a current requirement. Speculative generality is a finding until a second concrete consumer proves otherwise.
- **Premature abstractions** - Interfaces, factories, wrappers, classes, strategy objects, generic helpers, or plugin points introduced for one current caller without documented near-term need. Suggest inline code or a smaller concrete helper.
- **Redundant indirection** - Pass-through layers, aliases, wrappers, dispatch functions, or adapters that obscure the real operation without adding behavior.
- **Single-use helpers that hide simple logic** - Helpers whose body is clearer than their name or whose only caller would be easier to read inline.
- **Defensive code for impossible conditions** - Null checks, try/catch blocks, fallback branches, or validation for states prevented by the type system, parser, schema, or caller contract.
- **Duplicated logic** - Near-identical blocks, repeated control flow, repeated parsing/validation, or repeated data-shaping. Suggest one extraction point and the call sites to replace.
- **Repeated inline logic that deserves a shared helper** - Same pattern repeated enough that one named helper would reduce total code and clarify intent.
- **Dead code introduced by the change** - Unused variables, imports, functions, branches, config, comments, files, or generated scaffolding.
- **Bad module boundaries** - Logic placed in the wrong layer, new coupling across unrelated subsystems, data-shape translation spread across layers, or a module doing more than one job.
- **Hidden state or lifecycle complexity** - Mutable state, caches, registries, initialization ordering, global flags, or cleanup flows whose complexity is not required by the current behavior.
- **Poor data flow** - Procedural sequences, mutation-heavy transformations, or scattered conditionals that would be simpler as a direct data transformation, table, map, or small pure function.
- **Inconsistent local style** - Naming, file shape, dependency direction, or formatting that diverges from nearby project conventions.
- **Simpler alternative available** - Any place where the implementation uses a heavier pattern than the local codebase needs. Name the simpler pattern in the finding.
- **Full-refactor candidate** - Code structured badly enough that the honest fix is to tear out, rewrite, consolidate, or relocate a module, abstraction, or cross-file flow.

## Scope Language

When the fix has architectural scope, make the breadth explicit in the finding's suggested fix. Include files, modules, call-site counts, deletions, or affected subsystems where known.

Use direct fix language:

```
tear out X across N files
consolidate Y to one helper used at N call sites
rewrite Z module as a single function
remove W abstraction and inline it at the M call sites
move data-shape translation into X and delete the duplicate mappers in Y/Z
```

Do not soften architectural findings to fit the current plan scope. The orchestrator owns disposition.

## Non-Findings

Do not file a simplicity finding when the complexity is required by:

- A current acceptance criterion or inferred requirement.
- A real second consumer already in the codebase.
- A project convention used consistently nearby.
- A correctness, security, or compatibility constraint that would be violated by the simpler form.

When a real constraint justifies the complexity, leave it alone or mention the constraint under Observations only if it helps the orchestrator.

## Self-Check

Before approving a review with no simplicity findings, explicitly re-scan for:

- One-caller abstractions.
- Pass-through wrappers.
- Duplicate logic.
- Impossible defensive paths.
- New mutable state or lifecycle ordering.
- Cross-layer coupling.
- Full-refactor candidates.

If any item exists, report it as a finding.
