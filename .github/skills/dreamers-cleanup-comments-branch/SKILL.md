---
name: dreamers-cleanup-comments-branch
description: 'Branch-scoped comment cleanup. Same as /dreamers-cleanup-comments but scoped to the current feature-branch diff. Standalone pre-PR comment sweep. Triggers: /dreamers-cleanup-comments-branch, comment cleanup branch scope, pre-PR comment sweep.'
argument-hint: '(no args; scope is automatic from the current branch diff)'
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
- [ ] Phase 1 — audit branch-diff scope for comment-rules violations
- [ ] Phase 2 — proposal + user approval
- [ ] Phase 3 — apply cleanup inline
- [ ] Phase 4 — optional Vigil review (if requested)
- [ ] Phase 5 — commit

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Scope detection

Detect default branch (canonical two-step):
```bash
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
```

Fetch the remote before computing the diff (otherwise a stale local `origin/$DEFAULT` will produce a wrong or empty file list):
```bash
git fetch origin
```

If `git rev-parse origin/$DEFAULT` fails after the fetch, halt with: "Could not resolve `origin/$DEFAULT`. Check your remote configuration."

Scope = files in `git diff origin/$DEFAULT...HEAD --name-only`.

If the working tree is on the default branch (no feature-branch diff), halt with an error: "This skill operates on a feature branch's diff. Use `/dreamers-cleanup-comments` for project-wide cleanup."

---

## Phases

Phases 1–5 are identical to `/dreamers-cleanup-comments`, scoped to the branch-diff file list:

1. **Audit** the branch-diff scope; categorize comment-rules violations.
2. **Propose** changes; `request_information` for approval.
3. **Apply** changes inline; stage with `git add`.
4. **Optional Vigil review** of changed files. Assign Vigil a fresh path and collect its handoff using the contract below. Halt on a missing handoff or blocked status and raise open questions before applying findings.
5. **Commit** with message `chore: comment cleanup on feature branch`. Do NOT push.

## When this skill is the right tool

- Pre-PR polish — after a feature is done, before opening the PR, when you want the branch's comments inspected before they ship.
- Targeted clean-up scoped to the changes a single feature branch introduced, without auditing the entire project.

For project-wide cleanup (not branch-scoped), use `/dreamers-cleanup-comments`.

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
