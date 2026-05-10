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

**Step 3 — Probe workspace reset (Bolt)**
Probe is the only agent that maintains per-cycle workspace artifacts. Invoke **Bolt** to wipe live Probe files back to "No active work / No pending items":
- `.dreamers/probe/test-plan.md`, `.dreamers/probe/runbook.md`, `.dreamers/probe/bugs.md`
- Also `.dreamers/probe/regression-analysis.md` if present from a prior user-bug cycle.
- Use `printf 'No active work.\n' > <path>` for each file.

**Legacy workspace cleanup (optional)** — pre-refine cycles wrote files under `.dreamers/forge/`, `.dreamers/sentinel/`, `.dreamers/hone/`, `.dreamers/echo/`. Those agents no longer write workspace files. Optionally have Bolt delete the directories: `rm -rf .dreamers/{forge,sentinel,hone,echo}/`.

After Bolt completes, prune any surviving Probe file that exceeds ~200 lines or ~20KB — delete stale content, rewrite to only current actionable items (this requires judgment — do it directly).

**Step 4 — Project state contradiction scan**

Read these durable surfaces and check for drift / contradictions:
- `.dreamers/improvements.md` — open items still relevant?
- `.dreamers/plans/` — any leftover plans from merged PRs (covered in Step 2)?
- Probe artifacts (`test-plan.md`, `bugs.md`, `regression-analysis.md`) — anything stale?
- Project-level `.github/copilot-instructions.md` Echo-owned sections (Tech stack, Repo structure, Conventions, Key files) — match the actual codebase?
- Recent `git log` on default branch — major shifts (tech stack, architecture, tooling) reflected in instruction files?

**Propose** all changes to the user — do not auto-apply. Present a list and wait for approval. Exception: clearly stale entries pointing to nonexistent files can be removed without asking.

**Step 5 — Report**
Summarise in chat:
- Improvements actioned / deferred / closed (one line each)
- Plan files deleted / kept
- Workspace files pruned
- Proposed memory updates (if any)

