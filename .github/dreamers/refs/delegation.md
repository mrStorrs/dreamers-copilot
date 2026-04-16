# Delegation Protocol

Each Agent tool invocation must include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously (by whom, and absolute paths to any output files to read)
- **What is needed** — specific deliverable expected from this agent
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file paths** — absolute paths to relevant plan file(s)

## MANDATORY — Agent mode

**All agents MUST be invoked with `mode: "background"` + `wait: true` via `read_agent`.**

- Fire the agent with `mode: "background"`
- Immediately call `read_agent(agent_id, wait: true)` to block until it completes
- Read only the summary the agent returns — substantive output goes to markdown files, not the orchestrator's context window
- Gate on the result before firing the next agent — never fire two agents in parallel in the pipeline

This keeps the orchestrator's context window lean (summaries only) while maintaining strict sequential, gated handoffs.

## MANDATORY — Reading refs and templates

**All refs and templates MUST be read in full using the `view` tool.**  
Never use shell commands (`cat`, `head`, `tail`, powershell) to read refs or templates — they truncate content. Never skip or skim a ref. Every line matters.

## Agent selection

Use the right agent for the job:
- **Forge** (Sonnet) — implementation, code changes
- **Sentinel** (Sonnet) — code review
- **Probe** (Sonnet) — test writing and strategy
- **Hone** (Sonnet) — simplification: readability, maintainability, redundancy reduction. Runs once after all sub-plan cycles complete, before the final Sentinel + Probe pass and close-out.
- **Echo** (Haiku) — documentation
- **Nova** (Opus) — replanning between sub-plans only
- **Bolt** (Haiku) — mechanical execution: run tests, git push, PR creation, issue closing, build commands, type-checks. Use Bolt for anything that requires zero reasoning.

**Rule of thumb:** If the task requires judgment, use the appropriate specialist. If it's just executing a command and reporting output, use Bolt.

## Conflict resolution

If agents produce conflicting outputs, summarize the tradeoffs, recommend a decision, and record it in `decisions.md`.
