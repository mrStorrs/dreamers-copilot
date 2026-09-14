---
name: dreamers
description: "Deliver a task from approved proposal through implementation, Vigil review, docs, and PR. Detailed planning is opt-in."
argument-hint: "<task> [--plan] | <plan paths> | <manifest.md> | help"
---

$ARGUMENTS

## Route

Empty input, help, --help, or -h: use /dreamers-help and stop before repository inspection.
Otherwise accept a task, plan paths, or manifest; ask if none is identifiable.

Read [shared rules](../../instructions/dreamers.instructions.md) and [git workflow](../../dreamers/refs/git-workflow.md) once.

## Establish the plan

- Task: follow [the Grill](../../dreamers/refs/planning-grill.md). Present a proposal using [proposal fields](../../dreamers/templates/proposal.md), including critique and all accepted decisions. Ask for approval. On approval, save the approved proposal as .dreamers/plans/feature-<slug>/plan-01-<name>.md, link the saved transcript, mark it Active, and start implementation immediately. No second start gate.
- Only if the user requests detailed planning or --plan: use /dreamers-plan first. Its approval is the implementation approval; continue immediately when it returns approved paths.
- Supplied plan(s)/manifest: resolve feature-relative paths under .dreamers/plans/. Read the files, preserve their order and manifest context, and proceed without planning or start approval. Require readable plan-*.md files or manifest.md within that directory. Accept proposal, lite, standard, complex, and usable legacy plans; block missing files, shell drafts, placeholders, unresolved decisions, or non-actionable scope.
- For multiple plans, include ATOMIC versus INCREMENTAL in the task proposal approval. Recommend ATOMIC for coupled work; INCREMENTAL for independent deliverables. Supplied plans default to ATOMIC unless the user specifies otherwise.

Set up the feature branch once per git workflow. Review open .dreamers/improvements.md items; act only on relevant authorized work.

## Implement each plan

1. Invoke /dreamers-implement with the absolute plan path and relevant shared context. Stop if validation is blocked.
2. Invoke /dreamers-review --branch with that plan and validation evidence. Vigil is the default; pass alternate reviewer flags only when the user explicitly requested them. Read this run's artifacts.
3. Follow [apply findings](../../dreamers/refs/apply-findings.md), including scope gates, deferrals, validation, and justified reruns. Decide whether the final simplicity suggestion improves the code without weakening correctness.
4. Require user testing when the plan calls for it, behavior is user-facing, build/distribution is needed, a reviewer requests it, or the user asked to test. Use [the user-testing gate](../../dreamers/templates/user-testing-gate.md). For reported bugs, fix, verify, apply the review-rerun policy, and present the gate again. Otherwise record why no manual check is needed.
5. Before the next plan, check it against the current code. Surface material drift for revision, skip, or halt. ATOMIC: commit the completed cycle and continue without pushing. INCREMENTAL: update affected docs with /dreamers-docs, commit, get pre-PR approval with scope and validation results, invoke /dreamers-pr, wait for merge confirmation, then branch from updated default for the next cycle.

## Final close-out

1. Write .dreamers/retros/retro-<yyyymmdd-hhmmss>-<slug>.md: results, what worked, friction, improvements, outcome verification, manual-test bugs, and regression analysis for bug fixes.
2. Append dated improvements with the retro link to .dreamers/improvements.md. Record "none identified" if justified; do not invent suggestions.
3. Invoke /dreamers-docs --branch. Ensure test-benchmarks.md includes every successful test command. Commit final changes per git workflow.
4. Present the milestone summary, verification, and PR scope for user approval. On approval invoke /dreamers-pr, passing any issue reference. On halt, leave a precise resume command.
5. Report PR/artifact paths, open improvements, and any project-state drift. No automatic post-PR edits or commits.
