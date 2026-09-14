---
applyTo: "**"
---

# Dreamers

- The main agent implements, validates, fixes findings, and performs git work. Skills run in that same context; the outermost skill owns progress and approvals.
- Delegate only the role a skill calls for: Vigil for code review, Echo for docs, Sage for research. Sentinel/Probe/Hone require explicit user selection. Forge/Nova are user-entered personas.
- Pass subagents the task, scope, approved proposal/plan or inferred intent, constraints, prior artifacts, validation results, and output path. Pass paths, not repeated document contents. The parent owns the todo. Read returned artifacts before acting; on failure, resume from completed work.
- Proposal approval in /dreamers authorizes immediate implementation. Detailed plans are optional. Never add another implementation-start gate.
- Keep proposals/plans, transcripts, reviews, retros, and improvements under gitignored .dreamers/. Keep test-benchmarks.md and defered.md at the project root.
- On an explicit user deferral, append date, source/artifact, suggestion, proposed action, and reason to defered.md; create with "# Deferred Suggestions" if absent. Stage it with related changes.
- Read linked rules only when needed and only once per context. Relative links resolve from the file containing them, both in .github/ and the installed Copilot home.

[Code laws](dreamers.laws.instructions.md) and [comment rules](dreamers.comment-rules.instructions.md) apply when coding or reviewing. Workflow-specific rules stay in their owning skill.
