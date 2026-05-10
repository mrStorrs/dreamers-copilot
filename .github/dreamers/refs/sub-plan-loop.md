# Sub-plan Loop (multi-part features)

For features with an umbrella plan + sub-plans, loop through each sub-plan sequentially:

```
[Planning phase — umbrella + all sub-plans approved]
  → [for each sub-plan]:
      Forge → Sentinel (fix-on-sight) → Probe (fix-on-sight in test files)
      → if "User testing required: yes":
            build/distribute per `.github/instructions/build.instructions.md` (or ask user if file absent or instructions are unclear)
            → call `request_info` (PAUSE) → wait for user sign-off
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
- `yes` — then **pause the pipeline by calling the `request_info` tool**. Do not commit, invoke `/dreamers-plan-verify`, or start the next sub-plan until the user explicitly approves via the `request_info` response.

### `request_info` content (mandatory)

The `request_info` call MUST include every item below — do not abbreviate or omit. The user reads only what is in this prompt; anything missing means they cannot test:

- **Sub-plan being tested:** ID + path (e.g. `plan-{slug}-a` → `.dreamers/plans/plan-{slug}-a.md`).
- **Build distribution details:** check for `.github/instructions/build.instructions.md` at the project root.
  - **If present:** follow it exactly — it is the project's authoritative build/distribution playbook. Execute only the steps it explicitly authorises the orchestrator to run. Surface every user-action step (install on device, launch app, open URL, version/build number to verify) verbatim in the `request_info` payload so the user knows what to do.
  - **If absent:** state plainly that there is no `build.instructions.md` and ask the user to either (a) build/distribute the test build themselves and confirm when ready, or (b) provide the steps so a `build.instructions.md` can be created. Do not invent build steps and do not run unspecified commands.
- **What changed in this sub-plan:** 1–3 bullets summarising the user-visible behaviour delivered.
- **Step-by-step test steps:** numbered, concrete, reproducible. Derive directly from the sub-plan's Acceptance Criteria and Probe's Given/When/Then test cases. Each step states the action to take and the expected observation.
- **Known limitations / out-of-scope:** anything the user might try that this sub-plan deliberately doesn't cover, so they don't flag it as a bug.
- **How to respond:** instruct the user to reply with one of:
  - `Approved — continue` (orchestrator proceeds to the Bolt commit step)
  - `Bug: <description>` (orchestrator routes the bug to Sentinel, re-runs Probe, re-runs build/distribution per `build.instructions.md` — or asks the user again if the file is absent — then re-issues `request_info`)
  - Freeform notes / corrections are also accepted and treated as bugs unless clearly approving.

### Resume rules
- On `Approved — continue` → proceed to Bolt commit, then `/dreamers-plan-verify`, then next sub-plan.
- On any bug or correction → fix-and-re-test cycle: re-spawn Sentinel scoped to the bug → re-run Probe → re-run build/distribution per `.github/instructions/build.instructions.md` (or ask the user again if the file is absent) → re-call `request_info`. Do **not** commit until explicit approval is received. The orchestrator only runs build/distribution commands explicitly authorised by `build.instructions.md`; otherwise it surfaces them to the user.
