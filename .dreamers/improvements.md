# Improvements

Ongoing improvement suggestions from retros. Review at each milestone start.

---

## D1 — Dreamers System Cleanup (2026-04-17)

1. **sentinel.agent.md** — Add an explicit JSON output example and hard rejection constraint to the findings format section; agents wrote prose in multiple D1 cycles despite the JSON schema being present.
2. **hone.agent.md** — Add `New-Item -ItemType Directory -Force -Path .dreamers/hone | Out-Null` as an explicit pre-write step before `simplification.md` is written; Hone stalled waiting for the orchestrator to create the directory.
3. **dreamers-simplify/SKILL.md** — Document the no-remote/no-gh-cli fallback: ask the user to confirm the default branch name rather than silently defaulting to `main`.
4. **Platform alignment sub-plans** — Include an explicit POSIX sweep (`grep -r '2>/dev/null\|mkdir -p\|rm -rf' .github/`) as a required scope-gathering step to catch POSIX residue before Probe does.
