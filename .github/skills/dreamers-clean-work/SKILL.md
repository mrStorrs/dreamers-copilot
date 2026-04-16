---
name: dreamers-clean-work
description: 'Between-milestone maintenance pass: prune stale files, check consistency, clean workspace. Triggers: /dreamers-clean-work, clean up, maintenance pass, between milestones.'
argument-hint: '$ARGUMENTS'
---

Run a between-milestone maintenance pass. No implementation, no planning, no agents — do all of this directly.

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

**Step 1 — Improvements audit**
Read `.dreamers/improvements.md` (repo-local). For each open item:
- Decide: action now, defer with a reason, or close as no longer relevant.
- If actionable as a direct text edit to an agent file or ref (meta work): make the edit now.
- If it requires Forge or a full pipeline: defer it — add a note with why and which skill to use.
- Remove actioned/closed items. Leave only open deferred items with defer reasons.

**Step 2 — Plan file cleanup**
In `.dreamers/plans/` (repo-local), for each `plan-*.md`:
- Check if its associated PR is merged (`gh pr list --state merged` or `gh pr view <number>`).
- **Merged:** delete the plan file. The PR description is the lasting record.
- **Open or not yet created:** leave it.
- Report what was deleted and what was kept (with reason).

**Step 3 — Workspace file reset (Bolt)**
Invoke **Bolt** to wipe all live status files in `.dreamers/` (repo-local) back to "No active work / No pending items":
- `forge/status.md`, `probe/status.md`, `sentinel/status.md`
- Use `printf 'No active work.\n' > <path>` for each file.

After Bolt completes, prune any workspace file (across all agents) that exceeds ~200 lines or ~20KB — delete stale content, rewrite to only current actionable items (this requires judgment — do it directly).

**Step 4 — Workspace contradiction scan**

Read all active workspace files under `.dreamers/` (forge, sentinel, probe, etc.). Check for:
- Tech stack drift or architecture pivots not reflected across agent workspaces
- Milestone status that has fallen behind
- Rule conflicts across agent definitions
- Stale entries in `decisions.md`, `assumptions.md`, or `questions.md` that have been resolved but not pruned

**Propose** all memory changes to the user — do not auto-apply. Present a list and wait for approval. Exception: stale index entries pointing to nonexistent files can be removed without asking.

**Step 5 — Report**
Summarise in chat:
- Improvements actioned / deferred / closed (one line each)
- Plan files deleted / kept
- Workspace files pruned
- Proposed memory updates (if any)

