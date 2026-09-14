# /dreamers-review

Vigil reviews by default, with a supplied proposal/plan or inferred intent. Review scope includes pending work. --branch selects the feature diff; --paths narrows scope; --all audits the codebase.

Vigil checks supplied validation evidence against the shared verification policy, including navigation coverage. The orchestrator runs tests.

Only explicit user selection activates --full (Sentinel + Probe + Hone), --lens, or --lenses. Plan depth never changes this default.

Reviewers write durable findings and finish with **How could I make this code simpler?** The caller reads the artifact and decides fixes. Transcripts are consulted only when needed.

See [the workflow](SKILL.md).
