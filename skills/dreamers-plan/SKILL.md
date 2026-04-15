---
name: dreamers-plan
description: 'Planning only — produce a plan file from a task description without implementing anything. Use when you want a plan before committing to implementation. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '$ARGUMENTS'
---

Read these refs before starting:
- `~/.copilot/dreamers/refs/planning-protocol.md`
- `~/.copilot/dreamers/refs/plan-rules.md`
- `~/.copilot/dreamers/refs/feature-decomposition.md`
- `~/.copilot/dreamers/refs/plan-content.md`
- `~/.copilot/dreamers/refs/testing-mandate.md`
- `~/.copilot/dreamers/refs/citation-accuracy.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

Produce a plan only for the following task. Do not proceed to implementation.

$ARGUMENTS

Run the full requirements conversation directly with the user:
- Phase 1: Hash it out — ask clarifying questions (one round)
- Phase 2: Present the approval gate — wait for explicit user approval
- Phase 3: Write the plan file(s)

This is a direct conversation. When the user approves the plan, write the plan files and present the file path(s).

**HARD STOP after Phase 3.** Do NOT proceed to implementation. Do NOT mark todos `in_progress`. Do NOT delegate to Forge, Probe, Sentinel, or any other agent. Do NOT query the SQL todos table to find "ready" work. The moment plan files are written and file paths are presented, your job is done. Tell the user to run `/dreamers-implement` when they are ready to build.

