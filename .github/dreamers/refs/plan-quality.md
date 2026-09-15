## Plan quality

Check plans against `plan-format`: complete metadata, clear scope, and measurable ACs with layers. Preserve every accepted requirement, decision, correction, and constraint from the proposal and user discussion, using the verbatim transcript when present. Reject unresolved decisions, placeholders, and unverifiable citations presented as facts. Fix gaps before presenting a plan or starting implementation.

If implementation reveals required adjacent files, update scope before editing them; keep changes within the same goal.

Existing plans may retain older headings if they contain the same information. A missing `Plan-type` requires a warning and explicit user approval. Shell plans must go through planning before implementation.

## Multi-plan ship strategy

Recommend INCREMENTAL for 4+ independent plans, different subsystems, or standalone user value from plan A. Recommend ATOMIC for overlapping files, ordering dependencies, schema/migration/API contracts, or verification requiring all plans. Conflicting signals default to ATOMIC.
