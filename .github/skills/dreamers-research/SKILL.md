---
name: dreamers-research
description: "Scope a research topic, run Sage research/review pairs, and synthesize a cited report."
argument-hint: "<topic>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Spawn Sage in preliminary mode for the topic, writing .dreamers/sage/scope.md. Read the proposed subtopics and depths. Ask the user to select/adjust subtopics or cancel; no deep research before selection.
2. For each selected subtopic, spawn Sage in deep mode with scope, depth, source budget, and .dreamers/sage/<slug>/ output path. Then spawn Sage in review mode for that output. Independent pairs may run in parallel, up to six at once.
3. Read reports and review results. Revise critical research problems with a scoped follow-up. Log failed subtopics in .dreamers/sage/errors.md; continue independent work and clearly identify incomplete areas.
4. Spawn Sage in synthesis mode with the report/review paths, producing .dreamers/sage/final-report.md. Read it before delivery.
5. Return the executive summary, report links, source count, confidence, and unresolved gaps. Ask whether the user wants a particular subtopic expanded.
