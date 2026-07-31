# /dreamers-explain — flow

General-purpose, read-only explanation skill. Source of truth is `SKILL.md`.

```mermaid
flowchart TD
    Start(["/dreamers-explain $ARGUMENTS"]) --> Resolve["Resolve subject, goal,<br/>audience, and depth"]
    Resolve --> Missing{"Subject missing or<br/>materially ambiguous?"}
    Missing -->|Yes| Ask["Ask one concise question"]
    Ask --> Resolve
    Missing -->|No| Route{"Evidence route"}
    Route -->|Local subject| Local["Inspect named material<br/>and surrounding context"]
    Route -->|Supplied source| Supplied["Ground in supplied text or URL"]
    Route -->|Current, uncertain,<br/>high-stakes, or sourced| External["Retrieve authoritative sources<br/>and cross-check when needed"]
    Route -->|Stable foundation| Knowledge["Explain without unnecessary search"]
    Local --> Build
    Supplied --> Build
    External --> Build
    Knowledge --> Build
    Build["Direct answer → orientation → mental model<br/>→ mechanics → example → edges → takeaway"] --> Learn{"Interactive learning<br/>requested?"}
    Learn -->|Yes| Check["Prediction, application,<br/>or graduated hints"]
    Learn -->|No| Final["Verify accuracy, support,<br/>clarity, and useful depth"]
    Check --> Final
    Final --> Deliver(["Deliver in conversation"])
```

## Key invariants

- Read-only unless the user explicitly requests an artifact.
- Focused explanation stays inline; durable multi-perspective reports belong to `/dreamers-research`.
- Local claims cite repository evidence. Current, uncertain, disputed, or high-stakes claims use authoritative external sources.
- Explanations lead with the core answer, then add intuition, mechanics, examples, and boundaries as needed.
- Quizzes and Socratic pacing are opt-in, not forced on ordinary explanation requests.
