---
name: dreamers-cleanup-comments
description: 'Project-wide comment cleanup pass per comment-rules.md. Audit → propose → user approval → apply inline → optional Sentinel review. Triggers: /dreamers-cleanup-comments, clean up comments, audit comments, remove fluff comments.'
argument-hint: '[--scope <path>] (defaults to project source root)'
---

## What this skill does

Walks the project source and removes / improves comments to match `comment-rules.md`:

- Delete redundant comments that restate obvious code.
- Delete separator comments (`// ---`, `// ===`, `// ###`, blank-comment lines, visual dividers).
- Delete plan / ticket / agent / milestone references in source code.
- Delete spec-rationalization comments.
- Delete redundant JSDoc/KDoc that only repeats the function signature.
- Shorten comments exceeding two lines (or flag the underlying code for refactoring).
- Preserve: non-obvious logic explanations, public API docs callers need, actionable TODO/FIXME, license headers.

Orchestrator does the work inline. Optionally Sentinel reviews at end.

For branch-scoped cleanup (inside a parent pipeline, scoped to the feature diff), use `/dreamers-cleanup-comments-branch` instead.

## Pre-flight reads

- `~/.copilot/dreamers/refs/comment-rules.md` — the binding spec
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — comment-writing discipline

$ARGUMENTS

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

Call `ask_user` with `["Approved — apply cleanup"]` and allow inline freeform corrections (e.g., "preserve license headers in src/vendor/").

- Approval → proceed to Phase 3.
- Corrections → revise proposal; re-present.

## Phase 3 — Apply

Edit files inline; stage with `git add`. Follow `orchestrator-discipline.md` implementation rules: only edit files in scope; no while-I'm-here changes to actual logic.

Run the project's type-check command after edits (comments don't usually affect type-check but verify).

## Phase 4 — Optional Sentinel review

Ask the user: *"Want a Sentinel review before commit?"* — Sentinel's maintainability lens catches anything the cleanup missed or any newly-introduced ambiguity.

- Yes → invoke `agent_type: "sentinel"` with changed-files scope. Apply findings inline.
- No → proceed to commit.

## Phase 5 — Commit

`git status` to confirm staged content. Commit message: `chore: comment cleanup per comment-rules.md`. Do NOT push.

## What this skill does NOT do

- Does NOT modify code logic or behavior — comments only.
- Does NOT touch comments in tests beyond rule violations (tests are code too; same rules apply).
- Does NOT auto-apply without Phase 2 approval.
