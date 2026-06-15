# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers runs the planning → tests-first → implementation → full review → Vigil follow-up review → docs → PR flow.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Forge, Nova personas; reviewers, Echo, Sage)
├── skills/           # Skill entry points
├── dreamers/
│   ├── refs/         # Shared reference docs (inlined into consumers at build time)
│   └── templates/    # Plan-writing guide, PR description shape, etc.
└── instructions/     # Auto-loaded instruction files
```

## Agents

| Agent | Type | Role |
|---|---|---|
| **Forge** | Persona | Implementation orchestrator. Routes user requests to the right skill. `/agents forge`. |
| **Nova** | Persona | Planning specialist. Mirrors `/dreamers-plan`. `/agents nova`. |
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only except one `.dreamers/reviews/` artifact. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge cases, regression risk). Read-only except one `.dreamers/reviews/` artifact. |
| **Hone** | Subagent | Reviewer — simplicity, over-engineering, redundancy, architectural quality. Read-only except one `.dreamers/reviews/` artifact; surfaces full-refactor recommendations without softening. |
| **Vigil** | Subagent | Single-pass reviewer for `/dreamers-lite`, skill-internal reviews outside `/dreamers-full` and `/dreamers-review`, and `/dreamers-full` follow-up review reruns. Combines Sentinel, Probe, and the shared Hone architecture rubric; writes one `.dreamers/reviews/` artifact with a required architecture audit section. |
| **Echo** | Subagent | Documentarian — Echo-owned sections of project docs, README, CHANGELOG. |
| **Sage** | Subagent | Researcher — deep multi-perspective research. |

Sentinel, Probe, and Hone spawn through `/dreamers-review` according to the selected review lane and each write a durable review artifact. `/dreamers-full` runs the full triad once per plan; follow-up review reruns use Vigil by default. Other skills that need a review call Vigil, not individual Sentinel/Probe/Hone lanes, except `/dreamers-find-refactors`, which intentionally uses section-scoped Hone calls for refactor discovery. A second triad or selected lane is user-gated for major-change reruns. Echo spawns per milestone via `/dreamers-docs`. Sage is invoked by `/dreamers-research`.

## Skills

Explicit user instructions can skip or alter skill phases/actions.

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers-full` | End-to-end pipeline. Accepts a task description, existing plan path(s), or manifest. Task mode invokes `/dreamers-plan` and uses the plan review / implementation-start gate; plan path and manifest modes skip planning and the implementation-start gate, then use supplied artifacts directly. Implements each plan inline (tests-first), invokes full `/dreamers-review` once per plan, applies findings with major-refactor gate, uses Vigil for normal review reruns, asks before any extra triad/selected-lane rerun, halts for templated user testing when triggered, then close-out (inline + `/dreamers-docs` + pre-PR approval + `/dreamers-pr`). |
| `/dreamers-lite` | Lean pipeline. Accepts a task description or existing plan path(s). Task mode reviews context, proposes a compact plan with critique, and writes the approved plan; plan path mode skips planning, plan writing, and implementation-start approval, then uses the supplied plan file(s) directly. Implements tests-first, runs Vigil once, applies findings, runs docs when triggered, commits, then opens the PR. No second plan gate or pre-PR gate. |
| `/dreamers-plan` | 3-phase planning (interactive Hash-out → Write → Review). Critiques the proposal before approval, writes plan file(s) + optional manifest, then verifies plan coverage against the proposal and user discussion before the review gate. Hard-stops at the review gate. |
| `/dreamers-implement` | One-shot implementation: write failing tests, implement, run tests. Exits at green tests. |
| `/dreamers-review` | Spawns the selected reviewer lane, reads reviewer artifacts, and reports structured findings. Read-only. `--lens <name>` for a single-lens audit; `--lenses sentinel,probe` for a selected subset; no flag keeps the full triad. |
| `/dreamers-docs` | Spawns Echo to update project docs based on the diff. Stages edits; user commits. |
| `/dreamers-pr` | Pushes the branch and opens the PR using the `pr-description.md` template. |
| `/dreamers-fix` | Self-contained bug-fix pipeline: branch + regression test + implement + run tests. Escalates to `/dreamers-full` on scope blowup. |
| `/dreamers-find-refactors` | Refactor discovery pipeline. Selects refactor lenses, sections the repo, runs section-scoped Hone audits, synthesizes findings, writes Dreamers plan files, and stops. No implementation, branch, commit, push, or PR. |

### Focused Vigil audit wrappers

`/dreamers-test` and `/dreamers-simplify` call Vigil with a focused prompt for test coverage or simplicity. Use `/dreamers-review --lens <name>` only when the user explicitly asks for a selected Sentinel/Probe/Hone lane.

### Review lanes

| Lane | Reviewers | Normal use |
|---|---|---|
| `sentinel` | Sentinel | Explicit correctness/security/maintainability audit through `/dreamers-review`. |
| `probe` | Probe | Test coverage, AC/layer coverage, regression-risk audit. |
| `hone` | Hone | Simplicity, architecture, over-engineering audit. |
| `standard` | Sentinel + Probe | User-selected follow-up check when both correctness and coverage need review but Hone is not warranted. |
| `full` | Sentinel + Probe + Hone | Required once per `/dreamers-full` plan; invoke as `/dreamers-review` with no lens flags. After that, use only when the user selects it from the `/dreamers-full` major-change rerun gate or explicitly requests full review. |

### Utility + orthogonal

| Skill | Purpose |
|---|---|
| `/dreamers-pr-resolve` | Resolve PR review comments inline; Vigil reviews accepted changes before thread resolution. |
| `/dreamers-add-logging` | Phased pass to add/improve logging per `logging-standards.md`. |
| `/dreamers-cleanup-comments` | Project-wide comment cleanup per `comment-rules.md`. |
| `/dreamers-cleanup-comments-branch` | Same cleanup, scoped to current feature-branch diff. |
| `/dreamers-research` | Deep research via Sage. |
| `/dreamers-issue` | Create structured GitHub issues with acceptance criteria. |
| `/dreamers-new-project` | Bootstrap a brand new project (discovery → stack → brief → shell plans). |
| `/dreamers-plan-verify` | Inline drift check on a plan vs current code. |
| `/dreamers-clean-work` | Between-milestone maintenance (improvements audit, archive, drift scan). |

## Pipeline shape

```
/dreamers-full <task | plan paths | manifest.md>
  ├─ Phase 1   → /dreamers-plan   (Mode 1 only: 3-phase planning conversation; plan/manifest modes skip)
  ├─ Phase 1.5 → Plan review / implementation-start gate (Mode 1 only)
  │               multi-plan approval includes INCREMENTAL vs ATOMIC choice
  │               plan/manifest modes skip this gate and default to ATOMIC unless explicitly supplied
  ├─ Phase 2   → per plan, inline:
  │               1. Write failing tests
  │               2. Implement
  │               3. Type-check + run tests
  │               4. Invoke /dreamers-review (full lane → artifacts → findings, read-only)
  │               5. Apply findings + major-refactor gate
  │               6. User-testing gate (when triggered; bug-fix review reruns use Vigil unless user selects another lane)
  │               ↳ between cycles: drift check + INCREMENTAL pre-PR gate / ATOMIC continuation
  └─ Phase 3   → close-out (inline + /dreamers-docs + /dreamers-pr)
                   improvements append → Echo docs → retro → final commit
                   → user approval gate → push + PR → plan archive → post-PR scan (no prompt)
```

`/dreamers-lite <task | plan paths>` uses one approval gate for compact plan approval plus implementation start in task mode. When passed plan path(s), it skips planning, plan writing, and implementation-start approval, then uses the supplied plan file(s) directly. `/dreamers-full` also skips planning when passed plan path(s) or a manifest; those modes skip Phase 1.5, default multi-plan strategy to ATOMIC unless explicitly supplied, and move straight to implementation after artifact checks. Lite replaces the full triad with Vigil's single artifact-backed review. `/dreamers-full` still runs the full triad once per plan, then uses Vigil for normal review reruns; extra triad or selected-lane reruns require a major-change gate and user choice. Vigil applies the same shared Hone architecture rubric used by Hone and must include a dedicated architecture audit section in its artifact. Both flows use the same durable `.dreamers/reviews/` handoff pattern. Lite validates tests/type-checks, surfaces full-refactor findings, runs user testing when triggered, and opens the PR through `/dreamers-pr`.

Each skill is independent — no skill invokes another mid-flow except `/dreamers-full`, which orchestrates the sequence. Refs in `.github/dreamers/refs/` are inlined into consumers at build time via `scripts/sync-refs.ps1` or `scripts/sync-refs.sh`. CI's `verify-refs` workflow fails any PR whose inlined content drifts from source.

## Maintaining Dreamers

Use `/dreamers-update` for changes to Dreamers system files. The Copilot repo (`C:\projects\dreamers-copilot`) is the upstream source of truth; the skill branches, applies, validates, commits, pushes, and opens the Copilot PR first. It then stops for user approval, supports repeated Copilot PR revisions, and transfers to Codex only after approval.

## Install

Install agents, skills, refs, and templates into your global `~/.copilot/` directory:

```powershell
.\Install-Dreamers.ps1
```

Options:
- `-Force` — overwrite existing files without prompting
- `-CopilotHome "D:\custom\.copilot"` — install to a custom location

Instruction files in `.github/instructions/` (including `dreamers.instructions.md`) are auto-loaded by Copilot CLI. The installer copies them to `~/.copilot/instructions/` for global use. Your personal `~/.copilot/copilot-instructions.md` is never touched.

## Uninstall

```powershell
.\Remove-Dreamers.ps1
```

Options:
- `-DryRun` — preview what would be removed without deleting
- `-CopilotHome "D:\custom\.copilot"` — target a custom location

## Project setup

For a new project that wants to use Dreamers, see [project-bootstrap.md](.github/dreamers/refs/project-bootstrap.md):

1. Ensure `.dreamers/` is in the project's `.gitignore`.
2. Create the project-level `.github/copilot-instructions.md` (auto-loaded by Copilot CLI).
3. Create `.dreamers/plans/` directory.
4. Copy `.github/instructions/comment-rules.instructions.md` into the project's `.github/instructions/`.
