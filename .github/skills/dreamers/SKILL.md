---
name: dreamers
description: 'Deliver a task, approved plan(s), or manifest through planning, implementation, review, user testing, docs, and PR. Empty/help input opens /dreamers-help. Triggers: /dreamers, plan and implement, new feature, ship a feature.'
argument-hint: '<help | task description> | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

## Route input

Normalize whitespace. Empty input, `help`, `--help`, or `-h`: invoke `/dreamers-help` read-only and stop before inspecting or changing repository, git, mailbox, or external state.

For delivery, declare a todo covering planning/start approval or artifact resolution, each plan cycle, and close-out. Apply `dreamers-kernel` and complete `git-workflow` startup verification before reading any `.dreamers/` files.

| Input | Route |
|---|---|
| Task description | Phase 1, then the implementation-start gate. |
| Plan path(s) | Resolve and read the plans in supplied order; skip Phase 1 and its start gate. |
| `manifest.md` | Resolve and read the manifest; capture its plan sequence and shared context; skip Phase 1 and its start gate. |

Treat `.md` path arguments, including `feature-<slug>/plan-NN-<name>.md` and `feature-<slug>/manifest.md`, as artifact input. Resolve feature-relative paths under `.dreamers/plans/`. Plans must be named `plan-*.md`; manifests must be named `manifest.md`. Reject missing paths or paths escaping `.dreamers/plans/`. Unrecognized input: halt and ask for a task, plan path, manifest, or help.

Supplied artifacts are implementation authorization: do not re-plan, replace them, or ask to start. For multiple supplied plans, honor the user's ship strategy; otherwise use ATOMIC without asking. Validate every plan with `plan-quality` before branch setup.

## Phase 1 — Planning and start approval (task input only)

1. Invoke `/dreamers-plan $ARGUMENTS`; capture the returned plan paths. If it halts without approval, halt here.
2. Read and validate the plans. Present paths, implementation scope, test intent, and the ship-strategy recommendation when multiple plans will run.
3. Use `request_information`:
   - Single plan: `Approved — start implementation` / `Revise plan` / `Halt` / `Other`.
   - Multiple plans: `Approved — start INCREMENTAL` / `Approved — start ATOMIC` / `Revise plan` / `Halt` / `Other`.
4. Capture the selected strategy. For revisions, apply unambiguous minor edits inline; return major rewrites to `/dreamers-plan` with the correction. Validate and re-present this gate.

## Phase 2 — Per-plan cycle

Set up the feature branch once per `git-workflow`. Action open items in `.dreamers/improvements.md` if present. Process plans in sequence, carrying manifest shared context into implementation.

### Implement and review

1. Invoke `/dreamers-implement <absolute-plan-path>`. A halted implementation halts the cycle.
2. On success, invoke `/dreamers-review --branch <absolute-plan-path>` once. It owns reviewer selection from plan complexity or explicit plan/user direction.
3. Read every returned review artifact and record its path in the cycle summary. Any `Blocked` result halts the cycle; surface it verbatim with its artifact path. Present open questions through `request_information` and carry the answers into fixes.

### Apply findings

Sort combined findings critical to low. For contradictory fixes at the same `file:line`, prioritize correctness/security, then coverage, then simplicity. Ask through `request_information` when ambiguous.

**Major-refactor gate:** ask before a fix introduces an unplanned module/top-level directory, changes schema/data models, crosses unrelated subsystems, adds an unplanned public export, touches files outside plan scope, or follows a Hone/Vigil full-refactor recommendation. This checklist is closed; uncertainty triggers the gate.

For each gate-triggering finding (or group with the same refactor scope), present reviewer + artifact path, severity, lens, location, finding, suggested fix, triggered criterion, rationale, and breadth estimate. Options: `Apply now` / `Defer — save to defered.md` / `Other`.

- Apply now: fix inline and stage.
- Defer: append to project-root `defered.md`; create with `# Deferred Suggestions` if absent and preserve existing entries. Record date, plan/branch, reviewer + artifact path, severity/lens/location, finding, suggested fix, triggered criterion, and deferral rationale. Stage and surface the path. Do not apply the finding or create a follow-up plan.
- Other: follow the user's direction; never silently apply or defer.

Apply remaining fixes inline and stage. Run project type-check + tests after fixes; correct regressions inline, at most three attempts, then halt if still failing.

### Review reruns

The initial review runs once per plan. After review fixes or user-reported bugs:

- Small fix covered by validation: skip rerun and record why.
- Rerun needed without a major-change trigger: invoke `/dreamers-review --vigil --branch <absolute-plan-path>` once.
- Major-change trigger: ask before rerunning. Triggers are new abstractions/modules/top-level directories; schema/data-model changes; public API/export/dependency/persistence changes; cross-subsystem refactors/broad rewrites; out-of-plan files; non-mechanical reviewer conflicts; or Hone/Vigil full-refactor scope. Uncertainty triggers the gate.

At the rerun gate, present reason, breadth, files touched, and validation status. Options:

- `Run Vigil`: invoke `/dreamers-review --vigil --branch <absolute-plan-path>` once.
- `Run full triad`: invoke `/dreamers-review --full --branch <absolute-plan-path>` once.
- `Run selected /dreamers-review lane`: ask for `sentinel`, `probe`, `hone`, or comma-separated lenses; invoke that lane once.
- `Skip reviewer rerun`: record the user-approved skip.
- `Other`: follow user direction without inferring another pass.

Read each rerun artifact, record its path, handle blocks/questions as above, and route findings through Apply findings.

### User testing

Trigger when the plan requires manual verification, the change is user-facing, build/distribution is needed, reviewers request user validation, or the user asked to test the area. Otherwise record `user testing skipped — no manual verification trigger` in the cycle summary.

When triggered, use `user-testing-gate` below. After bug fixes and automated validation, apply Review reruns before re-presenting the gate. Commit only at the applicable close-out.

### Between cycles

Before the next plan, check cited paths, signatures, and ACs against the landed diff. Surface drift for the user to revise, skip, or halt.

- **ATOMIC:** commit this plan with a `Plan: feature-<slug>/plan-NN-<name>` body line; do not push. Continue to the next cycle.
- **INCREMENTAL:** invoke `/dreamers-docs --branch` when this plan has user-facing/documentable changes; stage and commit with the `Plan:` body line. Present plan summary, validation, and PR scope through `request_information`: `Approved` / `Halt` / `Other`. On approval invoke `/dreamers-pr` and capture its URL. Wait for the user to confirm merge, then repeat feature-branch setup from updated default before the next cycle.

At either pre-PR gate, Halt means emit a resume command and stop; Other follows user direction.

## Phase 3 — Milestone close-out

1. Append dated, one-sentence improvements to `.dreamers/improvements.md`, each referencing the retro below.
2. Invoke `/dreamers-docs --branch` and stage Echo's edits.
3. Write `.dreamers/retros/retro-d<N>-<name>.md`: what worked, friction, proposed improvements, rolled-up AC coverage matrix, user-testing bugs if any, and regression analysis if the originating task was a bug fix.
4. Stage explicit paths (`git add <paths>`, no `-A`) and commit remaining changes with a conventional subject, `Plan:` body line, and kernel trailer. Skip if nothing is staged.
5. Present the milestone summary through `request_information`: `Approved` / `Halt` / `Other`. Approval is required before `/dreamers-pr`; pass `--issue <#|url>` if input referenced an issue. Capture the PR URL.
6. Post-PR, surface open improvements and project-state drift: compare PR description to shipped plans; check `git log origin/$DEFAULT_BRANCH -10`, `.dreamers/improvements.md`, and `.dreamers/retros/`. No new prompt or automatic post-PR commit.

<dreamers-kernel>
## User overrides

Explicit user instructions can skip or alter phases/actions.

## Subagent allowlist (HARD RULE)

Do not use any non-Dreamers agent unless explicitly authorized by user.

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

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

## Branch setup (before invoking `/dreamers-implement`)
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

<plan-quality>
## Plan quality

Before branch setup, read every plan and check the following. Reject missing requirements, unresolved questions, missing AC layers, or unverifiable citations presented as facts. Reject placeholders such as "relevant files", "handle edge cases", or "follow existing pattern" without exact details. A missing `Plan-type` is legacy: warn and require explicit user approval to continue.

### Common requirements

- Metadata: `# Plan-NN: {short-title}`, `**Date:**` YYYY-MM-DD, `**Status:**` Draft / Active / Completed / Superseded, `**Plan-type:**` lite / standard / complex, `**Branch:**` feat/{slug} or fix/{slug}, and `**User-testing-required:**` yes/no.
- When the sibling transcript exists: `**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)`.
- `Files Touched`: exact paths in a `Path | Action | Required change | Verification` table. No vague rows. Add adjacent required files only when discovered during implementation, justified by the same goal, and recorded before continuing.
- `Acceptance Criteria`: measurable Given/When/Then outcomes inside `<acceptance_criteria>`, each with `*Layer: ...*`. Labels: `unit`, `integration`, `E2E`, `perf`; compounds only when one assertion serves both purposes. No separate Test Cases section.
- `Verification` is last: project test and type-check commands, exact files to inspect, and specific smoke checks (one for lite; one or two for standard/complex).

### Required sections by type

| Type | Sections, in order | Additional requirements |
|---|---|---|
| lite | Goal, Files Touched, Acceptance Criteria, Verification | One-paragraph Goal. Context / Out of Scope only when useful. No code snippets except a minimal public interface contract. |
| standard | Goal, Context, Architecture, Files Touched, Acceptance Criteria, Out of Scope, Constraints, Verification | Design Decisions for non-obvious architecture/API/data/persistence/UI choices; UI for user-visible surfaces. |
| complex | Goal, Context, Architecture, Decision Log, Files Touched, Acceptance Criteria, Traceability, Out of Scope, Constraints, Quality Attributes, Risk / Mitigation, Verification | UI for user-visible surfaces. |

For standard/complex:
- Architecture covers current/target flow, boundary ownership, contracts (or `No contract changes.`), and failure/edge states. Include Mermaid for non-trivial flows, processes, state machines, lifecycles, async handoffs, branching, or multi-step workflows.
- Constraints use `<constraints>` with Technical (stack/perf/libraries), Process (gates/review/tests), and Hard rules (never-do constraints with rationale).

For complex:
- Context uses `Artifact | Verified fact` evidence; keep prose short.
- Architecture also covers data shapes, schema/API changes, retry, rollback, and migration behavior.
- Decision Log: `Decision | Recommended answer | User choice | Rationale | Rejected`.
- Traceability: `Decision / requirement | AC | Verification`.
- Quality Attributes: one line each, or `N/A - <reason>`, for security, privacy, accessibility, performance, migration, and observability.
- Risk / Mitigation: at most three `Risk | Mitigation | Verification` rows.

## Multi-plan ship strategy

Recommend INCREMENTAL for 4+ independent plans, different subsystems, or standalone user value from plan A. Recommend ATOMIC for overlapping files, ordering dependencies, schema/migration/API contracts, or verification requiring all plans. Conflicting signals default to ATOMIC.
</plan-quality>

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
