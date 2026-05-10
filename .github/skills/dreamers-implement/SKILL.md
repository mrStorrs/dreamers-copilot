---
name: dreamers-implement
description: 'Implementation only — execute against an existing approved plan. Use when a plan already exists. Triggers: /dreamers-implement, implement this plan, start implementation, execute the plan.'
argument-hint: 'path/to/plan.md'
---

## Pre-flight reads

Read these refs once at startup (use the `view` tool, full file):
- `~/.copilot/dreamers/refs/git-workflow.md` — branching, commits, push discipline
- `~/.copilot/dreamers/refs/close-out.md` — retro and PR procedure

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

The prompt must include a path to the existing plan file. If none provided, stop and ask before proceeding — do not invent or skip the plan.

---

## MANDATORY first actions (in order)

1. **User Input Audit** — Review the entire conversation thread. For every suggestion, correction, preference, or constraint the user expressed, confirm it is explicitly addressed in the plan file. If anything is missing, update the plan to incorporate it before proceeding.
2. **Plan quality self-check (MANDATORY, replaces former Gate 2)** — verify the plan against:
   - [ ] Filenames follow `plan-{slug}[-a..n].md`
   - [ ] Non-trivial features have an umbrella + sub-plans (not monolithic)
   - [ ] Every sub-plan / standalone has measurable Acceptance Criteria
   - [ ] Every sub-plan / standalone has Test Cases (Given/When/Then) for non-trivial cases
   - [ ] Every sub-plan / standalone has Design Decisions in the structured format
   - [ ] Every sub-plan / standalone has a Rollback Boundary
   - [ ] Every sub-plan / standalone has a Status field (Draft / Active / Completed / Superseded)
   - [ ] Plans reference only files/paths that exist (no invented paths)
   - [ ] Sub-plan splits at natural seams
   - [ ] No sub-plan's testability depends on a sibling not yet shipped
   - [ ] No code snippets (exception: interface/type contracts only)
   
   Any failure → halt and prompt the user with the specific item(s) that failed.
3. **Read `.dreamers/improvements.md`** if it exists. For every open improvement item, action it or explicitly re-defer.
4. **Implementation start approval gate (MANDATORY)** — Even though the user provided the plan path, present a final gate before implementation begins. Present this block in chat:

   ```
   **Plan ready for implementation:**

   - `path/to/plan.md` — [one-line summary from plan's Summary section]
   - (list any sub-plans if applicable, each with one-line summary)

   Reply "Approved — start implementation" to begin, or describe any corrections needed.
   ```

   Call `ask_user` with choice `["Approved — start implementation"]` and allow inline freeform corrections. If User Input Audit (step 1) updated the plan, this gate gives the user a chance to re-confirm before any agent edits code.

   - Approval → proceed to step 5
   - Corrections → revise the plan file(s), re-run quality self-check, re-present this gate. Loop until approved.

5. **Delegate branch setup to Bolt** via `task(agent_type: "bolt", mode: "sync")` per `git-workflow.md`:
   - Detect default branch (canonical two-step: `git symbolic-ref refs/remotes/origin/HEAD` with `gh repo view` fallback)
   - `git fetch origin && git checkout <DEFAULT> && git pull`
   - Cut `feat/d<N>-<name>` from default
   - Archive prior feature's plan files if its PR is merged (move to `.dreamers/plans/archive/`, never delete)
6. **Do not write or edit production files yourself.** All implementation goes through agents.

---

## Per sub-plan loop (sequential, fix-on-sight)

For each sub-plan:

1. **Forge** — `task(agent_type: "forge", mode: "sync")` — implements against the sub-plan. Forge stages, type-checks, signals done with the implementation chat output.
2. **Sentinel** — `task(agent_type: "sentinel", mode: "sync")` — fix-on-sight review in production-code lane. Severity-graded fixes-applied list. Type-checks after fixes.
3. **Probe** — `task(agent_type: "probe", mode: "sync")` — fix-on-sight in test-files lane. Writes AC coverage matrix, runbook, bugs.
4. **If Probe surfaces a production bug** — re-spawn Sentinel scoped to that bug, then re-run Probe.
5. **User-testing-required check** — if `yes`, then pause by calling the `request_info` tool. Required content and resume rules are defined in `~/.copilot/dreamers/refs/sub-plan-loop.md` → "User testing pause rule" — follow it exactly (sub-plan ID + path, build/distribution per `.github/instructions/build.instructions.md` if present — otherwise ask the user to build/distribute, what changed, step-by-step test steps from AC + Probe Given/When/Then, known limitations, approve / `Bug: <desc>` response format). Run only the build/distribution steps that `build.instructions.md` explicitly authorises; surface everything else to the user.
6. **Bolt commits the sub-plan** — single commit per sub-plan; commit message per `.github/instructions/git.instructions.md` plus the pipeline-specific `Plan: <slug>` body reference.
7. **`/dreamers-plan-verify`** — invoke with next sub-plan path. Halt if drift; continue if no change.

---

## Standalone-plan route

If the plan is a single standalone (no sub-plans), run the loop body once and skip plan-verify (no next sub-plan to verify).

---

## End of session

1. **`/dreamers-simplify`** — Hone fix-on-sight + project-defined test/lint pass.
2. **Echo** — `task(agent_type: "echo", mode: "sync")`. Pass: plan path, changed-files list, one-paragraph Sentinel summary, diff base.
3. **Close-out** per `close-out.md`: retro, final commit, Bolt opens PR via `gh pr create` with body from `pr-description.md` template.
4. **Issue close (if applicable)** via Bolt.
5. **`improvements.md` milestone-close append**.

### Push discipline
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out.

### Agent self-checks
The orchestrator does not re-read agent artifacts. Per `~/.copilot/dreamers/refs/quality-gates.md`, each agent self-asserts its DoD before signaling done.
