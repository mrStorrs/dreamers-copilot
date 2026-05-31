# /dreamers-review — flow

Visual map of the selected-lane review skill. Source of truth is `SKILL.md`. **Read-only** — does NOT apply fixes; the caller does.

```mermaid
flowchart TD
    Start(["/dreamers-review $ARGUMENTS"]) --> ModeCheck{"review flags?"}

    ModeCheck -->|No flag| Triad["Full triad:<br/>Sentinel + Probe + Hone<br/>in one batched task() call"]
    ModeCheck -->|--lenses csv| Selected["Selected subset:<br/>any non-empty mix<br/>of Sentinel / Probe / Hone"]
    ModeCheck -->|--lens sentinel| LensS["Single-lens: Sentinel"]
    ModeCheck -->|--lens probe| LensP["Single-lens: Probe"]
    ModeCheck -->|--lens hone| LensH["Single-lens: Hone"]

    Triad --> Spawn["mode: sync<br/>each prompt MUST include<br/>Do NOT call manage_todo_list"]
    Selected --> Spawn
    LensS --> Spawn
    LensP --> Spawn
    LensH --> Spawn

    Spawn --> Wait["Wait for all spawned<br/>reviewers to return"]
    Wait --> Collect["Collect chat outputs<br/>per reviewer-findings-format"]
    Collect --> Aggregate["Aggregate counts<br/>by severity + lens"]
    Aggregate --> CheckStatus{"Reviewer<br/>statuses?"}

    CheckStatus -->|Blocked| Surface1["Surface Blocked verbatim<br/>caller handles"]
    CheckStatus -->|Open questions| Surface2["Surface open questions<br/>caller handles"]
    CheckStatus -->|Approved + Findings| Report["Return findings<br/>verbatim to caller"]

    Surface1 --> End(["Exit with status"])
    Surface2 --> End
    Report --> End

    classDef gate fill:#92400e,stroke:#78350f,stroke-width:2px,color:#fff
    classDef phase fill:#166534,stroke:#14532d,stroke-width:2px,color:#fff
    classDef agent fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff

    class ModeCheck,CheckStatus gate
    class Triad,Selected,LensS,LensP,LensH agent
    class Spawn,Wait,Collect,Aggregate,Surface1,Surface2,Report phase
```

## Lens scope (read-only)

| Lens | Reviewer | Returns |
|---|---|---|
| Correctness / security / maintainability | Sentinel | Findings + plan-alignment summary |
| Test coverage (AC matrix, layer audit, gaps) | Probe | Findings + AC coverage table |
| Simplicity / over-engineering / architecture | Hone | Findings (incl. full-refactor recommendations) |

## Lane policy

| Lane | Reviewers | Normal use |
|---|---|---|
| `sentinel` | Sentinel | Focused correctness/security/maintainability audit. |
| `probe` | Probe | Focused test coverage or regression-risk audit. |
| `hone` | Hone | Focused architecture/simplicity audit. |
| `standard` | Sentinel + Probe | Default full-pipeline PR gate; invoke as `--lenses sentinel,probe`. |
| `full` | Sentinel + Probe + Hone | Architecture/refactor risk or explicit full-review request; invoke with no lens flag. |

## Key invariants

- **Read-only.** This skill does NOT apply fixes. The caller (`/dreamers-full` Step 5, or whoever invoked it) decides what to do with the findings.
- **No major-refactor gate here.** That logic lives in the caller. This skill just reports.
- **All reviewer prompts MUST include** `Do NOT call manage_todo_list.`
- **`--no-apply` doesn't exist anymore** — this skill is always read-only by design.
