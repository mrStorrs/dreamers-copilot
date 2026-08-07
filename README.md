# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers runs the planning → tests-first → implementation → selected review → Vigil follow-up review → docs → PR flow.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Forge, Nova personas; reviewers, Echo, Sage)
├── skills/           # Skill entry points
├── dreamers/
│   ├── refs/         # Shared reference docs (inlined into consumers at build time)
│   └── templates/    # Plan guide selector, lite/standard/complex guides, PR description shape, etc.
└── instructions/     # Auto-loaded instruction files
```

## Agents

| Agent | Type | Role |
|---|---|---|
| **Forge** | Persona | Implementation orchestrator. Routes user requests to the right skill. `/agents forge`. |
| **Nova** | Persona | Planning specialist. Mirrors `/dreamers-plan`, stores every Grill question and response verbatim beside the plans, and writes right-sized plans that link that transcript. `/agents nova`. |
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only except one `.dreamers/reviews/` artifact. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge cases, regression risk). Read-only except one `.dreamers/reviews/` artifact. |
| **Hone** | Subagent | Reviewer — simplicity, over-engineering, redundancy, architectural quality. Read-only except one `.dreamers/reviews/` artifact; surfaces full-refactor recommendations without softening. |
| **Vigil** | Subagent | Single-pass reviewer for lite plans, skill-internal reviews outside `/dreamers` and `/dreamers-review`, and `/dreamers` follow-up review reruns. Combines Sentinel, Probe, and the shared Hone architecture rubric; writes one `.dreamers/reviews/` artifact with a required architecture audit section. |
| **Echo** | Subagent | Documentarian — Echo-owned sections of project docs, README, CHANGELOG. |
| **Sage** | Subagent | Researcher — deep multi-perspective research. |

Vigil, Sentinel, Probe, and Hone spawn through `/dreamers-review` and each write a durable review artifact. The review skill selects Vigil for lite plans, Sentinel + Probe for standard plans, and Sentinel + Probe + Hone for complex plans unless the plan or user explicitly directs another lane. Without a plan, it infers the intended behavior from the user context, branch/PR metadata, diff, tests, and nearby code; if that evidence is ambiguous, it asks one concise question before reviewing. `/dreamers` applies findings and owns follow-up review, user-testing, and fix loops. A second triad or selected lane remains user-gated for major-change reruns. Echo spawns per milestone via `/dreamers-docs`. Sage is invoked by `/dreamers-research`.

## Skills

Explicit user instructions can skip or alter skill phases/actions.

Across Dreamers skills, an explicit user choice to defer a suggested change appends a structured entry to project-root `defered.md` without overwriting prior entries.

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers` | End-to-end pipeline. Accepts a task description, existing plan path(s), or manifest. Task mode invokes `/dreamers-plan`, then uses the plan review / implementation-start gate; plan path and manifest modes skip planning and the gate, then use supplied artifacts after plan-quality checks. Invokes `/dreamers-implement`, then `/dreamers-review`; the review skill selects reviewers from plan complexity or explicit plan/user direction. The orchestrator applies findings, appends deferred findings to project-root `defered.md`, owns user testing and fix loops, and preserves the original close-out through `/dreamers-docs`, pre-PR approval, and `/dreamers-pr`. |
| `/dreamers-plan` | 3-phase planning (interactive Hash-out → Write → Review). Runs Phase 1A Grill before proposal approval, stores every Grill question and response word for word in `grilling-transcript.md`, links it from each plan, selects lite / standard / complex, writes right-sized plan file(s) + optional manifest, then verifies coverage before the review gate. Hard-stops at the review gate. |
| `/dreamers-implement` | One-shot implementation: write failing tests, implement, type-check, and run tests. Exits at green tests; `/dreamers` invokes `/dreamers-review` next. |
| `/dreamers-review` | Selects reviewers from plan complexity or explicit plan/user direction. For plan-bound reviews, it reads the linked or sibling verbatim Grill transcript when present and supplies it as intent context. Without a plan it infers intent from code and context, asking if unclear. Read-only. |
| `/dreamers-docs` | Spawns Echo to update project docs based on the diff. Stages edits; user commits. |
| `/dreamers-pr` | Pushes the branch, opens the PR using the `pr-description.md` template, and archives shipped Dreamers plan artifacts. |
| `/dreamers-lite` | Self-contained lightweight bug-fix pipeline: branch + regression test + implement + run tests. Escalates to `/dreamers` on scope blowup. |
| `/dreamers-find-refactors` | Refactor discovery pipeline. Selects refactor lenses, sections the repo, runs section-scoped Hone audits, synthesizes findings, writes Dreamers plan files, and stops. No implementation, branch, commit, push, or PR. |

### Focused Vigil audit wrappers

`/dreamers-test` and `/dreamers-simplify` call Vigil with a focused prompt for test coverage or simplicity. Use `/dreamers-review --lens <name>` only when the user explicitly asks for a selected Sentinel/Probe/Hone lane.

### Review lanes

| Lane | Reviewers | Normal use |
|---|---|---|
| `vigil` | Vigil | Lite plan or explicit request. |
| `sentinel` | Sentinel | Explicit correctness/security/maintainability audit through `/dreamers-review`. |
| `probe` | Probe | Test coverage, AC/layer coverage, regression-risk audit. |
| `hone` | Hone | Simplicity, architecture, over-engineering audit. |
| `standard` | Sentinel + Probe | Standard plan or explicit combined correctness and coverage audit. |
| `full` | Sentinel + Probe + Hone | Complex plan, explicit full review, or standalone default. |

### Utility + orthogonal

| Skill | Purpose |
|---|---|
| `/dreamers-pr-resolve` | Resolve PR review comments inline; Vigil reviews accepted changes before thread resolution, and deferred Vigil findings are appended to project-root `defered.md`. |
| `/dreamers-add-logging` | Phased pass to add/improve logging per `logging-standards.md`. |
| `/dreamers-cleanup-comments` | Project-wide comment cleanup per `comment-rules.md`. |
| `/dreamers-cleanup-comments-branch` | Same cleanup, scoped to current feature-branch diff. |
| `/dreamers-explain` | Thorough, read-only explanations of topics, code, documents, systems, and decisions, with authoritative sources when needed. |
| `/dreamers-research` | Deep research via Sage. |
| `/dreamers-issue` | Create structured GitHub issues with acceptance criteria. |
| `/dreamers-new-project` | Bootstrap a brand new project (discovery → optional existing-solutions research → stack → brief → shell plans). |
| `/dreamers-plan-verify` | Inline drift check on a plan vs current code. |
| `/dreamers-clean-work` | Between-milestone maintenance (improvements audit, archive, drift scan). |

## Pipeline shape

```
/dreamers <task | plan paths | manifest.md>
  ├─ Phase 1   → /dreamers-plan   (Mode 1 only: Grill + right-sized planning; plan/manifest modes skip)
  ├─ Phase 1.5 → Plan review / implementation-start gate (Mode 1 only)
  │               multi-plan approval includes INCREMENTAL vs ATOMIC choice
  │               plan/manifest modes skip this gate and default to ATOMIC unless explicitly supplied
  ├─ Phase 2   → per plan:
  │               1–3. Invoke /dreamers-implement (failing tests → implementation → type-check + tests)
  │               4. Invoke /dreamers-review (reviewers selected from plan complexity or explicit direction)
  │               5. Apply findings + major-refactor gate (deferred → root defered.md)
  │               6. User-testing gate (when triggered; normal review reruns use Vigil)
  │               ↳ between cycles: drift check + INCREMENTAL pre-PR gate / ATOMIC continuation
  └─ Phase 3   → close-out (improvements + /dreamers-docs + retro + final commit
                   → user approval gate → /dreamers-pr → post-PR scan)
```

Lite, standard, and complex are plan-depth labels. They select the initial review lane through `/dreamers-review`: Vigil; Sentinel + Probe; or Sentinel + Probe + Hone. Explicit plan or user direction overrides that mapping. The review skill and its reviewers are read-only for project files; reviewers write the required `.dreamers/reviews/` artifacts. `/dreamers` applies findings and owns revalidation, review-rerun gates, user testing, and fix loops.

`/dreamers` is the only end-to-end pipeline. It invokes the specialized skills in order while preserving the original full-pipeline gates and close-out. Refs in `.github/dreamers/refs/` are inlined into consumers at build time via `scripts/sync-refs.ps1` or `scripts/sync-refs.sh`.

The retired `/dreamers-full` command has no forwarding alias. The install and removal scripts prune its known managed files while preserving unrelated user files.

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
4. Copy `.github/instructions/dreamers.comment-rules.instructions.md` into the project's `.github/instructions/`.
