# Dreamers

An agent orchestration system for GitHub Copilot CLI. Dreamers runs the planning → implementation + tests → selected review → Vigil follow-up review → docs → PR flow.

## Structure

Everything lives under `.github/`:

```
.github/
├── agents/           # Reviewers and Echo
├── skills/           # Skill entry points
├── dreamers/
│   ├── refs/         # Shared workflows and standards
│   └── templates/    # Plan, manifest, PR description, and logging templates
└── instructions/     # Auto-loaded instruction files
```

## Agents

| Agent | Type | Role |
|---|---|---|
| **Sentinel** | Subagent | Reviewer — correctness, security, maintainability. Read-only except one `.dreamers/reviews/` artifact. |
| **Probe** | Subagent | Reviewer — test coverage (AC matrix, layer audit, edge cases, regression risk). Read-only except one `.dreamers/reviews/` artifact. |
| **Hone** | Subagent | Reviewer — simplicity, over-engineering, redundancy, architectural quality. Read-only except one `.dreamers/reviews/` artifact; surfaces full-refactor recommendations without softening. |
| **Vigil** | Subagent | Single-pass reviewer for lite plans, skill-internal reviews outside `/dreamers` and `/dreamers-review`, and `/dreamers` follow-up review reruns. Reviews correctness, security, maintainability, test coverage, and simplicity; writes one `.dreamers/reviews/` artifact with a required architecture audit section. |
| **Echo** | Subagent | Documentarian — Echo-owned sections of project docs, README, CHANGELOG. |

Vigil, Sentinel, Probe, and Hone spawn through the shared `review-workflow.md` and each write a durable review artifact. The workflow selects Vigil for lite plans, Sentinel + Probe for standard plans, and Sentinel + Probe + Hone for complex plans unless the plan or user explicitly directs another lane. Without a plan, it infers the intended behavior from the user context, branch/PR metadata, diff, tests, and nearby code; if that evidence is ambiguous, it asks one concise question before reviewing. `/dreamers` applies findings and owns follow-up review, user-testing, and fix loops. Echo spawns per milestone through `documentation-workflow.md`. Standalone `/dreamers-review` and `/dreamers-docs` embed those same refs through XML sync.

## Skills

Every skill is an independent entry point. Shared behavior lives in workflow refs, synchronized into each consuming skill as XML blocks; skills never invoke other skills or load another skill's `SKILL.md`. Explicit user instructions can skip or alter phases/actions.

Use `/dreamers-help` or `/dreamers help` for read-only orientation. Empty or whitespace-only `/dreamers` input, `help`, `--help`, and `-h` use the embedded `help-workflow` block before repository or external inspection or mutation.

Across Dreamers skills, an explicit user choice to defer a suggested change appends a structured entry to project-root `defered.md` without overwriting prior entries.

### Pipeline

| Skill | Purpose |
|---|---|
| `/dreamers` | End-to-end pipeline. Accepts a task description, existing plan path(s), or manifest. Task mode executes the embedded `planning-workflow`, then uses the plan review / implementation-start gate; plan path and manifest modes skip planning and the gate and treat supplied artifacts as human-approved input. Executes the embedded `implementation-workflow`, then `review-workflow`; the review workflow selects reviewers from plan complexity or explicit plan/user direction. The orchestrator applies findings, appends deferred findings to project-root `defered.md`, owns user testing and fix loops, and preserves the original close-out through the documentation ref, pre-PR approval, and the PR ref. |
| `/dreamers-help` | Read-only orientation, examples, reviewer lanes, gates, specialized choices, and migration guidance. |
| `/dreamers-plan` | 3-phase planning (interactive Hash-out → Write → Review). Runs Phase 1A Grill before proposal approval, stores every Grill question and response word for word in `grilling-transcript.md`, links it from each plan, selects lite / standard / complex, writes plans with Goal, Scope and context, and Acceptance Criteria, plus an optional manifest, then verifies coverage before the review gate. Hard-stops at the review gate. |
| `/dreamers-implement` | One-shot implementation: implement a task or approved plan with tests, then type-check and run tests. Exits at green tests; `/dreamers` executes its embedded review workflow next. |
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
| `/dreamers-pr-resolve` | Resolve PR review comments inline; Vigil reviews accepted changes before thread resolution, and deferred Vigil findings are appended to project-root `defered.md`. |
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
  ├─ Phase 1   → planning-workflow.md + plan review / implementation-start gate (task input only)
  │               multi-plan approval includes INCREMENTAL vs ATOMIC choice
  │               plan/manifest modes use supplied human-approved artifacts
  ├─ Phase 2   → per plan:
  │               Implement: implementation-workflow.md (code + tests → type-check + test run)
  │               Review: review-workflow.md (reviewers selected from plan complexity or explicit direction)
  │               Apply findings + major-refactor gate (deferred → root defered.md)
  │               User-testing gate (when triggered; normal review reruns use Vigil)
  │               ↳ between cycles: drift check + INCREMENTAL pre-PR gate / ATOMIC continuation
  └─ Phase 3   → close-out (documentation-workflow.md + final commit
                   → user approval gate → pr-workflow.md)
```

All plans use Goal, Scope and context, and Acceptance Criteria. Checks belong with their ACs; there are no separate Approach or Verification sections. Lite, standard, and complex label complexity for review routing. They select the initial review lane through `review-workflow.md`: Vigil; Sentinel + Probe; or Sentinel + Probe + Hone. Explicit plan or user direction overrides that mapping. The review workflow and its reviewers are read-only for project files; reviewers write the required `.dreamers/reviews/` artifacts. `/dreamers` applies findings and owns revalidation, review-rerun gates, user testing, and fix loops.

`/dreamers` delivers plans; `/dreamers-lite` delivers tasks without planning. Both halt on blocked reviews or unresolved findings at their review caps (3 and 2 fix cycles, respectively). Workflow refs and shared standards in `.github/dreamers/refs/` are inlined into every consumer by `scripts/sync-refs.ps1` or `scripts/sync-refs.sh`. Consumers declare flat XML blocks and contain all required content after sync, with no runtime ref-file reads. Edit the source refs, run sync, and verify before shipping.

Both delivery skills resume after conversational detours and keep one todo aligned with confirmed results. Related bug reports resume the existing `Implement and review loop` at step 1 without re-invoking the delivery skill, unless the user requests discussion or says otherwise. Corrections to an open PR repeat implementation, review, and the docs check before requesting approval to commit and push the update. Every skill has a Required workflow checklist. Its stages drive one todo through the synced `workflow-progress` standard; conditional stages are added only when needed. Help uses a response checklist without creating a todo.

Workflow refs are reusable operation bodies with explicit inputs, boundaries, and results. Each skill owns its headings, todo, and transitions, placing the synced operation directly in the phase that uses it. Shared rules and formats appear once in a named section. Operation refs do not carry standalone-skill titles, todo setup, or delivery routing; the shared `workflow-progress` standard tracks the skill-owned checklist; template headings stay inside fenced examples. XML sync adds blank lines around each body for Markdown rendering. The same source body serves standalone and delivery skills without runtime file loading.

The retired `/dreamers-full` command has no forwarding alias. The install and removal scripts prune its known managed files while preserving unrelated user files.

Both delivery skills perform available automated and agent-operated checks first. User testing is requested only for required verification the agent cannot complete, or when the user explicitly wants to test personally. No plan flag is required. Missing build instructions or user-facing changes alone do not trigger a pause. User-reported bugs return to step 1 of the existing implementation, test, and review loop; active review counts and the branch are retained.

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
