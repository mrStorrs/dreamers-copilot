---
name: dreamers-clean-work
description: 'Between-milestone maintenance pass: prune stale files, archive merged plans, audit improvements.md, scan for project-state drift. All inline — no subagents. Triggers: /dreamers-clean-work, clean up, maintenance pass, between milestones.'
argument-hint: '$ARGUMENTS'
---

Run a between-milestone maintenance pass. No implementation, no planning, no subagents — do all of this directly.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Step 1 — Improvements audit

Read `.dreamers/improvements.md` (repo-local). For each open item:
- Decide: action now, defer with a reason, or close as no longer relevant.
- If actionable as a direct text edit to an agent file or ref (meta work): make the edit now.
- If it requires a full pipeline (`/dreamers-full`): defer it — add a note with why and which skill to use.
- Remove actioned/closed items. Leave only open deferred items with defer reasons.

## Step 2 — Plan file archive

In `.dreamers/plans/` (repo-local), for each `plan-*.md` (excluding files already in `archive/`):
- Check if its associated PR is merged (`gh pr list --state merged` or `gh pr view <number>`).
- **Merged:** move the plan file to `.dreamers/plans/archive/` (create the dir if it doesn't exist). The PR description is the lasting public record; the archived file stays for easy local reference. Use `mv` (or `Move-Item`), never delete.
- **Open or not yet created:** leave it.
- Report what was archived and what was kept (with reason).

## Step 3 — Legacy workspace cleanup (one-time)

The legacy multi-agent pipeline wrote per-cycle workspace artifacts under `.dreamers/{forge,probe,hone,sentinel,echo}/`. The current TDD pipeline writes none of those — Sentinel and Echo do not maintain workspace files.

If any of those directories exist, the user is welcome to delete them:

```bash
rm -rf .dreamers/{forge,probe,hone,sentinel,echo}
```

Do NOT auto-delete — surface as a recommendation. The user may want to keep historical workspace files for reference.

## Step 4 — Project state contradiction scan

Read these durable surfaces and check for drift / contradictions:
- `.dreamers/improvements.md` — open items still relevant?
- `.dreamers/plans/` — any leftover plans from merged PRs (covered in Step 2)?
- `.dreamers/retros/` — anything stale or contradicted by recent work?
- Project-level `.github/copilot-instructions.md` Echo-owned sections (Tech stack, Repo structure, Conventions, Key files) — match the actual codebase?
- Recent `git log` on the default branch — major shifts (tech stack, architecture, tooling) reflected in instruction files?

**Propose** all changes to the user — do not auto-apply. Present a list and wait for approval. Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

## Step 5 — Report

Summarise in chat:
- Improvements actioned / deferred / closed (one line each)
- Plan files archived / kept
- Legacy workspace recommendations (if any)
- Proposed memory updates (if any)
