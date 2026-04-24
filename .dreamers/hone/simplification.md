# Simplification Pass

**Branch:** feat/d1-dreamers-system-cleanup
**Diff base:** master

## Files edited

| File | Change | Rationale |
|---|---|---|
| `.github/agents/nova.agent.md` | Merged three "Nova does NOT…" sentences into two | Middle sentence's prohibitions folded into the first; no information lost |
| `.github/copilot-instructions.dreamers.md` | `sub-agent` → `subagent` (both instances) | Normalized to match all other files on the branch |
| `.github/skills/dreamers-simplify/SKILL.md` | Trimmed "Hone will:" list from 5 items to 3 | Items 2 and 3 restated hone.agent.md constraints verbatim |
| `.github/skills/dreamers-full/SKILL.md` | "Before PR creation" paragraph compressed to one sentence | Pipeline route already shows `dreamers-simplify`; only the non-obvious constraint is kept |
| `.github/skills/dreamers-implement/SKILL.md` | Same compression; kept "not just the latest sub-plan" qualifier | Qualifier adds context not visible from the pipeline diagram |
| `.github/dreamers/refs/sub-plan-loop.md` | Two-sentence `dreamers-simplify` note merged into one | No information lost |

## Simplifications not made

| Candidate | Reason skipped |
|---|---|
| Merge `dreamers-cleanup-comments-branch` pre-conditions into its parent skill | Behavior change risk — pre-conditions are discrete guard steps |
| Remove Atlas/orchestrator dual-naming | Would require cross-file coordination across out-of-scope files |

## Observations for Sentinel / Forge

1. **`dreamers-simplify/SKILL.md` step 3**: uses `git remote show origin | grep 'HEAD branch'` — differs from `git-workflow.md`'s canonical two-step detection with `gh repo view` fallback. Breaks if `origin` is absent.
2. **`dreamers-cleanup-comments-branch/SKILL.md`**: `git diff --name-only "origin/$DEFAULT_BRANCH"...HEAD` assumes a fetched `origin` remote. Sentinel should confirm the pre-condition is always satisfied before this skill runs.
3. **`nova.agent.md` frontmatter description**: "Fire-and-forget, artifact-in/artifact-out" — Nova is invoked with `wait: true`; description may mislead.
4. **`"Atlas"` vs `"orchestrator"`**: used interchangeably across files. If Atlas is a named agent, `atlas.agent.md` is missing. Sentinel should confirm canonical naming.
5. **`planning-protocol.md` line ~40**: embeds `grep -r "ComponentName" app/` — React-specific path, fails silently in non-React projects.
6. **`dreamers-fix/SKILL.md`**: Firebase/mobile distribution rule embedded in a general skill; should live in project-level `CLAUDE.md`.
