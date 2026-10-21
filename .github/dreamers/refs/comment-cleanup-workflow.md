# Comment cleanup workflow

Execute this workflow inline with the supplied input. Resolve links relative to this ref. Read the linked standards before acting. Keep the active skill's todo, gates, and delivery state.

Read and apply [comment-rules](comment-rules.md).

Read and apply [dreamers-kernel](dreamers-kernel.md).

---

## Todo list

At workflow entry, declare via `manage_todo_list`:
- [ ] Phase 1 — audit comment-rules violations
- [ ] Phase 2 — proposal + user approval
- [ ] Phase 3 — apply cleanup inline
- [ ] Phase 4 — optional Vigil review (if requested)
- [ ] Phase 5 — commit

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Phase 1 — Audit

Scope: use the explicit file list supplied by the active skill when present; otherwise use the project source root, or `--scope <path>` to restrict. An empty explicit file list means no work; never broaden it to the project root.

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
- Halt for now → output "Audit complete. No changes applied. Resume with the same user-selected cleanup command and scope." and stop.
- Corrections → revise proposal; re-present.

## Phase 3 — Apply

Edit files inline; stage with `git add`. Follow `dreamers-kernel.md` implementation discipline: only edit files in scope; no while-I'm-here changes to actual logic.

Run the project's type-check command after edits (comments don't usually affect type-check but verify).

## Phase 4 — Optional Vigil review

Call `request_information` with `["Yes — review before commit", "No — skip review", "Other"]`. Vigil's maintainability lens catches anything the cleanup missed or newly-introduced ambiguity.

- Yes → invoke `agent_type: "vigil"` with changed-files scope. Prompt Vigil to focus on comment-rules and maintainability, while still reporting correctness/security/coverage/simplicity findings if they appear. Apply findings inline.
- Require Vigil to write one `.dreamers/reviews/vigil-*.md` artifact and return only status, counts, artifact path, blocked reason, and open questions. Read the artifact before applying findings.
- No → proceed to commit.

## Phase 5 — Commit

`git status` to confirm staged content. Commit message: use the message supplied by the active skill, defaulting to `chore: comment cleanup per comment-rules.md`. Do NOT push.
