# Logging

1. Use the consuming project's .github/instructions/logging.instructions.md when present. Otherwise match the logger library, levels, and message format in the same module or its nearest neighbors. Do not introduce a second logger alongside an existing one.
2. Never log secrets, credentials, tokens, PII, or complete request/response bodies. Sanitize arguments, configuration, URLs, return values, and errors before logging.
3. Record useful events at the project's established levels. Avoid noisy loop logging and redundant entry/exit calls that add no diagnostic value.
4. Keep logging changes within the approved scope. Leave unrelated logging alone unless an accepted finding requires a change.
5. If neither project instructions nor surrounding code provide a usable convention, ask one focused question before adding log calls.
