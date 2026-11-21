---
name: dreamers-cleanup-comments
description: 'Project-wide comment cleanup pass per comment-rules.md. Audit → propose → user approval → apply inline → optional Vigil review. Triggers: /dreamers-cleanup-comments, clean up comments, audit comments, remove fluff comments.'
argument-hint: '[--scope <path>] (defaults to project source root)'
---

<comment-rules>
## Core principle
Comments must add value that the code cannot express itself. Concise, no fluff, no separators.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

## Strict prohibitions
- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words
</comment-rules>

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Echo uses the sole prompt defined in `/dreamers-docs`. All other `task()` invocations MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1 — audit comment-rules violations
- [ ] Phase 2 — proposal + user approval
- [ ] Phase 3 — apply cleanup inline
- [ ] Phase 4 — optional Vigil review (if requested)
- [ ] Phase 5 — commit

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Phase 1 — Audit

Scope: project source root by default; `--scope <path>` to restrict.

Walk the scope and identify each comment-rules violation. Categorize:
- **Redundant** — restates what code already says.
- **Separator** — visual dividers / `// ---` style.
- **Reference** — plan / ticket / agent / milestone string in source.
- **Spec-rationalization** — comments arguing the spec permits a pattern.
- **Redundant docstring** — JSDoc/KDoc that just mirrors the signature.
- **Excessive length** — inline comment > 2 lines.

Produce a count per category in chat + paths of the worst offenders.

## Phase 2 — Proposal + user approval

Present in chat: total comment removals, summary by category, list of files most-affected.

Call `request_information` with `["Approved — apply cleanup", "Halt for now", "Other"]`. Freeform corrections (e.g., "preserve license headers in src/vendor/") go through Other.

- Approved → proceed to Phase 3.
- Halt for now → output "Audit complete. No changes applied. Resume by re-invoking `/dreamers-cleanup-comments`." and stop.
- Corrections → revise proposal; re-present.

## Phase 3 — Apply

Edit files inline; stage with `git add`. Follow `dreamers-kernel.md` implementation discipline: only edit files in scope; no while-I'm-here changes to actual logic.

Run the project's type-check command after edits (comments don't usually affect type-check but verify).

## Phase 4 — Optional Vigil review

Call `request_information` with `["Yes — review before commit", "No — skip review", "Other"]`. Vigil's maintainability lens catches anything the cleanup missed or newly-introduced ambiguity.

- Yes → invoke `agent_type: "vigil"` with changed-files scope. Prompt Vigil to focus on comment-rules and maintainability, while still reporting correctness/security/coverage/simplicity findings if they appear.
- Assign Vigil a fresh path and collect its handoff using the contract below. Halt on a missing handoff or blocked status and raise open questions before applying findings inline.
- No → proceed to commit.

## Phase 5 — Commit

`git status` to confirm staged content. Commit message: `chore: comment cleanup per comment-rules.md`. Do NOT push.

<reviewer-findings-format>
# Reviewer Findings Format

## Review handoff

The caller assigns an unused absolute path under the target worktree's `.dreamers/reviews/` for each invocation. Use `<reviewer>-<scope>-<unique-id>.md` with the section in the scope for section audits. Pass the exact path and this handoff requirement in the agent prompt.

The reviewer prepares one complete report in its assigned format, ending with `End of handoff` on its own line. Create the parent directory if needed, attempt to write the report at the assigned path, and return the same complete report in the final reply, even if the write fails.

For each expected reviewer invocation, check the assigned file and the final reply from that invocation. A complete report has a valid status, the required sections for the reported outcome, the stated number of findings, and the closing line. A blocked report needs the blocker and any open questions in addition to the closing line. Use the complete file if available, otherwise use the complete reply. Process one copy per invocation. If neither copy is complete, report the missing handoff for that reviewer and scope. Preserve blocked status, findings, and open questions from the accepted report and apply the caller's existing gates.

**Status line** (one of):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:

```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

- `severity` ∈ `critical` / `high` / `medium` / `low`
- `lens-tag` ∈ `correctness` / `security` / `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` — absolute or repo-relative path + line number
- `what was wrong → suggested fix` — one-line description + targeted fix the caller can apply mechanically

**Observations** (optional) — out-of-scope notes that aren't findings. The caller may or may not act on them.

**Open questions** (optional) — items needing user judgment. Use "none" if no questions.

Reviewers deliver findings. The caller owns fix application and validation.
</reviewer-findings-format>
