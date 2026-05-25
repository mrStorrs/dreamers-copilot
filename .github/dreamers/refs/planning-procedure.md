# Planning Procedure (canonical)

Sole source of truth for the Dreamers planning phase. Both `/dreamers-plan` (standalone) and `/dreamers-full` (end-to-end pipeline) follow this procedure. There is no composed-mode branching — the procedure is the procedure.

The orchestrator drives every phase inline. There is no planning subagent. Plan-writing rules and structure live in `.github/dreamers/templates/plan-writing-guide.md` — read it via the `view` tool at Phase 1b entry.

**Inputs:** task description (`$ARGUMENTS`); project's `.github/copilot-instructions.md`; read access to `.dreamers/plans/` (manifest backfill check).
**Outputs:** plan files at `.dreamers/plans/feature-<slug>/plan-NN-<name>.md`; optional `manifest.md`; explicit user approval at Phase 1c.

---

## Phase 1a — Hash out with user

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions. Ask every clarifying question in ONE round via `request_information`. Do not trickle questions across multiple message turns.
3. After clarifications: present this proposal block in chat and get explicit approval via `request_information`:

```
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…
```

Treat any non-approval response as corrections; revise and re-present until explicit approval.

4. Decide **plan count + manifest**:
   - Default to ONE plan inside a feature directory.
   - Produce MULTIPLE plans when scope exceeds one cycle (see `plan-writing-guide.md` § "Multi-plan work" for thresholds and splitting rules).
   - Decide whether to produce a manifest (see `plan-writing-guide.md` § "Manifest pattern" for triggers and skip rules).
   - **Manifest backfill check (mandatory):** before writing plans, check `.dreamers/plans/feature-<slug>/`. If it already exists, contains `plan-01-*.md`, has NO `manifest.md`, AND this conversation is producing what will become plan-02-*.md or later — a manifest MUST be created in Phase 1b. Surface this to the user: "Feature dir already exists with plan-01; creating manifest as part of plan-02 (backfill rule)."
   - State the decision in chat: "Producing ONE plan: …" or "Producing N plans: …" + manifest yes/no with one-sentence rationale.

## Phase 1b — Write plan file(s)

1. Read `.github/dreamers/templates/plan-writing-guide.md` in full via the `view` tool. This is mandatory — never skip or skim. The template defines metadata, required sections, AC format, constraints format, XML escaping, plan length cap, and every other structural rule.
2. Create the feature directory if it does not exist: `mkdir -p .dreamers/plans/feature-<slug>/`.
3. Write each plan file per the template, following the directory + filename conventions from the guide.
4. If a manifest was decided in 1a, write it at `.dreamers/plans/feature-<slug>/manifest.md` per the guide.
5. **Component usage check:** when a plan modifies a shared component, search for all references across the project's source root (from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.
6. **Citation accuracy:** verify every cited artifact's source during this session (see guide § "Citation accuracy"). Mark unverifiable citations as "assumption pending verification" — never present as confirmed fact.
7. **Quality self-check (mandatory before exiting Phase 1b):** re-read `plan-writing-guide.md` and verify each plan against every structural rule there. Mandatory checks: path/filename, metadata block, section order with Verification last, ACs XML-wrapped with Layer annotations (≥ 2 ACs soft minimum), Constraints XML-wrapped, no banned sections, no code (interface contracts only), length ≤ 600. Multi-plan: independently shippable, same feature dir. Manifest (if any): Plan sequence + ≥ 1 of shared constraints / design decisions / data models / end-to-end ACs. Any hard fail → halt, fix, re-run check.

## Phase 1c — User review gate (mandatory)

Present:

```
**Plans written and ready for review:**

- `.dreamers/plans/feature-<slug>/plan-NN-<name>.md` — [one-line summary from plan Goal]
- … (list all plans)

Manifest (if produced): `.dreamers/plans/feature-<slug>/manifest.md`

Please read the plan file(s) above. Choose how to proceed.
```

Call `request_information` with these choices:
- **Approved — start implementation** → planning ends; consuming skill proceeds.
- **Minor edit — orchestrator fixes inline** → user describes the edit in freeform; orchestrator applies inline, re-runs the Phase 1b self-check on the edited plan, re-presents this gate.
- **Major rewrite — back to 1a** → planning loops back to Phase 1a with the user's correction as the new starting context. Re-runs 1a → 1b → 1c.
- **Halt — planning only** → exit cleanly with plan paths surfaced. Resume later by re-invoking the planning flow.
- **Other** → treat as freeform correction; route to minor or major based on the orchestrator's read of the user input; re-present this gate.

### What happens after Phase 1c approval

- **`/dreamers-full`** on `Approved`: proceed directly to Phase 1.5 / Phase 2. The approval IS the proceed signal — no second continuation prompt.
- **`/dreamers-plan`** on `Approved — start implementation`: exit cleanly and surface `/dreamers-full <plan-paths>` as the next-step command. The standalone skill does NOT invoke `/dreamers-full` (would violate single-owner todo per `orchestration-flow.md`).
