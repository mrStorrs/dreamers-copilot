# Code laws

- Simplicity and correctness come first. Prefer the smallest clear design that meets current requirements. Preserve required behavior when simplifying.
- Reuse local patterns. Avoid speculative abstractions, pass-through layers, duplicate logic, dead code, and defensive paths for impossible states.
- Tests must protect observable behavior and remain stable through harmless refactors. Never test by matching source, prompt, or documentation wording, or snapshotting implementation details. No filler or duplicate tests.
- For a bug, add or improve a meaningful regression test when feasible; otherwise record the verification and coverage gap. Tests-first is optional.
- If a real constraint requires an exception to these laws, explain it. If missing scaffolding caused an avoidable mistake, record a concrete improvement.
