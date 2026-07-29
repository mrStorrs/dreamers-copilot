# /dreamers-review — flow

Visual map of the selected-lane review skill. Source of truth is `SKILL.md`. **Read-only** — does NOT apply fixes; the caller does.

```mermaid
flowchart TD
    Start(["/dreamers-review $ARGUMENTS"]) --> Basis{"plan available?"}
    Basis -->|yes| ModeCheck{"explicit lane or<br/>plan type?"}
    Basis -->|no| Infer["Infer intent from user context,<br/>branch/PR, diff, tests, and code"]
    Infer --> Clear{"one reliable<br/>interpretation?"}
    Clear -->|no| Ask["Ask user one concise<br/>clarifying question"]
    Ask --> Infer
    Clear -->|yes| ModeCheck

    ModeCheck -->|lite plan or --vigil| Vigil["Single combined reviewer:<br/>Vigil"]
    ModeCheck -->|standard plan| Standard["Sentinel + Probe<br/>spawned in parallel"]
    ModeCheck -->|complex, --full, or inferred intent| Triad["Sentinel + Probe + Hone<br/>spawned in parallel"]
    ModeCheck -->|--lenses csv| Selected["Selected subset:<br/>any non-empty mix<br/>of Sentinel / Probe / Hone"]
    ModeCheck -->|--lens sentinel| LensS["Single-lens: Sentinel"]
    ModeCheck -->|--lens probe| LensP["Single-lens: Probe"]
    ModeCheck -->|--lens hone| LensH["Single-lens: Hone"]

    Triad --> Spawn["mode: sync<br/>each prompt MUST include<br/>Do NOT call manage_todo_list"]
    Standard --> Spawn
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
    class Triad,Standard,Vigil,Selected,LensS,LensP,LensH agent
    class Spawn,WriteArtifact,Wait,Collect,Aggregate,Surface1,Surface2,Report phase
```

## Lens scope (read-only)

| Lens | Reviewer | Returns |
|---|---|---|
| Combined correctness, security, maintainability, coverage, and simplicity | Vigil | One artifact with findings, intent alignment, requirement coverage, and architecture audit |
| Correctness / security / maintainability | Sentinel | Artifact with findings + intent-alignment summary |
| Test coverage (requirement matrix, layer audit, gaps) | Probe | Artifact with findings + requirement coverage table |
| Simplicity / over-engineering / architecture | Hone | Artifact with findings incl. full-refactor recommendations |

## Lane policy

| Lane | Reviewers | Normal use |
|---|---|---|
| vigil | Vigil | Lite plan or explicit request. |
| sentinel | Sentinel | Focused correctness, security, or maintainability audit. |
| probe | Probe | Focused test coverage or regression-risk audit. |
| hone | Hone | Focused architecture or simplicity audit. |
| standard | Sentinel + Probe | Standard plan or explicit combined correctness and coverage audit. |
| full | Sentinel + Probe + Hone | Complex plan, explicit full review, or standalone default. |

Selection precedence is explicit user direction or lane flag, then an explicit reviewer requirement in the plan, then `Plan-type`: lite → Vigil; standard → Sentinel + Probe; complex → Sentinel + Probe + Hone. Without a plan, it infers the intended behavior from user context, branch/PR metadata, the selected diff, tests, changed code, and nearby conventions; an ambiguous basis gets one user question before review. Inferred-intent reviews use the full triad unless the user chose a lane. This skill owns selection and execution, then reports artifact-backed results.

## Key invariants

- **Read-only.** This skill does NOT apply fixes. The caller (`/dreamers` Step 5, or whoever invoked it) decides what to do with the findings. Reviewers may write only their required `.dreamers/reviews/` artifacts.
- **`/dreamers` reruns.** Routine follow-up review reruns use `/dreamers-review --vigil`. A full or selected-lane rerun runs only when the major-change rerun gate asks the user and the user selects it.
- **No major-refactor gate here.** That logic lives in the caller. This skill just reports.
- **Artifacts are the handoff.** Each selected reviewer writes one `.dreamers/reviews/<reviewer>-*.md` artifact; this skill reads those files before reporting.
- **All reviewer prompts MUST include** `Do NOT call manage_todo_list.`
- **`--no-apply` doesn't exist** — this skill is always read-only by design.
- **Todo ownership is contextual.** Standalone review owns its two-step todo; when invoked by /dreamers, it completes the phase under the outer todo.
