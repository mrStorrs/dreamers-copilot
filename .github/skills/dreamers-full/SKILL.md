---
name: dreamers-full
description: 'Full Dreamers pipeline: plan a feature, implement with agent delegation (fix-on-sight Sentinel/Probe/Hone), and ship. Use when starting a new feature or significant change from scratch. Triggers: /dreamers-full, full pipeline, plan and implement, new feature.'
---

## Pre-flight reads

Read these refs once at startup (use the `view` tool, full file):
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, push discipline
- `~/.copilot/dreamers/refs/close-out.md` — retro and PR procedure

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Phase 1 — Planning

Three-phase requirements conversation directly with the user.

### Phase 1a — Hash it out
1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question — use the `ask_user` tool one question at a time within a single round. Do not trickle questions across multiple message turns.
4. Wait for the user's responses before proceeding.

If the task is fully unambiguous, skip to Phase 1b with a brief "I understand the goal as: …" confirmation.

### Phase 1b — User Input Audit (gate)
Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it.

### Phase 1c — Approval gate
Present this proposal block in chat:

```
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…
```

Call `ask_user` with choice `["Approved"]` and allow inline freeform corrections in the same interaction. Treat any non-approval freeform response as corrections; revise and re-present until explicit approval.

### Phase 1d — Write plan files

Plan filenames follow `plan-{slug}.md` (umbrella or standalone) and `plan-{slug}-a.md`, `plan-{slug}-b.md`, … (sub-plans). No numeric prefix. Slug rules: lowercase, replace non-alphanumerics with single hyphen, trim, collapse repeats; if empty use `misc`. Plans live in `./.dreamers/plans/`.

Use templates as starting structure:
- `~/.copilot/dreamers/templates/plan-sub.md` — sub-plans and standalone plans
- `~/.copilot/dreamers/templates/plan-umbrella.md` — umbrella plans (only when decomposing)

**Each sub-plan must include:**
- `# Plan — {Short Title} ({Letter})`
- Metadata: Owner, Date, Scope, Parent (link to umbrella), Depends-on (prior sub-plans if any), Status (Draft/Active/Completed/Superseded), User-testing-required (yes/no), Links
- Sections: Summary, Scope/Non-goals, Constraints, Design Decisions, Acceptance Criteria, Test Cases for Probe (Given/When/Then for non-trivial), Rollback boundary, Risks/Mitigations

**Design Decisions format** (one entry per significant choice):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User testing required:** `yes` if a human must manually verify before next sub-plan begins (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Umbrella plans (`plan-{slug}.md`) include:** Summary, Problem/Motivation, Scope/Non-goals (shared), Sub-plans (ordered table: ID | File | Summary | Status), Constraints (shared), End-to-end Acceptance Criteria, Rollback/Observability strategy.

**Plans MUST NOT include code snippets.** One exception: interface and type contracts where the signature itself is the design decision.

### Phase 1e — Plan quality self-check (MANDATORY, replaces former Gate 2)

Before exiting Phase 1, verify the plan(s) against:
- [ ] Filenames follow `plan-{slug}[-a..n].md`
- [ ] Non-trivial features have an umbrella + sub-plans (not monolithic)
- [ ] Every sub-plan / standalone has measurable Acceptance Criteria
- [ ] Every sub-plan / standalone has Test Cases (Given/When/Then) for non-trivial cases
- [ ] Every sub-plan / standalone has Design Decisions in the structured format
- [ ] Every sub-plan / standalone has a Rollback Boundary
- [ ] Every sub-plan / standalone has a Status field (Draft / Active / Completed / Superseded)
- [ ] Plans reference only files/paths that exist (no invented paths)
- [ ] Sub-plan splits at natural seams (not arbitrary line-count cuts)
- [ ] No sub-plan's testability depends on a sibling not yet shipped
- [ ] No code snippets (exception: interface/type contracts only)

Any failure → halt and prompt the user with the specific item(s) that failed.

### Component usage check (mandatory)
When a plan modifies a shared component, run `grep -r "ComponentName" .` (substitute the project's actual source root from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Citation accuracy
Before citing the behavior of any existing artifact in the plan, read and verify the source. Do not cite from memory.

### Phase 1f — Implementation start approval gate (MANDATORY)

Phase 1c approved the high-level goal. Phase 1f approves the **actual decomposed plan files** before any implementation work begins. The user must read the plan files and explicitly approve before Phase 2 starts.

Present this block in chat:

```
**Plans written and ready for review:**

- `path/to/plan-{slug}.md` — umbrella (if applicable)
- `path/to/plan-{slug}-a.md` — [one-line summary from the plan's Summary section]
- `path/to/plan-{slug}-b.md` — [one-line summary]
- ...

Please read the plan file(s) above. Reply "Approved — start implementation" to begin Phase 2, or describe any corrections needed.
```

Then call `ask_user` with choice `["Approved — start implementation"]` and allow inline freeform corrections.

**Looping behavior:**
- Approval → proceed to Phase 2
- Corrections → revise the relevant plan file(s) (or re-run Phase 1d if structural changes are needed), re-run Phase 1e quality check, then re-present Phase 1f. Loop until approved.

**Do not proceed to Phase 2 until the user explicitly approves the plan files at this gate.** The Phase 1c goal-level approval is not sufficient — the user must approve the actual plan content.

---

## Phase 2 — Implementation

### MANDATORY first actions (in order)

1. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer with a note. (`improvements.md` milestone-start read.)
2. **Delegate branch setup to Bolt** via `task(agent_type: "bolt", mode: "sync")` per `git-workflow.md`:
   - Detect default branch (canonical two-step: `git symbolic-ref refs/remotes/origin/HEAD` with `gh repo view` fallback)
   - `git fetch origin && git checkout <DEFAULT> && git pull`
   - Cut `feat/d<N>-<name>` from default
   - Clean up prior feature's plan files if its PR is merged (`gh pr list --state merged`)
   - Do not proceed until Bolt confirms.
3. **Do not write or edit production files yourself.** All implementation goes through the agents below.

### Per sub-plan loop (sequential, fix-on-sight)

For each sub-plan:

1. **Forge** — `task(agent_type: "forge", mode: "sync")` — implements the sub-plan against its plan file. Forge stages with `git add`, type-checks, signals done with the implementation chat output.
2. **Sentinel** — `task(agent_type: "sentinel", mode: "sync")` — fix-on-sight review in production-code lane. Reports severity-graded fixes-applied list. Type-checks after fixes.
3. **Probe** — `task(agent_type: "probe", mode: "sync")` — fix-on-sight in test-files lane. Writes AC coverage matrix to `test-plan.md`, exact commands to `runbook.md`, bug records to `bugs.md`.
4. **If Probe surfaces a production bug** — re-spawn Sentinel scoped to that bug, then re-run Probe. Production bugs belong to Sentinel's lane (test-and-fix style behavior emerges from sequential Sentinel→Probe→Sentinel routing).
5. **User-testing-required check** — if the sub-plan's `User testing required: yes`**pause by calling the `request_info` tool**. The call must include every item required by `~/.copilot/dreamers/refs/sub-plan-loop.md` → "User testing pause rule" → "`request_info` content (mandatory)" — sub-plan ID + path, build/distribution per `.github/instructions/build.instructions.md` (if present; otherwise ask the user to build/distribute), what changed, step-by-step test steps derived from the sub-plan's Acceptance Criteria and Probe's Given/When/Then cases, known limitations, and the approve / `Bug: <desc>` response format. Run only the build/distribution steps `build.instructions.md` explicitly authorises; surface user-action steps verbatim. Follow the resume rules in that ref: on approval proceed to step 6; **on any bug, re-spawn only Forge scoped to the reported bug (no Sentinel, no Probe — the user is the test layer for user-testing rounds) → re-build/distribute per the same file-or-ask rule → re-call `request_info` with refreshed test steps that verify the fix (do not commit until explicit approval).**
6. **Bolt commits the sub-plan** — `task(agent_type: "bolt", mode: "sync")` — single commit covering all staged changes for this sub-plan. Commit message per `.github/instructions/git.instructions.md`; reference the plan in the body (`Plan: plan-{slug}-a`). One commit per sub-plan.
7. **`/dreamers-plan-verify`** — invoke the wrapper skill with the next sub-plan's path. If `Drift detected — halt`, surface drift items to user and halt. If `No change — proceed`, continue to next sub-plan.

### Agent self-checks (no orchestrator-side gates 3a/3b/4)

The orchestrator does not re-read agent artifacts. Each agent self-asserts its DoD before signaling done (per `~/.copilot/dreamers/refs/quality-gates.md`). The orchestrator only confirms the agent signaled completion. If an agent's chat output is missing required content, re-prompt that agent with the specific gap.

### Preservation behaviors

The orchestrator preserves throughout Phase 2:
- Branch setup discipline (canonical default detection, `feat/<slug>` cut, prior-merged plan cleanup) — handled by Bolt at startup
- Single commit per sub-plan — handled by Bolt at step 6
- **Single push exactly once at PR** — happens in Phase 3 close-out only; never push between sub-plans
- User-testing-required pause — step 5
- Component-usage grep — Phase 1d as part of finalizing scope; agents verify in their own work
- `improvements.md` milestone-start read — first action in Phase 2

---

## Phase 3 — End of session

After all sub-plans complete:

1. **`/dreamers-simplify`** — invoke the skill. It runs Hone (fix-on-sight, branch-diff scope, behavior-preserving) + a single project-defined test/lint pass.
2. **Echo** — `task(agent_type: "echo", mode: "sync")` to update project docs. Pass:
   - Plan file path
   - List of changed files (`git diff --name-only origin/<DEFAULT>...HEAD`)
   - One-paragraph Sentinel summary (concatenated from sub-plan Sentinel chat outputs)
   - Default branch name as diff base
3. **Close-out** — follow `~/.copilot/dreamers/refs/close-out.md`: write retro, final commit if any remaining changes (e.g., Echo's doc updates), Bolt opens PR via `gh pr create` with body drafted from `~/.copilot/dreamers/templates/pr-description.md`.
4. **Issue close (if applicable)** — if the original task referenced a GitHub issue number/URL: pass `gh issue close <number> --comment "Resolved in <PR URL>"` to Bolt.
5. **`improvements.md` milestone-close append** — append new improvement suggestions from this cycle's retro to `.dreamers/improvements.md`.

### Push discipline
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out (per `git-workflow.md`).
