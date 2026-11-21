---
name: dreamers-retro
description: "Review problems from a task and propose evidence-backed instruction changes. Use when the user asks for a task retrospective or wants to prevent a workflow problem from recurring."
argument-hint: '<task or evidence, optional>'
---

$ARGUMENTS

## Review the task

- Use the current task or the task evidence the caller supplies. Ask which task to review if neither identifies one. Examine concrete problems using user corrections, failed checks, review findings, or task artifacts.
- For each finding, record what happened, its impact, and the evidence. Read the instructions that applied to the agent at the time, including applicable project, scoped, skill, and runtime guidance. Check scope and precedence before attributing the problem to the instructions.
- If an existing rule covered the situation, cite its file and section and explain how it applied. Keep the finding without an edit when the rule was already clear. If the evidence shows that a missing or unclear instruction affected the outcome, use the shared guide below. For each proposed edit to project instructions, name the file and section, give the exact wording to insert, replace, or delete, and explain which decision it would have changed.

## Record and propose

- Save a concise Markdown retro in `.dreamers/retros/` using a new filename that identifies the task. Include the findings, applicable rules, and any proposed edits. If evidence is insufficient or no change is warranted, record that conclusion and why.
- Share the retro path and any proposed edits. If there are no proposals, return after reporting the result. Otherwise, ask which edits to approve or whether to skip them, then wait for explicit user approval before editing instructions. If the user skips the edits, return without editing. Apply only the approved edits. If the target text has changed and the proposal needs revision, present the revised edit for approval.

<instruction-writing-guide>
Before adding or revising an instruction, ask two questions. Does another instruction, tool, or workflow already handle this? Can the instruction use fewer tokens while preserving the same behavior, scope, and exceptions?

- Keep guidance an agent can’t reliably infer from the repo, such as a misleading legacy pattern, a non-obvious test command, or a team decision.
- Write each rule as a self-contained instruction. Put the condition first, then name the action.
- For each proposed rule, name a real task, what the agent would likely do with its current guidance, and what the rule would change.
- Cite the evidence for an addition.
- Put each rule in the narrowest location that reaches the agents who need it, and keep it in one maintained location.
</instruction-writing-guide>
