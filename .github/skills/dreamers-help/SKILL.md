---
name: dreamers-help
description: 'Read-only guide to the Dreamers system, delivery workflow, specialized skills, examples, reviewer lanes, gates, and migration choices. Use for /dreamers-help, /dreamers with no input, help, --help, -h, choosing a Dreamers command, or understanding how planning, review, gates, and PR delivery work.'
---

## Boundary

This is read-only guidance. Do not inspect or change repository, git, mailbox, filesystem, or external state. Do not start another skill unless the user explicitly chooses a next command.

## Response

Orient the user briefly: the Dreamers system combines planning, tests-first implementation, artifact-backed review, targeted user gates, documentation, and PR delivery.

Explain the primary entry point with concrete examples:

- /dreamers add offline export
- /dreamers feature-search/plan-01-indexing.md
- /dreamers feature-search/manifest.md

Explain that task descriptions use /dreamers-plan with Grill by default. Existing plan and manifest inputs skip planning and the implementation-start gate while retaining plan-quality and drift checks.

Explain adaptive review:

- lite plans use Vigil.
- standard plans use Sentinel + Probe.
- complex plans use Sentinel + Probe + Hone.

Explicit plan or user direction overrides the default reviewer lane. Reviewers are read-only for project files and write their required `.dreamers/reviews/` artifacts; the caller applies accepted findings and owns revalidation.

Offer specialized choices when they fit better:

- /dreamers-plan for planning only.
- /dreamers-implement for an approved plan without end-to-end close-out.
- /dreamers-review, /dreamers-test, or /dreamers-simplify for read-only audits.
- /dreamers-lite for a bounded bug fix.
- /dreamers-research, /dreamers-issue, /dreamers-new-project, /dreamers-find-refactors, and /dreamers-explain for focused discovery or explanation.
- /dreamers-docs, /dreamers-pr, and /dreamers-pr-resolve for documentation, PR creation, or PR feedback.
- /dreamers-add-logging, /dreamers-cleanup-comments, /dreamers-cleanup-comments-branch, /dreamers-clean-work, and /dreamers-plan-verify for maintenance and verification.
- /dreamers-update for Dreamers system-file maintenance and the approved Copilot-to-Codex transfer.

State the mandatory gates: plan approval for task input, major scope expansion, triggered user testing, and final pre-PR approval.

Explain that `/dreamers` is the only end-to-end delivery pipeline and that lite, standard, and complex are plan-depth labels, not separate delivery tiers. The retired `/dreamers-full` command has no forwarding alias.

End with one invitation: "Describe your goal and I can suggest the next command."
