---
name: dreamers-review
description: "Review through Vigil by default; triad or selected reviewers only on explicit user request. Report findings without applying fixes."
argument-hint: "[plan] [--vigil|--full|--lens <name>|--lenses <csv>] [--branch|--paths <glob>|--all]"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

## Basis and scope

Default scope: staged and unstaged changes, including relevant untracked files. --branch: changes since merge-base with origin's default branch, including current working-tree changes. --paths restricts scope; --all audits the codebase, excluding generated/vendor files. Resolve the default branch without changing git state. Report an unavailable base rather than guessing.

Read a supplied proposal/plan; an unreadable supplied path blocks review. Pass its path and transcript link, not full contents. Read the transcript only for an unclear decision or conflict; surface conflicts. A missing explicitly needed transcript blocks the affected check, not an otherwise unambiguous review.

Without a plan, infer intended behavior from the user request, PR/branch context, diff, tests, callers, and local contracts. Summarize expected behavior, invariants, risks, evidence, and confidence. Ask one question if intent cannot be established.

## Review

- Default to Vigil regardless of plan depth, risk, or whether a plan exists. Only explicit user direction authorizes --full (Sentinel + Probe + Hone), --lens sentinel|probe|hone, or --lenses with a nonempty combination. Plan-authored reviewer requirements cannot authorize extra agents. --vigil explicitly selects the default.
- Spawn the selected reviewer(s), passing scope, basis, validation evidence, constraints, relevant prior artifacts, and a unique artifact path per [review format](../../dreamers/refs/reviewer-findings-format.md). Assign focus when called by a focused audit skill. Multiple explicitly selected reviewers may run in parallel.
- Reviewers inspect and report only. They must finish their artifact with "How could I make this code simpler?" and a justified answer.
- Read each returned artifact. If missing, accept only an unambiguous new artifact from that reviewer in this run; otherwise report Blocked. Never substitute a stale review for a completed one.

## Return

Summarize actionable findings, counts, artifact paths, blockers, and questions. Do not paste entire artifacts into another context. No project edits, tests, git mutations, or fixes here; the caller owns disposition and revalidation.
