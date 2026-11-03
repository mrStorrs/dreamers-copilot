---
name: dreamers-issue
description: 'Create a structured GitHub issue with acceptance criteria from a task description. Triggers: /dreamers-issue, create an issue, open a GitHub issue, file an issue.'
argument-hint: '[#]<task description>  (# prefix triggers discussion mode with clarifying questions)'
---

$ARGUMENTS

## Required workflow

1. **Route input** — use discussion mode for the `#` prefix; otherwise draft directly.
2. **Resolve repository and labels** — confirm the destination and existing labels.
3. **Draft** — write the issue with testable acceptance criteria.
4. **Create** — open the issue and return its URL.

<workflow-progress>

Use this skill's Required workflow as the single `manage_todo_list`. Reuse existing progress on follow-ups. Mark each stage `in_progress` when starting and `completed` only from confirmed results; update as work proceeds, not in a batch at the end.

Add conditional stages only when they apply. Follow the detailed sections for scope, gates, loop limits, and exits; the checklist does not expand them. Record explicit user skips.

Corrections can reopen earlier stages. Resume the appropriate step with the current context, then repeat affected validation and downstream work. Preserve the branch, applicable approvals, and active review count; do not restart the skill or silently reset a cap.

</workflow-progress>

Create a GitHub issue from the supplied request.

---

## User overrides

- Explicit user instructions can skip or alter phases/actions.

**Routing — check for `#` prefix**

If the arguments start with `#`, enter **discussion mode**:
- Strip the `#` and treat the rest as the topic.
- Ask focused questions to clarify scope, intent, and acceptance criteria.
- Continue the conversation until you have enough to write concrete, testable ACs.
- Then proceed to Step 1 below. ACs produced this way are **real** — no "potential" qualifier.

If the arguments do NOT start with `#`, enter **direct mode**:
- Do NOT ask questions.
- Proceed immediately to Step 1. ACs produced this way are **potential** — prefix each with `[potential]`.

---

**Step 1 — Repo detection**
Run `gh repo view --json nameWithOwner` to confirm the current repo. If not in a git repo or no remote is set, call `request_information` asking the user which repo to target (`OWNER/REPO` format) before proceeding.

**Step 2 — Label check**
Run `gh label list` to see available labels. Pick the most appropriate existing label(s) — do not invent labels. Common mappings:
- New capability → `feature`
- Something broken → `bug`
- Docs gap → `documentation`
- Unclear ownership → `question`

**Step 3 — Minimal exploration (optional)**
Light exploration is allowed — e.g. confirm a feature exists, glance at a config, check a directory structure. Keep it to 1-3 lookups max. Deep codebase analysis belongs in `/dreamers-plan`, not here.

**Step 4 — Draft the issue**
Write a focused, minimal issue from the user's input (and any brief exploration from Step 3).

Use the template at `~/.copilot/dreamers/templates/github-issue.md` as the structure. Keep the body concise — no padding, no restatement of the title.

ACs must be written from a **product owner perspective** — user-facing outcomes, not technical implementation. "User can filter by date" not "Add dateFilter param to query handler".

**Step 5 — Create**
Run `gh issue create` with the drafted title, body, and label(s). Report the issue URL when done.

