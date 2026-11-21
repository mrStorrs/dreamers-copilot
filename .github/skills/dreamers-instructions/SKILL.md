---
name: dreamers-instructions
description: "Review project AI instructions and apply approved edits. Use when the user asks to audit, prune, reconcile, or add project AI guidance."
---

## Review

- Work in the current project. Find root and nested `AGENTS.md` and `AGENTS.override.md` files, the Copilot project file (.github/copilot-instructions.md), scoped files matching `.github/instructions/**/*.instructions.md`, and other instruction files configured for the project or named by the user, including `CODEX.md` where applicable. Include tracked and non-ignored untracked files. Honor any narrower scope the user requests and read applicable parent instructions for context.
- Check where each rule applies, including directory scope, file globs, precedence, and runtime. Distinguish active rules from rules shadowed by an override. Verify suspected stale rules against current project evidence. Flag stale, duplicated, conflicting, or unnecessarily verbose rules. Keep separate rules where merging them would change who receives them or when they apply.
- For each proposed edit, show the file and section, the exact insertion, replacement, or deletion, and a brief reason. For each addition, name the decision it would change and cite evidence such as a user preference, project constraint, or recurring mistake. If rules conflict and the intended behavior is unclear, ask which rule should govern before proposing a resolution. If no edits are needed, report that and stop.

## Apply

- Present the proposals and wait for explicit approval before editing. Apply only the edits the user approved, including any approved file creation or deletion. Leave unresolved conflicts and unrelated changes alone.
- Recheck affected text and scope markers before editing. If the approved edit no longer fits, show the revised proposal and ask for approval. Inspect the resulting diff and summarize the changes by file.

<instruction-writing-guide>
Before adding or revising an instruction, ask two questions. Does another instruction, tool, or workflow already handle this? Can the instruction use fewer tokens while preserving the same behavior, scope, and exceptions?

- Keep guidance an agent can’t reliably infer from the repo, such as a misleading legacy pattern, a non-obvious test command, or a team decision.
- Write each rule as a self-contained instruction. Put the condition first, then name the action.
- For each proposed rule, name a real task, what the agent would likely do with its current guidance, and what the rule would change.
- Cite the evidence for an addition.
- Put each rule in the narrowest location that reaches the agents who need it, and keep it in one maintained location.
</instruction-writing-guide>
