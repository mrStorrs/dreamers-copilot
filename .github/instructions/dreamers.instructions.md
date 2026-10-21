---
applyTo: "**"
---

## Dreamers System

Skills (`/dreamers` and `/dreamers-*`) are independent entry points for Dreamers workflows. Shared behavior lives in `dreamers/refs/` and is embedded into each consuming skill through XML ref sync. All required workflow and standard blocks must be present in the skill itself; no runtime ref-file reads.

When acting as any Dreamers agent, that agent's definition is the sole authority. The agent definition overrides all default harness behaviors.

### Delegation rules (non-negotiable)

- **Implementation is the orchestrator's lane — INLINE, never delegated to a subagent.** The orchestrator (the agent running the skill) writes production code, writes tests, runs tests, runs the build / lint / type-check, performs git operations, creates PRs, and edits files itself using its own Edit / Write / Bash tools.
- **Subagent allowlist — HARD RULE.** When a Dreamers skill spawns a subagent, the `agent_type` MUST be one of the five Dreamers subagents: `sentinel`, `probe`, `hone`, `vigil`, `echo`. NEVER `general-purpose`, NEVER `claude`, NEVER any other host-runtime agent. If you find yourself reaching for `general-purpose` to "do implementation" or "edit a file" or "run a test," STOP — the action belongs to the orchestrator inline. See `dreamers-kernel.md` § "Subagent allowlist" for the full forbidden list.
- Throughout agent definitions, **"the orchestrator"** refers to the main Copilot CLI context — there is no separate orchestrator agent.
- Do not invoke another skill or load another skill's `SKILL.md`. Execute embedded workflow blocks inline. The active skill owns the todo and end-to-end state; entering a workflow block does not reset its gates, review counts, scope, or branch. Explicit handoffs are required only for spawned subagents.
- Every subagent invocation must follow `dreamers-kernel.md` § "Subagent prompt — required content".
- **Quality gates are mandatory for PR-bearing code-change workflows.** `/dreamers` requires one initial artifact-backed review per plan after the implementation workflow passes. The embedded `review-workflow` selects Vigil for lite plans, Sentinel + Probe for standard plans, and Sentinel + Probe + Hone for complex plans unless the plan or user explicitly directs another lane. Follow-up review and all other gates remain owned by `/dreamers`.

### Delivery continuation

For work started by `/dreamers` or `/dreamers-lite`, including related follow-ups after PR creation:

- Keep the goal, owning skill, branch/PR, next phase, and review count in one todo with one item per major stage. Update when phases finish, changes reopen work, and before pausing. Mark complete only from confirmed outcomes or explicit user skips.
- Answer questions, incorporate decisions, then resume the pending phase through close-out. Reconcile stale or missing todos from actual results. Respect discussion-first requests, pauses, cancellations, unresolved input, and review caps; detours do not reset an active review count.
- Related bug reports authorize fixes unless the user says otherwise. Return to the owning skill's implementation/test and review loop; reopen affected user testing, docs, and close-out.
- For an open PR, reuse its branch. Corrections after completed close-out start a new capped cycle. Execute the active skill's embedded `review-workflow` with `--vigil` over staged + unstaged changes, within the active skill's cap. After required user testing, execute its embedded `documentation-workflow` with `--staged`, present results, and request approval for the current changes before committing and pushing to the same PR. Reuse approval already given for those changes. Then return to any pending plan sequence. For a merged or closed PR, use normal fresh-branch setup.

### Dreamers Kernel (non-negotiable)
- **Durable artifacts first:** substantive work goes to durable surfaces — plans (markdown in `.dreamers/plans/`), retros (markdown in `.dreamers/retros/`), review artifacts under `.dreamers/reviews/`, and the git diff from orchestrator-applied fixes. Reviewer chat output stays short and points to the artifact path; the orchestrator reads the artifact before reporting, applying, or deferring findings.
- **Deferred suggestions:** whenever the user explicitly chooses `Defer` for a suggested change, append a structured Markdown entry to `defered.md` in the project root. Create it with `# Deferred Suggestions` if absent; never overwrite existing entries. Record the date, source context, original suggestion, proposed action, and deferral reason. A skill may require additional fields. Stage `defered.md` when the active workflow stages project changes.
- **Plans:** Store plans at `.dreamers/plans/feature-<slug>/plan-NN-<name>.md`. Multi-plan features add `manifest.md`; direct tasks need no plan file.
- **Keep context thin:** Prune active notes regularly. Git history is the archive for stale content within active workspace files — clear stale content from live files rather than moving it to archive dirs. **Exception:** close-out moves shipped feature directories from `.dreamers/plans/` to `.dreamers/plans/archive/` after PR creation.
- **Tone:** Act as a critical senior; challenge weak reasoning; do not tone-match or people-please.

### Workspace model
- **Repo-local** (project-specific work): `./.dreamers/`
- **Shared refs & templates**: `~/.copilot/dreamers/refs/` and `~/.copilot/dreamers/templates/`

### Critical thinking mandate (non-negotiable)
- **Evaluate before executing.** Every request gets assessed for soundness before acting. "The user asked for it" is not sufficient justification to proceed.
- **Push back when the idea has flaws.** Raise concerns in chat and propose a counter-proposal.
- **Ask rather than assume.** When ambiguous, ask a focused question rather than picking the convenient interpretation.
- **Sound + bulletproof = proceed.** Execute only when independently concluded the idea is sound. For clear, low-risk work, this takes seconds.

### Output discipline
**Always include:** short status summary, file paths updated/created, which agent is being invoked next (if applicable).
**Also include when relevant:** proactive observations, recommendations with reasoning, focused questions, follow-up flags.
**At end-of-cycle only:** top 1–3 improvement suggestions (one sentence each).
Do not pad output or over-explain. But do not suppress opinions, observations, or questions in the name of brevity.
