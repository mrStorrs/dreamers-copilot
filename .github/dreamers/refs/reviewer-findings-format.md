# Review artifact

Write exactly one .dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md file. Use the requested path when supplied. Existing artifacts are context, not the result of this run.

Include:
- Status: Approved (no findings), Findings reported (count), or Blocked (reason).
- Scope and review basis: approved proposal/plan or inferred intent.
- Findings: [critical|high|medium|low] [correctness|security|maintainability|test-coverage|simplicity] file:line — problem, evidence/impact, suggested fix.
- Verification coverage: required outcomes and the tests/manual checks that support them; identify gaps and weak assertions. Focused reviewers cover their assigned lens.
- Open questions and any unreviewed/blocked scope.
- Final section: **How could I make this code simpler?** Name a concrete alternative and rationale, or explain why no worthwhile simplification remains.

Avoid duplicate findings and empty all-clear tables. Distinguish defects from optional improvements and state broader refactor scope explicitly.

Return only status, counts, artifact path, and blockers/questions in chat. The caller reads the artifact and decides fixes. Reviewers may write this artifact only; no project edits, git changes, installs, or test runs.
