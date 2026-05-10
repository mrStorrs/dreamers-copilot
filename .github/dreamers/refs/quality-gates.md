# Quality Gates

## Gate 2 — Plan quality check (orchestrator-side, MANDATORY)

Before routing to Forge for implementation, the orchestrator (`/dreamers-plan` Phase 3 exit, `/dreamers-full` Phase 1 exit, `/dreamers-implement` startup) reads the plan file(s) and verifies:

- [ ] Plan file(s) named per naming convention (`plan-{slug}.md`, `plan-{slug}-{letter}.md`)
- [ ] Non-trivial features have an umbrella plan + sub-plans (not one monolithic plan)
- [ ] Each sub-plan has **Acceptance Criteria** — numbered, measurable, Forge-verifiable (not vague)
- [ ] Each sub-plan has **Test Cases for Probe** using Given/When/Then format for non-trivial cases
- [ ] Each sub-plan has a **Design Decisions** section using the structured format
- [ ] Each sub-plan has a **Rollback Boundary** declaration
- [ ] Each sub-plan references only files/paths that actually exist in the codebase — no invented paths
- [ ] Sub-plan splits are at natural seams, not arbitrary line-count cuts
- [ ] No sub-plan's testability depends on a sibling sub-plan that hasn't shipped yet
- [ ] Plan contains no code snippets (exception: interface/type contracts only)

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
