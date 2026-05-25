---
name: dreamers-plan
description: 'Planning-only entry point. Runs the canonical planning procedure (`planning-procedure.md`) and exits at the implementation-start approval gate. Does NOT invoke implementation. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '<task description>'
---

## What this skill does

Standalone entry point for the planning phase. The user invokes this when they want plan files written but are NOT yet ready to ship — they'll run `/dreamers-full` themselves later when ready.

This skill follows `~/.copilot/dreamers/refs/planning-procedure.md` end-to-end (Phase 1a → 1g) and exits cleanly at the approval gate. It does NOT invoke any other skill (no `Invoke /dreamers-full`, no chained-skill invocation). The user is in control of what runs next.

If the user wants planning + implementation + close-out in one go, they should run `/dreamers-full <task description>` instead — that skill follows the same planning procedure but continues into implementation automatically.

---

## Pre-flight reads (MUST READ IN FULL — no globbing, no grepping)

Read these refs in full using the `view` tool at skill entry. Top to bottom. Pattern-skipping is forbidden per `orchestration-flow.md` § "Must-read refs rule."

- `~/.copilot/dreamers/refs/orchestration-flow.md` — single-owner todo + continuation principle + must-read rule
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — implementation + comment + logging + test-writing + git rules (applies during plan-writing too: no code snippets except interface contracts, etc.)
- `~/.copilot/dreamers/refs/planning-procedure.md` — the procedure this skill follows
- `~/.copilot/dreamers/refs/plan-content.md` — plan section requirements + format
- `~/.copilot/dreamers/refs/plan-rules.md` — plan naming + directory layout
- `~/.copilot/dreamers/refs/feature-decomposition.md` — when to write multiple plans + manifest pattern
- `~/.copilot/dreamers/refs/citation-accuracy.md` — verify before citing existing artifacts
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations the plan must capture
- `~/.copilot/dreamers/templates/plan.md` — plan template
- `~/.copilot/dreamers/templates/manifest.md` — manifest template (when multi-plan with shared context)

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, test commands, source roots.

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Read planning-procedure.md
- [ ] Phase 1a — hash it out
- [ ] Phase 1b — user input audit
- [ ] Phase 1c — approval gate
- [ ] Phase 1d — decide plan count (and manifest backfill check)
- [ ] Phase 1e — write plan file(s)
- [ ] Phase 1f — plan quality self-check
- [ ] Phase 1g — implementation-start approval gate

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

This skill is the sole owner of the todo. No subagents are spawned in this skill, so no subagent prompts need the "do NOT touch todo" reminder. But the rule still applies if any subagent IS spawned in the future.

---

## Procedure

Follow `~/.copilot/dreamers/refs/planning-procedure.md` Phase 1a through Phase 1g, exactly as written. The procedure handles its own approval gates (Phase 1c, Phase 1g) and quality self-check (Phase 1f). Update this skill's todo as each phase is completed.

At Phase 1g, the user picks one of three options. Handle each per the planning-procedure.md "What happens after Phase 1g approval" section:

- **`Approved — start implementation`** — exit this skill with success. Surface the saved plan path(s) to the user and the next-step command:
  - Single plan: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md`
  - Multiple plans, no manifest: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md .dreamers/plans/feature-<slug>/plan-02-<name>.md ...`
  - Multiple plans with manifest: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/manifest.md`

  This skill does NOT itself invoke `/dreamers-full`. Skill-calls-skill chaining is forbidden under the new architecture (see `orchestration-flow.md` § "Single-owner todo rule"). The user invokes the next skill themselves.

- **`Halt — planning only`** — exit cleanly. Output: `Planning complete. Plan file(s) saved at <paths>. To begin implementation later, run /dreamers-full with the plan paths.` Stop. Do not invoke any further skill.

- **`Other` / corrections** — apply inline per the planning-procedure.md guidance. Revise plan files, re-run Phase 1f, re-present the Phase 1g gate. Loop until the user picks Approved or Halt.

---

## Exit behavior

On Phase 1g approval (any approval choice or Halt): exit with success. Tell the user:
- The approved plan file path(s).
- If a manifest was produced: the manifest path.
- Next step: run `/dreamers-full <plan-paths>` (or `/dreamers-full <manifest-path>` for manifest mode) when ready to begin implementation.

---

## What this skill does NOT do

- Does NOT proceed to implementation. That's `/dreamers-full`'s job.
- Does NOT auto-invoke `/dreamers-full` or any other skill. The user invokes the next step themselves.
- Does NOT spawn any subagent. Planning is entirely inline by the orchestrator (this skill, running in your context).
- Does NOT write code or test files. Plan files only.

## HARD STOP after Phase 1g

When plan files are written and the approval gate clears, the skill exits. No edits beyond plan files. No invocations of other skills. The user is in control of what happens next.

If the user asks "now start implementing" in the same session: surface the `/dreamers-full <plan-paths>` command to them and stop. They run it.
