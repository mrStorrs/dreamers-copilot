---
name: dreamers-cleanup-comments
description: 'Project-wide comment cleanup pass per comment-rules.md. Audit → propose → user approval → apply inline → optional Vigil review. Triggers: /dreamers-cleanup-comments, clean up comments, audit comments, remove fluff comments.'
argument-hint: '[--scope <path>] (defaults to project source root)'
---

$ARGUMENTS

## Required workflow

1. **Audit** — inspect comments within the selected scope.
2. **Propose and approve** — agree on the cleanup.
3. **Apply** — edit comments and type-check.
4. **Review, if requested** — obtain Vigil findings and apply accepted fixes.
5. **Commit** — commit the cleanup and report.

<workflow-progress>

Use this skill's Required workflow as the single `manage_todo_list`. Reuse existing progress on follow-ups. Mark each stage `in_progress` when starting and `completed` only from confirmed results; update as work proceeds, not in a batch at the end.

Add conditional stages only when they apply. Follow the detailed sections for scope, gates, loop limits, and exits; the checklist does not expand them. Record explicit user skips.

Corrections can reopen earlier stages. Resume the appropriate step with the current context, then repeat affected validation and downstream work. Preserve the branch, applicable approvals, and active review count; do not restart the skill or silently reset a cap.

</workflow-progress>

## Cleanup

<comment-cleanup-workflow>

**Input:** explicit file list, or project source root restricted by optional `--scope <path>`, plus an optional commit message. Apply the embedded `comment-rules` and `dreamers-kernel` rules. An empty explicit file list means no work; never broaden it to the project root.

**1. Audit**

Walk the scope and identify each comment-rules violation. Categorize:
- **Redundant** — restates what code already says.
- **Separator** — visual dividers / `// ---` style.
- **Reference** — plan / ticket / agent / milestone string in source.
- **Spec-rationalization** — comments arguing the spec permits a pattern.
- **Redundant docstring** — JSDoc/KDoc that just mirrors the signature.
- **Excessive length** — inline comment > 2 lines.

Produce a count per category in chat + paths of the worst offenders.

**2. Approve the proposal**

Present in chat: total comment removals, summary by category, list of files most-affected.

Call `request_information` with `["Approved — apply cleanup", "Halt for now", "Other"]`. Freeform corrections (e.g., "preserve license headers in src/vendor/") go through Other.

- Approved → proceed to Apply.
- Halt for now → output "Audit complete. No changes applied. Resume with the same user-selected cleanup command and scope." and stop.
- Corrections → revise proposal; re-present.

**3. Apply**

Edit files inline; stage with `git add`. Follow the embedded `dreamers-kernel` implementation discipline: only edit files in scope; no while-I'm-here changes to actual logic.

Run the project's type-check command after edits (comments don't usually affect type-check but verify).

**4. Review if requested**

Call `request_information` with `["Yes — review before commit", "No — skip review", "Other"]`. Vigil's maintainability lens catches anything the cleanup missed or newly-introduced ambiguity.

- Yes → invoke `agent_type: "vigil"` with changed-files scope. Prompt Vigil to focus on comment-rules and maintainability, while still reporting correctness/security/coverage/simplicity findings if they appear. Apply findings inline.
- Require Vigil to write one `.dreamers/reviews/vigil-*.md` artifact and return only status, counts, artifact path, blocked reason, and open questions. Read the artifact before applying findings.
- No → proceed to commit.

**5. Commit**

`git status` to confirm staged content. Commit message: use the supplied message, defaulting to `chore: comment cleanup per comment-rules.md`. Do NOT push.

**Result:** audit counts and scoped changes, with validation, review status, and commit ID when cleanup was approved.

</comment-cleanup-workflow>

## Rules and formats

### Comments

<comment-rules>

**Core principle**

Comments must add value that the code cannot express itself. Concise, no fluff, no separators.

**When to comment**

- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes

**When NOT to comment**

- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

**Strict prohibitions**

- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.

**Style**

- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words

</comment-rules>

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
