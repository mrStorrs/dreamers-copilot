---
name: dreamers-test
description: "Standalone focused Vigil review (test coverage audit). Read-only — reports Vigil's findings for AC coverage, layer audit, edge cases, and regression risks. No auto-fix. Triggers: /dreamers-test, test coverage audit, audit tests, check test gaps."
argument-hint: '[--branch] [--paths <glob>] [--all]'
---

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Echo uses the sole prompt defined in `/dreamers-docs`. All other `task()` invocations MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Scope adherence:** edit only files in the task or plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System
```
</dreamers-kernel>

<testing-mandate>
## Plan template
Plans use Goal and Acceptance criteria, matching GitHub issue proposals. Choose appropriate test layers from the observable outcomes; layer annotations are not required in plans.

## Coverage requirement (every plan)

Implementation tests must cover the following whenever applicable to the work:

**Unit layer**
- Each significant function, method, or class in isolation.
- All branches: happy path, edge cases (boundary values, empty/null/max), negative cases (invalid input, error states).
- Any pure logic that does not require a real device, network, or database.

**Integration layer**
- Interactions between layers: repository ↔ data source, ViewModel ↔ repository, service ↔ external API.
- Database reads/writes (real or in-memory, not mocked).
- Auth flows end-to-end within the backend.
- Cloud function triggers and side-effects.

**UI / E2E layer**
- Full user journeys through the UI: screen load → interaction → outcome visible on screen.
- Navigation flows between screens.
- Error and empty states rendered correctly in the UI.
- Any flow that requires a real device or emulator.
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), verify the changed navigation through E2E coverage. Probe checks this in the layer audit.

If a layer cannot be covered automatically (e.g., camera permission flows), put the manual steps, expected result, and reason under the relevant AC; set `User-testing-required: yes`.

## Test benchmarks

Keep `./test-benchmarks.md` at the project root and commit it to version control.

- If the file is absent, create it after the first successful test run. Include only a Markdown table with `Command`, `Last Run`, and `Recommended Timeout`, in that order. Use the template below.
- For each successful run, add or update the row for its command. Record the latest successful duration in `Last Run` and set `Recommended Timeout` to `max(2 × last run, 30s)`. Use an existing command's recommended timeout when preparing to run it.
- If the existing table has extra columns, ask the user before backfilling it. If approved, keep every command row and its recorded duration and timeout, map the duration column to `Last Run`, and remove the extra columns and explanatory prose. If declined, keep the existing layout and continue updating its timing fields after successful runs.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).
</testing-mandate>

$ARGUMENTS

---

## Argument parsing

Default scope (no flags): staged + unstaged changes.

- `--branch` — scope to feature-branch diff vs default:
  ```bash
  DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
  ```
- `--paths <glob>` — scope to files matching the glob.
- `--all` — entire codebase. Emit a chat warning before invoking; rare.

---

## Spawn Vigil

Assign Vigil a fresh handoff path using the review handoff contract in `~/.copilot/dreamers/refs/reviewer-findings-format.md`.

Invoke via the runtime's subagent-spawn mechanism:

```
agent_type: "vigil"
mode: "sync"
prompt:
  Context: Standalone focused Vigil audit via /dreamers-test. No plan binding (ad-hoc audit).
  Scope: <list of files from arg parsing above>
  Branch: <current feature branch>
  Default branch: <detected default>
  Focus: test coverage (AC matrix is N/A here — no plan binding; prioritize layer audit + edge cases + regression risks for the scope, while still reporting critical correctness/security/maintainability/simplicity findings if they appear).
  Handoff: <assigned path>. Attempt to save the full report there and return the same full report in your final reply.
```

## Output

Collect Vigil's complete handoff using the same contract. Report a missing handoff if neither copy is complete. Pass the accepted report to the user verbatim. Do NOT write any tests — this is a read-only audit. Surface any `Blocked` status or open questions for user follow-up.

If the user wants missing tests written from the findings, suggest: "Run `/dreamers-implement` with a plan that addresses these coverage gaps."
