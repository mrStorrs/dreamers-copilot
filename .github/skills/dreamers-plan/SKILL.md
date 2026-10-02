---
name: dreamers-plan
description: 'Grill, critique a proposal, and write concise plans with Goal, Scope and context, and Acceptance Criteria. Preserve the verbatim transcript and stop at plan approval; never implement. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<task description>'
---

$ARGUMENTS

If the task is missing, ask. Work inline and write only `.dreamers/plans/` artifacts; do not change project files or git state. When standalone, own a todo for the three steps below; otherwise use the caller's todo.

## 1: Grill
<planning-grill>
### Grill

Resolve decisions and their dependencies until the goal, scope, and constraints are understood. Explore the codebase for answers before asking the user. For unresolved decisions, use `request_information`, one blocking question at a time, with exactly:

1. Recommended answer, labeled recommended.
2. Strongest viable alternative.
3. `Other` for freeform direction.

Incorporate each answer before continuing. Do not propose while required decisions remain open.

Capture every question and response verbatim, in order, including complete tool questions, choice labels, and descriptions. Keep responses separate; never summarize, paraphrase, normalize, or omit text. When writing plans, save the exchange to `.dreamers/plans/feature-<slug>/grilling-transcript.md`, adding only speaker/sequence headings. Do not create an empty transcript.
</planning-grill>

## 2: Generate plan(s) proposal
- generate plans following `plan-format`
- plans should be the smallest shippable chunks. do not break up arbitrarily if doing so would cause more work. 
- when more than one plans are needed generate a manifest.md

## 3: Propose to user
- If: change requires a single plan. then present the full plan to the user. 
- Else: Then present the manifest when task requires multiple plans.

Present the proposal and any critiques through `request_information`: risks, assumptions, tradeoffs, and simpler alternatives. Answer questions and corrections with reasoning and a recommendation; revise and re-present until approved.

## 3: Write plan(s)
- Create `.dreamers/plans/feature-<slug>/`.
- Write numbered `plan-NN-<name>.md` files using `plan-format`; add `manifest.md` when multi-plan task

## 3: Review gate

Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`.

- Minor edit: apply, repeat Step 2 checks, and re-present.
- Major rewrite: return to Step 1 with the correction.
- Halt: stop and surface paths.
- Other: follow the user's direction.

On approval, return plan paths. If standalone use and not invoked from an outerskill, ask user if they would like to proceed with `/dreamers-implement`

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
