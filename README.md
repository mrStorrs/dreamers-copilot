# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers coordinates specialized AI agents through structured pipelines — planning, implementation, review, testing, and documentation — to deliver production-grade code changes.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Forge, Sentinel, Probe, Echo, Nova, Bolt, Sage)
├── skills/           # Skill entry points for each pipeline (dreamers-full, dreamers-fix, etc.)
├── dreamers/
│   ├── refs/         # Shared reference docs (delegation protocol, git workflow, quality gates, etc.)
│   └── templates/    # Plan templates, PR descriptions, logging standards
└── instructions/     # Auto-injected instruction files (comment rules, etc.)
```

## Agents

| Agent | Role | Model |
|-------|------|-------|
| **Forge** | Coder — implements changes against a plan | Sonnet |
| **Sentinel** | Reviewer (fix-on-sight, production-code lane) — correctness, security, maintainability | Sonnet |
| **Probe** | Tester (fix-on-sight, test-files lane) — derives tests from acceptance criteria | Sonnet |
| **Hone** | Simplifier (fix-on-sight, branch-diff scope, behavior-preserving) — readability, maintainability, redundancy reduction | Sonnet |
| **Nova** | Planning specialist (multi-mode: verify / replan / plan-new) | Opus |
| **Echo** | Documentarian — README, CHANGELOG, project-level `.github/copilot-instructions.md` (Echo-owned sections), project-specific docs | Haiku |
| **Bolt** | Runner — git ops, test execution, PR creation | Haiku |
| **Sage** | Researcher — deep multi-perspective research | Sonnet |

## Skills (Pipelines)

### Pipeline orchestrators
| Skill | Purpose |
|-------|---------|
| `dreamers-full` | Full pipeline: plan → implement → fix-on-sight Sentinel → fix-on-sight Probe → plan-verify → simplify → docs → PR |
| `dreamers-plan` | Planning only — produce a plan without implementing |
| `dreamers-implement` | Implement an existing approved plan |
| `dreamers-fix` | Bug triage and fix (Tier 1 quick / Tier 2 full pipeline) |

### Agent wrappers (ergonomic arg-flag invocation of a single agent)
| Skill | Purpose |
|-------|---------|
| `dreamers-review` | Sentinel-backed review with arg flags (`--branch`, `--paths`, `--all`); fix-on-sight in production-code lane |
| `dreamers-test` | Probe-backed test pass with arg flags; fix-on-sight in test-files lane |
| `dreamers-simplify` | Hone fix-on-sight (branch-diff scope, behavior-preserving) + project-defined test/lint pass |
| `dreamers-plan-verify` | Nova verify mode — lightweight applicability check on the next sub-plan; halts on drift |
| `dreamers-docs` | Echo-backed doc update with arg flags |

### Specialty pipelines
| Skill | Purpose |
|-------|---------|
| `dreamers-research` | Deep research with phased workflow |
| `dreamers-pr-resolve` | Resolve PR review comments |
| `dreamers-issue` | Create structured GitHub issues |
| `dreamers-new-project` | Bootstrap a new project |
| `dreamers-cleanup-comments` | Code comment cleanup pass |
| `dreamers-cleanup-comments-branch` | Branch-scoped comment cleanup for use inside parent pipelines |
| `dreamers-clean-work` | Between-milestone maintenance |
| `dreamers-add-logging` | Add production-grade logging |
| `dreamers-atlas-choice` | Route to the correct pipeline |

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
