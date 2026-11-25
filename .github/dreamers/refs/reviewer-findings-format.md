# Reviewer Findings Format

## Review handoff

The caller assigns an unused absolute path under the target worktree's `.dreamers/reviews/` for each invocation. Use `<reviewer>-<scope>-<unique-id>.md` with the section in the scope for section audits. Pass the exact path and this handoff requirement in the agent prompt.

The reviewer prepares one complete report in its assigned format, ending with `End of handoff` on its own line. Create the parent directory if needed, attempt to write the report at the assigned path, and return the same complete report in the final reply, even if the write fails.

For each expected reviewer invocation, check the assigned file and the final reply from that invocation. A complete report has a valid status, the required sections for the reported outcome, the stated number of findings, and the closing line. A blocked report needs the blocker and any open questions in addition to the closing line. Use the complete file if available, otherwise use the complete reply. Process one copy per invocation. If neither copy is complete, report the missing handoff for that reviewer and scope. Preserve blocked status, findings, and open questions from the accepted report and apply the caller's existing gates.

**Status line** (one of the following, allowing the reviewer format's `Status:` prefix and hyphen separator):
- `Approved — no findings`
- `Findings reported — N items`
- `Blocked — <reason>`

**Findings** (if any) — one bullet per finding, exact format:

```
[severity] [lens-tag] file:line — what was wrong → suggested fix
```

- `severity` ∈ `critical` / `high` / `medium` / `low`
- `lens-tag` ∈ `correctness` / `security` / `maintainability` (Sentinel) / `test-coverage` (Probe) / `simplicity` (Hone)
- `file:line` — absolute or repo-relative path + line number
- `what was wrong → suggested fix` — one-line description + targeted fix the caller can apply mechanically

**Observations** (optional) — out-of-scope notes that aren't findings. The caller may or may not act on them.

**Open questions** (optional) — items needing user judgment. Use "none" if no questions.

Reviewers are report-only for code, tests, docs, config, scripts, and git state. The caller applies fixes per its own orchestrator-as-fixer behavior.

## MVP assessment (Hone and Vigil)

For change reviews, establish the minimum implementation that satisfies the agreed acceptance criteria while preserving required security, data integrity, performance constraints, and existing contracts. For each distinct addition, identify the requirement or evidenced constraint it serves. Ask what would fail if it were removed or replaced with the simplest existing mechanism. If nothing required would fail, report the addition as unnecessary and name what to delete. Apply this check to behavior, abstractions, configuration, dependencies, tests, and supporting changes. Future usefulness and tests added by the change do not establish necessity.

Prefer deletion, reuse, or a local simplification. Recommend a broader refactor only with a concrete explanation of why it is needed to correct the changed implementation; separate unrelated architectural improvements from required fixes. Refactor cost alone does not justify suppressing a necessary finding. State the affected files, modules, call sites, and deletions where known.

Every completed Hone or Vigil change review, including approval, must include a brief **MVP assessment** identifying the minimum approach and any non-obvious additions retained, with their requirement or constraint justification. Cite concrete paths or symbols; a claim that the code is minimal is insufficient. Report removable additions as findings, not optional observations. If scope is uncertain, surface the uncertainty instead of treating implemented behavior as an agreed requirement. For an audit without a proposed change, use its stated audit objective rather than inventing feature ACs.
