---
name: dreamers
description: 'Deliver a task, approved plan(s), or manifest through shared workflow refs for planning, implementation, review, user testing, docs, and PR. Empty/help input returns read-only guidance. Triggers: /dreamers, plan and implement, new feature, ship a feature.'
argument-hint: '<help | task description> | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Route input

Empty input, `help`, `--help`, or `-h`: use the embedded `help-workflow` below, return its guidance, and stop before inspecting or changing repository, git, mailbox, or external state.

Use the embedded workflow blocks below when their phases begin, with each phase's input. Each block's write restrictions and exit apply only to that phase. Keep ownership of the todo, gates, review counts, and delivery state; do not invoke other skills or load their `SKILL.md` files.

For delivery, keep one todo covering planning/start approval or artifact resolution, implementation/tests, review, user testing, docs, and close-out. Follow `Delivery continuation` in `dreamers.instructions.md` across follow-ups; resume the pending phase instead of repeating setup. Apply `dreamers-kernel` and complete `git-workflow` startup verification before reading any `.dreamers/` files.

| Input | Route |
|---|---|
| Task description | Phase 1, then the implementation-start gate. |
| Plan path(s) | Resolve and read the plans in supplied order; skip Phase 1 and its start gate. |
| `manifest.md` | Resolve and read the manifest; capture its plan sequence and shared context; skip Phase 1 and its start gate. |

Treat `.md` path arguments, including `feature-<slug>/plan-NN-<name>.md` and `feature-<slug>/manifest.md`, as artifact input. Resolve feature-relative paths under `.dreamers/plans/`. Unrecognized input: halt and ask for a task, plan path, manifest, or help.

Supplied artifacts are implementation authorization: do not re-plan, replace them, or ask to start. 

## Phase 1: Planning and start approval (task input only)

1. Execute the embedded `planning-workflow` below with the task input; capture the returned plan paths.
2. Validate the plans artifacts were created. Present paths, implementation scope, test intent, and the ship-strategy recommendation when multiple plans will run.
3. Use `request_information`:
   - Single plan: `Approved — start implementation` / `Revise plan` / `Halt` / `Other`.
   - Multiple plans: `Approved — start INCREMENTAL` / `Approved — start ATOMIC` / `Revise plan` / `Halt` / `Other`.
4. Capture the selected strategy. For revisions, apply unambiguous minor edits inline.

## Phase 2 — Per-plan cycle

Set up the feature branch once per `git-workflow`.  Process plans in sequence, carrying manifest shared context into implementation.

### Implement and review

1. Execute the embedded `implementation-workflow` below with the absolute plan path and manifest context, retaining the existing feature branch.
2. On success, execute the embedded `review-workflow` below with `--branch` and the absolute plan path once.
3. Apply findings and repeat implementation + the review workflow with `--vigil --branch` and the absolute plan path up to 3 times. Ask before major refactors; record deferred findings in root `defered.md`.
4. Halt temporarily on a blocked review or unresolved findings at the cap; report what remains. Ask user if you should proceed with another review, or closeout.

### User testing

Trigger when the plan requires manual verification, the change is user-facing, build/distribution is needed, reviewers request user validation, or the user asked to test the area. Otherwise record `user testing skipped — no manual verification trigger` in the cycle summary.

When triggered, use `user-testing-gate` below. After bug fixes and automated validation, execute the review workflow with `--vigil` on the staged + unstaged changes within the review cap before re-presenting the gate. Commit only at the applicable close-out.

For revisions to an open PR, use the post-PR close-out in `Delivery continuation` instead of the between-cycle or milestone close-out below.

### Between cycles

Before the next plan, check cited paths, signatures, and ACs against the landed diff. Surface drift for the user to revise, skip, or halt.

- **ATOMIC:** commit this plan with a `Plan: feature-<slug>/plan-NN-<name>` body line; do not push. Continue to the next cycle.
- **INCREMENTAL:** Execute the embedded `documentation-workflow` below with `--branch` when this plan has user-facing/documentable changes; stage and commit with the `Plan:` body line. Present plan summary, validation, and PR scope through `request_information`: `Approved` / `Halt` / `Other`. On approval execute the embedded `pr-workflow` below and capture its URL. Wait for the user to confirm merge, then repeat feature-branch setup from updated default before the next cycle.

At either pre-PR gate, Halt means emit a resume command and stop; Other follows user direction.

## Phase 3 — Milestone close-out

1. If there were any issues involving the ai or workflow suggest any edits to repository ai instruction scaffolding. 
2. Execute the embedded `documentation-workflow` below with `--branch`
3. stage explicit paths (`git add <paths>`, no `-A`) and commit remaining changes with a conventional subject
4. present the milestone summary through `request_information`: `Approved` / `Halt` / `Other`. 
5. upon approval execute the embedded `pr-workflow` below; pass `--issue <#|url>` if input referenced an issue. Capture the PR URL.
6. present PR url to user. 

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
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

<git-workflow>
# Git Workflow (mandatory)

Every milestone uses a feature branch + PR — never work directly on the default branch.

## Startup verification (do this FIRST)
1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

## Branch setup (before implementation)
1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Confirm `.dreamers/` is in the project's `.gitignore`. If not, add it before any further edits.
4. No init commit — the first commit for the milestone is the first thing in the PR diff.

## Commit discipline (non-negotiable)
1. **Commit at end of each cycle** — one commit per plan in the sequence (single-plan: one commit total; multi-plan: N commits, one per plan).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

## Push discipline (non-negotiable)
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between cycles, or at any other point in the pipeline.

## Post-PR push discipline
If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

## Commit structure (one commit per cycle)
- Exactly **one** commit per plan/cycle, immediately after the reviewer findings have been applied and tests are green (and user testing, if required, is signed off).
- The orchestrator stages changes with `git add` throughout the cycle but does **not** run `git commit` until the cycle ends.
- Commit message subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes).

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Unless explicitly requested by the user.
</git-workflow>


<user-testing-gate>
# User Testing Gate Template

Use this template whenever the Dreamers pipeline pauses for user testing.

Call `request_information`. Do not replace this gate with an unstructured chat prompt unless the tool is unavailable.

## Prompt body

The prompt body must contain exactly these two sections, in this order:

### Testing steps

Number every required user action and verification step with `1.`, `2.`, `3.`.

Include:
- Plan ID + path.
- A one-sentence summary of what changed in this cycle.
- Every special action required before testing, including build type, packaging, deploy, install, cache reset, seed data, feature flag, account state, device/browser, or distribution steps.
- Build/distribute steps from `.github/instructions/build.instructions.md` when present.
- If `.github/instructions/build.instructions.md` is absent and a build/distribution action is needed, include a numbered step asking the user to perform the project-specific build/distribution manually.
- Every manual test the user should perform, derived from the plan ACs and any reviewer-requested validation.
- The expected result for each test step.

Do not collapse tests into a paragraph. Do not use bullets for the testing steps.

### Notes

Include:
- Known limitations and out-of-scope items.
- Relevant automated validation already run.
- Any environment assumptions or risks the user should know before approving.

Use `None` only when there are no notes.

## Options

Provide exactly these three options:

1. `Approved`
2. `Bug found (enter text)`
3. `Other (enter text)`

`Bug found (enter text)` and `Other (enter text)` must accept freeform text.

## Response handling

- `Approved` -> continue the pipeline.
- `Bug found (enter text)` -> capture the bug text, fix inline, rerun required automated validation, then present this same user-testing gate again.
- `Other (enter text)` -> follow the user's direction. If the result still needs user testing sign-off, present this same gate again.
</user-testing-gate>

<help-workflow>
# Help workflow

## Boundary

This is read-only guidance. Do not inspect or change repository, git, mailbox, filesystem, or external state. Suggest next commands for the user; do not execute them.

## Response

Orient the user briefly: the Dreamers system combines planning, implementation and tests, artifact-backed review, targeted user gates, documentation, and PR delivery.

Explain the primary entry point with concrete examples:

- /dreamers add offline export
- /dreamers feature-search/plan-01-indexing.md
- /dreamers feature-search/manifest.md

Explain that task descriptions use the planning workflow with Grill by default, shared with the standalone /dreamers-plan command. Existing plan and manifest inputs skip planning and the implementation-start gate using the human-reviewed artifacts.

Explain adaptive review:

- lite plans use Vigil.
- standard plans use Sentinel + Probe.
- complex plans use Sentinel + Probe + Hone.

Explicit plan or user direction overrides the default reviewer lane. Reviewers are read-only for project files and write their required `.dreamers/reviews/` artifacts; the caller applies accepted findings and owns revalidation.

Offer specialized choices when they fit better:

- /dreamers-plan for planning only.
- /dreamers-implement for a task or approved plan without end-to-end close-out.
- /dreamers-review, /dreamers-test, or /dreamers-simplify for read-only audits.
- /dreamers-lite for task delivery without planning, with up to 2 Vigil fix cycles, docs, commit, and PR approval.
- /dreamers-issue, /dreamers-new-project, /dreamers-find-refactors, and /dreamers-explain for focused discovery or explanation.
- /dreamers-docs, /dreamers-pr, and /dreamers-pr-resolve for documentation, PR creation, or PR feedback.
- /dreamers-add-logging, /dreamers-cleanup-comments, /dreamers-cleanup-comments-branch, /dreamers-clean-work, and /dreamers-plan-verify for maintenance and verification.
- /dreamers-update for Dreamers system-file maintenance and the approved Copilot-to-Codex transfer.

State the `/dreamers` gates: plan approval for task input, major scope expansion, triggered user testing, and final pre-PR approval.

Explain that `/dreamers` delivers plans and `/dreamers-lite` delivers tasks without planning and that all plans use Goal, Scope and context, and Acceptance Criteria; lite, standard, and complex label complexity for review routing. Checks belong with ACs, without separate Approach or Verification sections. The retired `/dreamers-full` command has no forwarding alias.

End with one invitation: "Describe your goal and I can suggest the next command."
</help-workflow>

<planning-workflow>
# Planning workflow

Apply the embedded `planning-grill`, `plan-format`, `manifest-format` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

If the task is missing, ask. Work inline and write only `.dreamers/plans/` artifacts; do not change project files or git state. When used standalone, own a planning todo; as a delivery phase, use the active skill's existing todo.

## 1: Grill
Apply `planning-grill` below.

## 2: Generate plan(s) proposal
- generate plans following `plan-format`
- plans should be the smallest shippable chunks. do not break up arbitrarily if doing so would cause more work.
- when more than one plans are needed generate a manifest.md

## 3: Propose to user
- If: change requires a single plan. then present the full plan to the user.
- Else: Then present the manifest when task requires multiple plans.

Present the proposal and any critiques through `request_information`: risks, assumptions, tradeoffs, and simpler alternatives. Answer questions and corrections with reasoning and a recommendation; revise and re-present until approved.

## 3: Write plan(s)
- Create `.dreamers/plans/feature-<slug>/`.
- Write numbered `plan-NN-<name>.md` files using `plan-format`; add `manifest.md` when multi-plan task

## 3: Review gate

Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`.

- Minor edit: apply, repeat Step 2 checks, and re-present.
- Major rewrite: return to Step 1 with the correction.
- Halt: stop and surface paths.
- Other: follow the user's direction.

On approval, return plan paths. When used standalone, stop and suggest `/dreamers-implement <plan-path>` as a next command for the user. As a delivery phase, return to the active skill's implementation-start gate.
</planning-workflow>

<implementation-workflow>
# Implementation workflow

Apply the embedded `dreamers-kernel`, `git-workflow`, `testing-mandate`, `comment-rules`, `logging-discipline` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Todo
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## 1: Implement
- Implement the task or approved plan in the supplied input per `comment-rules` + `logging-discipline` + `testing-mandate` (Kernel). For tasks, use the stated requirements as acceptance criteria; no plan file is needed. Stage as you go.

## 2: Type-check + run tests
- Run the project's type-check + test command (from `.github/copilot-instructions.md`). Fix inline (max 3 attempts) then halt.
- Update `./test-benchmarks.md` row after passing (if the project uses one).

## Exit
- Return requirement/AC coverage and validation results at green tests.
</implementation-workflow>

<review-workflow>
# Review workflow

Apply the embedded `dreamers-kernel`, `reviewer-findings-format`, `logging-discipline`, `agent-recovery` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Modes
- `--full` Full triad: Sentinel + Probe + Hone in parallel.
- `--vigil` Single-agent combined review through Vigil.
- `--lens <name>` Single-lens audit (`sentinel` / `probe` / `hone`).
- `--lenses <csv>` Selected-lens audit (`sentinel`, `probe`, `hone` in any non-empty combination).
- With a plan and no lane flag: select from the plan as described below.
- Without a plan or lane flag: infer a review basis, then default to the full triad.

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

## Todo - Before you begin.
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## Step 1 — Establish the review basis
- If a readable plan is supplied, use it as the review basis. A user-supplied path that cannot be read remains a blocking error; do not silently replace it with an inferred basis.
- For a supplied plan, resolve `**Grilling transcript:**` relative to the plan. If the metadata is absent, check for sibling `grilling-transcript.md` for compatibility. When a readable transcript exists, read it in full and bind its absolute path + verbatim contents alongside the plan as authoritative user-intent context. If the plan references a transcript that is missing or unreadable, block instead of silently dropping it. If no transcript exists or is referenced, continue with the plan alone.
- If no plan is supplied or no plan is available, infer the intended behavior from, in order: explicit user direction; PR title/body and branch name; commits and diff in the selected scope; changed tests; changed code and its callers; then nearby conventions and public interfaces.
- Write a concise inferred-intent summary with the observable behavior, invariants, likely regression risks, evidence paths, and confidence. Treat that summary as the review basis, not as a replacement plan.
- If the evidence does not support one reliable interpretation of the change, ask the user one concise question before spawning reviewers. Do not guess or use the full triad to decide the requirement.

## Step 2 — Spawn reviewers
- Determine the selected reviewers in this order:
  1. Honor an explicit lane flag or explicit user direction.
  2. Honor an explicit reviewer requirement written in the plan.
  3. Otherwise read `**Plan-type:**`: `lite` = Vigil; `standard` = Sentinel + Probe; `complex` = Sentinel + Probe + Hone.
  4. If no plan or Plan-type is available, use Sentinel + Probe + Hone.
- Before spawning, record existing matching artifacts under `.dreamers/reviews/{vigil,sentinel,probe,hone}-*.md` so stale files are never mistaken for this run.
- For multiple selected reviewers, launch every reviewer in parallel through the runtime's batched-spawn mechanism, each with `mode: "sync"`. Never spawn or await reviewers sequentially.
- Vigil and single-lens modes spawn only the chosen reviewer.
- Every reviewer prompt MUST include `Do NOT call manage_todo_list.`
- Every reviewer prompt MUST include the review basis: either the absolute plan path or the inferred-intent summary with its evidence and confidence. For a plan-bound review with a resolved Grill transcript, include its absolute path and full verbatim contents; require the reviewer to use it when checking intent alignment and to report any plan/transcript conflict rather than silently choosing one. Explicitly say `no plan binding` for inferred-intent reviews.
- Every reviewer prompt MUST require exactly one artifact under `.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md` and short chat output containing only status, counts, artifact path, blocked reason, and open questions.
- Per-lens prompt context:
  - **Vigil** — combined correctness, security, maintainability, test coverage, and simplicity review with the required architecture audit. Artifact contains findings, intent alignment, requirement coverage, and architecture audit sections.
  - **Sentinel** — correctness / security / maintainability. Apply `logging-discipline` (Kernel) when assessing log calls: flag deviations from `.github/instructions/logging.instructions.md` if present, otherwise from surrounding-code conventions; never-log violations are `security` severity. Artifact contains findings + intent-alignment summary.
  - **Probe** — test coverage (requirement matrix, layer audit, edge cases, gaps). Artifact contains findings + requirement coverage table.
  - **Hone** — simplicity / over-engineering / redundancy / architecture. Mandate verbatim: "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly so the caller can route it through their major-refactor gate."
- Wait for all spawned reviewers to return.

## Step 3 — Report
- For each selected reviewer, read the artifact path returned in chat. If the path is missing or unreadable, inspect only new matching artifacts created for this review; if exactly one exists for that reviewer, read it. Otherwise surface `Blocked — review artifact missing for <reviewer>` and stop.
- Return per-reviewer artifact contents verbatim to the caller, including artifact paths.
- Aggregate counts by severity + lens from the artifacts for a one-line summary.
- Surface any `Blocked` status from any artifact (caller handles).
- Surface any open questions raised by any artifact (caller handles).

## Exit
- Artifact-backed structured findings per `reviewer-findings-format` (Kernel). The caller applies (or defers) findings on its own terms.

## Lane policy

This workflow owns reviewer selection and execution. The caller owns all finding disposition, gates, fixes, revalidation, and user testing. This workflow does not modify project code, tests, docs, config, dependencies, or git state. Each spawned reviewer is read-only for those same project files; its sole write is exactly one `.dreamers/reviews/` artifact.

Lane choices:

| Lane | Reviewers | Use when |
| --- | --- | --- |
| vigil | Vigil | Lite plan or explicit request. |
| sentinel | Sentinel | Correctness, security, or maintainability audit. |
| probe | Probe | Test coverage, AC layer, edge-case, or regression-risk audit. |
| hone | Hone | Simplicity, architecture, or over-engineering audit. |
| standard | Sentinel + Probe | Standard plan or explicit combined correctness and coverage audit. |
| full | Sentinel + Probe + Hone | Complex plan, explicit full review, or the standalone default. |
</review-workflow>

<documentation-workflow>
# Documentation workflow

Apply the embedded `dreamers-kernel` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Todo - Before you begin.
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## Step 1 — Resolve diff scope
- `--branch` (default): scope = `git diff --name-only origin/$DEFAULT...HEAD`.
- `--staged`: scope = union of `git diff --cached --name-only` and `git diff --name-only`.
- If the changed-files list is empty → output `No changes detected` and exit.

## Step 2 — Spawn Echo
- `task(agent_type: "echo", mode: "sync")`. Prompt MUST include `Do NOT call manage_todo_list.`
- Pass: context (ad-hoc or milestone close-out — caller-supplied), changed-files list, diff base, plan paths (if applicable), prior review summary (if applicable).
- Constraint to Echo: edits docs only — no production code, no tests. Stage with `git add`; do NOT commit.
- Wait for Echo to return its structured chat output.

## Step 3 — Handle output
- `Docs updated — N files changed` → surface doc-changes log to user.
- `No doc updates needed` → exit.
- Open questions → present each via `request_information`; capture answers; re-spawn Echo with clarification if needed.

## Exit
- Files Echo touched. The caller commits (this workflow does NOT commit, push, or open a PR).
</documentation-workflow>

<pr-workflow>
# PR workflow

Apply the embedded `dreamers-kernel`, `git-workflow`, `pr-description` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Todo - Before you begin.
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## Step 1 — Pre-push verification
- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

## Step 2 — Push
- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

## Step 3 — Open the PR
- Draft the PR body using the embedded `pr-description` template below.
- `gh pr create --base <DEFAULT> --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

## Step 4 — Archive shipped plan artifacts
- If this PR ships a Dreamers plan from `.dreamers/plans/feature-<slug>/`, archive after the PR is created.
- Single-plan feature directory: move `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/`.
- Multi-plan feature directory or manifest sequence: create `.dreamers/plans/archive/feature-<slug>/` if needed, move only the shipped `plan-NN-*.md` file(s) into it, and leave unfinished plans in the live feature directory.
- If `manifest.md` exists, keep it live while any unfinished plan file remains. After the last unfinished plan ships, move `manifest.md` into the same archive directory and remove the now-empty live feature directory.
- If no feature directory applies, skip this step.

## Exit
- PR URL. Include moved archive path(s) when Step 4 archived anything.
</pr-workflow>

<planning-grill>
### Grill

Resolve decisions and their dependencies until the goal, scope, and constraints are understood. Explore the codebase for answers before asking the user. For unresolved decisions, use `request_information`, one blocking question at a time, with exactly:

1. Recommended answer, labeled recommended.
2. Strongest viable alternative.
3. `Other` for freeform direction.

Incorporate each answer before continuing. Do not propose while required decisions remain open.

Capture every question and response verbatim, in order, including complete tool questions, choice labels, and descriptions. Keep responses separate; never summarize, paraphrase, normalize, or omit text. When writing plans, save the exchange to `.dreamers/plans/feature-<slug>/grilling-transcript.md`, adding only speaker/sequence headings. Do not create an empty transcript.
</planning-grill>

<plan-format>
Use this structure for every plan type. Keep decisions, contracts, UI details, and risks in Scope and context only when relevant. When they clarify the change, include Mermaid diagrams of flows or example UI layouts/wireframes in Scope and context. Acceptance Criteria carry validation intent; do not add separate Approach, Verification, or Test Cases sections.

```markdown
# Plan-NN: <short title>

**Date:** YYYY-MM-DD
**Status:** Draft
**Plan-type:** <lite|standard|complex>
**Branch:** <feat/slug|fix/slug>
**User-testing-required:** <yes|no>
**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)

## Goal
<The outcome this plan delivers.>

## Scope and context
<Exact affected paths, relevant current behavior, agreed decisions, constraints, and exclusions.>

## Acceptance Criteria
<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: <unit|integration|E2E|perf>.*
</acceptance_criteria>
```

Include the transcript link only when the sibling artifact exists. Compound layers are allowed when one assertion serves both purposes. Under the relevant AC, add a test command or check when project instructions and the outcome are insufficient. For manual checks, include the steps, expected result, and why automation cannot cover them; set `User-testing-required: yes`.
</plan-format>

<manifest-format>
```markdown
# Feature: <short name>

**Date:** YYYY-MM-DD
**Status:** Draft

## Summary
<The outcome delivered by the complete feature.>

## Plan sequence
| Order | Plan file | Summary |
|---|---|---|
| 1 | [plan-01-<name>.md](plan-01-<name>.md) | <Outcome> |

## Shared context
<Only constraints, decisions and their rationale, or contracts needed by multiple plans. Include cross-plan rollback conditions and order when needed.>

## Acceptance Criteria
<acceptance_criteria>
1. Given <feature-level state>, when <whole-feature trigger>, then <observable outcome>.
   *Layer: E2E.*
</acceptance_criteria>
```

Keep plans in execution order. Manifest ACs cover outcomes requiring the whole sequence; plan ACs cover each plan. Omit shared context or feature-level ACs when none apply; do not duplicate plan content.
</manifest-format>

<testing-mandate>
## Plan template
Every plan must express its test coverage intent through the Acceptance Criteria's Layer annotations.

```
## Acceptance Criteria
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
```

Layer label set (closed): `unit` / `integration` / `E2E` / `perf`. Compound labels allowed when one assertion serves two purposes (e.g., `*Layer: integration / perf.*`).

**Test coverage intent is expressed via the `*Layer: ...*` annotation on each Acceptance Criterion — not via a standalone Test Cases section.** Do not write a separate Test Cases section in a plan; embed the test layer directly in the AC. This keeps ACs and test specification in one place so they never drift.

## Coverage requirement (every plan)

Across all of a plan's ACs, the layer mix must cover the following whenever applicable to the work — think through each layer explicitly:

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
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), the plan must include at least one AC with `*Layer: E2E.*` — not just unit/integration. Probe enforces this in the layer audit and blocks if missing.

If a layer cannot be covered automatically (e.g., camera permission flows), put the manual steps, expected result, and reason under the relevant AC; set `User-testing-required: yes`.

## Test benchmarks

Each project that uses `/dreamers-implement` maintains a `./test-benchmarks.md` file at the project root. The file records measured run times per test command so the orchestrator can set realistic timeouts.

- **File path:** `./test-benchmarks.md` at the project root (committed to version control).
- **Recommended-timeout formula:** `max(last_run_time × 2, 30s)` — the 2× multiplier accounts for machine variance; 30s is a non-negotiable floor.
- **Orchestrator updates** the row for each test command after every successful test run. **Humans may edit** the `Notes` column to capture CI environment factors or known flakiness.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).
</testing-mandate>

<comment-rules>
## Core principle
Comments must add value that the code cannot express itself. Concise, no fluff, no separators.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does (`const isRunning` does not need `// tracks whether running`)

## Strict prohibitions
- **No plan/ticket references** — never mention plan files, milestone names (D25, plan-3), ticket numbers, or agent names in source code
- **No separator comments** — never use `// ---`, `// ===`, `// ###`, blank-comment lines, or visual dividers
- **No spec rationalization** — never write comments arguing a spec permits a pattern; implement cleanly and let review judge
- **No redundant JSDoc/KDoc** that only repeats the function signature
- **No em dashes. no exceptions**
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines to be useful, the code needs refactoring, not more words
</comment-rules>

<logging-discipline>
1. **Project rule first.** If `.github/instructions/logging.instructions.md` exists, it is the binding spec.
2. **Else: match surrounding code.** Existing log calls in the same module and nearest neighbors define:
   - Logger library / import path (do not introduce a new logger where one already exists).
   - Level conventions in use (ERROR / WARN / INFO / DEBUG, or whatever the codebase uses).
   - Message format (structured fields vs interpolated strings, key names, casing).
</logging-discipline>

<reviewer-findings-format>
# Reviewer Findings Format

## Artifact contract

Each reviewer writes exactly one markdown artifact under `.dreamers/reviews/`:

`.dreamers/reviews/<reviewer>-<slug>-<yyyymmdd-hhmmss>.md`

Use the branch, plan slug, or task slug for `<slug>`. If unavailable, use `review`.

The artifact is the durable handoff. Chat output is only a short status pointer with the artifact path. The caller must read the artifact before reporting, applying, or deferring findings.

**Status line** (one of):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:

```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

- `severity` ∈ `critical` / `high` / `medium` / `low`
- `lens-tag` ∈ `correctness` / `security` / `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` — absolute or repo-relative path + line number
- `what was wrong → suggested fix` — one-line description + targeted fix the caller can apply mechanically

**Observations** (optional) — out-of-scope notes that aren't findings. The caller may or may not act on them.

**Open questions** (optional) — items needing user judgment. Use "none" if no questions.

Reviewers are read-only / report-only for code, tests, docs, config, scripts, and git state. The only allowed write is the single review artifact. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

<agent-recovery>
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>

<pr-description>
# PR Description Template

Use this structure for `gh pr create --body`.

---

## Summary
plan/task summary here

- [bullet: what was delivered]
- [bullet: why / what problem it solves]

## Test counts

- Desktop Vitest: N pass
- Mobile Jest: N pass

*(Omit platforms not touched by this PR.)*

## Fixes applied

- [SEVERITY] file:line — what was fixed (from reviewer artifacts / commit messages)

*(Omit if no fixes applied.)*
</pr-description>
