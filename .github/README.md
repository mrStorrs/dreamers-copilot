# Dreamers for GitHub Copilot CLI

Dreamers provides one adaptive delivery workflow plus specialized planning, review, documentation, research, maintenance, and PR skills.

Start with:

~~~text
/dreamers <task | plan paths | manifest>
/dreamers
~~~

Empty or whitespace-only /dreamers input, help, --help, and -h route directly to the read-only /dreamers-help guide before any repository or external inspection or mutation.

## How delivery adapts

Task descriptions use /dreamers-plan with Grill by default. --no-grill or unmistakable natural-language direction skips the interview while retaining proposal critique and plan quality. Supplied plan paths and manifests preserve their sequence and skip Grill, replanning, rewriting, and implementation-start approval while retaining artifact quality and drift checks.

The orchestrator chooses each checkpoint independently:

- lite, standard, or complex plan depth;
- INCREMENTAL or ATOMIC shipping;
- Vigil for low-risk lite and standard plans, or Sentinel + Probe + Hone for complex plans and the shared danger rubric;
- reviewer reruns;
- documentation;
- retrospective and improvements.

It states each decision and rationale, honors explicit user overrides, and asks only when classification is genuinely ambiguous.

The danger rubric covers security, authentication, authorization, privacy, payment, secret, and permission changes; schema, migration, persistence, destructive-data, concurrency, and irreversible-side-effect changes; public or breaking API, dependency, build, distribution, and cross-subsystem changes; and rollback that requires operator action or data recovery. Anything outside that list is not silently escalated.

Documentation runs when the landed diff is user-facing or otherwise documentable. A retrospective and improvements entry is written only for multi-plan learning, repeated or failed validation, review-driven redesign, a user-testing bug, a deferred finding, or an explicit request; otherwise the skip is recorded.

## Agents

| Agent | Type | Role |
|---|---|---|
| Forge | Persona | Routes end-to-end work through /dreamers and focused work through specialized skills. |
| Nova | Persona | Default-on Grill, proposal critique, plan writing, and plan approval. |
| Sentinel | Subagent | Correctness, security, and maintainability. |
| Probe | Subagent | Test coverage, AC layers, edge cases, and regression risk. |
| Hone | Subagent | Simplicity, architecture, redundancy, and over-engineering. |
| Vigil | Subagent | Combined proportional review for low-risk plans and normal reruns. |
| Echo | Subagent | Documentation updates from the actual diff. |
| Sage | Subagent | Citation-backed research. |

Reviewers are read-only except for one .dreamers/reviews artifact. The delivery orchestrator reads artifacts and applies accepted findings inline.

## Skills

### Primary workflow

| Skill | Purpose |
|---|---|
| /dreamers | Plan or consume approved artifacts, implement tests-first, select proportional review, apply findings, run triggered gates/docs/retro, and open the approved PR. |
| /dreamers-help | Read-only orientation, examples, specialized choices, overrides, and migration guidance. |
| /dreamers-plan | Planning only; default-on Grill, right-sized plan guides, and hard stop at approval. |
| /dreamers-implement | One approved implementation cycle through green validation. |
| /dreamers-review | Read-only Sentinel, Probe, Hone, selected-subset, or triad execution. |
| /dreamers-docs | Echo documentation pass. |
| /dreamers-pr | Push once and open the PR from the shared template. |
| /dreamers-fix | Bounded regression-first bug fix. |
| /dreamers-find-refactors | Read-only refactor discovery and plan writing. |

### Focused workflows

| Skill | Purpose |
|---|---|
| /dreamers-test | Vigil test-coverage audit. |
| /dreamers-simplify | Vigil architecture audit. |
| /dreamers-pr-resolve | Address PR feedback and resolve accepted threads after Vigil. |
| /dreamers-research | Deep research through Sage. |
| /dreamers-issue | Structured issue creation. |
| /dreamers-new-project | Project discovery, brief, and shell plans. |
| /dreamers-plan-verify | Plan drift check. |
| /dreamers-add-logging | Logging audit and improvement. |
| /dreamers-cleanup-comments | Project comment cleanup. |
| /dreamers-cleanup-comments-branch | Branch comment cleanup. |
| /dreamers-clean-work | Between-milestone maintenance. |
| /dreamers-update | Copilot-first maintenance and approved Codex transfer. |

## Flow

~~~mermaid
flowchart TD
    I[/dreamers input/] --> R{Help, task, or artifact?}
    R -->|empty or help flags| H[/dreamers-help/]
    R -->|task| P[/dreamers-plan/]
    R -->|plan or manifest| Q[Quality and drift checks]
    P --> A[Approved plan sequence]
    Q --> A
    A --> T[Tests-first implementation]
    T --> V[Automated validation]
    V --> S{Plan type or risk}
    S -->|low-risk lite or standard| G[Vigil]
    S -->|complex or high risk| F[Sentinel + Probe + Hone]
    G --> X[Apply findings]
    F --> X
    X --> U{User-testing trigger?}
    U -->|yes| UG[User-testing gate]
    U -->|no| C[Adaptive close-out]
    UG --> C
    C --> PR[Pre-PR approval and /dreamers-pr]
~~~

Plan approval for task input authorizes implementation. The other mandatory gates are major scope expansion, triggered user testing, and pre-PR approval.

## Package layout

~~~text
.github/
├── agents/
├── skills/
├── dreamers/
│   ├── refs/
│   └── templates/
└── instructions/
~~~

Shared refs are synchronized into marked consumers. CI runs both package validators and exercises installer migration in an isolated Copilot home.

## Migration

The retired /dreamers-lite and /dreamers-full commands were removed without aliases. Install and removal scripts prune only their known managed files, preserve unrelated user content, and remove legacy directories only when empty. Plan-type lite remains valid because it describes plan depth, not a delivery tier.
