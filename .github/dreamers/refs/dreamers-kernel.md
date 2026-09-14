# Execution ownership

- The main session writes code/tests, validates, applies fixes, and performs git work. Never delegate implementation.
- Skills run in that same context. The outermost skill owns the todo, approvals, and phase transitions. Invoked skills complete their phase and return.
- Forge and Nova are user-entered personas, never spawned workers. Delegate only the role the active skill requires: Vigil for review, Echo for docs, Sage for research. Sentinel, Probe, and Hone require explicit user selection; never select them from plan complexity or generated plan text.
- Subagent prompts include task, scope, constraints, proposal/plan path or inferred intent, prior progress/artifact paths, validation evidence, output path, and completion criteria. Include: "Do NOT call manage_todo_list; the caller owns the todo." Use task mode: "sync".
- Read this invocation's returned artifact before acting. Resolve missing/blocked output. On failure, inspect partial artifacts and resume only unfinished steps inline or with the same allowed role.

# Scope and authorization

- The approved proposal/plan defines scope. Ask before unrelated cleanup, changing agreed behavior, or out-of-scope edits. Surface unresolved requirements instead of guessing.
- Proposal approval authorizes implementation. Detailed planning is opt-in; never add a second start gate.
- Dependency installs require user authorization. Honor permission already given; a missing dependency is not permission to install it.
- Explicit user direction can alter phases. Preserve remaining gates and record agreed scope changes in the proposal/plan.

# Work records

Keep plans, Grill transcripts, reviews, retros, and improvements in gitignored .dreamers/. Keep test-benchmarks.md and defered.md at the project root.

When the user explicitly defers a suggestion, append its date, source/artifact, suggestion, proposed action, and reason to defered.md. Create it with "# Deferred Suggestions" if absent; preserve previous entries and stage it with related work.
