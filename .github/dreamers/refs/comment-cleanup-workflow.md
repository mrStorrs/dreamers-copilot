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
