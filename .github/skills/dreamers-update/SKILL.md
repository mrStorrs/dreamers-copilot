---
name: dreamers-update
description: "Maintain Copilot first, then transfer to Codex only after explicit approval."
argument-hint: "<change>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Resolve the Copilot source repo and sibling Codex target from the workspace or user paths (legacy Windows defaults: C:/projects/dreamers-copilot and C:/projects/dreamers-codex).
2. In Copilot, follow [git workflow](../../dreamers/refs/git-workflow.md), preserve current work, and apply the canonical change. Update affected docs/catalog/package tooling. Run the package validators.
3. Commit and open the Copilot PR via /dreamers-pr. Ask whether to transfer to Codex or revise Copilot. Revisions stay on that PR; validate, commit, push, and return to this gate.
4. Only after transfer approval, branch in Codex from updated default. Transfer equivalent behavior with runtime/layout adaptations; read the target's conventions and validate with its existing tooling.
5. Commit and open the Codex PR separately. Report both URLs, changed surfaces, and checks.

Transfer map: Copilot .github/skills → Codex skills; .github/agents/*.agent.md → agents/*.toml; .github/dreamers → dreamers; .github/instructions → dreamers/instructions. Adapt catalog paths, installers, tool names, and Copilot home → Codex home. Preserve semantic behavior; do not copy Copilot runtime syntax blindly or edit consuming projects.

Copilot references are linked, not inlined. If Codex still uses synchronized refs, follow its tooling rather than reintroducing copies in Copilot.
