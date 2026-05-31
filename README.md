# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers runs the planning → tests-first → implementation → parallel-review → docs → PR flow.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Forge, Nova personas; Sentinel, Probe, Hone, Echo, Sage subagents)
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
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge cases, regression risk). Read-only. |
| **Hone** | Subagent | Reviewer — simplicity, over-engineering, redundancy, architectural quality. Read-only; surfaces full-refactor recommendations without softening. |
| **Echo** | Subagent | Documentarian — Echo-owned sections of project docs, README, CHANGELOG. |
| **Sage** | Subagent | Researcher — deep multi-perspective research. |

Sentinel + Probe + Hone spawn in parallel per cycle via `/dreamers-review`. Echo spawns per milestone via `/dreamers-docs`. Sage is invoked by `/dreamers-research`.

## Skills

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers-full` | End-to-end pipeline. Invokes `/dreamers-plan`, halts for plan review / implementation start, implements each plan inline (tests-first), invokes `/dreamers-review`, applies findings with major-refactor gate, halts for user testing when triggered, then close-out (inline + `/dreamers-docs` + pre-PR approval + `/dreamers-pr`). |
| `/dreamers-plan` | 3-phase planning (interactive Hash-out → Write → Review). Critiques the proposal before approval, then writes plan file(s) + optional manifest. Hard-stops at the review gate. |
| `/dreamers-implement` | One-shot implementation: write failing tests, implement, run tests. Exits at green tests. |
| `/dreamers-review` | Spawns Sentinel + Probe + Hone in parallel; reports structured findings. Read-only. `--lens <name>` for a single-lens audit. |
| `/dreamers-docs` | Spawns Echo to update project docs based on the diff. Stages edits; user commits. |
| `/dreamers-pr` | Pushes the branch and opens the PR using the `pr-description.md` template. |
| `/dreamers-fix` | Self-contained bug-fix pipeline: branch + regression test + implement + run tests. Escalates to `/dreamers-full` on scope blowup. |

### Single-lens reviewer wrappers (legacy aliases)

`/dreamers-review --lens sentinel` (or `probe`/`hone`) covers the same ground. The standalone skills `dreamers-test` (Probe) and `dreamers-simplify` (Hone) remain as convenient aliases.

### Utility + orthogonal

| Skill | Purpose |
|---|---|
| `/dreamers-pr-resolve` | Resolve PR review comments inline; parallel review of accepted changes. |
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
  ├─ Phase 1   → /dreamers-plan   (Mode 1 only: 3-phase planning conversation)
  ├─ Phase 1.5 → Plan review / implementation-start gate
  │               multi-plan approval includes INCREMENTAL vs ATOMIC choice
  ├─ Phase 2   → per plan, inline:
  │               1. Write failing tests
  │               2. Implement
  │               3. Type-check + run tests
  │               4. Invoke /dreamers-review (triad → findings, read-only)
  │               5. Apply findings + major-refactor gate
  │               6. User-testing gate (when triggered)
  │               ↳ between cycles: drift check + INCREMENTAL pre-PR gate / ATOMIC continuation
  └─ Phase 3   → close-out (inline + /dreamers-docs + /dreamers-pr)
                   improvements append → Echo docs → retro → final commit
                   → user approval gate → push + PR → plan archive → post-PR scan (no prompt)
```

Each skill is independent — no skill invokes another mid-flow except `/dreamers-full`, which orchestrates the sequence. Refs in `.github/dreamers/refs/` are inlined into consumers at build time via `scripts/sync-refs.ps1`. CI's `verify-refs` workflow fails any PR whose inlined content drifts from source.

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
