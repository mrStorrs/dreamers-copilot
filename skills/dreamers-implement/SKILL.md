---
name: dreamers-implement
description: 'Implementation only — execute against an existing plan file. Use when a plan already exists and is approved. Triggers: /dreamers-implement, implement this plan, start implementation, execute the plan.'
argument-hint: 'path/to/plan.md'
---

### ⚠️ MANDATORY FIRST ACTIONS — do these before anything else, in this exact order

1. **Read ALL of the following refs** (no skipping):
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/quality-gates.md`
- `~/.copilot/dreamers/refs/delegation.md`
- `~/.copilot/dreamers/refs/close-out.md`
- `~/.copilot/dreamers/refs/agent-recovery.md`

If the plan has sub-plans, also read:
- `~/.copilot/dreamers/refs/sub-plan-loop.md`

2. **Invoke Bolt** to set up the feature branch per `git-workflow.md` (checkout main, pull, cut `feat/d<N>-<name>`, wipe agent workspaces). Do not proceed until Bolt confirms.
3. **Do not write or edit code yourself.** All implementation must go through the agents below.

---

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

A plan already exists. Go straight to implementation for the following task:

$ARGUMENTS

The prompt must include a path to the existing plan file. If no plan file path is provided, stop and ask for it before proceeding — do not invent or skip the plan.

**User Input Audit (before Gate 2):** Review the entire conversation thread. For every suggestion, correction, preference, or constraint the user expressed, confirm it is explicitly addressed in the plan file. If anything is missing, update the plan to incorporate it before proceeding. Do not skip this step.

**Single plan route:** Forge → Sentinel → Probe → Simplify → Close-out (Bolt handles push + PR)
**Sub-plan route:** Loop per sub-plan (see sub-plan-loop.md), then Simplify → Close-out (Bolt handles push + PR)

Run Gate 2 (plan quality check) first. Run quality gates at every handoff boundary. Follow delegation.md for all agent invocations (use Bolt for mechanical tasks like test runs, git push, PR creation, issue closing). Follow git-workflow.md for branching, commits, and push discipline. Follow close-out.md for retro and PR creation.

**Before PR creation:** Run `/simplify` to review changed code for reuse opportunities, quality issues, and efficiency improvements. Fix any issues found before proceeding to close-out.

If the prompt references a GitHub issue number or URL, pass it to Bolt at close-out to close: `gh issue close <number> --comment "Resolved in <PR URL>"`.

