---
name: dreamers
description: 'End-to-end Dreamers delivery orchestrator. Accepts a task description, existing plan file(s), or a feature manifest. Preserves the full pipeline gates and close-out while invoking specialized planning, implementation, review, documentation, and PR skills. Reviewers are selected by /dreamers-review from plan complexity or explicit plan/user direction; deferred findings are recorded in project-root defered.md. Triggers: /dreamers, plan and implement, new feature, ship a feature.'
argument-hint: '<task description> | feature-<slug>/plan-NN-<name>.md [more] | feature-<slug>/manifest.md'
---

$ARGUMENTS

If no task description, plan path, or manifest was provided, halt + ask.

## Modes
| Mode | `$ARGUMENTS` | Phase 1 / 1.5 behavior |
|---|---|---|
| 1 | Task description | Invoke `/dreamers-plan $ARGUMENTS` for the Grill phase + right-sized plans → capture plan paths from its output → run Phase 1.5 gate |
| 2 | Plan path(s) | Skip planning and Phase 1.5; use supplied plan file(s) after plan-quality checks |
| 3 | `manifest.md` | Skip planning and Phase 1.5; read manifest → capture plan sequence + shared-context payload → run plan-quality checks |

Plan path mode:
- Treat arguments ending in `.md` as plan paths when they resolve under `.dreamers/plans/`, or when they match `feature-<slug>/plan-NN-<name>.md`.
- Resolve `feature-<slug>/plan-NN-<name>.md` under `.dreamers/plans/`.
- Preserve the provided order as the implementation sequence.
- Resolve and read each supplied plan file before branch setup; halt if any file is missing, is outside `.dreamers/plans/`, or is not a `plan-*.md` file.
- Do not invoke `/dreamers-plan`, re-plan, write replacement plan files, or ask for implementation-start approval.
- For multi-plan runs, honor an explicit user-supplied strategy; otherwise set `strategy=ATOMIC` without asking.

Manifest mode:
- Treat `manifest.md` as manifest mode when it resolves under `.dreamers/plans/`, or when it matches `feature-<slug>/manifest.md`.
- Resolve `feature-<slug>/manifest.md` under `.dreamers/plans/`.
- Read the manifest before branch setup, capture the plan sequence and shared-context payload, and preserve that sequence through Phase 2.
- Do not invoke `/dreamers-plan`, re-plan, write replacement plan files, or ask for implementation-start approval.
- Honor an explicit user-supplied strategy; otherwise set `strategy=ATOMIC` without asking.

Plan quality check before branch setup (all modes):
- Read each plan and detect `**Plan-type:** lite / standard / complex`.
- Read `plan-guide-selector.md`, then read only the matching guide for each plan.
- Do not implement from a bare plan: reject missing required sections for its plan type, placeholder content, missing AC layer annotations, unresolved open questions, or unverifiable citations presented as facts.
- If `Plan-type` is missing, treat the plan as legacy: surface the missing-type warning and continue only after explicit user approval.

## Todo - Before you begin.
- Declare a todo list marking all phases at entry. Mode 1: Phase 1 / Phase 1.5 / Phase 2 cycle-N / Phase 3. Modes 2 and 3: Artifact resolution / Phase 2 cycle-N / Phase 3.
- Before reading `.dreamers/` files, read and apply `~/.copilot/dreamers/refs/dreamers-kernel.md` and `~/.copilot/dreamers/refs/git-workflow.md`, including startup verification.

## Phase 1 — Planning (Mode 1 only)
- Invoke `/dreamers-plan $ARGUMENTS`.
- The planning pass writes the smallest selected-guide plan that preserves quality.
- Wait. Capture plan paths.
- Halt this skill if `/dreamers-plan` halts without approval.

## Phase 1.5 — Plan review / implementation start gate (Mode 1 only)
- Do not run Phase 1.5 for plan path or manifest mode. After artifact checks pass, proceed directly to Phase 2.
- Read the plan path(s). If manifest mode, also read the manifest shared-context payload.
- If multiple plans will run, score against `plan-guide-selector.md` § "Ship strategy."
- Present the written plan path(s), implementation scope, test intent, and any ship-strategy recommendation.
- `request_information`:
  - Single-plan: `Approved — start implementation` / `Revise plan` / `Halt` / `Other`.
  - Multi-plan: `Approved — start INCREMENTAL` / `Approved — start ATOMIC` / `Revise plan` / `Halt` / `Other`.
- On `Revise plan`, apply explicit minor edits inline when unambiguous, then re-present this gate. Major rewrite → return to `/dreamers-plan` with the correction as context. Capture selected `strategy` for multi-plan runs.

## Phase 2 — Per plan implementation + review

Branch setup once per `git-workflow`: fetch + checkout default + pull + cut `feat/<slug>`. Confirm `.dreamers/` is gitignored. Action open items in `.dreamers/improvements.md` if present.

For each plan in sequence:

### Steps 1–3 — Implement
- Invoke `/dreamers-implement <absolute-plan-path>` with the shared manifest context when present.
- Wait. A halted implementation halts this cycle.

### Step 4 — Spawn review
- Invoke `/dreamers-review --branch <absolute-plan-path>` once per plan.
- `/dreamers-review` selects Vigil, Sentinel + Probe, or Sentinel + Probe + Hone from plan complexity or explicit plan/user direction.
- This is the only automatic initial review pass for the plan.
- Wait. Read every returned `.dreamers/reviews/` artifact before continuing.
- Capture all reviewer artifact paths in the cycle summary.
- `Blocked` from any reviewer artifact → halt cycle + surface verbatim with artifact path.
- Open questions from any reviewer artifact → present each via `request_information`; capture; carry decisions into Step 5.

### Step 5 — Apply findings (orchestrator-as-fixer)
- Concatenate findings from the reviewer artifacts; sort by severity (critical → low).
- Conflict resolution: same `file:line` with contradicting fixes → correctness/security > test-coverage > simplicity. Genuine ambiguity → `request_information` before applying.
- **Major-refactor gate.** A finding is "major-refactor scope" if its suggested fix meets ANY of:
  - New module or top-level directory not in the plan's scope.
  - Schema / data-model change.
  - Cross-cutting refactor (touches multiple unrelated subsystems).
  - New public exported symbols not specified in the plan.
  - Files outside the plan's scope.
  - Hone- or Vigil-recommended full refactor (scope language like "tear out X across N files," "rewrite Y module").
  Closed checklist. Ambiguous → fire the gate.
- For each gate-triggering finding (or batched group sharing the same refactor scope), `request_information` with: reviewer, severity, lens, location, finding, suggested fix, triggered criterion, rationale, breadth estimate. Options: `Apply now` / `Defer — save to defered.md` / `Other`.
  - **Apply now** → fix inline; stage; re-run tests after.
  - **Defer** → do NOT apply or create a follow-up plan. Append a Markdown entry to `defered.md` in the project root; create it with `# Deferred Suggestions` if absent, and never overwrite existing entries. Record the date, current plan or branch, reviewer + artifact path, severity / lens / location, finding, suggested fix, triggered criterion, and deferral rationale. Stage `defered.md`, surface its path, and continue with remaining findings.
  - **Other** → freeform redirect. Never silently apply/defer.
- Apply each non-deferred fix as a targeted Edit. Stage with `git add`. Re-run type-check + tests after applying. Regression → fix inline (max 3 attempts) before halting.

### Step 5.5 — Review rerun policy
- Never re-run the initial reviewer lane automatically after Step 4. Step 4 is the single automatic review pass for this plan.
- After Step 5 fixes or Step 6 bug fixes, skip reviewer rerun when the fix is small and validation covers it. Record why in the cycle summary.
- If a reviewer rerun is needed and no major-change trigger applies, invoke `/dreamers-review --vigil --branch <absolute-plan-path>` once. Read the Vigil artifact before applying findings. Route Vigil findings through Step 5.
- A major-change rerun trigger fires when the post-review fix set includes any of:
  - New abstraction, module, or top-level directory.
  - Schema / data-model change.
  - Public API, exported symbol, dependency, or persistence change.
  - Cross-subsystem refactor or broad rewrite.
  - Files outside the plan's scope.
  - Conflicting reviewer feedback that cannot be resolved mechanically.
  - Hone/Vigil full-refactor scope language.
  Ambiguous → fire the gate.
- On a major-change trigger, ask the user before rerunning review. Provide the reason, breadth estimate, files touched, validation status, and options: `Run Vigil` / `Run full triad` / `Run selected /dreamers-review lane` / `Skip reviewer rerun` / `Other`.
  - `Run Vigil` → invoke `/dreamers-review --vigil --branch` once as above.
  - `Run full triad` → invoke `/dreamers-review --full --branch` once, capture artifact paths, and route findings through Step 5.
  - `Run selected /dreamers-review lane` → ask for `sentinel`, `probe`, `hone`, or comma-separated lenses; invoke that lane once and route findings through Step 5.
  - `Skip reviewer rerun` → record the user-approved skip and continue.
  - `Other` → follow user direction; never infer an extra review pass.

### Step 6 — User testing gate (when triggered)
- Trigger this gate when the plan requires manual verification, the change is user-facing, build/distribution steps are needed, reviewer findings request user validation, or the user asked to test this area.
- If no trigger applies, record "user testing skipped — no manual verification trigger" in the cycle summary and continue.
- When triggered, read `.github/dreamers/templates/user-testing-gate.md` and present the gate through `request_information` exactly as specified there.
- The gate prompt must include a numbered `Testing steps` section and a `Notes` section.
- The gate must provide exactly three options: `Approved` / `Bug found (enter text)` / `Other (enter text)`.
- `Bug found (enter text)` and `Other (enter text)` must accept freeform text.
- On bug → capture text, fix inline, rerun required automated validation, then apply Step 5.5. Then re-present the same templated gate.
- On Approved → continue.
- No commit yet (commit happens at close-out for FULL, or in the LIGHT close-out between cycles for INCREMENTAL).

### Between cycles (more plans remain)
- **Drift check** (inline): read next plan; cited paths exist; signatures match; ACs valid vs landed diff. Drift → surface; user revises/skips/halts.
- **INCREMENTAL** (light close-out for this plan):
  - Invoke `/dreamers-docs --branch` if the just-completed plan's diff has user-facing or documentable changes.
  - `git commit` per project commit style; body includes `Plan: feature-<slug>/plan-NN-<name>`.
  - **Pre-PR approval gate**: present plan summary, validation status, and PR scope. `request_information` Approved/Halt/Other. Halt → emit resume command + stop.
  - Invoke `/dreamers-pr`. Capture PR URL.
  - Halt until the user confirms the PR has merged, then re-cut feature branch from default → next cycle.
- **ATOMIC**:
  - `git commit` for this plan (body includes `Plan:` line). Do NOT push. → next cycle.

## Phase 3 — Close-out (FULL, milestone end)
- Append improvements to `.dreamers/improvements.md` (dated, one sentence each, reference retro path below).
- Invoke `/dreamers-docs --branch`. Stage Echo's edits.
- Write retro `.dreamers/retros/retro-d<N>-<name>.md`:
  - What worked well
  - Friction points
  - Proposed improvements
  - AC coverage matrix (rolled up from cycles)
  - Bugs from user-testing (if any)
  - Regression analysis (only if originating task was a bug fix)
- Final commit: `git add <explicit-paths>` (no `-A`) + `git commit` per conventional-commits with `Plan:` body + trailer. Skip if nothing staged.
- **User approval gate** (MANDATORY, last halt before PR): present milestone summary. `request_information` Approved/Halt/Other. Halt → emit resume command + stop.
- Invoke `/dreamers-pr` (pass `--issue <#|url>` if `$ARGUMENTS` referenced one). Capture PR URL.
- **Post-PR scan**: surface open retro improvements and project-state drift only (PR description vs plans shipped; `git log origin/$DEFAULT -10`; `.dreamers/improvements.md` open items; `.dreamers/retros/` open items). No new prompt, no auto-commit after PR opens.
