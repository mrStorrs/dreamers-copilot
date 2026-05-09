# Implementation

## Why

Probe was leaking AC labels (`// AC-3:`), section dividers, and what-restating comments into test files because neither the global nor repo-local Probe definition contained comment rules. Repo-local Sentinel had no "Code comment review" block, so violations were never flagged at review time.

## Files Changed

| File | Location | Reason |
|------|----------|--------|
| `C:\Users\cjsto\.claude\agents\probe.md` | Global (outside repo) | Added `## Code comment rules (strict)` section, inlined (mirrors Forge's global structure), inserted before `## Git commit conventions (mandatory)` |
| `.github/agents/probe.agent.md` | Repo-local | Added `## Code comment rules (strict)` section referencing `comment-rules.md`, with Probe-specific reinforcement, inserted before `## Git staging discipline (non-negotiable)` |
| `.github/agents/sentinel.agent.md` | Repo-local | (a) Added `### Code comment review (mandatory)` section after `### Logging review (mandatory)` and before `### Review checklist`; (b) Appended code-comments line to the Review checklist |

## Files Read for Context

- `C:\Users\cjsto\.claude\agents\probe.md`
- `.github/agents/probe.agent.md`
- `.github/agents/sentinel.agent.md`

## How to Run

Not applicable — markdown-only agent config.

## How to Test (Verification)

Re-read each of the three files and confirm:

1. **Global probe.md** — `## Code comment rules (strict)` block appears between the end of `## Probe role responsibilities (Tester)` and `## Git commit conventions (mandatory)`.
2. **Repo-local probe.agent.md** — `## Code comment rules (strict)` block appears between the end of `## Probe role responsibilities (Tester)` and `## Git staging discipline (non-negotiable)`.
3. **Repo-local sentinel.agent.md** — `### Code comment review (mandatory)` block appears after `### Logging review (mandatory)` and before `### Review checklist`; the Review checklist ends with the "Code comments" bullet.

## Git Status

Two files staged: `.github/agents/probe.agent.md`, `.github/agents/sentinel.agent.md`. The global file edit (`C:\Users\cjsto\.claude\agents\probe.md`) is outside the repo and is not tracked by git.

## Known Limitations / Follow-ups

None. No deferred AC items — this task had no acceptance criteria beyond the three structural edits.

## Sentinel Finding Fixes (S-01, S-02)

Applied after initial review:

- **S-01** (`sentinel.agent.md` line 130): Changed `below` to `above` in the Review checklist "Code comments" bullet — the "Code comment review" section sits above the checklist, not below it.
- **S-02** (`probe.agent.md` after line 61): Added two missing prohibition bullets to the "Code comment rules (strict)" Probe-specific reinforcement list: (1) no redundant JSDoc/KDoc on test helpers/fixtures; (2) no spec-rationalization comments in tests.
