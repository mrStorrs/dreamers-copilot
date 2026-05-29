---
name: dreamers-clean-work
description: 'Between-milestone maintenance pass: prune stale files, archive legacy unarchived feature plan directories, audit improvements.md, scan for project-state drift. All inline — no subagents. Triggers: /dreamers-clean-work, clean up, maintenance pass, between milestones.'
argument-hint: '(no args; full maintenance pass)'
---

Run a between-milestone maintenance pass. No implementation, no planning, no subagents — do all of this directly.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Step 1 — improvements audit
- [ ] Step 2 — feature plan directory archive
- [ ] Step 3 — legacy workspace cleanup (recommend only)
- [ ] Step 4 — project state contradiction scan
- [ ] Step 5 — report

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Improvements audit

Read `.dreamers/improvements.md` (repo-local). For each open item:
- Decide: action now, defer with a reason, or close as no longer relevant.
- If actionable as a direct text edit to an agent file or ref (meta work): make the edit now.
- If it requires a full pipeline (`/dreamers-full`): defer it — add a note with why and which skill to use.
- Remove actioned/closed items. Leave only open deferred items with defer reasons.

## Step 2 — Feature plan directory archive

In `.dreamers/plans/` (repo-local), for each `feature-<slug>/` directory (excluding directories already in `archive/`):
- Check whether the PR that ships the full feature/plan set was created by inspecting recent PR bodies, branch names, commit `Plan:` lines, or explicit feature-directory references. For older runs missed by the PR-created archive trigger, a merged shipping PR is enough legacy evidence (`gh pr list --state merged` or `gh pr view <number>`).
- **Shipping PR created, and no later plans remain unshipped:** move the whole feature directory to `.dreamers/plans/archive/feature-<slug>/` (create the archive dir if it doesn't exist). The PR description is the lasting public record; the archived directory stays for easy local reference. Use `mv` (or `Move-Item`), never delete.
- **Early incremental PR, open/not yet created shipping PR, unknown shipping state, or later plans remain:** leave it.
- Do not archive individual plan files. Legacy flat `plan-*.md` files at the plans root stay in place unless the user explicitly asks for manual cleanup.
- Report what was archived and what was kept (with reason).

## Step 3 — Legacy workspace cleanup (one-time)

The legacy multi-agent pipeline wrote per-cycle workspace artifacts under `.dreamers/{forge,probe,hone,sentinel,echo}/`. The current pipeline writes none of those — Sentinel, Probe, Hone, and Echo do not maintain workspace files.

If any of those directories exist, the user is welcome to delete them:

```bash
# Unix / macOS
rm -rf .dreamers/{forge,probe,hone,sentinel,echo}
```

```powershell
# Windows PowerShell
Remove-Item -Recurse -Force .dreamers\forge, .dreamers\probe, .dreamers\hone, .dreamers\sentinel, .dreamers\echo
```

Do NOT auto-delete — surface as a recommendation. The user may want to keep historical workspace files for reference.

## Step 4 — Project state contradiction scan

Read these durable surfaces and check for drift / contradictions:
- `.dreamers/improvements.md` — open items still relevant?
- `.dreamers/plans/` — any leftover feature directories from created shipping PRs or older merged PRs (covered in Step 2)?
- `.dreamers/retros/` — anything stale or contradicted by recent work?
- Project-level `.github/copilot-instructions.md` Echo-owned sections (Tech stack, Repo structure, Conventions, Key files) — match the actual codebase?
- Recent `git log` on the default branch — major shifts (tech stack, architecture, tooling) reflected in instruction files?

**Propose** all changes to the user — do not auto-apply. Present a numbered list of proposed updates, then call `request_information` (multi-select) with one option per proposed change plus `"Apply none"` and `"Other"` for freeform direction. Apply only the items the user selects. Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

## Step 5 — Report

Summarise in chat:
- Improvements actioned / deferred / closed (one line each)
- Feature plan directories archived / kept
- Legacy workspace recommendations (if any)
- Proposed memory updates (if any)
