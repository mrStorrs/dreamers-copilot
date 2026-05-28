---
name: dreamers-update
description: 'Project-only skill for editing the Dreamers Copilot CLI system files. Sets directory scope, copilot-not-Claude framing, style standards, and cross-file sync rules (refs, /dreamers-full mirror, READMEs, catalog). Triggers: /dreamers-update.'
argument-hint: '<what to change>'
---

$ARGUMENTS

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

If no task description was provided, halt + ask via `request_information`.

## Scope (hard rules)

1. **This project directory only.** Stay inside the project working tree. Do not read, edit, or reference files outside it unless the user names a path.
2. **Copilot CLI, not Claude.** Do not import Claude tool names, agent names, or CLAUDE.md conventions. Runtime is Copilot CLI: `task()`, `request_information`, `view`, `manage_todo_list`.
3. **Halt on ambiguity.** One `request_information` round, not a chain of guesses.

## Style (apply to every edit)

- Minimal. To the point. No fluff.
- Structured but not over-structured. Headings where they aid scanning, not for ceremony.
- Written for AI consumers, not human reading. Optimize for clarity-per-token. No restating the obvious, no "Note that...", no marketing tone.
- Prefer editing existing files. Match the tone of sibling skills.
- The harness does the work. These files are guides + standards, not procedures the LLM follows blindly.

## Sync rules (after any edit)

1. **Kernel blocks.** Source-of-truth = `.github/dreamers/refs/*.md`. Inlined copies in skills must match byte-for-byte. If you edited inlined content, edit the source ref too and run `scripts/sync-refs.ps1`. CI's `verify-refs` workflow fails on drift.
2. **/dreamers-implement is inlined in `/dreamers-full` Phase 2.** Edits to `/dreamers-implement`'s flow (test-writing, type-check, apply-findings, user-testing gate) must be mirrored in `.github/skills/dreamers-full/SKILL.md`.
3. **READMEs.** Update root `README.md` AND `.github/skills/<skill>/readme.md` when a skill's flow, args, or triggers change.
4. **Catalog.** Update `.github/catalog.json` `items[]` (description / path / tags) + `collections[].members[]` for new or renamed skills, agents, refs, or templates. Project-only skills (not installed via `Install-Dreamers.ps1`) skip this.

## Git / PR

- Branch: `feat/<slug>` or `fix/<slug>` cut from fresh `origin/<default>`.
- Stage files by name. No `git add -A`.
- Commit trailer:
  ```
  Co-authored-by: The Dreamers System
  ```
- One PR per logical change. Combine related fixes.
- No `--no-verify`, no force-push, no destructive ops without explicit user request.

## Exit

Report in chat: files changed, sync checks performed (refs / `/dreamers-full` Phase 2 mirror / READMEs / catalog), halts or questions raised.
