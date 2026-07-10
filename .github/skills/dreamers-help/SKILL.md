---
name: dreamers-help
description: 'Read-only guide to the Dreamers system, delivery workflow, specialized skills, examples, overrides, and migration choices. Use for /dreamers-help, /dreamers with no input, help, --help, -h, choosing a Dreamers command, or understanding how planning, review, gates, and PR delivery work.'
---

## Boundary

This is read-only guidance. Do not inspect or change repository, git, mailbox, filesystem, or external state. Do not start another skill unless the user explicitly chooses a next command.

## Response

Orient the user briefly: the Dreamers system combines planning, tests-first implementation, artifact-backed review, targeted user gates, documentation, and PR delivery.

Explain the primary entry point with concrete examples:

- /dreamers add offline export
- /dreamers --no-grill fix the settings copy
- /dreamers feature-search/plan-01-indexing.md
- /dreamers feature-search/manifest.md

Explain that task descriptions use /dreamers-plan with Grill by default, while --no-grill, "do not grill," or "skip the interview" opt out. Existing plan and manifest inputs skip Grill but retain quality and drift checks.

Explain adaptive review: low-risk lite and standard plans use Vigil; complex or dangerous work uses Sentinel + Probe + Hone. The user may explicitly override the reviewer lane or ask to skip review, with accepted risk surfaced.

Offer specialized choices when they fit better:

- /dreamers-plan for planning only.
- /dreamers-implement for an approved plan without end-to-end close-out.
- /dreamers-review, /dreamers-test, or /dreamers-simplify for read-only audits.
- /dreamers-fix for a bounded bug fix.
- /dreamers-research, /dreamers-issue, /dreamers-docs, and /dreamers-pr for their focused workflows.

State the mandatory gates: plan approval for task input, major scope expansion, triggered user testing, and final pre-PR approval.

Include the migration note: the retired /dreamers-lite and /dreamers-full commands were removed rather than kept as aliases. Planning may still be lite, standard, or complex because those labels describe plan depth.

End with one invitation: "Describe your goal and I can suggest the next command."
