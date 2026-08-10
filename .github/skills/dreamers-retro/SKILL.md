---
name: dreamers-retro
description: 'Evidence-gated retrospective for Dreamers delivery sessions. Reviews the current session for real blockers, AI mistakes, or developer corrections that justify a minimal repo-local AI scaffolding improvement. Writes no retro when evidence is absent and never targets Dreamers core. Triggers: /dreamers-retro, retrospective, invoked after /dreamers and /dreamers-lite.'
argument-hint: '[optional task or session label]'
---

Review the current session. Work inline; do not use subagents. When invoked by another skill, return control to that skill.

$ARGUMENTS

## Boundaries

- Suggest only. Do not apply scaffolding changes.
- Target only AI-facing scaffolding inside the current repository, such as `.github/copilot-instructions.md`, project-specific `.github/instructions/`, non-Dreamers `.github/skills/` or `.github/agents/`, and AI support scripts or templates.
- Never target global files, installed skills, or Dreamers-owned skills, agents, refs, templates, instructions, catalogs, installers, or validation harnesses. A Dreamers core concern is out of scope even when this repository contains Dreamers source.
- Treat `.dreamers/retros/` and `.dreamers/improvements.md` as local proposal artifacts, not scaffolding changes.

## Evidence gate

Start with the current session, not a general repository audit. A candidate requires at least one observed event:

- A blocker caused by missing, wrong, or ambiguous repo-local AI guidance.
- An AI mistake that a specific repo-local instruction or deterministic check could plausibly prevent.
- An explicit developer correction that expresses a durable, repo-specific rule.

Keep a candidate only when all are true:

1. Cite the observed event in one sentence.
2. Explain the repo-local scaffolding gap that contributed to it.
3. Name one exact target file and one minimal proposed change.
4. Inspect that target and confirm the rule is not already clear.

Reject generic best practices, speculative risks, successful steps, praise, product-code issues, external tool or permission failures, one-off preferences, and cases where the AI merely ignored an existing clear rule. Reject every proposal whose target is Dreamers core.

If no candidate survives, do not create or modify any file. Return exactly:

`No retrospective warranted — no repo-scaffolding blocker, AI mistake, or developer correction found.`

## Record qualifying improvements

Keep at most three high-confidence suggestions.

1. Confirm `.dreamers/` is gitignored. If it is not, do not change `.gitignore`; return the suggestions in chat and state that local artifacts were skipped.
2. Write `.dreamers/retros/retro-YYYY-MM-DD-<short-label>.md`. Add a numeric suffix if the path exists. Include only:
   - Session context
   - Evidence-backed event
   - Scaffolding gap
   - Exact target
   - Minimal suggested change
3. Append one dated sentence per new suggestion to `.dreamers/improvements.md`, referencing the retro path. Preserve existing content and do not duplicate an equivalent open item.
4. Return the retro path, the suggestions, and `No scaffolding changes applied.`

Do not include full transcript excerpts, secrets, credentials, personal data, or unrelated session history in either artifact.
