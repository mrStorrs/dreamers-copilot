# Logging Discipline

When adding or modifying log calls during implementation:

1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, follow it. It is the binding spec; do not override with personal judgment.
2. **Else: match surrounding code.** Read existing log calls in the same module and nearest neighbors. Match:
   - Logger library / import path (do not introduce a new logger).
   - Level conventions actually in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).
   - Never-log values inferred from existing patterns (secrets, tokens, PII, full request/response bodies).
3. **Neither yields a clear answer** → raise an open question via `request_information` rather than guessing.

Do not add log calls outside the plan's scope as while-I'm-here cleanup. If the plan does not call for new logging, leave existing logging untouched unless a finding requires a change.
