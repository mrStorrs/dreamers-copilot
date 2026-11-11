# Codex Runtime Mapping

Use this reference when executing Dreamers skills generated from the shared repository.

Before running a skill, read package-local `../../dreamers/instructions/dreamers.instructions.md` and `../../dreamers/instructions/dreamers.laws.md` relative to its directory. Codex does not auto-load compatibility instruction files.

## Inputs
- Treat the user's prompt as the skill input. Former slash commands such as `dreamers-plan` are now Codex skill names such as `dreamers-plan`.
- If a skill names another Dreamers skill, invoke it in the same orchestrator context when it is available. The outermost skill keeps ownership of progress and end-to-end state. If the named skill is unavailable, execute its named phase inline.

## Resource Resolution
Resolve Dreamers shared files in this order:
1. Package-local files relative to the skill directory: `../../dreamers/refs`, `../../dreamers/templates`.
2. Direct-install files under `$CODEX_HOME/dreamers` or `~/.codex/dreamers`.
3. Project-local compatibility files under `.github/dreamers` when working in a repository that still carries the Copilot layout.

Dreamers role definitions are Codex agents. Resolve them from package-local `../../agents/*.toml` relative to the skill directory, or direct-install `$CODEX_HOME/agents/*.toml` / `~/.codex/agents/*.toml`. Do not deploy or resolve role definitions from `$CODEX_HOME/dreamers/agents`.

Project instructions may live in `AGENTS.md`, `CODEX.md`, `.github/copilot-instructions.md`, or project-specific docs. Read whichever exist and let more local project instructions override general Dreamers defaults.

## User Gates
- A gate is mandatory when the skill asks for approval, ship strategy, major-refactor disposition, user testing, PR approval, or continuation.
- Ask the user directly and wait. If a structured input tool is available, it may be used, but do not silently continue past a gate.
- Follow the active runtime's input-tool restrictions; use chat for approvals when a structured tool cannot request them. Explicit authorization already given for the current action satisfies its gate.
- On halt, provide the exact skill name and input needed to resume.

## Planning And Progress
- The outermost Dreamers skill owns progress tracking with `update_plan` when available; otherwise keep a concise progress record in the conversation. Helper skills may make standalone todos optional.
- Delivery skills keep the goal, owning skill, branch/PR, next phase, and review count across follow-ups per `Delivery continuation` in `dreamers/instructions/dreamers.instructions.md`. Questions and detours do not reset the workflow or review cap.
- Spawned reviewer or documentarian roles must not call `update_plan`; their output is the handoff.

## Delegation
- Use the available Codex `spawn_agent` and `wait_agent` tools. References to `multi_agent_v1` also apply to the equivalent `collaboration` namespace when that is the runtime's tool surface.
- Delegate only when the invoked Dreamers workflow explicitly includes reviewer or documentarian roles, such as `dreamers-review`, `dreamers-docs`, `dreamers-find-refactors`, or `dreamers`.
- Spawn by Codex `agent_type` using one of the five Dreamers role names: `sentinel`, `probe`, `hone`, `vigil`, or `echo`. Put the workflow-specific context in `message`; do not paste or load Markdown role prompt files. Planning, research, implementation, tests, and git operations stay inline.
- For a multi-reviewer lane, launch every selected reviewer concurrently before waiting for results. Never spawn and await reviewers sequentially.
- If multi-agent tools are unavailable, run the requested lens inline and label the output with the role name.

## Tool Translation
- Former `request_information`: ask the user in the conversation and wait.
- Former `task()`: `multi_agent_v1.spawn_agent` with `agent_type`, followed by `wait_agent` when the result is needed.
- Former `view`: read the local file with available file tools.
- Former `manage_todo_list`: `update_plan` in the parent conversation only.
- Former Copilot global home `~/.copilot`: `$CODEX_HOME` when set, otherwise `~/.codex`.

## Git And Shell Safety
Follow Codex's current shell, sandbox, approval, and git-worktree rules. Do not install dependencies, push, open PRs, or run destructive commands without the approvals required by the active Codex environment.
