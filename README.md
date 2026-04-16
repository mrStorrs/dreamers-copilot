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
| **Sentinel** | Reviewer — correctness, security, maintainability | Sonnet |
| **Probe** | Tester — derives tests from acceptance criteria | Sonnet |
| **Echo** | Documentarian — READMEs, changelogs, ADRs | Haiku |
| **Nova** | Replanner — re-verifies remaining plans between sub-plan cycles | Opus |
| **Bolt** | Runner — git ops, test execution, PR creation | Haiku |
| **Sage** | Researcher — deep multi-perspective research | Sonnet |

## Skills (Pipelines)

| Skill | Purpose |
|-------|---------|
| `dreamers-full` | Full pipeline: plan → implement → review → test → document → PR |
| `dreamers-plan` | Planning only — produce a plan without implementing |
| `dreamers-implement` | Implement an existing approved plan |
| `dreamers-fix` | Bug triage and fix |
| `dreamers-research` | Deep research with phased workflow |
| `dreamers-pr-resolve` | Resolve PR review comments |
| `dreamers-issue` | Create structured GitHub issues |
| `dreamers-new-project` | Bootstrap a new project |
| `dreamers-cleanup-comments` | Code comment cleanup pass |
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

The installer manages your `copilot-instructions.md` safely:
- **New install:** creates the file with the Dreamers section
- **Existing file:** appends a marked Dreamers section (your personal instructions are never touched)
- **Re-install/update:** replaces only the marked section between `DREAMERS-START` / `DREAMERS-END` markers

### Instruction files

Instruction files (`.github/instructions/`) are repo-local — Copilot auto-injects them when working on matching files. Copy them into each project that uses Dreamers:

```powershell
Copy-Item -Recurse .github\instructions\ <your-project>\.github\instructions\
```

## Uninstall

Remove only Dreamers-managed files from `~/.copilot/`:

```powershell
.\Remove-Dreamers.ps1
```

Options:
- `-DryRun` — preview what would be removed without deleting
- `-CopilotHome "D:\custom\.copilot"` — target a custom location

The uninstaller strips only the marked Dreamers section from `copilot-instructions.md` — your personal instructions remain intact.

## Project setup

When bootstrapping a new project to use Dreamers, see the [project bootstrap ref](.github/dreamers/refs/project-bootstrap.md) for the checklist:

1. Ensure `.dreamers/` is in the project's `.gitignore`
2. Create the project-level `CLAUDE.md`
3. Create `.dreamers/plans/` directory
4. Copy instruction files to `.github/instructions/`
