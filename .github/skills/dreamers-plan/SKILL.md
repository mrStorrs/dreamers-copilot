---
name: dreamers-plan
description: 'Grill, critique a proposal, and write concise plans with Goal, Scope and context, and Acceptance Criteria. Preserve the verbatim transcript and stop at plan approval; never implement. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<task description>'
---

$ARGUMENTS

If the task is missing, ask. Work inline and write only `.dreamers/plans/` artifacts; do not change project files or git state. When standalone, own a todo for the three steps below; otherwise use the caller's todo.

## 1: Agree on the proposal

Summarize the goal in one paragraph, then run the Grill.

<planning-grill>
### Grill

Resolve decisions and their dependencies until the goal, scope, and constraints are understood. Explore the codebase for answers before asking the user. For unresolved decisions, use `request_information`, one blocking question at a time, with exactly:

1. Recommended answer, labeled recommended.
2. Strongest viable alternative.
3. `Other` for freeform direction.

Incorporate each answer before continuing. Do not propose while required decisions remain open.

Capture every question and response verbatim, in order, including complete tool questions, choice labels, and descriptions. Keep responses separate; never summarize, paraphrase, normalize, or omit text. When writing plans, save the exchange to `.dreamers/plans/feature-<slug>/grilling-transcript.md`, adding only speaker/sequence headings. Do not create an empty transcript.
</planning-grill>

Select complexity and plan count using `plan-selection`. Present the proposal and critique through `request_information`: risks, assumptions, tradeoffs, and simpler alternatives. Approval is valid only after the critique is shown. Answer questions and corrections with reasoning and a recommendation; revise and re-present until approved.

## 2: Write plans

- Create `.dreamers/plans/feature-<slug>/`. Save any Grill exchange before writing plans.
- Write numbered `plan-NN-<name>.md` files using `plan-format`; add `manifest.md` when required by `plan-selection`, using `manifest-format`. Fill the outlines, omitting their outer sync tags and placeholder instructions.
- For shared components, search the project for callers and include affected callers in scope. Verify cited artifacts; label unverifiable citations `assumption pending verification`.
- Run `plan-quality` checks against the written plans, approved proposal and critique, and all user discussion. Fix omissions, contradictions, ambiguous or weakened requirements; repeat citation, structure, and coverage checks before presenting paths.

## 3: Review gate

Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`.

- Minor edit: apply, repeat Step 2 checks, and re-present.
- Major rewrite: return to Step 1 with the correction.
- Halt: stop and surface paths.
- Other: follow the user's direction.

On approval, return plan paths. Standalone use stops here; an outer skill receives control. Never invoke implementation.

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
