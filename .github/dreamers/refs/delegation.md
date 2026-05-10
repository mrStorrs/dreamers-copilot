# Delegation Protocol

Each Agent tool invocation must include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously (by whom, and absolute paths to any output files to read)
- **What is needed** — specific deliverable expected from this agent
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file paths** — absolute paths to relevant plan file(s)

## MANDATORY — Agent mode

**All agents MUST be invoked with `mode: "sync"`.**

- Fire the agent with `task(mode: "sync")` — it blocks until the agent completes and returns the summary inline
- Substantive output goes to durable surfaces (Probe's workspace artifacts) or to chat output (Sentinel/Hone/Forge/Echo per their Output discipline) — never directly into the orchestrator's working context. The summary the agent returns is what the orchestrator carries forward.
- Gate on the result before firing the next agent — never fire two agents in parallel in the pipeline

This keeps the orchestrator's context window lean (summaries only) while maintaining strict sequential, gated hand-offs.

## MANDATORY — Reading refs and templates

**All refs and templates MUST be read in full using the `view` tool.**  
Never use shell commands (`cat`, `head`, `tail`, powershell) to read refs or templates — they truncate content. Never skip or skim a ref. Every line matters.

## Agent selection

Use the right agent for the job:
- **Forge** (Sonnet) — implementation, code changes. Type-checks before signaling done.
- **Sentinel** (Sonnet) — code review. **Fix-on-sight in production-code lane.** No findings JSON; severity-graded fixes-applied list in chat output.
- **Probe** (Sonnet) — test writing and strategy. **Fix-on-sight in test-files lane only.** Production bugs reported in `bugs.md` for orchestrator routing back to Sentinel.
- **Hone** (Sonnet) — simplification: readability, maintainability, redundancy reduction. **Fix-on-sight in branch-diff scope, behavior-preserving.** Runs once after all sub-plan cycles complete via `/dreamers-simplify`.
- **Echo** (Haiku) — documentation. Reads orchestrator-passed change context + `git diff`; no longer reads dropped Forge/Sentinel artifacts.
- **Nova** (Opus) — multi-mode planning specialist: `verify` (lightweight applicability check between sub-plans, called via `/dreamers-plan-verify`), `replan` (heavy drift recovery), `plan-new` (full new-feature planning conversation).
- **Bolt** (Haiku) — mechanical execution: run tests, git push, PR creation, issue closing, build commands, type-checks. Use Bolt for anything that requires zero reasoning.

**Rule of thumb:** If the task requires judgment, use the appropriate specialist. If it's just executing a command and reporting output, use Bolt.

## Fix-on-sight lanes (non-negotiable)

- **Sentinel** edits production code (and test-file comments only — comments are not test logic). Does NOT edit test logic.
- **Probe** edits test files. Does NOT edit production code.
- **Hone** edits files in `git diff origin/<DEFAULT>...HEAD`. Behavior-preserving only.

A sub-plan boundary runs Sentinel → Probe sequentially. Sentinel handles production fixes first; Probe handles test coverage and any test-file fixes against the settled production state.

## Conflict resolution

If agents produce conflicting outputs (e.g., Sentinel and Probe disagree on whether a behavior is correct), the orchestrator summarizes the tradeoffs in chat, recommends a decision, and records the rationale in the next commit message body. If the disagreement requires human judgment, surface it to the user before proceeding.
