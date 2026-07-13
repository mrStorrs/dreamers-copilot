---
name: dreamers-update
description: 'Two-repo maintainer for Dreamers system files. Updates the Dreamers Copilot CLI source first, then transfers the equivalent change into the Dreamers Codex conversion with Codex-only adaptations. Triggers: /dreamers-update.'
argument-hint: '<what to change>'
---

$ARGUMENTS

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

If no task description was provided, halt + ask via `request_information`.

## User overrides

- Explicit user instructions can skip or alter phases/actions.

## Repository roles

- **Dreamers Copilot = upstream source of truth.** Default path: `C:\projects\dreamers-copilot`. This is the Copilot CLI version and owns the canonical behavior, wording, refs, templates, agents, skills, READMEs, and catalog.
- **Dreamers Codex = converted target.** Default path: `C:\projects\dreamers-codex`. This is the Codex version and must receive the same system change after adapting only runtime/tooling/layout details required by Codex.
- **Order is mandatory:** complete the Copilot branch + PR first, then stop at a user gate. Transfer to Codex only after explicit approval.

## Workflow

1. **Copilot branch.** Derive a short slug from the requested change. In `C:\projects\dreamers-copilot`, detect the default branch, fetch, check out the default branch, pull, then create `feat/<slug>` or `fix/<slug>` from fresh `origin/<default>` before editing. Never start system edits on the default branch. If work already exists on the default branch, create the feature branch immediately with the dirty tree preserved, then continue and report the recovery.
2. **Copilot source pass.** Apply the canonical change, update required READMEs/catalog entries, run ref sync/verify, and validate any Copilot-specific checks.
3. **Copilot PR close-out.** Stage explicit paths, commit with the trailer below, push the Copilot branch, and open the Copilot PR. Prefer `/dreamers-pr` when available; otherwise run the same push + `gh pr create` flow directly. Capture the PR URL.
4. **Mandatory gate.** Stop and ask via `request_information`: proceed to Codex transfer, or make additional Copilot PR changes. Do not edit Codex before approval.
5. **Copilot PR revision loop.** If the user requests Copilot changes, apply them on the existing Copilot branch, validate, commit, push to the existing PR, then return to the mandatory gate. Repeat until the user approves Codex transfer.
6. **Codex branch.** After explicit approval, create the Codex branch in `C:\projects\dreamers-codex` from fresh `origin/<default>` using the same branch naming rules.
7. **Codex transfer pass.** Transfer the same behavior into Codex with only Codex runtime/layout adaptations, then run Codex ref sync/verify and `scripts/Test-DreamersCodex.ps1` or `scripts/Test-DreamersCodex.sh` for the active shell.
8. **Codex PR close-out.** Stage explicit paths, commit with the trailer below, push the Codex branch, and open the Codex PR. Prefer `/dreamers-pr` when available; otherwise run the same push + `gh pr create` flow directly. Capture the PR URL.

## Scope (hard rules)

1. **Only the two Dreamers package repos.** Stay inside `C:\projects\dreamers-copilot` and `C:\projects\dreamers-codex` unless the user names another path. Do not touch consuming project repos while running this skill.
2. **Copilot CLI, not Claude.** Do not import Claude tool names, agent names, or CLAUDE.md conventions. Runtime is Copilot CLI: `task()`, `request_information`, `view`, `manage_todo_list`.
3. **Codex transfer is semantic, not blind copy.** Preserve Copilot behavior, but adapt paths, frontmatter, runtime names, agent formats, installer names, and validation commands to Codex conventions.
4. **Halt on ambiguity.** One `request_information` round, not a chain of guesses.

## Transfer map

Use this map when carrying the Copilot change into Codex:

| Copilot source | Codex target |
| --- | --- |
| `.github/skills/<skill>/SKILL.md` | `skills/<skill>/SKILL.md` with Codex runtime preamble |
| `.github/skills/<skill>/readme.md` | `skills/<skill>/readme.md` when that README exists |
| `.github/agents/*.agent.md` | `agents/*.toml` Codex agent definitions |
| `.github/dreamers/refs/*.md` | `dreamers/refs/*.md` |
| `.github/dreamers/templates/*.md` | `dreamers/templates/*.md` |
| `.github/instructions/*.instructions.md` | `dreamers/instructions/*.instructions.md` |
| `.github/catalog.json` | `.github/catalog.json` with Codex paths and skill names |
| `Install-Dreamers.ps1` / `Remove-Dreamers.ps1` | `Install-DreamersCodex.ps1` / `Remove-DreamersCodex.ps1` |
| `scripts/sync-refs.ps1` / `scripts/sync-refs.sh` | `scripts/sync-refs.ps1` / `scripts/sync-refs.sh` adapted for Codex layout |

Codex adaptations are limited to runtime/tool/layout differences: `~/.copilot` -> `$CODEX_HOME`/`~/.codex`, slash commands -> skill names, `task()` -> Codex agent spawning rules, `request_information` -> asking the user, `.github/dreamers` -> `dreamers`, `.github/skills` -> `skills`, and `.github/agents/*.agent.md` -> `agents/*.toml`.

## Style (apply to every edit)

- Minimal. To the point. No fluff.
- Structured but not over-structured. Headings where they aid scanning, not for ceremony.
- Written for AI consumers, not human reading. Optimize for clarity-per-token. No restating the obvious, no "Note that...", no marketing tone.
- Prefer editing existing files. Match the tone of sibling skills.
- The harness does the work. These files are guides + standards, not procedures the LLM follows blindly.

## Sync rules (after any edit)

1. **Script selection.** Use `.sh` validation scripts when running in bash/Linux. Use `.ps1` validation scripts when running in PowerShell/Windows. Treat the matching `.sh` and `.ps1` scripts as equivalent validation surfaces.
2. **Copilot refs.** Source-of-truth = `C:\projects\dreamers-copilot\.github\dreamers\refs\*.md`. Inlined copies in Copilot skills must match byte-for-byte. If you edited inlined content, edit the source ref too and run `scripts/sync-refs.ps1 -Sync` or `scripts/sync-refs.sh -Sync`, then verify with the matching script in the Copilot repo.
3. **Codex refs.** Source-of-truth = `C:\projects\dreamers-codex\dreamers\refs\*.md`. Inlined copies in Codex skills and agent TOMLs must match byte-for-byte. Run `scripts/sync-refs.ps1 -Sync` or `scripts/sync-refs.sh -Sync`, then verify with the matching script in the Codex repo.
4. **Delivery ownership parity.** Preserve the full delivery gate/order wording in the `/dreamers` orchestrator. Keep planning, implementation, reviewer execution, documentation, and PR mechanics in their owning specialized skills, replacing only the former inline phase mechanics with skill calls.
5. **READMEs.** Update each repo's root `README.md` and skill README when a skill's flow, args, or triggers change. Copilot path: `.github/skills/<skill>/readme.md`; Codex path: `skills/<skill>/readme.md`.
6. **Catalog.** Update each repo's `.github/catalog.json` `items[]` (description / path / tags) + `collections[].members[]` for new or renamed installed skills, agents, refs, or templates. Project-only skills skip catalog entries unless they become installable.
7. **Validation.** After transfer, run Copilot ref verify and Codex ref verify + `scripts/Test-DreamersCodex.ps1` or `scripts/Test-DreamersCodex.sh` for the active shell.

## Git / PR

- Branch before edits in each repo: `feat/<slug>` or `fix/<slug>` cut from fresh `origin/<default>`. Create the Codex branch only after the user approves transfer.
- If the branch already exists, inspect it and ask before reusing or replacing it. Do not delete branches automatically.
- Stage files by explicit path. No `git add -A`, `git add .`, or directory-wide staging unless that directory is the intended complete unit of work.
- Keep Copilot and Codex commits and PRs separate unless the user explicitly asks for a different git shape.
- Commit after validation in each repo. Use conventional commits; include the trailer below.
- Push each branch with `git push -u origin <branch>`. No force-push.
- Open the Copilot PR before the mandatory gate. Push Copilot gate-requested revisions to that existing PR before asking again.
- Open the Codex PR only after explicit transfer approval and Codex validation. Prefer `/dreamers-pr`; pass through issue references from the original request when relevant. If `/dreamers-pr` is unavailable, draft the PR body from the repo's PR template and run `gh pr create`.
- Commit trailer:
  ```
  Co-authored-by: The Dreamers System
  ```
- One PR per logical change. Combine related fixes.
- No `--no-verify`, no force-push, no destructive ops without explicit user request.

## Exit

Report in chat: Copilot files changed, Codex files changed, sync checks performed in each repo (refs / READMEs / catalog), validations run, halts or questions raised.
