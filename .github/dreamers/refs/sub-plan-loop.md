# Sub-plan Loop (multi-part features)

For features with an umbrella plan + sub-plans, loop through each sub-plan sequentially:

```
[Planning phase — umbrella + all sub-plans approved]
  → [for each sub-plan]:
      Forge → Sentinel → Probe → Gate 3b → Gate 4
      → if "User testing required: yes":
            distribute build → PAUSE → wait for user sign-off
      → commit sub-plan
      → Nova (subagent, Opus — re-verify remaining plan)
      → [repeat for next sub-plan]
  → [all sub-plans done] → dreamers-simplify (Hone; full branch diff) → PR opened → user reviews + merges
```

After all sub-plan cycles complete, run `dreamers-simplify` before opening the PR — it runs Hone on the full feature-branch diff, then a final Sentinel + Probe pass internally.

## Sub-plan commit and PR rules
- Forge and Probe stage changes with `git add` throughout the pipeline but do **not** commit.
- After Probe passes (and user sign-off, if required), **Bolt makes exactly one commit** covering all staged changes for this sub-plan — this is the only commit for the sub-plan.
- The PR is opened **only once, after all sub-plans are complete**. The PR diff covers the entire feature.

## Inter-sub-plan boundary rule
After each sub-plan's pipeline completes (Forge + Sentinel + Probe all pass), invoke Nova as a true subagent (Opus) with:
- Absolute paths to: `forge/implementation.md`, `probe/bugs.md`, `probe/test-plan.md`, `sentinel/findings.md`
- Which sub-plan was just completed
- The full list of remaining sub-plan files to re-verify

## User testing pause rule
Check the completed sub-plan's `User testing required` field:
- `no` — commit immediately, invoke Nova re-verify, continue without pausing.
- `yes` — distribute a build per the project's distribution method (check the project-level `CLAUDE.md` Distribution section), notify the user, and **pause the pipeline**. Do not invoke Nova or start the next sub-plan until the user explicitly gives the go-ahead.
