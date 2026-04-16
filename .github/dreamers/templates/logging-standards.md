# Logging Standards

Shared standard used by Forge (when writing log calls) and Sentinel (when reviewing them).

---

## Log levels

### ERROR
Unhandled or unexpected failures only. Always include the full error object and stack trace. Never swallow an error silently at this level.

### WARN
Recoverable issues, unexpected-but-handled states, and deprecations. The system continues operating, but something worth investigating occurred.

### INFO
Lifecycle and business signal. Use for:
- App startup — key resolved config values (never secrets), framework version, environment
- App shutdown / service teardown
- Incoming requests — method, path, response status, duration
- Outbound API/HTTP calls — target service, endpoint, response status, duration
- Auth events — login, logout, token refresh, auth failures (never log credentials or tokens)
- Key business events that a product owner would care about

### DEBUG
High-traceability internal flow. Be liberal — the goal is that enabling DEBUG gives a complete picture of what the code did and why, without needing a debugger attached. Log at DEBUG for:
- Function entry/exit on non-trivial functions — sanitized args in, return value out
- Every branch taken in conditional logic that affects a business outcome
- Repository / data-layer calls — what was queried, row/record count returned
- Cache hits and misses
- Background job / worker lifecycle — started, iteration count, items processed, finished
- Retry attempts — attempt number, delay, reason
- State transitions in state machines or multi-step flows
- Middleware pipeline — each middleware entered and exited
- Config values resolved at startup (non-secret)

High-frequency loop internals are **allowed** at DEBUG if they add traceability value. Mark them with a `// high-freq` comment so Sentinel can assess the noise risk.

---

## Never log (hard rules — no exceptions)

- Passwords, API keys, tokens, secrets of any kind
- PII: email addresses, phone numbers, names, addresses, payment data
- Full request or response bodies (log status codes and durations instead)
