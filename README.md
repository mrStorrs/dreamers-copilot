# Dreamers

An agent orchestration system for GitHub Copilot CLI and Codex. Dreamers runs the planning → implementation + tests → selected review → Vigil follow-up review → docs → PR flow.

The examples below use Copilot slash commands. In Codex, ask for the same skill by name, such as `dreamers-plan` or `dreamers-review`.

## Structure

The shared source keeps the Copilot layout under `.github/`:

```
.github/
├── agents/           # Reviewers and Echo
├── skills/           # Skill entry points
├── dreamers/
│   ├── refs/         # Shared reference docs (inlined into consumers at build time)
│   └── templates/    # Plan, manifest, PR description, and logging templates
├── instructions/     # Auto-loaded instruction files for Copilot
└── catalog.json      # Existing catalog paths and collections
```

Copilot catalog loading uses this source tree directly. Codex runtime differences live in `adapters/codex/`; `scripts/build-codex.py` generates the Codex skills, TOML agents, shared resources, a global instruction fragment, and package metadata. Generated output belongs in an ignored directory such as `.dreamers/build/` and is never edited by hand.

## Agents

| Agent | Type | Role |
|---|---|---|
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only except one `.dreamers/reviews/` artifact. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge cases, regression risk). Read-only except one `.dreamers/reviews/` artifact. |
| **Hone** | Subagent | Reviewer — simplicity, over-engineering, redundancy, architectural quality. Read-only except one `.dreamers/reviews/` artifact; surfaces full-refactor recommendations without softening. |
| **Vigil** | Subagent | Single-pass reviewer for lite plans, skill-internal reviews outside `/dreamers` and `/dreamers-review`, and `/dreamers` follow-up review reruns. Reviews correctness, security, maintainability, test coverage, and simplicity; writes one `.dreamers/reviews/` artifact with a required architecture audit section. |
| **Echo** | Subagent | Documentarian — Echo-owned sections of project docs, README, CHANGELOG. |

Vigil, Sentinel, Probe, and Hone spawn through `/dreamers-review` and each write a durable review artifact. The review skill selects Vigil for lite plans, Sentinel + Probe for standard plans, and Sentinel + Probe + Hone for complex plans unless the plan or user explicitly directs another lane. Without a plan, it infers the intended behavior from the user context, branch/PR metadata, diff, tests, and nearby code; if that evidence is ambiguous, it asks one concise question before reviewing. `/dreamers` applies findings and owns follow-up review, user-testing, and fix loops. Echo spawns per milestone via `/dreamers-docs`.

## Skills

Explicit user instructions can skip or alter skill phases/actions.

Use `/dreamers-help` or `/dreamers help` for read-only orientation. Empty or whitespace-only `/dreamers` input, `help`, `--help`, and `-h` route there before repository or external inspection or mutation.

Across Dreamers skills, an explicit user choice to defer a suggested change appends a structured entry to project-root `defered.md` without overwriting prior entries.

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers` | End-to-end pipeline. Accepts a task description, existing plan path(s), or manifest. Task mode invokes `/dreamers-plan`, then uses the plan review / implementation-start gate; plan path and manifest modes skip planning and the gate and treat supplied artifacts as human-approved input. Invokes `/dreamers-implement`, then `/dreamers-review`; the review skill selects reviewers from plan complexity or explicit plan/user direction. The orchestrator applies findings, appends deferred findings to project-root `defered.md`, owns user testing and fix loops, and preserves the original close-out through `/dreamers-docs`, pre-PR approval, and `/dreamers-pr`. |
| `/dreamers-help` | Read-only orientation, examples, reviewer lanes, gates, specialized choices, and migration guidance. |
| `/dreamers-plan` | 3-phase planning (interactive Hash-out → Write → Review). Runs Phase 1A Grill before proposal approval, stores every Grill question and response word for word in `grilling-transcript.md`, links it from each plan, selects lite / standard / complex, writes plans with Goal, Scope and context, and Acceptance Criteria, plus an optional manifest, then verifies coverage before the review gate. Hard-stops at the review gate. |
| `/dreamers-implement` | One-shot implementation: implement a task or approved plan with tests, then type-check and run tests. Exits at green tests; `/dreamers` invokes `/dreamers-review` next. |
| `/dreamers-review` | Selects reviewers from plan complexity or explicit plan/user direction. For plan-bound reviews, it reads the linked or sibling verbatim Grill transcript when present and supplies it as intent context. Without a plan it infers intent from code and context, asking if unclear. Read-only. |
| `/dreamers-docs` | Spawns Echo to update project docs based on the diff. Stages edits; user commits. |
| `/dreamers-pr` | Pushes the branch, opens the PR using the `pr-description.md` template, and archives shipped Dreamers plan artifacts. |
| `/dreamers-lite` | Task delivery without planning: implement + test, Vigil review (up to 2 fix cycles), docs from the uncommitted diff, commit, then PR approval. Halt on blocked review or unresolved findings at the cap. |
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
| `/dreamers-pr-resolve` | Resolve PR review comments inline; Vigil reviews accepted fixes, deferred findings go to project-root `defered.md`, and each comment gets a `fixed: in commit <SHA>`, `blocked: <reason>`, or `no-action: <reason>` reply. Only fully fixed threads are resolved. |
| `/dreamers-add-logging` | Phased pass to add/improve logging per `logging-standards.md`. |
| `/dreamers-cleanup-comments` | Project-wide comment cleanup per `comment-rules.md`. |
| `/dreamers-cleanup-comments-branch` | Same cleanup, scoped to current feature-branch diff. |
| `/dreamers-explain` | Thorough, read-only explanations of topics, code, documents, systems, and decisions, with authoritative sources when needed. |
| `/dreamers-issue` | Create structured GitHub issues with acceptance criteria. |
| `/dreamers-new-project` | Bootstrap a brand new project (discovery → optional existing-solutions research → stack → brief → shell plans). |
| `/dreamers-plan-verify` | Inline drift check on a plan vs current code. |
| `/dreamers-clean-work` | Between-milestone maintenance (improvements audit, archive, drift scan). |

## Pipeline shape

```
/dreamers <task | plan paths | manifest.md>
  ├─ Phase 1   → /dreamers-plan + plan review / implementation-start gate (task input only)
  │               multi-plan approval includes INCREMENTAL vs ATOMIC choice
  │               plan/manifest modes use supplied human-approved artifacts
  ├─ Phase 2   → per plan:
  │               Implement: /dreamers-implement (code + tests → type-check + test run)
  │               Review: /dreamers-review (reviewers selected from plan complexity or explicit direction)
  │               Apply findings + major-refactor gate (deferred → root defered.md)
  │               User-testing gate (when triggered; normal review reruns use Vigil)
  │               ↳ between cycles: drift check + INCREMENTAL pre-PR gate / ATOMIC continuation
  └─ Phase 3   → close-out (/dreamers-docs + final commit
                   → user approval gate → /dreamers-pr)
```

All plans use Goal, Scope and context, and Acceptance Criteria. Checks belong with their ACs; there are no separate Approach or Verification sections. Lite, standard, and complex label complexity for review routing. They select the initial review lane through `/dreamers-review`: Vigil; Sentinel + Probe; or Sentinel + Probe + Hone. Explicit plan or user direction overrides that mapping. The review skill and its reviewers are read-only for project files; reviewers write the required `.dreamers/reviews/` artifacts. `/dreamers` applies findings and owns revalidation, review-rerun gates, user testing, and fix loops.

`/dreamers` delivers plans; `/dreamers-lite` delivers tasks without planning. Both halt on blocked reviews or unresolved findings at their review caps (3 and 2 fix cycles, respectively). Refs in `.github/dreamers/refs/` are inlined into consumers at build time via `scripts/sync-refs.ps1` or `scripts/sync-refs.sh`.

Both delivery skills resume after conversational detours and keep one todo aligned with confirmed results. Related bug reports resume the existing `Implement and review loop` at step 1 without re-invoking the delivery skill, unless the user requests discussion or says otherwise. Corrections to an open PR repeat implementation, review, and the docs check before requesting approval to commit and push the update. Short standalone helper skills have optional todos.

The retired `/dreamers-full` command has no forwarding alias. The install and removal scripts prune its known managed files while preserving unrelated user files.

## Maintaining Dreamers

Use `/dreamers-update` for changes to Dreamers system files. Maintain shared behavior in `.github/` and Codex runtime adaptations in `adapters/codex/`. One branch and PR cover both targets; validate both before close-out. The existing `.github/catalog.json` paths, collections, and folder targets remain the Copilot catalog interface.

Codex installers generate and validate a temporary package before copying files, then clean up that package. To inspect a generated package separately, use Python 3.11 or newer (standard library only) and an empty destination:

```bash
python3 scripts/build-codex.py --output .dreamers/build/codex
```

PowerShell equivalent: `./scripts/Build-DreamersCodex.ps1 -OutputDirectory .dreamers/build/codex`. Choose a fresh or empty directory for each build; the generator refuses populated destinations. Builds translate runtime wiring and regenerate inlined refs from the shared sources, rejecting adapter drift and unsupported runtime tokens.

Validate with the scripts for your shell:

```bash
bash scripts/Test-DreamersCopilot.sh
bash scripts/Test-DreamersCodex.sh
```

```powershell
./scripts/Test-DreamersCopilot.ps1
./scripts/Test-DreamersCodex.ps1
```

CI validates the Copilot source and generated Codex package, with Codex PowerShell installation/removal checks on Ubuntu and Windows. The former Codex repository is no longer needed for future maintenance after adopting this workflow; this migration does not archive or delete it.

The update skill also refreshes an existing local Codex installation with the force flag after backing up its managed files, and verifies installed bytes against a fresh generated package. Global instruction updates preserve personal `AGENTS.md` content outside the managed block. Start a new Codex session to load refreshed skills, agents, and global instructions.

## Install

### Copilot

Install agents, skills, refs, and templates into your global `~/.copilot/` directory:

```powershell
.\Install-Dreamers.ps1
```

Options:
- `-Force` — overwrite existing files without prompting
- `-CopilotHome "D:\custom\.copilot"` — install to a custom location

Instruction files in `.github/instructions/` (including `dreamers.instructions.md`) are auto-loaded by Copilot CLI. The installer copies them to `~/.copilot/instructions/` for global use. Your personal `~/.copilot/copilot-instructions.md` is never touched.

### Codex

Requires Python 3.11 or newer. Install from this repository using Bash or PowerShell:

```bash
bash ./Install-DreamersCodex.sh
```

```powershell
./Install-DreamersCodex.ps1
```

The destination is `CODEX_HOME` when set, otherwise `~/.codex`. Use `--force` / `-Force` to refresh existing files, and `--codex-home <path>` / `-CodexHome <path>` for a custom destination. Without force, existing package files and an existing Dreamers global block are skipped. The migrated installers retain their managed-file cleanup and preserve unrelated skills, agents, and configuration.

The generated package places skills in `skills/`, agent TOMLs in `agents/`, and refs, templates, and compatibility instructions in `dreamers/`. Its root `AGENTS.md` fragment contains every translated global instruction source: system rules, laws, and comment rules, with Copilot `applyTo` frontmatter removed. Direct installers merge it into the Codex home's `AGENTS.md` between `<!-- BEGIN DREAMERS GLOBAL INSTRUCTIONS -->` and `<!-- END DREAMERS GLOBAL INSTRUCTIONS -->`. Codex loads this guidance globally, including sessions that do not invoke Dreamers. Skills retain explicit local instruction reads as a fallback for package-only installations without the global block.

A first install adds the block even when personal `AGENTS.md` instructions already exist; later refreshes require force. All personal bytes outside the block are preserved. Before changing an existing `AGENTS.md`, the installer creates and verifies a timestamped backup under this repository's `.dreamers/backups/codex-instructions/` and prints its location. An identical force refresh does not rewrite the file or create another backup.

Malformed or duplicate markers and a symlink `AGENTS.md` stop installation. A nonempty `AGENTS.override.md` also stops installation because it would mask the global file; reconcile that override before installing. Restart Codex after installation.

## Uninstall

Copilot:

```powershell
.\Remove-Dreamers.ps1
```

Options:
- `-DryRun` — preview what would be removed without deleting
- `-CopilotHome "D:\custom\.copilot"` — target a custom location

Codex (PowerShell, with Python 3.11 or newer available):

```powershell
./Remove-DreamersCodex.ps1 -DryRun
./Remove-DreamersCodex.ps1
```

Use `-CodexHome <path>` for a custom destination. The remover generates the managed-file inventory before removal and preserves unrelated files. It removes only the Dreamers block from global `AGENTS.md`, preserving personal text and backing up the existing file before a change. `-DryRun` leaves the file unchanged; an empty `AGENTS.md` created by installation may remain after removal.

## Project setup

For a new Copilot project, see [project-bootstrap.md](.github/dreamers/refs/project-bootstrap.md):

1. Ensure `.dreamers/` is in the project's `.gitignore`.
2. Create the project-level `.github/copilot-instructions.md` (auto-loaded by Copilot CLI).
3. Create `.dreamers/plans/` directory.
4. Copy `.github/instructions/dreamers.comment-rules.instructions.md` into the project's `.github/instructions/`.

For Codex projects, create or extend `AGENTS.md` and follow the generated `dreamers/refs/project-bootstrap.md` in the installed Codex home. Reference compatibility instruction files from the project instructions when needed.
