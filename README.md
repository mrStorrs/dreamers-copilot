# Dreamers

A TDD-pipeline agent orchestration system for GitHub Copilot CLI. Dreamers runs the planning → tests-first → implementation → parallel-review → docs → PR flow with most work done inline by the orchestrator. Per cycle, three specialized read-only reviewers (Sentinel + Probe + Hone) spawn in parallel and return structured findings; the orchestrator applies fixes inline.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Sentinel, Probe, Hone, Echo, Sage)
├── skills/           # Skill entry points for each pipeline phase
├── dreamers/
│   ├── refs/         # Shared reference docs (TDD orchestrator discipline, git workflow, planning, etc.)
│   └── templates/    # Plan templates, PR descriptions, logging standards
└── instructions/     # Auto-injected instruction files (comment rules, etc.)
```

## Agents (5 total)

| Agent | Role | When invoked |
|-------|------|--------------|
| **Sentinel** | Reviewer (read-only / report-only). Three lenses: correctness, security, maintainability. | Per cycle in `/dreamers-implement`, parallel with Probe + Hone |
| **Probe** | Tester (read-only / report-only). Lens: test coverage (AC matrix, layer audit, edge + negative cases, regression risk). | Per cycle in `/dreamers-implement`, parallel with Sentinel + Hone |
| **Hone** | Simplifier (read-only / report-only). Lens: simplicity / over-engineering / redundancy (behavior-preserving). | Per cycle in `/dreamers-implement`, parallel with Sentinel + Probe |
| **Echo** | Documentarian — updates Echo-owned sections of `.github/copilot-instructions.md` plus other project docs (README, CHANGELOG, etc.). | At close-out via `/dreamers-docs` |
| **Sage** | Researcher — deep multi-perspective research. | Standalone via `/dreamers-research` |

The three reviewers (Sentinel + Probe + Hone) are spawned **in parallel** by `/dreamers-implement` and `/dreamers-pr-resolve`. All three are read-only; they return structured findings; the orchestrator applies fixes inline. Conflict-resolution rule: correctness > simplicity. Ambiguity surfaces to user.

## Skills (11 total)

### TDD pipeline (composable phases)

| Skill | Purpose | Invokable standalone? |
|-------|---------|----------------------|
| `dreamers-full` | Orchestrator — wires plan → implement → close-out together. Owns branch setup, umbrella-vs-cohesive routing, inline drift check between sub-plans. | Yes — full pipeline |
| `dreamers-plan` | Phase 1 — three-phase planning conversation, writes plan files, hard-stops at the approval gate. | Yes — plan only |
| `dreamers-implement` | Phase 2 — per-cycle loop (tests-first → implement → run → coverage sweep → Sentinel → optional user-test → commit). | Yes — with an approved plan |
| `dreamers-close-out` | Phase 3 wrapper — improvements append + docs + retro + final commit + user gate + push + PR + post-PR discipline. | Yes — at end of a milestone |
| `dreamers-docs` | Sub-phase — spawn Echo for project-doc updates. | Yes — ad-hoc doc update |
| `dreamers-pr` | Sub-phase — push + `gh pr create` + optional issue close. The single push of the milestone. | Yes — push & PR a branch |

### Orthogonal skills

| Skill | Purpose |
|-------|---------|
| `dreamers-research` | Deep research with phased workflow (Sage subagent). |
| `dreamers-pr-resolve` | Resolve PR review comments inline + Sentinel review of accepted changes. |
| `dreamers-issue` | Create structured GitHub issues with acceptance criteria. |
| `dreamers-new-project` | Bootstrap a brand new project (discovery → tech stack → brief → shell plans). |
| `dreamers-clean-work` | Between-milestone maintenance (improvements audit, plan archive, drift scan). |

## Pipeline shape

```
/dreamers-full
  ├─ Phase 1 → /dreamers-plan         (three-phase planning conversation, exit at Phase 1g approval)
  ├─ Phase 2 → /dreamers-implement    (per cycle)
  │             1. write failing tests
  │             2. implement inline
  │             3. type-check + run tests
  │             4. coverage sweep
  │             5. spawn Sentinel + Probe + Hone in PARALLEL  ← three read-only reviewers
  │             6. apply combined findings inline; re-run tests
  │             7. optional user-test pause
  │             8. commit
  │             ↳ loops per sub-plan in umbrella mode, with inline drift check between
  └─ Phase 3 → /dreamers-close-out    (improvements append + retro + final commit + push + PR)
                ├─ /dreamers-docs     (spawns Echo)
                └─ /dreamers-pr       (single push + PR creation)
```

Most work is inline in the orchestrator. Per cycle, three reviewers spawn in parallel; per milestone, Echo spawns once:
- **Sentinel + Probe + Hone** — parallel review, each on one lens. Read-only / report-only. Orchestrator applies the combined findings.
- **Echo** — once per milestone, updates project docs.

## Install

Install agents, skills, refs, and templates into your global `~/.copilot/` directory:

```powershell
.\Install-Dreamers.ps1
```

Options:
- `-Force` — overwrite existing files without prompting
- `-CopilotHome "D:\custom\.copilot"` — install to a custom location

### Instruction files

Instruction files in `.github/instructions/` (including the Dreamers kernel `dreamers.instructions.md`) are auto-loaded by Copilot CLI. The installer copies them to `~/.copilot/instructions/` for global use; a project-scoped loader can drop the same files into a target repo's `.github/instructions/` instead. Either way, your personal `~/.copilot/copilot-instructions.md` is never touched.

## Uninstall

Remove only Dreamers-managed files from `~/.copilot/`:

```powershell
.\Remove-Dreamers.ps1
```

Options:
- `-DryRun` — preview what would be removed without deleting
- `-CopilotHome "D:\custom\.copilot"` — target a custom location

The uninstaller removes only files the installer placed (agents, skills, refs, templates, and the Dreamers instruction files in `~/.copilot/instructions/`). Your personal `copilot-instructions.md` is never touched.

## Project setup

When bootstrapping a new project to use Dreamers, see the [project bootstrap ref](.github/dreamers/refs/project-bootstrap.md) for the checklist:

1. Ensure `.dreamers/` is in the project's `.gitignore`
2. Create the project-level `.github/copilot-instructions.md` (Copilot CLI auto-loads this for the project)
3. Create `.dreamers/plans/` directory
4. Copy instruction files to `.github/instructions/`
