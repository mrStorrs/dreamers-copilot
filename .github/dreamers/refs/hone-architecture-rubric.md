# Simplicity review

Find a simpler correct design for the actual requirements. Inspect speculative abstractions, pass-through wrappers, duplicated logic, single-use helpers that hide clearer code, impossible defensive branches, dead code, confused boundaries, hidden state, and awkward data flow.

Name a concrete alternative and explain why it is easier to understand or maintain. A smaller diff or fewer lines alone is not evidence. Keep complexity required for correctness, security, compatibility, or useful clarity; do not turn every helper or defensive check into a finding.

If a broad refactor is the simplest fix, report its files, modules, callers, deletions, and behavior constraints. Refactor cost must not hide a useful finding. The orchestrator decides disposition and scope approval.

End the report by answering: **How could I make this code simpler?** Give the best justified opportunity, or explain why the current form is already the simplest correct approach. Do not invent an improvement to fill the section.
