# Dreamers — GitHub Copilot CLI

An agent orchestration system for GitHub Copilot CLI. Runs the planning → tests-first → implementation → parallel-review → docs → PR flow.

## Quick start

```powershell
.\Install-Dreamers.ps1
```

Then invoke any skill from Copilot CLI: `/dreamers-full <task>`, `/dreamers-plan <task>`, `/dreamers-fix <bug>`, etc.

## Layout

```
.github/
├── agents/       # Agent definitions
├── skills/       # Skill entry points (/dreamers-*)
├── dreamers/
│   ├── refs/     # Shared reference docs inlined into consumers at build time
│   └── templates/# Plan, manifest, PR description, logging standards, etc.
└── instructions/ # Auto-loaded instruction files (Copilot CLI picks these up)
```

Refs in `dreamers/refs/` are the single source of truth. They're inlined into skill and agent files via `<tag>...</tag>` markers and synced by `scripts/sync-refs.ps1`. CI's `verify-refs` workflow fails PRs that drift.

## Agents

| Agent | Type | Role |
|---|---|---|
| **Forge** | Persona | Implementation orchestrator. Enter via `/agents forge` for a session pre-loaded with the pipeline. Routes user intent to the right skill. |
| **Nova** | Persona | Planning specialist. Enter via `/agents nova` for a multi-turn planning session. Hard-stops at the approval gate; does not implement. |
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only; returns structured findings. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge + negative cases, regression risk). Read-only. |
| **Hone** | Subagent | Reviewer — over-engineering, redundancy, bad architecture. Surfaces full-refactor recommendations without softening. Read-only. |
| **Echo** | Subagent | Documentarian — README, CHANGELOG, Echo-owned sections of `copilot-instructions.md`. Stages edits; never commits. |
| **Sage** | Subagent | Researcher — deep multi-perspective research with citation verification. |

Sentinel + Probe + Hone spawn in parallel per cycle via `/dreamers-review`. Echo spawns per milestone via `/dreamers-docs`. Sage is invoked by `/dreamers-research`.

## Skills

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers-full <task | plan paths | manifest>` | End-to-end pipeline: plan → implement → review → user-test → ship. |
| `/dreamers-plan <task>` | 3-phase planning (Hash-out → Write → Review). Produces plan file(s) + optional manifest. Hard-stops at approval. |
| `/dreamers-implement <plan>` | One cycle against an approved plan: failing tests → code → run tests. Exits at green tests. |
| `/dreamers-review` | Spawns Sentinel + Probe + Hone in parallel. Read-only structured findings. `--lens <name>` for single-lens audit. |
| `/dreamers-docs` | Spawns Echo to update project docs from the diff. `--branch` or `--staged` scope. |
| `/dreamers-pr` | Pushes the branch, drafts the PR body from the template, opens the PR via `gh`. |
| `/dreamers-fix <bug>` | Lightweight bug-fix pipeline: branch + regression test + implement + run tests. Escalates to `/dreamers-full` on scope blowup. |

### Standalone reviewer audits

| Skill | Purpose |
|---|---|
| `/dreamers-test` | Probe-only audit — test coverage findings on the current diff. |
| `/dreamers-simplify` | Hone-only audit — over-engineering and architectural findings. |

### Utility

| Skill | Purpose |
|---|---|
| `/dreamers-pr-resolve [#PR]` | Resolve unresolved PR review comments. Apply accepted fixes inline; parallel review of accepted changes. |
| `/dreamers-research <topic>` | Deep research via Sage: scoping → parallel sub-topic research → synthesis. |
| `/dreamers-issue <task>` | Create a structured GitHub issue with acceptance criteria. Prefix with `#` for discussion mode. |
| `/dreamers-new-project` | Bootstrap a new project: discovery → stack → brief → shell plans. |
| `/dreamers-cleanup-comments` | Project-wide comment cleanup per `comment-rules.md`. Audit → approve → apply. |
| `/dreamers-cleanup-comments-branch` | Same cleanup, scoped to the current feature-branch diff. |
| `/dreamers-add-logging` | Phased pass to add/improve logging per `logging-standards.md`. |
| `/dreamers-clean-work` | Between-milestone maintenance: archive merged plans, audit improvements, scan for drift. |
| `/dreamers-plan-verify <plan>` | Inline drift check: cited paths / signatures / data shapes still hold? |

## Pipeline shape (`/dreamers-full`)

```
Phase 1   → /dreamers-plan        (planning conversation, only in task-description mode)
Phase 1.5 → Ship-strategy gate    (INCREMENTAL vs ATOMIC, multi-plan only)
Phase 2   → per plan, inline:
              1. Write failing tests
              2. Implement
              3. Type-check + run tests
              4. /dreamers-review  (triad in parallel → structured findings)
              5. Apply findings    (major-refactor gate prompts on big fixes)
              6. User-testing gate
Phase 3   → Close-out
              improvements append → /dreamers-docs → retro → final commit
              → user approval gate → /dreamers-pr → plan archive → post-PR scan
```

Each skill is independent — no skill invokes another mid-flow except `/dreamers-full`, which orchestrates the sequence.

## Install / uninstall

```powershell
.\Install-Dreamers.ps1          # copies files into ~/.copilot/
.\Install-Dreamers.ps1 -Force   # overwrite existing files

.\Remove-Dreamers.ps1           # remove Dreamers-owned files
.\Remove-Dreamers.ps1 -DryRun   # preview only
```

Instruction files in `.github/instructions/` are auto-loaded by Copilot CLI once installed.

## Project setup

For a project that wants to use Dreamers, see [`dreamers/refs/project-bootstrap.md`](dreamers/refs/project-bootstrap.md):

1. Add `.dreamers/` to the project's `.gitignore`.
2. Create the project-level `.github/copilot-instructions.md` (auto-loaded by Copilot CLI).
3. Create `.dreamers/plans/` for plan files.
4. Copy `instructions/comment-rules.instructions.md` into the project's `.github/instructions/`.
