---
name: dreamers-update
description: 'Two-repo maintainer for Dreamers system files. Updates the Dreamers Copilot CLI source first, then transfers the equivalent change into the Dreamers Codex conversion with Codex-only adaptations. Triggers: /dreamers-update.'
argument-hint: '<what to change>'
---

$ARGUMENTS

## Required workflow

1. **Prepare Copilot** — start or resume the source feature branch.
2. **Update and validate** — change canonical sources, sync refs, and check docs and package integrity.
3. **Publish Copilot** — commit and create or update the source PR.
4. **Transfer gate** — obtain explicit Codex-transfer approval; Copilot revisions return to the source pass.
5. **Transfer, when approved** — prepare the Codex branch, adapt the change, and validate.
6. **Publish Codex** — commit, publish, and report both repository results.

<workflow-progress>

Use this skill's Required workflow as the single `manage_todo_list`. Reuse existing progress on follow-ups. Mark each stage `in_progress` when starting and `completed` only from confirmed results; update as work proceeds, not in a batch at the end.

Add conditional stages only when they apply. Follow the detailed sections for scope, gates, loop limits, and exits; the checklist does not expand them. Record explicit user skips.

Corrections can reopen earlier stages. Resume the appropriate step with the current context, then repeat affected validation and downstream work. Preserve the branch, applicable approvals, and active review count; do not restart the skill or silently reset a cap.

</workflow-progress>

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
3. **Copilot PR close-out.** Stage explicit paths and commit with the trailer below. Execute the embedded `pr-workflow` below inline to push the Copilot branch and open the PR. Capture the PR URL.
4. **Mandatory gate.** Stop and ask via `request_information`: proceed to Codex transfer, or make additional Copilot PR changes. Do not edit Codex before approval.
5. **Copilot PR revision loop.** If the user requests Copilot changes, apply them on the existing Copilot branch, validate, commit, push to the existing PR, then return to the mandatory gate. Repeat until the user approves Codex transfer.
6. **Codex branch.** After explicit approval, create the Codex branch in `C:\projects\dreamers-codex` from fresh `origin/<default>` using the same branch naming rules.
7. **Codex transfer pass.** Transfer the same behavior into Codex with only Codex runtime/layout adaptations, then run Codex ref sync/verify and `scripts/Test-DreamersCodex.ps1` or `scripts/Test-DreamersCodex.sh` for the active shell.
8. **Codex PR close-out.** Stage explicit paths and commit with the trailer below. Execute the PR workflow inline to push the Codex branch and open the PR. Capture the PR URL.

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
4. **Independent skills.** Preserve the full delivery gate/order wording in the `/dreamers` orchestrator. Keep shared planning, implementation, reviewer execution, documentation, and PR mechanics in workflow refs. Sync those refs into standalone and delivery skills with XML marker blocks; never introduce skill-to-skill calls or load another skill's `SKILL.md`. Shared workflows and standards must be embedded in every consumer; never replace synced blocks with runtime file reads.
   Workflow refs are operation bodies with inputs, boundaries, and results. Skills own headings, Required workflow checklists, phase transitions, and final exits. Embed the `workflow-progress` standard for checklist tracking; help stays response-only. Place each workflow at its execution point and group shared rules once. Keep ref fragments free of document headings outside fenced examples and standalone-skill lifecycle instructions. Sync supplies blank lines inside the XML markers; do not hand-format generated bodies.
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
- Open the Codex PR only after explicit transfer approval and Codex validation. Execute the embedded PR workflow; pass through issue references from the original request when relevant.
- Commit trailer:
  ```
  Co-authored-by: The Dreamers System
  ```
- One PR per logical change. Combine related fixes.
- No `--no-verify`, no force-push, no destructive ops without explicit user request.

## Exit

Report in chat: Copilot files changed, Codex files changed, sync checks performed in each repo (refs / READMEs / catalog), validations run, halts or questions raised.

## Publish the prepared repository

Use at the authorized Copilot or Codex PR close-out. Supply that repository's committed branch and validation summary; return its URL to the active repository phase.

<pr-workflow>

**Input:** committed feature branch, delivery and validation summary, optional shipped plan paths, and optional `--issue <#|url>`. Enter only when publishing is authorized. Apply the embedded `dreamers-kernel`, `git-workflow`, and `pr-description` rules.

**1. Verify**

- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

**2. Push**

- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

**3. Open the PR**

- Draft the PR body using the embedded `pr-description` format.
- `gh pr create --base "$DEFAULT_BRANCH" --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

**4. Archive shipped plans**

- If this PR ships a Dreamers plan from `.dreamers/plans/feature-<slug>/`, archive after the PR is created.
- Single-plan feature directory: move `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/`.
- Multi-plan feature directory or manifest sequence: create `.dreamers/plans/archive/feature-<slug>/` if needed, move only the shipped `plan-NN-*.md` file(s) into it, and leave unfinished plans in the live feature directory.
- If `manifest.md` exists, keep it live while any unfinished plan file remains. After the last unfinished plan ships, move `manifest.md` into the same archive directory and remove the now-empty live feature directory.
- If no feature directory applies, skip this step.

**Result:** PR URL and any moved archive paths.

</pr-workflow>

## Rules and formats

### Core rules

<dreamers-kernel>

**User overrides**

Explicit user instructions can skip or alter phases/actions.

**Subagent allowlist**

Do not use any non-Dreamers agent unless explicitly authorized by user.

**Subagent prompt — required content**

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

**Implementation discipline**

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

**Commit trailer**

Every commit body includes:

```
Co-authored-by: The Dreamers System
```

</dreamers-kernel>

### Git workflow

<git-workflow>

Every milestone uses a feature branch + PR — never work directly on the default branch.

**Startup verification (do this FIRST)**

1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

**Branch setup (before implementation)**

1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Confirm `.dreamers/` is in the project's `.gitignore`. If not, add it before any further edits.
4. No init commit — the first commit for the milestone is the first thing in the PR diff.

**Commit discipline (non-negotiable)**

1. **Commit at end of each cycle** — one commit per plan in the sequence (single-plan: one commit total; multi-plan: N commits, one per plan).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

**Push discipline (non-negotiable)**

`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between cycles, or at any other point in the pipeline.

**Post-PR push discipline**

If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

**Commit structure (one commit per cycle)**

- Exactly **one** commit per plan/cycle, immediately after the reviewer findings have been applied and tests are green (and user testing, if required, is signed off).
- The orchestrator stages changes with `git add` throughout the cycle but does **not** run `git commit` until the cycle ends.
- Commit message subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes).

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

**What gets committed**

Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

**No worktrees**

The orchestrator works directly on the feature branch. Unless explicitly requested by the user.

</git-workflow>

### PR body format

<pr-description>

Use this structure for the PR body. Omit untouched platforms and the fixes section when no fixes apply.

```markdown
## Summary
plan/task summary here

- [bullet: what was delivered]
- [bullet: why / what problem it solves]

## Test counts

- Desktop Vitest: N pass
- Mobile Jest: N pass

*(Omit platforms not touched by this PR.)*

## Fixes applied

- [SEVERITY] file:line — what was fixed (from reviewer artifacts / commit messages)

*(Omit if no fixes applied.)*
```

</pr-description>
