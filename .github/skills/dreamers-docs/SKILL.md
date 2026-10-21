---
name: dreamers-docs
description: 'Docs skill — spawns Echo to update Echo-owned sections of .github/copilot-instructions.md plus other project docs (README, CHANGELOG) affected by recent changes. Echo stages edits; does not commit. Triggers: /dreamers-docs, update docs, echo docs update.'
argument-hint: '[--branch | --staged]'
---

$ARGUMENTS

Read [documentation workflow](../../dreamers/refs/documentation-workflow.md), resolving the link relative to this file, and execute it with the supplied arguments.
