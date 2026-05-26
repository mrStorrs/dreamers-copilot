---
name: dreamers-add-logging
description: 'Phased pass to add or improve project logging per logging-standards.md. Audit current state → propose changes → user approval → implement inline → optional Sentinel review. Triggers: /dreamers-add-logging, add logging, improve logging, audit log calls.'
argument-hint: '[--scope <path>] (defaults to project source root)'
---

## What this skill does

Walks a project (or a subdirectory) and brings the logging up to `logging-standards.md`:

- ERROR for unhandled failures with full stack traces
- WARN for recoverable issues
- INFO for lifecycle / business signal (startup config, request/response status+duration, auth events, business events)
- DEBUG for traceability (function entry/exit on non-trivial fns, branch decisions, repo calls, retries, state transitions)
- No secrets / PII / full request bodies logged

All work runs inline (no implementation subagent). Optionally spawns Sentinel at the end to review the changes.

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


Also load at runtime (not inlined — these are templates / project files):
- `~/.copilot/dreamers/templates/logging-standards.md` — the binding spec
- `.github/copilot-instructions.md` (project, if present) — project-specific logging conventions (logger library, format)

<dreamers-kernel>
<!-- GENERATED from .github/dreamers/refs/dreamers-kernel.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Dreamers Kernel

Universal rules. Inlined at the bottom of every Dreamers skill + agent by `scripts/sync-refs.ps1`.

## Subagent allowlist (HARD RULE)

The only `agent_type` values a skill may pass to `task()`:
- `sentinel`, `probe`, `hone`, `echo`, `sage`

Forbidden: `general-purpose`, `claude`, `claude-code-guide`, `Explore`, `Plan`, `bolt`, or any non-Dreamers agent. Exception: only if the user explicitly authorizes a fallback in the current run.

## Single-owner todo

Each user-invoked skill owns its own todo for its run. When skills compose (e.g., `/dreamers-full` invokes `/dreamers-implement`), the called skill creates its own todo on entry and closes it on exit. Sub-skills do not touch the caller's todo.

## Mandatory subagent prompt line

Every `task()` invocation MUST include this line in the prompt:

```
Do NOT call `manage_todo_list`. The skill that invoked you owns its todo.
```

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```
</dreamers-kernel>

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1 — audit current logging state
- [ ] Phase 2 — proposal + user approval
- [ ] Phase 3 — implement approved changes
- [ ] Phase 4 — optional Sentinel review
- [ ] Phase 5 — commit

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Phase 1 — Audit

Scope: project source root by default; `--scope <path>` to restrict.

Walk the scope and identify:
- Functions with no logging where DEBUG entry/exit would help.
- Branches without log statements that affect business outcomes.
- ERROR-level logs missing stack traces.
- INFO logs that include secrets, PII, or full request bodies (NEVER-LOG violations — high priority).
- DEBUG logs in high-frequency loops without `// high-freq` annotation.
- Log calls using the wrong level (e.g., ERROR for recoverable issues; INFO for incoming requests with full bodies).

Produce an audit summary in chat: file path → issues found.

## Phase 2 — Proposal + user approval

Present the proposed changes in chat:
- List of files to modify, with one-line summary per file.
- Net adds vs net changes (e.g., "12 new DEBUG calls, 3 ERROR-level fixes, 2 NEVER-LOG violations to remove").
- Any logger-library / format conventions detected from existing code (so additions are consistent).

Call `request_information` with `["Approved — apply changes", "Halt for now", "Other"]`. Freeform corrections go through Other.

- Approved → proceed to Phase 3.
- Halt for now → output "Audit complete. No changes applied. Resume by re-invoking `/dreamers-add-logging`." and stop.
- Corrections → revise proposal; re-present. Loop until approved.

## Phase 3 — Implement

Apply the approved changes inline. Stage with `git add` as you go. Follow `orchestrator-discipline.md` implementation rules — only edit files in scope; no while-I'm-here cleanup.

Run the project's type-check command after edits. Fix any type errors.

## Phase 4 — Optional Sentinel review

Call `request_information` with `["Yes — review before commit", "No — skip review", "Other"]`.

- Yes → invoke `agent_type: "sentinel"` with the changed-files scope. Sentinel reviews under correctness/security/maintainability lenses; comment-rules + logging-standards violations surface here. Apply findings inline.
- No → proceed to commit.

## Phase 5 — Commit

`git status` to confirm staged content. Commit message: `chore: improve logging per logging-standards.md` (or appropriate). Do NOT push (user pushes when ready, or invokes `/dreamers-close-out` which handles push + PR via `pr-procedure.md` inline).

## What this skill does NOT do

- Does NOT add a new logger library or change the logger framework.
- Does NOT add log calls in tests (tests don't need INFO/DEBUG log calls).
- Does NOT auto-apply changes without Phase 2 user approval.
