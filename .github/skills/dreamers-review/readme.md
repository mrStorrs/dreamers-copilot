# /dreamers-review — flow

Visual map of the selected-lane review skill. Source of truth is `SKILL.md`. **Read-only** — does NOT apply fixes; the caller does.

```mermaid
flowchart TD
    Start(["/dreamers-review $ARGUMENTS"]) --> ModeCheck{"review flags?"}

    ModeCheck -->|No flag| Triad["Full triad:<br/>Sentinel + Probe + Hone<br/>in one batched task() call"]
    ModeCheck -->|--vigil| Vigil["Single combined reviewer:<br/>Vigil"]
    ModeCheck -->|--lenses csv| Selected["Selected subset:<br/>any non-empty mix<br/>of Sentinel / Probe / Hone"]
    ModeCheck -->|--lens sentinel| LensS["Single-lens: Sentinel"]
    ModeCheck -->|--lens probe| LensP["Single-lens: Probe"]
    ModeCheck -->|--lens hone| LensH["Single-lens: Hone"]

    Triad --> Spawn["mode: sync<br/>each prompt MUST include<br/>Do NOT call manage_todo_list"]
    Vigil --> Spawn
    Selected --> Spawn
    LensS --> Spawn
    LensP --> Spawn
    LensH --> Spawn

    Spawn --> WriteArtifact["Each reviewer writes exactly one<br/>.dreamers/reviews artifact"]
    WriteArtifact --> Wait["Wait for all spawned<br/>reviewers to return"]
    Wait --> Collect["Read returned artifacts"]
    Collect --> Aggregate["Aggregate counts<br/>by severity + lens"]
    Aggregate --> CheckStatus{"Reviewer<br/>statuses?"}

    CheckStatus -->|Blocked| Surface1["Surface Blocked verbatim<br/>caller handles"]
    CheckStatus -->|Open questions| Surface2["Surface open questions<br/>caller handles"]
    CheckStatus -->|Approved + Findings| Report["Return artifact findings<br/>verbatim to caller"]

    Surface1 --> End(["Exit with status"])
    Surface2 --> End
    Report --> End

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class ModeCheck,CheckStatus gate
    class Triad,Vigil,Selected,LensS,LensP,LensH agent
    class Spawn,WriteArtifact,Wait,Collect,Aggregate,Surface1,Surface2,Report phase
```

## Lens scope (read-only)

| Lens | Reviewer | Returns |
|---|---|---|
| Combined correctness, security, maintainability, coverage, and simplicity | Vigil | One artifact with findings, plan alignment, AC coverage, and architecture audit |
| Correctness / security / maintainability | Sentinel | Artifact with findings + plan-alignment summary |
| Test coverage (AC matrix, layer audit, gaps) | Probe | Artifact with findings + AC coverage table |
| Simplicity / over-engineering / architecture | Hone | Artifact with findings incl. full-refactor recommendations |

## Lane policy

| Lane | Reviewers | Normal use |
|---|---|---|
| vigil | Vigil | Combined proportional review selected by a delivery caller or explicit user request. |
| sentinel | Sentinel | Focused correctness, security, or maintainability audit. |
| probe | Probe | Focused test coverage or regression-risk audit. |
| hone | Hone | Focused architecture or simplicity audit. |
| standard | Sentinel + Probe | Explicit combined correctness and coverage audit. |
| full | Sentinel + Probe + Hone | Adaptive triad selection or explicit full review. |

The adaptive /dreamers caller owns lane selection and invokes this skill for every lane, including Vigil for low-risk lite and standard plans. This skill only executes the requested lane and reports artifact-backed results; explicit user overrides remain authoritative.

## Key invariants

- **Project-file read-only.** This skill and every reviewer leave project code, tests, docs, config, dependencies, and git state unchanged. Each reviewer may write exactly one .dreamers/reviews artifact.
- **Caller applies findings.** This skill does not apply fixes; the caller decides what to apply or defer.
- **No major-scope gate here.** That logic remains in the caller.
- **Reviewer artifacts are the subagent handoff.** This skill reads every selected reviewer's artifact before reporting.
- **Every reviewer prompt includes the parent-todo prohibition.**
- **Todo ownership is contextual.** Standalone review owns its two-step todo; when invoked by /dreamers, it completes the phase under the outer todo.
