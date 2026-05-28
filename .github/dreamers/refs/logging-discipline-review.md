# Logging Discipline (reviewer lens)

When Sentinel reviews log calls in the diff:

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, treat it as the binding spec. Flag any log call that violates it.
2. **Else: surrounding-code conformity.** Compare added/changed log calls to existing calls in the same module and nearest neighbors. Flag mismatches in:
   - Logger library / import path (introduces a new logger where one already exists).
   - Level usage (e.g., ERROR for recoverable issues, INFO with full bodies).
   - Message format (structured fields vs interpolated strings, key naming, casing) that breaks local convention.
3. **Never-log violations are `security` severity.** Secrets, tokens, PII, or full request/response bodies in any log call → flag at `security` regardless of lens.

Severity mapping: never-log violation → `security`; library/format/level deviation → `maintainability`. Findings follow the format in `reviewer-findings-format` (Kernel).
