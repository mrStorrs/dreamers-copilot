# Sub-plan Loop (multi-part features)

For features with an umbrella plan + sub-plans, loop through each sub-plan sequentially:

```
[Planning phase — umbrella + all sub-plans approved]
  → [for each sub-plan]:
      Forge → Sentinel (fix-on-sight) → Probe (fix-on-sight in test files)
      → if "User testing required: yes":
            distribute build → PAUSE → wait for user sign-off
      → commit sub-plan
      → /dreamers-plan-verify (lightweight Nova verify mode)
      → [repeat for next sub-plan]
  → [all sub-plans done] → /dreamers-simplify (Hone fix-on-sight + project-defined test/lint pass) → PR opened → user reviews + merges
```

Per sub-plan: 3 sequential agent spawns (Forge → Sentinel → Probe) + 1 inline `/dreamers-plan-verify`. Sentinel and Probe are fix-on-sight in their respective lanes, so no findings-JSON round-trip and no separate Forge fix cycle.

## Sub-plan commit and PR rules
- Forge, Sentinel, Probe, Hone all stage edits with `git add` throughout the pipeline but do **not** commit.
- After Probe passes (and user sign-off, if required), **Bolt makes exactly one commit** covering all staged changes for this sub-plan — this is the only commit for the sub-plan.
- The PR is opened **only once, after all sub-plans are complete**. The PR diff covers the entire feature.

## Inter-sub-plan boundary rule

After each sub-plan's pipeline completes (Forge + Sentinel + Probe all signal done), the orchestrator invokes `/dreamers-plan-verify` (which spawns Nova in `verify` mode) with:
- The next sub-plan file path
- The just-completed sub-plan's commit hash (Nova reads `git diff <commit>` and `git log <commit> -1 --format=%B`)
- Surviving Probe artifacts (`test-plan.md`, `bugs.md`, `regression-analysis.md` if present)

`/dreamers-plan-verify` returns one of:
- `No change — proceed` → orchestrator moves to next sub-plan
- `Drift detected — halt` → orchestrator surfaces drift items to user; user can request escalation to Nova `replan` mode if recovery is needed

## Production bug found by Probe

If Probe surfaces a production bug after Sentinel ran, the orchestrator spawns Sentinel again scoped to the bug (Sentinel is the production-fix lane), then re-runs Probe. This rare path keeps lanes clean while handling the edge case.

## User testing pause rule
Check the completed sub-plan's `User testing required` field:
- `no` — commit immediately, invoke `/dreamers-plan-verify`, continue without pausing.
- `yes` — distribute a build per the project's distribution method (check the project-level `.github/copilot-instructions.md` Distribution section), notify the user, and **pause the pipeline**. Do not invoke `/dreamers-plan-verify` or start the next sub-plan until the user explicitly gives the go-ahead.
