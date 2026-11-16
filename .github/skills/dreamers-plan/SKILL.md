---
name: dreamers-plan
description: 'Investigate code and propose concise plans with clear acceptance criteria for approval. Save approved plans; never implement. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<goal>'
---

$ARGUMENTS

<proposal>
Follow YAGNI principles.

Look into how code works today. Propose the requested change for [goal], built around clear acceptance criteria. Resolve questions from the codebase where possible. Ask the user about unclear goals, scope, constraints, or tradeoffs that would materially change the proposal. Clarify these before presenting the proposal. Before presenting the proposal, review the code for potential concerns or unintended behaviours. Report them to the user with suggested acceptance criteria to address them. Present the proposal for approval before creating the requested artifact.

```markdown
## Goal
What should improve, for whom, and why?

## Acceptance criteria
- [ ] Observable outcome.
```
</proposal>

Split work into multiple plans only when they are independently shippable. Present the full plan for a single-plan task, or the manifest and proposed plan contents for a multi-plan task. Incorporate corrections and obtain approval for the revised proposal.

After approval, write only `.dreamers/plans/` artifacts; do not change project files or git state.

Save numbered `plan-NN-<name>.md` files in `.dreamers/plans/feature-<slug>/`. Each plan starts with:

```markdown
# Plan-NN: <short title>

**User-testing-required:** <yes|no>
```

Follow that heading with the approved Goal and Acceptance criteria.

For multiple plans, add `manifest.md` using `manifest-format`.

Check the saved artifacts against the approved proposal and return their paths. Stop when standalone; otherwise return control to the caller. Never implement.

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

## Acceptance criteria
- [ ] Observable outcome.
```

Keep plans in execution order. Manifest ACs cover outcomes requiring the whole sequence; plan ACs cover each plan. Omit shared context or feature-level ACs when none apply; do not duplicate plan content.
</manifest-format>
