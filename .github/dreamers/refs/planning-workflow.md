**Input:** task description. Ask if missing. Apply the embedded `planning-grill`, `plan-format`, and `manifest-format` rules. Work inline; write only `.dreamers/plans/` artifacts, without changing project files or git state.

1. **Grill.** Resolve decisions using `planning-grill`; preserve the full question/response exchange for the transcript.
2. **Propose.** Use `plan-format` and choose the smallest shippable chunks; do not split arbitrarily when that creates more work. Present the full plan for a single-plan task, or the manifest for multiple plans. Through `request_information`, include risks, assumptions, tradeoffs, and simpler alternatives. Answer corrections with reasoning and a recommendation; revise and re-present until approved.
3. **Write.** Create `.dreamers/plans/feature-<slug>/` and numbered `plan-NN-<name>.md` files. Save the verbatim Grill transcript when present and link it from each plan. Add `manifest.md` for multiple plans.
4. **Check.** Verify that scope, ACs, cited paths, and accepted decisions match the approved proposal and current codebase.
5. **Approve.** Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`. Apply minor edits, repeat the checks, and re-present. For a major rewrite, return to the Grill with the correction. On Halt, stop and surface paths. Follow Other as directed.

**Result:** approved plan paths, plus the manifest path when present. Planning ends here; implementation authorization belongs to the containing skill.
