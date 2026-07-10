# Dreamers

Dreamers is an adaptive agent-orchestration system for GitHub Copilot CLI. One delivery entry point combines right-sized planning, tests-first implementation, proportional artifact-backed review, triggered user testing and documentation, and approved PR creation.

## Quick start

Use the primary delivery skill with a task, approved plan paths, or a manifest:

~~~text
/dreamers add offline export
/dreamers --no-grill fix the settings copy
/dreamers feature-search/plan-01-indexing.md
/dreamers feature-search/manifest.md
~~~

Empty or whitespace-only /dreamers input, help, --help, and -h route directly to the read-only /dreamers-help guide before any repository or external inspection or mutation.

Task descriptions invoke /dreamers-plan and Grill by default. The --no-grill flag or unmistakable direction such as "do not grill" or "skip the interview" suppresses the interview without weakening proposal review or plan quality. Supplied plan paths and manifests preserve their sequence and skip Grill, replanning, rewriting, and implementation-start approval while retaining artifact quality and drift checks.

## Layout

~~~text
.github/
├── agents/           # Forge and Nova personas; reviewer, docs, and research roles
├── skills/           # /dreamers plus specialized skill entry points
├── dreamers/
│   ├── refs/         # Shared policies synchronized into consumers
│   └── templates/    # Plan guides, manifest, PR, and testing templates
└── instructions/     # Auto-loaded Copilot CLI policy
~~~

## Adaptive delivery

The delivery orchestrator decides these checkpoints independently and surfaces a one-sentence rationale:

- Plan depth: lite, standard, or complex.
- Ship strategy: INCREMENTAL or ATOMIC.
- Initial reviewer lane and any rerun.
- Documentation need.
- Retrospective and improvements need.

Explicit user overrides remain authoritative. Routine decisions proceed without a confirmation gate; genuine ambiguity returns to the user.

### Review selection

| Plan or risk | Initial lane |
|---|---|
| Low-risk lite or standard | Vigil |
| Complex | Sentinel + Probe + Hone through /dreamers-review |
| A danger trigger in the shared closed rubric | Sentinel + Probe + Hone, regardless of plan size |

Vigil combines correctness, security, maintainability, test coverage, and the shared Hone architecture rubric in one artifact. Sentinel, Probe, and Hone each write their own artifact. Reviewers never apply fixes; the orchestrator reads the artifacts, applies accepted findings inline, and revalidates.

The danger rubric covers security, authentication, authorization, privacy, payment, secret, and permission changes; schema, migration, persistence, destructive-data, concurrency, and irreversible-side-effect changes; public or breaking API, dependency, build, distribution, and cross-subsystem changes; and rollback that requires operator action or data recovery. Anything outside that list is not silently escalated; genuine ambiguity returns to the user.

The mandatory delivery gates are plan approval for task input, major scope expansion, triggered user testing, and final pre-PR approval. Plan approval also authorizes implementation; there is no second start gate.

Documentation runs when the landed diff is user-facing or otherwise documentable. A retrospective and improvements entry is written only for multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or an explicit request; otherwise the skip is recorded.

## Agents

| Agent | Type | Role |
|---|---|---|
| Forge | Persona | Routes implementation work to the appropriate Dreamers skill. Enter with /agents forge. |
| Nova | Persona | Runs default-on Grill, right-sized planning, and plan approval. Enter with /agents nova. |
| Sentinel | Subagent | Correctness, security, and maintainability reviewer. |
| Probe | Subagent | AC coverage, layer, edge-case, and regression reviewer. |
| Hone | Subagent | Simplicity, architecture, redundancy, and over-engineering reviewer. |
| Vigil | Subagent | Proportional single-agent review for low-risk plans and normal reruns. |
| Echo | Subagent | Updates project documentation from the actual diff. |
| Sage | Subagent | Conducts citation-backed research. |

Every reviewer writes a durable .dreamers/reviews artifact. Echo is invoked through /dreamers-docs and Sage through /dreamers-research.

## Skills

### Delivery and planning

| Skill | Purpose |
|---|---|
| /dreamers | Adaptive end-to-end delivery for task text, approved plans, and manifests. |
| /dreamers-help | Read-only system guide, examples, overrides, and command selection. |
| /dreamers-plan | Default-on Grill, proposal critique, right-sized plan writing, and plan approval; never implements. |
| /dreamers-implement | One approved plan cycle: failing tests, implementation, and automated validation. |
| /dreamers-review | Read-only Sentinel, Probe, Hone, selected-lens, or full-triad review. |
| /dreamers-docs | Echo documentation pass scoped to a branch or staged diff. |
| /dreamers-pr | Push once, draft the PR body, open the PR, and archive shipped plan artifacts. |
| /dreamers-fix | Bounded regression-first bug-fix workflow; recommends /dreamers if scope expands. |
| /dreamers-find-refactors | Read-only Hone-based refactor discovery that writes plans and stops. |

### Focused and utility workflows

| Skill | Purpose |
|---|---|
| /dreamers-test | Focused Vigil test-coverage audit. |
| /dreamers-simplify | Focused Vigil architecture and over-engineering audit. |
| /dreamers-pr-resolve | Apply accepted PR feedback, run Vigil, and resolve review threads. |
| /dreamers-research | Deep research through Sage. |
| /dreamers-issue | Create a structured GitHub issue with acceptance criteria. |
| /dreamers-new-project | Bootstrap project discovery, brief, and shell plans. |
| /dreamers-plan-verify | Drift-check an existing plan against current code. |
| /dreamers-add-logging | Audit and improve logging under the shared standards. |
| /dreamers-cleanup-comments | Project-wide comment cleanup. |
| /dreamers-cleanup-comments-branch | Feature-branch comment cleanup. |
| /dreamers-clean-work | Between-milestone workspace and improvement maintenance. |
| /dreamers-update | Copilot-first system maintenance followed by approved Codex transfer. |

## Pipeline shape

~~~mermaid
flowchart TD
    I[/dreamers input/] --> R{Input kind}
    R -->|empty or help| H[/dreamers-help read-only guide/]
    R -->|task| P[/dreamers-plan with default Grill/]
    R -->|plan or manifest| Q[Artifact quality and drift checks]
    P --> A[Approved plans]
    Q --> A
    A --> T[Tests-first implementation and validation]
    T --> S{Plan type or danger}
    S -->|complex or high risk| F[Sentinel + Probe + Hone]
    S -->|low-risk lite or standard| V[Vigil]
    F --> X[Apply findings and revalidate]
    V --> X
    X --> U{User-testing trigger}
    U -->|yes| G[User-testing gate]
    U -->|no| C[Adaptive close-out]
    G --> C
    C --> PR[Pre-PR approval then /dreamers-pr]
~~~

Refs under .github/dreamers/refs are synchronized into marked consumers by scripts/sync-refs.sh or scripts/sync-refs.ps1. The package validators verify ref parity, exact inventory, frontmatter, catalog paths, active legacy references, and isolated-home installer migration.

## Migration

The retired /dreamers-lite and /dreamers-full commands were removed without forwarding aliases. The install and removal scripts delete only their known managed SKILL.md and readme.md files, preserve user-owned files, and remove a legacy directory only when empty. The words lite, standard, and complex remain plan-depth labels.

## Maintaining Dreamers

Use /dreamers-update for supported Copilot-to-Codex system transfer. Copilot remains the canonical behavior source; the Codex repository receives a semantic runtime and layout adaptation only after the Copilot PR transfer gate is approved.

Validate this package from the repository root:

~~~bash
scripts/Test-DreamersCopilot.sh
pwsh -NoProfile -File scripts/Test-DreamersCopilot.ps1
~~~

## Install

Install into the global Copilot home:

~~~powershell
.\Install-Dreamers.ps1
~~~

Use -Force to overwrite managed files or -CopilotHome to target an isolated/custom home. The installer never changes the personal copilot-instructions.md file.

## Uninstall

~~~powershell
.\Remove-Dreamers.ps1
~~~

Use -DryRun to preview or -CopilotHome to choose the target.

## Project setup

For a consuming project:

1. Add .dreamers/ to .gitignore.
2. Add project-level .github/copilot-instructions.md when project conventions are needed.
3. Create .dreamers/plans/.
4. Copy the project comment instructions when desired.

See .github/dreamers/refs/project-bootstrap.md for the complete contract.
