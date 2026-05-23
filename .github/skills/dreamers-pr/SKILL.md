---
name: dreamers-pr
description: 'PR-creation phase of the Dreamers pipeline. Pushes the current feature branch, opens a PR via `gh pr create` using the `pr-description.md` template, optionally closes a referenced issue. Invokable standalone or composed from `/dreamers-close-out`. Triggers: /dreamers-pr, push and open PR, create pull request.'
argument-hint: '(optional inputs auto-detected; orchestrator passes via composed mode)'
---

## What this skill does

The final mechanical step of the close-out flow. Performs:

1. `git push -u origin <branch>` — the single push of the milestone.
2. `gh pr create` with body drafted from `pr-description.md`.
3. Optionally `gh issue close <number>` if an issue is referenced.
4. Captures the PR URL.

No subagent spawned. No user approval gate inside this skill — the gate runs upstream in `/dreamers-close-out` before this skill is invoked.

## Pre-flight reads

Read these refs once at startup:

- `~/.copilot/dreamers/refs/git-workflow.md` — push discipline (single push, no force, exactly at PR close-out)
- `~/.copilot/dreamers/refs/close-out.md` — post-PR rules
- `~/.copilot/dreamers/templates/pr-description.md` — body template
- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — discipline framing

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, any PR-creation constraints.
- `.github/instructions/git.instructions.md` (root, if present) — commit message style (for the PR title convention).

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Pre-push verification (branch identity, clean working tree, branch ahead of remote)
- [ ] Step 1 — push branch
- [ ] Step 2 — draft PR body
- [ ] Step 3 — open PR
- [ ] Step 4 — issue close (if applicable)
- [ ] Report PR URL to caller

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-close-out`, do NOT declare a new list — update the parent's matching Step 6 item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## Invocation modes

### Composed mode (called by `/dreamers-close-out`)

The caller passes a set of inputs in the prompt. Inputs vary by which close-out mode invoked this skill:

**From FULL close-out (milestone end):**
- Current branch name
- Default branch name
- Plan file paths (list shipped this milestone — may be one or many)
- Retro file path (for PR body content)
- Sentinel summary string (concatenated across all cycles in the milestone)
- Issue number / URL (if applicable)
- Final commit hash (if any docs were committed by close-out)

**From LIGHT close-out (per-plan PR during INCREMENTAL ship mode):**
- Current branch name
- Default branch name
- Plan file path (SINGLE plan — the one just completed)
- Retro file path: **omitted** (retro happens at the milestone's final plan, not per plan)
- Sentinel summary string (just THIS plan's reviewer summary, not concatenated across milestone)
- Issue number / URL (if applicable)
- Final commit hash (if docs were committed by light close-out)

PR body drafting (Step 2 below) handles both: when retro path is provided, the body references it; when not provided, the body omits the retro section entirely. The PR title and Summary section adapt — milestone PR titles describe the feature, per-plan PR titles describe the single plan.

### Standalone mode (user invokes directly)

Auto-detect:
- Branch: `git branch --show-current`.
- Default branch: canonical two-step.
- Plan paths: scan `.dreamers/plans/` for files matching the current branch's commit messages (`git log origin/<DEFAULT>..HEAD --format=%B | grep -E "^Plan:"`).
- Sentinel summary: not available in standalone mode; PR body uses "Standalone PR creation — no Sentinel summary captured" placeholder.
- Issue reference: ask the user before opening the PR. Format expected: number (e.g. `42`) or full URL.

---

## Mandatory pre-push verification

Before pushing, verify:

1. **Branch identity** — `git branch --show-current` must NOT be the default branch. If on default, halt with error: "Refuse to push: working tree is on $DEFAULT, not a feature branch."
2. **Working tree clean** — `git status --porcelain` must be empty. If not, halt: "Working tree has uncommitted changes; commit them before opening the PR." (If called from `/dreamers-close-out`, this should already be handled by Step 4 final commit; if not, surface the discrepancy.)
3. **Branch is ahead of remote** — `git log origin/$(git branch --show-current)..HEAD` should have commits, or the branch should not yet exist on remote. If the branch exists on remote and is up-to-date with local, halt: "Nothing to push." (Edge case: re-running this skill on an already-pushed branch.)
4. **No force-push intent** — never use `--force` or `--force-with-lease` for the initial push. If a previous push exists and there's divergence, halt and ask the user.

---

## Step 1 — Push

```bash
git push -u origin <branch-name>
```

This is the ONLY push in the whole milestone pipeline. If push fails:
- **Rejected (non-fast-forward):** halt; surface the error. Ask the user how to proceed. Do not auto-force.
- **Network / auth error:** halt; surface; the user resolves credentials.
- **Hook failure:** halt; surface the pre-push hook output; do not skip hooks.

## Step 2 — Draft PR body

Use `~/.copilot/dreamers/templates/pr-description.md` as the base template. Fill in:

- **Summary** — one paragraph: plan title + 1–3 bullets of what was delivered + why.
- **Test counts** — only if test platforms are touched. Otherwise omit the section.
- **Fixes applied** — severity-graded list from the Sentinel summary string (if present in composed mode).

Title format: short (under 70 chars). Body details, not the title.

### Co-authored attribution (mandatory)

Any co-author trailer in commit messages MUST use the standard git trailer key + this exact author identity:

```
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```

Notes:
- The key is `Co-authored-by:` (lowercase with hyphens, ending in `by:`) — this is git's standard trailer key for co-authors, required so that `git interpret-trailers` and GitHub recognize it.
- The author name is **`The Dreamers System`**. Do NOT use any specific AI model name (e.g., `Claude`, `Claude Opus`, `GPT-5.4`, `claude-opus-4-7`). The Dreamers system as a whole is the contributor; specific model implementations are detail that ages poorly. If a tool's default commit-attribution template includes a model name, override it.
- The email `<noreply@dreamers.local>` is a placeholder. It won't link to a GitHub profile (no such user exists), but it satisfies the trailer's expected `Name <email>` format so git tooling treats the line as a real trailer.

The PR body should NOT include a `Co-authored-by:` line — co-author trailers belong on commits, not on PR descriptions. The PR description summarises the change; commit messages carry attribution.

## Step 3 — Open the PR

```bash
gh pr create \
  --title "<short title>" \
  --body "<drafted body>" \
  --base <DEFAULT_BRANCH>
```

Capture the returned PR URL.

If `gh pr create` fails:
- **Authentication:** halt; ask user to `gh auth login`.
- **PR already exists for this branch:** halt; surface the existing URL.
- **Repo permission denied:** halt; surface.

## Step 4 — Issue close (if applicable)

If an issue number/URL was passed (composed mode) or detected (standalone, after user input):

```bash
gh issue close <number> --comment "Resolved in <PR URL>"
```

If the issue close fails, surface the error but do not roll back the PR — the PR is valid even if the issue close has problems.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (yes/no/N/A).
- Push result (success / failure with reason).

When called **from `/dreamers-close-out`**, the orchestrator captures the PR URL and proceeds to the post-PR discipline phase (which lives in `/dreamers-close-out`, not here).

When called **standalone**, tell the user:
- The PR URL.
- Reminder of post-PR discipline (no auto-commit, ask before pushing additional changes) — which lives in `/dreamers-close-out` if they want to invoke that wrapper; otherwise the user follows the discipline manually.

## Push discipline (reiteration)

This skill is the SINGLE point where `git push` runs in the whole milestone. After this skill exits, any further changes (review-comment fixes, CI failures) must be committed + pushed only with explicit user approval per `close-out.md` post-PR rules.
