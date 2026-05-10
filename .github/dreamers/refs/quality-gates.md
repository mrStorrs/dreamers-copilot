# Quality Gates

## Gate 2 — Plan quality check (orchestrator-side, MANDATORY)

Before routing to Forge for implementation, the orchestrator (`/dreamers-plan` Phase 3 exit, `/dreamers-full` Phase 1 exit, `/dreamers-implement` startup) verifies plan quality.

### Mechanical checks (run the linter)
```bash
~/.copilot/dreamers/scripts/dreamers-plan-lint.sh path/to/plan.md
# or, for every plan in .dreamers/plans/:
~/.copilot/dreamers/scripts/dreamers-plan-lint.sh
```
The linter enforces:
- Filename matches `plan-{slug}.md` or `plan-{slug}-{letter}.md`
- H1 starts with `# Plan —`
- Status field present and ∈ {Draft, Active, Completed, Superseded}
- Sub-plan / standalone has `Acceptance Criteria`, `Design Decisions`, `Rollback`, and `Test Cases for Probe` sections
- Umbrella has `Sub-plans` section
- No fenced code blocks outside an `Interface contracts` / `Type contracts` section

Non-zero exit ⇒ halt and surface the failed items to the user.

### Judgment-only checks (the orchestrator must still verify by hand)
- Non-trivial features have an umbrella + sub-plans (not one monolithic plan)
- Acceptance Criteria are numbered, measurable, Forge-verifiable (not vague)
- Design Decisions follow the structured `Decision / Rationale / Rejected` format
- Plan references only files/paths that actually exist in the codebase
- Sub-plan splits are at natural seams, not arbitrary line-count cuts
- No sub-plan's testability depends on a sibling sub-plan that hasn't shipped yet

**Any failure = halt and prompt the user with the specific item(s) that failed.**

Gate 2 is the only orchestrator-side gate. It catches plan-quality issues before any implementation effort is wasted.

---

### What each agent self-asserts before signaling done

| Agent | Self-check requirements |
|---|---|
| Forge | Chat output contains: status line, files-changed list, files-read-for-context list, how-to-test, known-limitations (or "none"), Deferred AC items if any. Type-check passed. |
| Sentinel | Chat output contains: status line, severity-graded fixes-applied list, plan-alignment summary. Type-check passed. |
| Probe | `test-plan.md` (with AC coverage matrix + Coverage Expansion section), `runbook.md`, `bugs.md`, and `regression-analysis.md` (if user-bug invocation) all written. Every plan AC has a covering test (or documented reason). |
| Hone | Chat output contains: status line, files-edited list, simplifications-not-made section, observations section. |
| Nova | Chat output contains: mode, decision, file paths if changed, mode-specific notes (drift items / change summary / plan paths). |
| Echo | Chat output contains: status line, doc-changes log, comment audit results, open questions if any. |

### Orchestrator side

The orchestrator only confirms the agent **signaled completion in chat**. It does not re-read agent artifacts. If an agent's chat output is missing required content, the agent's own self-check should have caught it — the orchestrator escalates by re-prompting the agent with the specific gap.

---
