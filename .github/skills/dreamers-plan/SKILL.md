---
name: dreamers-plan
description: 'Investigate code and propose concise plans with clear acceptance criteria for approval. Save approved plans; never implement. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<goal>'
---

$ARGUMENTS

Look into how code works today. Propose a short plan for [goal], built around clear acceptance criteria. Follow YAGNI principles. Ask questions if needed; if the goal is missing, ask for it. Before presenting the proposal, review the code for potential concerns or unintended behaviours. Report them to the user with suggested acceptance criteria to address them. Present the proposal for approval before writing the plan.

Use `plan-format` below. Split work into multiple plans only when they are independently shippable; use `manifest-format` for their execution order and shared context. Present the full plan for a single-plan task, or the manifest and proposed plan contents for a multi-plan task. Incorporate corrections and obtain approval for the revised proposal.

After approval, write only `.dreamers/plans/` artifacts; do not change project files or git state. Save numbered `plan-NN-<name>.md` files in `.dreamers/plans/feature-<slug>/`, with `manifest.md` when needed. If questions were asked, save the questions and responses verbatim, including tool choices and descriptions, in sibling `grilling-transcript.md` and link it from each plan. Do not create an empty transcript. Check the saved artifacts against the approved proposal and return their paths. Stop when standalone; otherwise return control to the caller. Never implement.

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
