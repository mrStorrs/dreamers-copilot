# Apply review findings

Read this run's artifacts. Resolve blocked reviews and material open questions before continuing. Evaluate findings by evidence; correctness/security outrank test coverage, then simplicity. Apply justified fixes and worthwhile simplifications in scope; explain rejected suggestions.

Ask before a fix introduces a new out-of-scope module/directory, changes a schema/data model, crosses unrelated subsystems, adds an unplanned public export, touches out-of-scope files, or recommends a full refactor. Ambiguity also triggers the gate. Present impact, breadth, and rationale; offer Apply now, Defer, or freeform direction. On Defer, append to root defered.md with the source artifact, finding, proposed fix, trigger, and reason; do not create a follow-up plan automatically.

Stage approved fixes and run [verification](testing-mandate.md), including timing updates. Fix regressions within three attempts.

Review again only when warranted: small fixes covered by validation can skip with a recorded reason; otherwise use one Vigil follow-up pass. Before rerunning after a new abstraction/module, API/schema/dependency/persistence change, broad rewrite, scope expansion, or unresolved conflicting feedback, ask which review to run or whether to skip. Only an explicit user request can select the triad or an individual alternative reviewer. Read new artifacts and apply this same disposition process.
