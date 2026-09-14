---
name: dreamers-new-project
description: "Discover a new project, approve its stack and brief, bootstrap it, and write shell milestones."
argument-hint: "<project idea>"
---

$ARGUMENTS

Read [shared rules](../../instructions/dreamers.instructions.md) if not already loaded.

1. Use [discovery questions](../../dreamers/templates/discovery-questions.md), one unresolved question at a time. Keep discovery conversational.
2. Ask whether to research existing solutions. Only after approval, run a focused inline scan with cited comparisons; keep it conversational and carry findings into the brief.
3. Recommend a simple stack with reasons and meaningful alternatives. Obtain stack approval before writing the brief.
4. Write .dreamers/atlas/project-brief.md from [the brief template](../../dreamers/templates/project-brief.md). Present it for approval before repository bootstrap.
5. Follow [bootstrap rules](../../dreamers/refs/project-bootstrap.md). For a new GitHub repo, ask visibility before gh repo create. Work in the approved project location.
6. Write dependency-ordered milestones under .dreamers/plans/feature-<slug>/ using [shell plans](../../dreamers/templates/shell-plan.md). Present for approval or revision; stop when approved. Shell plans need a resolved proposal before implementation: use /dreamers with the milestone as task context, or /dreamers-plan for detailed planning.
