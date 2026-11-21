---
name: dreamers-instructions
description: "Review project AI instructions and apply approved edits. Use when the user asks to audit, prune, reconcile, or add project AI guidance, or maintain a project architecture index or test command guide."
---

## Review

- Work in the current project. Find root and nested `AGENTS.md` and `AGENTS.override.md` files, the Copilot project file (.github/copilot-instructions.md), scoped files matching `.github/instructions/**/*.instructions.md`, and other instruction files configured for the project or named by the user, including `CODEX.md` where applicable. Include tracked and non-ignored untracked files. Honor any narrower scope the user requests and read applicable parent instructions for context.
- Check where each rule applies, including directory scope, file globs, precedence, and runtime. Distinguish active rules from rules shadowed by an override. Verify suspected stale rules against current project evidence. Flag stale, duplicated, conflicting, or unnecessarily verbose rules. Keep separate rules where merging them would change who receives them or when they apply.
- Use the workflows below to review architecture indexes and test command guides. For each proposed instruction-rule edit, show the file and section, the exact insertion, replacement, or deletion, and a brief reason. For each addition, name the decision it would change and cite evidence such as a user preference, project constraint, or recurring mistake. If rules conflict and the intended behavior is unclear, ask which rule should govern before proposing a resolution. If the requested review yields no proposed edits, report that and stop.

## Architecture index

- Include the index in a project-wide review or when the user requests architecture maintenance. Check the project's AI configuration and instruction files for evidence of runtime use. `AGENTS.md` alone does not establish Codex use. Honor an explicit user choice. If the evidence is inconclusive, default to the runtime invoking this skill. For Copilot, use `.github/instructions/architecture.instructions.md`. For Codex, use an `## Architecture` section in root `AGENTS.md`. If both are in use and the user has not selected one, ask which index to maintain before proposing changes.
- Inspect the repository's main components, entry points, and supporting directories. Use repository-relative paths and one short purpose description per entry. Group files that serve the same purpose.
- If the selected index is missing, ask whether to create it and show the exact proposed content and location for approval. For a new Copilot file, include `applyTo: "**"` in its frontmatter. Preserve surrounding content when adding a section to an existing file.
- If the index exists, verify its paths and descriptions against the repository. Preserve existing Copilot frontmatter unless proposing an explicit scope correction. Show the exact additions and corrections for approval. Separately show each proposed removal of a stale, redundant, or overly detailed entry and why it should be removed. Ask for separate approval to prune so additions and corrections can proceed while the user keeps any of those entries.

## Test command guide

- Include the guide in a project-wide review or when the user requests test guidance. Use the architecture workflow's runtime evidence and fallback to determine which runtimes the project uses. For Copilot, use `.github/instructions/testing.instructions.md`. For Codex, use a `## Testing` section in root `AGENTS.md`. If both are in use and the user has not selected a destination, ask where to maintain the guide before proposing edits.
- Check existing guidance, test runner configuration, project scripts, and CI. Verify that each proposed command selects the intended tests and note any required working directory or prerequisites. Use real test names or repository-relative paths in selection examples.
- Cover one named test, multiple selected tests, the non-integration suite, the integration suite, the full suite, and any additional cases the user requests. For each supported case, give the command and briefly explain when to run it. Say which requested cases the current tooling cannot select.
- Reuse accurate guidance already maintained elsewhere by referencing it from the guide. Show the exact proposed creation or update for approval. For a new Copilot file, include `applyTo: "**"` in its frontmatter. Preserve existing frontmatter and surrounding instructions. Show stale or redundant entries as separate pruning proposals with reasons so additions and corrections can be approved independently.

## Apply

- Present the proposals and wait for explicit approval before editing. Apply only the edits the user approved, including any approved file creation or deletion. Apply architecture index and test command guide removals only with separate pruning approval. Leave unresolved conflicts and unrelated changes alone.
- Recheck affected text and scope markers before editing. If the approved edit no longer fits, show the revised proposal and ask for approval. Inspect the resulting diff and summarize the changes by file.

<instruction-writing-guide>
Before adding or revising an instruction, ask two questions. Does another instruction, tool, or workflow already handle this? Can the instruction use fewer tokens while preserving the same behavior, scope, and exceptions?

- Keep guidance an agent can’t reliably infer from the repo, such as a misleading legacy pattern, a non-obvious test command, or a team decision.
- Write each rule as a self-contained instruction. Put the condition first, then name the action.
- For each proposed rule, name a real task, what the agent would likely do with its current guidance, and what the rule would change.
- Cite the evidence for an addition.
- Put each rule in the narrowest location that reaches the agents who need it, and keep it in one maintained location.
- Omit editorial ownership labels from proposed and written project instructions. For example, use `## Testing` in place of `## Testing (maintainer-owned)`.
- When reviewing existing project instructions, propose removing labels such as “Echo-owned” that only identify who maintains the text. Preserve actionable requirements such as “Ask a maintainer before changing release settings.”
</instruction-writing-guide>
