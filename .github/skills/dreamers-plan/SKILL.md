---
name: dreamers-plan
description: 'Grill, critique a proposal, and write concise plans with Goal, Scope and context, and Acceptance Criteria. Preserve the verbatim transcript and stop at plan approval; never implement. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<task description>'
---

$ARGUMENTS

## Required workflow

1. **Grill** — resolve requirements and preserve the verbatim exchange.
2. **Propose** — critique and agree on the plan or manifest.
3. **Write and check** — create the artifacts and verify scope and acceptance criteria.
4. **Approve** — revise until approved, then return paths and stop.

<workflow-progress>

Use this skill's Required workflow as the single `manage_todo_list`. Reuse existing progress on follow-ups. Mark each stage `in_progress` when starting and `completed` only from confirmed results; update as work proceeds, not in a batch at the end.

Add conditional stages only when they apply. Follow the detailed sections for scope, gates, loop limits, and exits; the checklist does not expand them. Record explicit user skips.

Corrections can reopen earlier stages. Resume the appropriate step with the current context, then repeat affected validation and downstream work. Preserve the branch, applicable approvals, and active review count; do not restart the skill or silently reset a cap.

</workflow-progress>

After approval, return the paths and stop; suggest `/dreamers-implement <plan-path>` as a next command for the user.

## Plan

<planning-workflow>

**Input:** task description. Ask if missing. Apply the embedded `planning-grill`, `plan-format`, and `manifest-format` rules. Work inline; write only `.dreamers/plans/` artifacts, without changing project files or git state.

1. **Grill.** Resolve decisions using `planning-grill`; preserve the full question/response exchange for the transcript.
2. **Propose.** Use `plan-format` and choose the smallest shippable chunks; do not split arbitrarily when that creates more work. Present the full plan for a single-plan task, or the manifest for multiple plans. Through `request_information`, include risks, assumptions, tradeoffs, and simpler alternatives. Answer corrections with reasoning and a recommendation; revise and re-present until approved.
3. **Write.** Create `.dreamers/plans/feature-<slug>/` and numbered `plan-NN-<name>.md` files. Save the verbatim Grill transcript when present and link it from each plan. Add `manifest.md` for multiple plans.
4. **Check.** Verify that scope, ACs, cited paths, and accepted decisions match the approved proposal and current codebase.
5. **Approve.** Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`. Apply minor edits, repeat the checks, and re-present. For a major rewrite, return to the Grill with the correction. On Halt, stop and surface paths. Follow Other as directed.

**Result:** approved plan paths, plus the manifest path when present. Planning ends here; implementation authorization belongs to the containing skill.

</planning-workflow>

## Rules and formats

### Planning questions

<planning-grill>

**Grill**

Resolve decisions and their dependencies until the goal, scope, and constraints are understood. Explore the codebase for answers before asking the user. For unresolved decisions, use `request_information`, one blocking question at a time, with exactly:

1. Recommended answer, labeled recommended.
2. Strongest viable alternative.
3. `Other` for freeform direction.

Incorporate each answer before continuing. Do not propose while required decisions remain open.

Capture every question and response verbatim, in order, including complete tool questions, choice labels, and descriptions. Keep responses separate; never summarize, paraphrase, normalize, or omit text. When writing plans, save the exchange to `.dreamers/plans/feature-<slug>/grilling-transcript.md`, adding only speaker/sequence headings. Do not create an empty transcript.

</planning-grill>

### Plan format

<plan-format>

Use this structure for every plan type. Keep decisions, contracts, UI details, and risks in Scope and context only when relevant. When they clarify the change, include Mermaid diagrams of flows or example UI layouts/wireframes in Scope and context. Acceptance Criteria carry validation intent; do not add separate Approach, Verification, or Test Cases sections.

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

Include the transcript link only when the sibling artifact exists. Compound layers are allowed when one assertion serves both purposes. Under the relevant AC, add a test command or check when project instructions and the outcome are insufficient. For manual checks, include the steps, expected result, and why automation cannot cover them. Set `User-testing-required: yes` only when the agent cannot complete the verification with available authorized tools or the user explicitly wants to test personally. Delivery can discover a need for user testing even when the flag is `no`.

</plan-format>

### Manifest format

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
