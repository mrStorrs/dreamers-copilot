# Logging standards

Use the project's logger and formatting conventions. Apply these levels:

| Level | Use |
| --- | --- |
| ERROR | Unexpected/unhandled failures; include the sanitized error and stack. |
| WARN | Recoverable problems, unexpected handled states, deprecations. |
| INFO | Startup/shutdown, business/auth events, requests and outbound calls with method/endpoint/status/duration. |
| DEBUG | Useful internal flow: non-trivial entry/exit, business branches, queries/counts, cache results, jobs, retries, state transitions, middleware, resolved configuration. |

DEBUG should explain what happened without a debugger. High-frequency details need real diagnostic value and a high-freq comment so review can assess noise.

Never log secrets, credentials, tokens, PII, or complete request/response bodies. Sanitize args, return values, config, endpoints, and errors before logging.
