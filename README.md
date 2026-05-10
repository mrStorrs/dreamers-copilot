# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers coordinates specialized AI agents through structured pipelines — planning, implementation, review, testing, and documentation — to deliver production-grade code changes.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Agent definitions (Forge, Sentinel, Probe, Echo, Nova, Bolt, Sage)
├── skills/           # Skill entry points for each pipeline (dreamers-full, dreamers-fix, etc.)
├── scripts/          # Bash helper scripts called by skills/refs (see Scripts section)
├── dreamers/
│   ├── refs/         # Shared reference docs (delegation protocol, git workflow, quality gates, etc.)
│   └── templates/    # Plan templates, PR descriptions, logging standards
└── instructions/     # Auto-injected instruction files (comment rules, etc.)
```

## Scripts

A small set of bash scripts in `.github/scripts/` handle the routines where the LLM most often got things wrong (GraphQL string assembly, mechanical lint checklists). Skills call them as `~/.copilot/dreamers/scripts/<name>.sh`. Everything else stays as inline bash inside the skills/refs.

| Script | Purpose |
|--------|---------|
| `dreamers-pr-unresolved.sh <PR#>` | JSON of unresolved review threads (GraphQL, since REST `resolved` is unreliable). |
| `dreamers-pr-resolve-thread.sh <threadId>` | Resolve one review thread via the `resolveReviewThread` mutation. |
| `dreamers-plan-lint.sh [<plan-path>]` | Lint the mechanical subset of the plan quality checklist (filename, sections, status, code-block rules). |
| `dreamers-catalog-lint.sh` | Verify `catalog.json` matches the actual `agents/` + `skills/` tree. Dev-time check for this repo. |
| `dreamers-deps-check.sh` | Verify the tools listed below are installed and `gh` is authenticated. |

### Dependencies

The scripts deliberately add **zero new runtime dependencies** beyond what Dreamers already needed for its inline bash. Run `dreamers-deps-check.sh` (or `/dreamers-setup`) to verify:

- **`bash`** — Git Bash on Windows is sufficient; WSL works.
- **`git`** — used by `dreamers-catalog-lint.sh`.
- **`gh`** — required by the PR scripts. Must be authenticated (`gh auth login`).
- **`python3`** — **only** `dreamers-catalog-lint.sh`, which is a dev-time tool for this repo. End users running pipelines do not need Python. The Microsoft Store `python3` stub on Windows does NOT work — install real Python and put it on PATH ahead of the stub.
- **POSIX coreutils** (`sed`, `awk`, `grep`) — bundled with any bash environment.

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
| `dreamers-setup` | Detect missing script dependencies (via `dreamers-deps-check.sh`) and walk the user through installing them with OS-appropriate commands |

## Install

Install agents, skills, refs, scripts, and templates into your global `~/.copilot/` directory:

```powershell
.\Install-Dreamers.ps1
```

Then prepare the environment for the bash scripts. Two options:

- **Guided (recommended):** run `/dreamers-setup` in Copilot CLI. The skill detects missing tools, proposes OS-appropriate install commands, and confirms each one with you before running it.
- **Verify-only:** run the dep-check script directly — no installs, just a pass/fail report:
  ```bash
  ~/.copilot/dreamers/scripts/dreamers-deps-check.sh
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
