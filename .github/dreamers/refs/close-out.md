# Close-out Protocol

Run this when all Sentinel passes clear and Probe passes.

## Echo (documentation update)

Before final commit, invoke **Echo** (Haiku subagent) to update project documentation:
- Pass Echo the plan file path, `forge/implementation.md`, and any relevant context
- Echo updates the project-level `CLAUDE.md` (Echo-owned sections only) and any other docs that need updates based on what was shipped
- Echo logs all doc changes to `.dreamers/echo/docs-log.md`

## Final commit (before PR)

Before opening the PR, create a final commit capturing any remaining changes (including Echo's doc updates):
1. `git status` — check for uncommitted changes
2. If changes exist, commit with message: `docs: final cleanup before PR` (or appropriate message)
3. If no changes, skip — do not create empty commits

## PR creation (delegate to Bolt)

Invoke **Bolt** (Haiku subagent) for the mechanical PR steps. Pass Bolt:
1. Branch name to push: `git push -u origin <branch-name>`
2. PR title and body (use template at `~/.copilot/dreamers/templates/pr-description.md` — prepare the content before invoking Bolt)
3. Base branch (the repo's default branch — detected during branch setup per `git-workflow.md`)
4. If the original task referenced a GitHub issue number or URL, include it so Bolt can close it: `gh issue close <number> --comment "Resolved in <PR URL>"`

Bolt reports back: PR URL, issue closed (if applicable). User reviews the diff and merges.

## Post-PR changes (no auto-commit)

If any changes are made after the PR is created (e.g., addressing review comments, fixes):
1. **Do NOT auto-commit.** Ask the user: "I have changes ready. Should I commit and push these to the PR?"
2. Only commit and push after explicit user approval.
3. Use commit message: `fix: address PR feedback` (or appropriate message)

## Retrospective (run before opening PR)

1. Review the full cycle by reading:
   - Plan file for this milestone
   - `forge/implementation.md`
   - `sentinel/findings.md` and `sentinel/review.md`
   - `probe/bugs.md` and `probe/test-plan.md`
2. Write a retro file to `.dreamers/retros/retro-d<N>-<name>.md` containing:
   - **What worked well** — clean handoffs, agents that ran without rework
   - **Friction points** — weak output, rework, unclear handoffs
   - **Proposed improvements** — specific, actionable edits to agent prompts, refs, or delegation. Reference the exact section to change and why.
3. Append new improvement suggestions to `.dreamers/improvements.md` with retro date and cycle reference.

## Post-PR
1. **Surface improvements** from this cycle's retro — one sentence each. Ask: "Should I address any of these?" Do not apply without user go-ahead.
2. **Project state scan:** Review workspace files under `.dreamers/` (decisions, assumptions, questions). Check for: tech stack drift, architecture pivots not propagated, milestone status fallen behind, rule conflicts across agent definitions. **Propose all changes — do not auto-apply.**

## Rules for improvement suggestions
- Propose only; never auto-apply changes to agent files or refs.
- Prioritize recurring friction over one-off issues.
- If the same friction appears in two consecutive retros, escalate to top of list.

## improvements.md check (mandatory at milestone boundaries)
- **Milestone start:** Read `.dreamers/improvements.md` — action or explicitly re-defer each open item before invoking Forge.
- **Milestone close:** Append any new improvement suggestions from this cycle.
