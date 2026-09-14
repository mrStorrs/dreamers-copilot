---
name: dreamers-help
description: "Read-only Dreamers command guide, workflow, review options, and gates."
---

$ARGUMENTS

Explain the relevant commands from this guide without inspecting repositories or starting work.

- /dreamers <task>: Grill → proposal approval → save proposal as plan → implement → Vigil → fixes → required user testing → docs/retro/improvements → approved PR.
- /dreamers <task> --plan: explicitly request detailed plans before the same single implementation approval.
- /dreamers feature-search/plan-01-indexing.md or feature-search/manifest.md: use supplied artifacts directly; no new start gate.
- /dreamers-plan: detailed planning only. /dreamers-implement: implementation only. /dreamers-lite: bounded bug fix.
- /dreamers-review: Vigil by default. --full or --lens sentinel|probe|hone requires explicit user selection. Plan complexity never selects additional reviewers.
- /dreamers-test and /dreamers-simplify: focused Vigil audits. /dreamers-find-refactors: discovery and candidate plans.
- /dreamers-docs, /dreamers-pr, /dreamers-pr-resolve: docs, shipping, PR feedback.
- /dreamers-research, /dreamers-explain, /dreamers-issue, /dreamers-new-project: research, explanation, issues, bootstrap.
- /dreamers-add-logging, /dreamers-cleanup-comments, /dreamers-cleanup-comments-branch, /dreamers-clean-work, /dreamers-plan-verify: maintenance.
- /dreamers-update: Copilot first, user-approved Codex transfer.

Mandatory: proposal approval for new task scope, scope-change gates, triggered user testing, pre-PR approval, meaningful verification, test timings, retros, and improvements. Detailed planning and tests-first are optional. Transcripts stay saved but are read only when needed.

The retired /dreamers-full has no alias. Use /dreamers for delivery. Offer a relevant example and invite the user's task.
