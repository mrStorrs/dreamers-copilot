# Regression Analysis — dreamers-full approval/orchestrator cleanup

## Why wasn't this caught?
- No Probe coverage existed for docs-only workflow contracts in the shipped `.github` Dreamers files.
- The prior gap was at the documentation/regression layer: no deterministic content check asserted that the approval gate kept a one-click `Approved` path while accepting inline corrections, and no scoped terminology sweep asserted removal of whole-word `Atlas` references from committed `.github` docs.

## What was added?
- `TC-1` through `TC-5` in `C:\projects-gh\dreamers-copilot\.dreamers\probe\test-plan.md`
- Matching deterministic verification commands in `C:\projects-gh\dreamers-copilot\.dreamers\probe\runbook.md`

## What else might be missing?
- Future Dreamers doc changes can regress again unless content checks like these are repeated for approval-gate wording and orchestrator terminology.
- Planning should stop listing nonexistent committed files such as `hone.agent.md`; that kind of scope noise weakens AC verification.
- Unscoped local `.dreamers/` artifacts still mention `Atlas` by design; if the product decision is to retire the term repo-wide later, that needs a separate plan.
