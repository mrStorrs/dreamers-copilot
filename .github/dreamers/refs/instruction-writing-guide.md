Before adding or revising an instruction, ask two questions. Does another instruction, tool, or workflow already handle this? Can the instruction use fewer tokens while preserving the same behavior, scope, and exceptions?

- Keep guidance an agent can’t reliably infer from the repo, such as a misleading legacy pattern, a non-obvious test command, or a team decision.
- Write each rule as a self-contained instruction. Put the condition first, then name the action.
- For each proposed rule, name a real task, what the agent would likely do with its current guidance, and what the rule would change.
- Cite the evidence for an addition.
- Put each rule in the narrowest location that reaches the agents who need it, and keep it in one maintained location.
