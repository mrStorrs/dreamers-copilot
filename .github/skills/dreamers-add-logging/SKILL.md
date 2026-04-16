---
name: dreamers-add-logging
description: 'Add comprehensive production-grade logging to the project. Triggers: /dreamers-add-logging, add logging, improve logging, logging pass.'
---

Add comprehensive, production-grade logging to the project. Work through the phases in order. Do not touch code until the user approves the audit findings.

Read these refs:
- `~/.copilot/dreamers/refs/git-workflow.md`
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

---

## Phase 1 — Audit (do this directly, no agents)

**Stack detection:**
- Read `CLAUDE.md` (project-level), `package.json`, `build.gradle`, `pyproject.toml`, `go.mod` — whatever exists
- Identify: language(s), runtime, existing dependencies, package manager

**Existing logging inventory:**
- Search for `console.log`, `console.error`, `console.warn`, `print(`, `println(`, `Log.d(`, `Log.e(`, `logger.`, `logging.` and any existing logging framework imports
- Note: how many, where, what kind (debug noise vs. genuine signal)

**Key instrumentation areas:**
- Identify: app entry point / startup, server/service init, route handlers or API endpoints, database access layer, external API/HTTP calls, auth flows, background jobs or workers, top-level error handlers

**Framework recommendation:**
Based on detected stack, recommend one framework. Common mappings:
- Node.js / TypeScript → **pino** or **winston**
- Python → **structlog** or **loguru**
- Kotlin / Android → **Timber**
- Go → **zap** or **slog**
- Other → surface to user and ask

**Surface to user:**
1. Detected stack and package manager
2. Existing logging found (count, locations, quality assessment)
3. Recommended framework + rationale + rejected alternative(s)
4. Areas that will be instrumented
5. Ask: **"Does this look right? Approve or tell me what to adjust."**

Do not proceed until the user explicitly approves.

---

## Phase 2 — Branch setup

```
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
git checkout "$DEFAULT_BRANCH" && git pull origin "$DEFAULT_BRANCH"
git checkout -b chore/add-logging
```

---

## Phase 3 — Forge implementation

Invoke Forge (follow delegation.md). Forge's task:

- Install the approved framework using the project's package manager
- Set up central logger module with dev (pretty-printed) and prod (structured JSON) modes
- Follow `~/.copilot/dreamers/templates/logging-standards.md`
- Replace existing raw logging with appropriate log level calls
- Add logging to instrumentation areas from Phase 1

Single commit: `chore: add structured logging with [framework name]`

---

## Phase 4 — Sentinel review

Invoke Sentinel (follow delegation.md). Focus areas:
- Log calls exposing PII, credentials, or sensitive data
- Log calls in tight loops or hot paths at INFO level
- Missing stack traces on ERROR-level catches
- Inconsistent log levels
- Raw print/console calls Forge missed

Re-review only if findings include critical or high severity.

---

## Phase 5 — PR (Bolt)

Invoke **Bolt** to handle the mechanical close-out:
- Push the branch
- Open PR with title: `chore: add structured logging with [framework name]`
- Body: framework chosen, environments configured, areas instrumented, noise removed

Bolt reports the PR URL.

