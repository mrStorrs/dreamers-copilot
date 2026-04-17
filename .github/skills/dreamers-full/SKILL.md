---
name: dreamers-full
description: 'Full Dreamers pipeline: plan a feature, implement it with agent delegation, review, test, and ship. Use when starting a new feature or significant change from scratch. Triggers: /dreamers-full, full pipeline, plan and implement, new feature.'
---

## Phase 1 — Planning

Read these refs before starting — **use the `view` tool on each full path, never shell commands**:
- `~/.copilot/dreamers/refs/planning-protocol.md`
- `~/.copilot/dreamers/refs/plan-rules.md`
- `~/.copilot/dreamers/refs/feature-decomposition.md`
- `~/.copilot/dreamers/refs/plan-content.md`
- `~/.copilot/dreamers/refs/testing-mandate.md`
- `~/.copilot/dreamers/refs/citation-accuracy.md`

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

Run the full requirements conversation directly with the user:

- **Phase 1 — Hash it out:** Use the `ask_user` tool to ask clarifying questions. Ask one question at a time — do not bundle. One round only.
- **Phase Gate — User Input Audit:** Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it now.
- **Phase 2 — Approval gate:** Present the proposal block from `planning-protocol.md` in chat, then call `ask_user` with choices `["Approved", "Corrections needed"]`. If corrections, revise and re-present. Loop until approved.
- **Phase 3 — Write plan files** to `.dreamers/plans/` per `plan-rules.md`, `plan-content.md`, and `feature-decomposition.md`. Use `~/.copilot/dreamers/templates/plan-sub.md` as the starting structure.

Do not proceed to Phase 2 (implementation) until the user explicitly approves the plan.

---

## Phase 2 — Implementation

### ⚠️ MANDATORY FIRST ACTIONS — do these before anything else, in this exact order

1. **Read ALL Phase 2 refs** using the `view` tool — full file, no shell commands, no skipping:
   - `~/.copilot/dreamers/refs/git-workflow.md`
   - `~/.copilot/dreamers/refs/quality-gates.md`
   - `~/.copilot/dreamers/refs/delegation.md`
   - `~/.copilot/dreamers/refs/close-out.md`
   - `~/.copilot/dreamers/refs/agent-recovery.md`
   - If the plan has sub-plans, also read: `~/.copilot/dreamers/refs/sub-plan-loop.md`
2. **Delegate branch setup to Bolt** via `task(agent_type: "bolt", mode: "background")`, then immediately `read_agent(wait: true)` per `git-workflow.md` (detect default branch, checkout and pull it, cut `feat/d<N>-<name>` from it, wipe agent workspaces). Do not proceed until Bolt confirms.
3. **Do not write or edit production files yourself.** Never use `create`, `edit`, or `powershell` to modify source code. All implementation must go through the `task` tool.

---

The plan is already user-approved. Run Gate 2 (plan quality check) on the plan files, then orchestrate:

**Single plan route:** Forge → Sentinel → Probe → `dreamers-simplify` (Hone + final Sentinel + Probe; runs inside skill) → Close-out (Bolt handles push + PR)
**Sub-plan route:** Loop per sub-plan (see `sub-plan-loop.md`), then `dreamers-simplify` (Hone + final Sentinel + Probe; runs inside skill) → Close-out (Bolt handles push + PR)

### Agent delegation (all via `task` tool, `mode: "background"` + `read_agent(wait: true)`)

> **NEVER fire the next agent before the current one completes and is reviewed.** Always `read_agent(wait: true)` immediately after `task(mode: "background")`. Agents write substantive output to markdown files — the orchestrator only receives the summary, keeping context lean.

| Agent type | When to use |
|---|---|
| `"forge"` | Implementation — code changes |
| `"sentinel"` | Code review |
| `"probe"` | Test writing and execution |
| `"echo"` | Documentation |
| `"nova"` | Sub-plan re-verification (between sub-plans only) |
| `"bolt"` | Mechanical tasks: test runs, git push, PR creation, issue closing, build commands |

Run quality gates at every handoff per `quality-gates.md`. Follow `delegation.md` for all agent invocations. Follow `git-workflow.md` for branching, commits, and push discipline. Follow `close-out.md` for retro and PR creation.

**Before PR creation:** Invoke the `dreamers-simplify` skill — it runs Hone on the full feature-branch diff (not just the latest sub-plan), then a final Sentinel + Probe pass internally. Do not invoke Sentinel or Probe separately after the skill completes.

If the prompt references a GitHub issue number or URL, pass it to Bolt at close-out to close: `gh issue close <number> --comment "Resolved in <PR URL>"`.

