---
name: dreamers-plan
description: 'Planning skill — 3-phase requirements conversation (Hash-out / Write / Review). Produces plan file(s) under .dreamers/plans/feature-<slug>/ and optional manifest. Hard-stops at the review gate; never implements. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<task description>'
---

$ARGUMENTS

If no task description was provided, halt + ask.

Template read at runtime via `view`:
- `.github/dreamers/templates/plan-writing-guide.md` — plan structure, naming, ACs, decomposition, manifest.

## Todo - Before you begin.
- Declare a todo list marking all steps at entry: Step 1 / Step 2 / Step 3.

## Step 1 — Hash out
- Write a one-paragraph understanding summary of the goal.
- Identify ambiguities, gaps, open decisions. Ask all clarifying questions in ONE `request_information` round.
- Present the proposal + get explicit approval via `request_information`. Non-approval = corrections; revise + re-present until approved.
- Decide plan count + manifest per `plan-writing-guide.md`. Manifest backfill check: existing `feature-<slug>/` + `plan-01-*.md` + no `manifest.md` → manifest MUST be produced in Step 2.

## Step 2 — Write plans
- Read `plan-writing-guide.md` in full via `view`.
- `mkdir -p .dreamers/plans/feature-<slug>/`.
- Write each `plan-NN-<name>.md` + manifest if Step 1 decided yes.
- Component-usage check: for shared components, grep the project source root for callers; include them in scope.
- Citation accuracy: verify every cited artifact exists; mark unverifiable citations as "assumption pending verification."
- Self-check the written plans against the guide before exit. Hard fail on any structural rule violation → halt + fix + re-check.

## Step 3 — Review gate
- Present plan paths via `request_information` with: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`.
- Minor edits applied inline + re-run Step 2 self-check + re-present.
- Major rewrite → loop back to Step 1 with the correction as new context.

## Exit
- Surface plan paths. Hard stop — never invokes implementation.

## Dreamers Kernel
<dreamers-kernel>
# Dreamers Kernel

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

## Continuation principle

At every natural pause between phases — where the skill has produced a meaningful result and the user could redirect — call `request_information` with three choices: `Continue` / `Halt for now` / `Other` (freeform). Never silently advance; never silently stop. On `Halt`, emit a one-line resume command and stop.

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
