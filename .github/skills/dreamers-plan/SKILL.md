---
name: dreamers-plan
description: 'Planning skill — 3-phase requirements conversation (Hash-out / Write / Review). Produces plan file(s) under .dreamers/plans/feature-<slug>/ and optional manifest. Hard-stops at Phase 1c approval gate; never implements. Triggers: /dreamers-plan, plan a feature, write a plan.'
argument-hint: '<task description>'
---

$ARGUMENTS

Template read at runtime via `view` (not inlined):
- `.github/dreamers/templates/plan-writing-guide.md` — plan structure, naming, ACs, decomposition, manifest, ship-strategy heuristics.

---

## Todo

Declare at entry: Phase 1a / Phase 1b / Phase 1c.

---

## Phase 1a — Hash out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify ambiguities, gaps, open decisions. Ask all clarifying questions in ONE `request_information` round.
3. After clarifications: present the proposal + get explicit approval via `request_information`:

   ```
   **Goal:** [one sentence]
   **Scope:** [what is in]
   **Non-goals:** [only if ambiguous]
   **Acceptance criteria:**
   1. ...
   ```

   Non-approval = corrections; revise + re-present until approved.

4. **Decide plan count + manifest** per `plan-writing-guide.md`. **Manifest backfill check:** if `.dreamers/plans/feature-<slug>/` already exists with `plan-01-*.md` and no `manifest.md`, and this conversation is producing plan-02-*+, a manifest MUST be produced in Phase 1b.

---

## Phase 1b — Write plans

1. Read `.github/dreamers/templates/plan-writing-guide.md` in full via the `view` tool.
2. `mkdir -p .dreamers/plans/feature-<slug>/`.
3. Write each `plan-NN-<name>.md`. Write the manifest if Phase 1a decided yes.
4. **Component-usage check:** for shared components, grep the project source root for callers; include them in scope.
5. **Citation accuracy:** verify every cited artifact exists; mark unverifiable citations as "assumption pending verification."
6. **Self-check** the written plans against the guide before exit. Hard fail on any structural rule violation → halt + fix + re-check.

---

## Phase 1c — Review gate

Present plan paths via `request_information`:

- **Approved — start implementation** → exit. Surface next-step command: `/dreamers-full <plan-paths>` or `/dreamers-implement <plan-path>`.
- **Minor edit** → apply inline, re-run 1b self-check, re-present.
- **Major rewrite** → loop back to 1a with the correction as new context.
- **Halt — planning only** → exit cleanly; surface plan paths.
- **Other** → freeform redirect; route to minor or major.

This skill HARD STOPS at 1c — it never invokes `/dreamers-implement` or `/dreamers-full` itself. The user runs them.

---

## Dreamers Kernel

<dreamers-kernel>
<!-- GENERATED from .github/dreamers/refs/dreamers-kernel.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Dreamers Kernel

Universal rules. Inlined at the bottom of every Dreamers skill + agent by `scripts/sync-refs.ps1`.

## Subagent allowlist (HARD RULE)

The only `agent_type` values a skill may pass to `task()`:
- `sentinel`, `probe`, `hone`, `echo`, `sage`

Forbidden: `general-purpose`, `claude`, `claude-code-guide`, `Explore`, `Plan`, `bolt`, or any non-Dreamers agent. Exception: only if the user explicitly authorizes a fallback in the current run.

## Single-owner todo

Each user-invoked skill owns its own todo for its run. When skills compose (e.g., `/dreamers-full` invokes `/dreamers-implement`), the called skill creates its own todo on entry and closes it on exit. Sub-skills do not touch the caller's todo.

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
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```
</dreamers-kernel>
