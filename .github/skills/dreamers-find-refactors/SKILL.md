---
name: dreamers-find-refactors
description: 'Find refactoring opportunities across a codebase. Sections the project, runs section-scoped Hone audits, synthesizes findings, and writes Dreamers plan files. Read-only for project code; no implementation, branch, commit, push, or PR. Triggers: /dreamers-find-refactors, find refactors, refactor audit, refactoring opportunities.'
argument-hint: '[scope or directive]'
---

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist (HARD RULE)

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

$ARGUMENTS

Read-only discovery skill. It may write only:
- `.dreamers/refactor-audits/<slug>/sections.md`
- `.dreamers/refactor-audits/<slug>/summary.md`
- `.dreamers/reviews/hone-refactor-*.md` through Hone
- `.dreamers/plans/feature-refactor-<slug>/plan-NN-*.md`
- `.dreamers/plans/feature-refactor-<slug>/manifest.md` when needed

It must not edit project source, tests, docs, config, dependency files, git state, branches, commits, pushes, or PRs.

## Todo - Before you begin

Declare a todo list marking all phases at entry:
- Phase 1 - Refactor type selection
- Phase 2 - Project sectioning
- Phase 3 - Section Hone audits
- Phase 4 - Synthesis
- Phase 5 - Plan generation
- Phase 6 - Review gate

## Phase 1 - Refactor type selection

Ask the user to choose one or more refactor lenses. Use multi-select when available:
- `All refactor types`
- `Over-engineering / simplification`
- `Duplicate logic / consolidation`
- `Module boundaries / layering`
- `Coupling / dependency cleanup`
- `State or data-flow simplification`
- `Public API / contract cleanup`
- `Error handling / impossible defensive code`
- `Dead code / unused abstractions`
- `Testability seams`
- `Custom directive`

If the user supplied an explicit scope or directive in `$ARGUMENTS`, carry it into the prompt and still ask for lens selection unless the lens is already unambiguous.

If `Custom directive` is selected, capture the custom directive before Phase 2.

Do not proceed without at least one selected lens.

## Phase 2 - Project sectioning

Read project instructions and repo structure:
- `.github/copilot-instructions.md` when present
- `README.md` or project-specific docs only as needed
- top-level source, test, package, app, module, and config boundaries

Use `rg --files` to map files. Ignore generated/vendor/build/cache/output paths, including:
- `.git/`, `.dreamers/`, `node_modules/`, `vendor/`, `dist/`, `build/`, `coverage/`, `.next/`, `.nuxt/`, `.turbo/`, `.gradle/`, `.dart_tool/`, `Pods/`, `DerivedData/`, `target/`, `bin/`, `obj/`
- lockfiles unless the user's scope specifically includes dependency structure

Create sections by natural ownership boundary:
- app/package/module directories
- architectural layers
- major feature areas
- shared libraries/utilities
- tests only when they reveal testability refactors or duplicated setup

Keep sections small enough for Hone to inspect deeply. Split oversized sections; merge tiny related sections. Prefer 4-12 sections for a typical repo. If the repo is small, one section is acceptable.

Write:

`.dreamers/refactor-audits/<slug>/sections.md`

Format:

```
# Refactor Audit Sections: <slug>

Selected lenses:
- <lens>

Scope directive:
- <directive or none>

Sections
1. <section-slug>
   - Purpose: <why these files belong together>
   - Files:
     - <path>
   - Excluded:
     - <path or glob> - <reason>
```

Use a short slug from the user's task or repo name. If no clear slug exists, use `refactor-audit`.

## Phase 3 - Section Hone audits

Record existing `.dreamers/reviews/hone-refactor-*.md` files before spawning so stale artifacts are never mistaken for this run.

Spawn Hone once per section. Batch parallel calls with a sane concurrency limit, normally 4-6 at a time. If the runtime cannot batch, run sections sequentially.

Each Hone prompt MUST include all required Dreamers delegated-agent fields and:

```
Context: Section-scoped refactor discovery via /dreamers-find-refactors. This is read-only discovery for future plans, not implementation review.
Prior work: Section manifest written to <absolute path to sections.md>. Existing review artifacts before this run: <list or none>.
What is needed: Audit only this section for the selected refactor lenses. Write exactly one artifact at .dreamers/reviews/hone-refactor-<section-slug>-<yyyymmdd-hhmmss>.md. Return status, counts, artifact path, blocked reason, and open questions only.
Selected lenses: <selected lenses + custom directive if any>
Section: <section slug + purpose>
Scope: <section file list>
Constraints:
- Read-only for project code, tests, docs, config, scripts, and git state.
- Allowed write: exactly one markdown artifact under .dreamers/reviews/.
- Do not stage, commit, push, install dependencies, open PRs, or run mutating project commands.
- Refactor cost is not a moderating factor. Surface full refactors with explicit breadth.
- Do not turn each smell into a plan; report findings precisely so the parent can group them.
Definition of Done:
- Artifact exists at the requested path.
- Findings use reviewer format with [simplicity] and explicit file:line or scoped path.
- Full-refactor findings include breadth: files, modules, call sites, deletions where known.
- Observations and Open Questions are present.
Plan file path: none
Do NOT call manage_todo_list. The skill that invoked you owns its todo.
```

Hone artifact format should be the normal artifact contract plus:

```
Section: <section-slug>
Selected lenses:
- <lens>

Plan Candidates
- <candidate title> - <finding references or none>
```

## Phase 4 - Synthesis

Read every returned Hone artifact path. If a path is missing or unreadable:
1. Inspect only new `.dreamers/reviews/hone-refactor-*.md` artifacts created after Phase 3 started.
2. If exactly one new artifact matches the section, read it.
3. Otherwise mark that section as blocked in the summary and continue with other sections.

Deduplicate overlapping findings across sections. Group findings into coherent refactor candidates by implementation boundary, not by raw finding count:
- one module-level refactor can absorb many findings in one section
- cross-cutting abstractions should become one candidate with clear affected areas
- unrelated fixes stay separate
- low-value or speculative findings may be skipped with reason

Write:

`.dreamers/refactor-audits/<slug>/summary.md`

Format:

```
# Refactor Audit Summary: <slug>

Selected lenses
- <lens>

Artifacts
- <section>: <artifact path> - <status>

Candidates
1. <candidate title>
   - Severity: critical/high/medium/low
   - Source findings: <artifact path + finding bullets>
   - Affected files: <paths>
   - Suggested plan: <plan slug>
   - Rationale: <one sentence>

Skipped findings
- <finding> - <reason>

Blocked sections
- <section> - <reason>

Open questions
- none | <question>
```

If open questions affect whether a plan should exist, ask the user once before Phase 5.

## Phase 5 - Plan generation

Use `plan-selection` to classify each plan. Write `plan-NN-<name>.md` under `.dreamers/plans/feature-refactor-<slug>/` using `plan-format`, and `manifest-format` when shared context or sequencing needs a manifest. Fill the outlines without their outer sync tags.

Group findings into a few coherent refactor plans, not one plan per finding. Cite the source Hone artifacts, synthesis summary, and verified affected paths in Scope and context. Include code only when a minimal interface/type signature is an agreed contract.

Apply `plan-quality` checks; resolve open decisions and fix gaps before Phase 6.

<plan-selection>
## Plan selection

`Plan-type` labels complexity for review routing; all types use the same structure. Honor an explicit user choice, noting any mismatch in the proposal. Otherwise choose:

- **lite:** tiny localized work without new architecture, contracts, migration, public API, multi-step flows, or meaningful risk.
- **standard:** normal feature work and other changes that do not need complex coordination.
- **complex:** cross-module or multi-plan work; data/API changes; security/privacy/payment risk; non-trivial state, async, or UI flows; high rollback cost.

Use `feature-<slug>/manifest.md` when multiple plans share context, constraints, contracts, or feature-level ACs. Backfill a missing manifest when adding a second plan. Each plan must remain usable alone; `/dreamers <manifest>` passes shared context through the sequence, while direct plan invocations do not.
</plan-selection>

<plan-format>
Use this structure for every plan type. Keep decisions, contracts, UI details, and risks in Scope and context only when relevant. Acceptance Criteria carry validation intent; do not add separate Approach, Verification, or Test Cases sections.

```markdown
# Plan-NN: <short title>

**Date:** YYYY-MM-DD
**Status:** Draft
**Plan-type:** <lite|standard|complex>
**Branch:** <feat/slug|fix/slug>
**User-testing-required:** <yes|no>
**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)

## Goal
<The outcome this plan delivers.>

## Scope and context
<Exact affected paths, relevant current behavior, agreed decisions, constraints, and exclusions.>

## Acceptance Criteria
<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: <unit|integration|E2E|perf>.*
</acceptance_criteria>
```

Include the transcript link only when the sibling artifact exists. Compound layers are allowed when one assertion serves both purposes. Under the relevant AC, add a test command or check when project instructions and the outcome are insufficient. For manual checks, include the steps, expected result, and why automation cannot cover them; set `User-testing-required: yes`.
</plan-format>

<manifest-format>
```markdown
# Feature: <short name>

**Date:** YYYY-MM-DD
**Status:** Draft

## Summary
<The outcome delivered by the complete feature.>

## Plan sequence
| Order | Plan file | Summary |
|---|---|---|
| 1 | [plan-01-<name>.md](plan-01-<name>.md) | <Outcome> |

## Shared context
<Only constraints, decisions and their rationale, or contracts needed by multiple plans. Include cross-plan rollback conditions and order when needed.>

## Acceptance Criteria
<acceptance_criteria>
1. Given <feature-level state>, when <whole-feature trigger>, then <observable outcome>.
   *Layer: E2E.*
</acceptance_criteria>
```

Keep plans in execution order. Manifest ACs cover outcomes requiring the whole sequence; plan ACs cover each plan. Omit shared context or feature-level ACs when none apply; do not duplicate plan content.
</manifest-format>

<plan-quality>
## Plan quality

Check plans against `plan-format`: complete metadata, clear scope, and measurable ACs with layers. Preserve every accepted requirement, decision, correction, and constraint from the proposal and user discussion, using the verbatim transcript when present. Reject unresolved decisions, placeholders, and unverifiable citations presented as facts. Fix gaps before presenting a plan or starting implementation.

If implementation reveals required adjacent files, update scope before editing them; keep changes within the same goal.

Existing plans may retain older headings if they contain the same information. A missing `Plan-type` requires a warning and explicit user approval. Shell plans must go through planning before implementation.

## Multi-plan ship strategy

Recommend INCREMENTAL for 4+ independent plans, different subsystems, or standalone user value from plan A. Recommend ATOMIC for overlapping files, ordering dependencies, schema/migration/API contracts, or verification requiring all plans. Conflicting signals default to ATOMIC.
</plan-quality>

## Phase 6 - Review gate

Present:
- section manifest path
- summary path
- Hone artifact paths
- generated plan paths
- manifest path when created
- skipped/deferred findings
- blocked sections
- open questions, if any

Stop and ask the user:
- `Approved - use these plans`
- `Minor edit`
- `Major rewrite`
- `Halt`
- `Other`

Minor edits may be applied inline to `.dreamers/refactor-audits/` or `.dreamers/plans/` outputs, then re-run the plan self-check and re-present the gate.

Major rewrite loops back to the affected phase.

Never invoke `/dreamers-implement`, `/dreamers`, `/dreamers-pr`, or create a git branch from this skill.

## Exit

Return report paths and plan paths. Hard stop. No implementation.
