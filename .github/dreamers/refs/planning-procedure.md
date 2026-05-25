# Planning Procedure (canonical — read in full, no skipping)

This ref is the SOLE source of truth for the Dreamers planning phase. Both `/dreamers-plan` (standalone) and `/dreamers-full` (end-to-end pipeline) follow this procedure. There is no composed-mode branching — the procedure is the procedure.

**MUST-READ rule:** any skill citing this ref in its pre-flight reads MUST load this file in full using the `view` tool from top to bottom — no `grep`, no `head`, no pattern-matching shortcut. Pattern-skipping on procedural refs is a documented failure mode. Read every line before starting the procedure.

---

## Inputs

The orchestrator running this procedure must have at minimum:

- A **task description** from the user (verbatim, as `$ARGUMENTS` passed to the invoking skill).
- Access to the project's `.github/copilot-instructions.md` (auto-loaded by Copilot CLI).
- Read access to `.dreamers/plans/` to detect existing feature directories (for the manifest backfill check).

## Outputs

- One or more plan files at `.dreamers/plans/feature-<slug>/plan-NN-<name>.md` per `plan-rules.md`.
- Optional `manifest.md` at `.dreamers/plans/feature-<slug>/manifest.md` for multi-plan work with shared context.
- Explicit user approval recorded at Phase 1g.

The orchestrator's todo (a single list owned by the top-level skill) records phase completion.

---

## Phase 1a — Hash it out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question in ONE round via `request_information`. Do not trickle questions across multiple message turns.

If the task is fully unambiguous, skip to Phase 1b with a brief "I understand the goal as: …" confirmation.

After clarifications are received, proceed to Phase 1b.

## Phase 1b — User Input Audit (gate)

Before presenting the proposal, review the full conversation. Verify every suggestion, correction, preference, and constraint the user expressed is explicitly addressed. If anything is missing, incorporate it.

## Phase 1c — Approval gate

Present this proposal block in chat:

```
**Goal:** [one sentence]
**Scope:** [what is in]
**Non-goals:** [only if scope is genuinely ambiguous]
**Acceptance criteria:**
1. [AC 1]
2. [AC 2]
…
```

Call `request_information` with choice `["Approved"]` and allow inline freeform corrections in the same interaction. Treat any non-approval freeform response as corrections; revise and re-present until explicit approval.

## Phase 1d — Decide plan count

Default to ONE plan inside a feature directory. If the work's scope is too large to land cleanly in a single cycle, produce MULTIPLE independent plans inside the same feature directory per `feature-decomposition.md`.

"Too large" thresholds:
- More than ~300 lines of new/changed code across the touched files.
- More than one data-layer change PLUS more than one UI surface in the same cycle.
- Crosses natural seams (model → repository → viewmodel → screen → cloud function) such that one cycle's review would be unwieldy.

When splitting, each plan MUST be:
- **Independently shippable** — can merge to main alone; no dependency on a later plan.
- **Testable in isolation** — at least one machine-verifiable assertion per plan.
- **Coherent scope** — touches at most one data-layer change + one UI surface.
- **At a natural seam** — model/repo/viewmodel/screen/function boundary.

State your decision in chat: "Producing ONE plan: …" or "Producing N plans: …" with a one-sentence rationale.

### Phase 1d.1 — Decide whether to produce a manifest (multi-plan only)

If producing multiple plans, decide whether they warrant a `manifest.md` at `.dreamers/plans/feature-<slug>/manifest.md`. **Produce a manifest if ANY of these hold:**

- At least 2 shared constraints apply across all plans (e.g., "all plans must preserve API X's backward compat until plan-03 ships")
- Shared design decisions span plans (e.g., "all auth flows use the same state-machine abstraction")
- Shared data models referenced by multiple plans (interface / type contracts)
- End-to-end Acceptance Criteria exist (only verifiable after ALL plans ship)
- Cross-plan rollback rules (ordering dependencies, coordinated revert)

**Skip the manifest if:** the multiple plans are essentially unrelated. No shared context → manifest would be decorative.

State your manifest decision: "Manifest: yes (because …)" or "Manifest: no (plans are independent)."

### Phase 1d.2 — Manifest backfill detection (mandatory)

Before writing plans in Phase 1e, check: does a feature directory already exist for this work at `.dreamers/plans/feature-<slug>/`?

- **If NO:** new feature dir — proceed normally (will be created in Phase 1e).
- **If YES, and the existing dir contains `plan-01-*.md` but NO `manifest.md`:** this is the backfill scenario. The current work is producing what will become `plan-02-*.md` (or later) for the SAME feature. A manifest MUST be created in Phase 1e — even if Phase 1d.1's normal heuristics said "skip the manifest." The backfill rule overrides: when a feature has multiple plans, it has a manifest, period.
  - Use plan-01's content as seed context for the manifest's Shared constraints / Shared design decisions / Shared data models sections.
  - Surface this to the user in chat: "Feature dir already exists with plan-01; creating manifest as part of plan-02 (backfill rule)."
- **If YES, and `manifest.md` already exists:** normal multi-plan continuation. Read the existing manifest. The new plan goes in the same dir with the next `plan-NN-*.md` number.

## Phase 1e — Write plan file(s)

Plan paths follow the per-feature directory convention from `plan-rules.md`:

- **Plan file:** `.dreamers/plans/feature-<slug>/plan-NN-<name>.md` where NN is zero-padded order within the feature dir (`01`, `02`, ..., `99`).
- **Manifest (optional, multi-plan only):** `.dreamers/plans/feature-<slug>/manifest.md`.

Create the feature directory if it does not exist: `mkdir -p .dreamers/plans/feature-<slug>/`. If the directory already exists with prior plans, see Phase 1d.2 for the manifest backfill rule.

Use the templates as starting structure:
- `~/.copilot/dreamers/templates/plan.md` — every plan.
- `~/.copilot/dreamers/templates/manifest.md` — feature manifest.

**Each plan must include (per `plan-content.md`):**
- Metadata block: Date, Status (Draft/Active/Completed/Superseded), Branch, User-testing-required (yes/no). No Owner, no Scope, no Links — those belong in the PR description.
- Sections in order: Goal, Context (≤200 words), Acceptance Criteria (XML-wrapped, numbered G/W/T with Layer annotations), Out of Scope, Constraints (XML-wrapped), Design Decisions (optional), UI (optional, 3-layer), Verification (last, commands only).

**Acceptance Criteria — XML wrapping + Layer annotation (mandatory):**

```
<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. ...
</acceptance_criteria>
```

Layer label set (closed): `unit` / `integration` / `E2E` / `perf`. Compound labels allowed.

**Constraints — XML wrapping (mandatory):**

```
<constraints>
- **Technical:** ...
- **Process:** ...
- **Hard rules:** ...
</constraints>
```

**XML escaping:** if literal `</acceptance_criteria>` or `</constraints>` text needs to appear inside a wrapped block, use HTML entity escapes: `&lt;` / `&gt;` / `&amp;`. Phase 1f's parser is entity-aware.

**User-testing required:** `yes` if a human must manually verify before the cycle completes (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Plans MUST NOT include code snippets.** One exception: interface/type contracts where the signature itself is the design decision.

**Plans MUST NOT contain an "Open Questions" section.** All open questions are resolved in Phase 1a (Hash it out) BEFORE plan generation. If you discover a new question during Phase 1e, halt, surface it to the user via `request_information`, get the answer, then resume.

**Plan length:** target 200–400 lines. Hard cap 600.

### Phase 1e.1 — Component usage check

When a plan modifies a shared component, search for all references to it across the project's source root (from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 1e.2 — Citation accuracy

Before citing the behavior, structure, content, or API of any existing artifact in the plan — test file, test method, repository method, ViewModel property, Maestro YAML, UI assertion pattern, or any other code artifact — read and verify the source during this planning session. Claiming "method X does Y" or "test Z asserts W" without reading the file is a planning error.

- **If the artifact cannot be read** (belongs to a later plan in the same sequence and doesn't exist yet): state explicitly in the plan that the citation is an assumption pending verification.
- **UI assertion-string collision check** (when applicable): verify no other persistent UI element shares the asserted text. If a collision exists, specify a more-specific assertion that matches only the intended element.

## Phase 1f — Plan quality self-check (mandatory)

Before exiting Phase 1, verify each plan against:

**Structural checks:**
- [ ] File path matches `.dreamers/plans/feature-<slug>/plan-NN-<name>.md`
- [ ] Metadata block present with Date / Status / Branch / User-testing-required
- [ ] All mandatory sections present in order: Goal, Context, Acceptance Criteria, Out of Scope, Constraints, Verification
- [ ] Verification section is at the bottom (Anthropic recency-bias rule)
- [ ] No "Open Questions" section exists
- [ ] No "Risks / Mitigations" section exists (real risks folded into Constraints)
- [ ] No standalone "Test Cases" section exists (test layer captured via `*Layer: ...*` annotation on each AC)

**Content checks:**
- [ ] Goal is one paragraph stating the done-state
- [ ] Context is ≤ 200 words, bullet links only (no motivation prose)
- [ ] At least 2 Acceptance Criteria (soft warning if fewer — overridable with user confirmation)
- [ ] Every AC has a Layer annotation
- [ ] ACs are XML-wrapped in `<acceptance_criteria>...</acceptance_criteria>`
- [ ] Constraints are XML-wrapped in `<constraints>...</constraints>`
- [ ] XML is structurally valid (parser is entity-aware)
- [ ] Out of Scope has explicit "Will NOT" bullets
- [ ] Verification is 5–8 lines: test command + type-check command + files to inspect + smoke check
- [ ] References only files/paths that exist
- [ ] No code snippets (exception: interface/type contracts only)
- [ ] Plan length ≤ 600 lines

**UI section checks (only when UI section exists):**
- [ ] Layer 1 ASCII layout in code-fenced block
- [ ] Layer 2 component spec (table OR per-component subsections)
- [ ] Layer 3 Mermaid (optional)

**Multi-plan checks (when multiple plans are produced):**
- [ ] Each plan is independently shippable
- [ ] Each plan has at least one machine-verifiable AC testable in isolation
- [ ] Splits fall at natural seams
- [ ] All plans share the same `feature-<slug>/` directory

**Manifest checks (when a manifest is produced):**
- [ ] `feature-<slug>/manifest.md` exists at the feature directory root
- [ ] Manifest has a Plan sequence table listing all plans in the intended run order
- [ ] At least one of: shared constraints, shared design decisions, shared data models, or end-to-end ACs is populated
- [ ] Manifest does NOT have separate "Risks / Mitigations (cross-plan)" or "Rollback strategy (cross-plan)" sections

Any failure → halt and prompt the user with the specific item(s) that failed. Soft-warning items (fewer than 2 ACs) may be overridden with explicit user confirmation; all other items are hard fails.

## Phase 1g — Implementation start approval gate (mandatory)

Phase 1c approved the high-level goal. Phase 1g approves the actual plan files.

Present this block:

```
**Plans written and ready for review:**

- `.dreamers/plans/feature-<slug>/plan-01-<name>.md` — [one-line summary from plan Goal]
- `.dreamers/plans/feature-<slug>/plan-02-<name>.md` — [one-line summary]  (if multiple plans were produced)
- ...

Manifest (if produced): `.dreamers/plans/feature-<slug>/manifest.md`

Please read the plan file(s) above. Choose how to proceed.
```

Call `request_information` with choices `["Approved — start implementation", "Halt — planning only", "Other"]`.

### What happens after Phase 1g approval

This procedure ends at Phase 1g. What happens next depends on the consuming skill:

- **`/dreamers-full`** (end-to-end pipeline): on `Approved`, proceed directly to the implementation phase (read `implementation-procedure.md` if not already loaded, then start Phase 2 per cycle). Do NOT issue a second continuation prompt — Phase 1g approval is the signal to continue. On `Halt`, exit with the saved plan path(s) surfaced; on `Other` (corrections), revise inline, re-run Phase 1f, re-present this gate.
- **`/dreamers-plan` standalone**: on `Approved — start implementation`, the user has indicated they want implementation. The skill exits with success and surfaces the next-step command (`/dreamers-full <plan-paths>` for a full pipeline) to the user. The standalone skill does NOT itself invoke `/dreamers-full` — that would create a chained-skill invocation (see `orchestration-flow.md` § "Single-owner todo"). The user runs `/dreamers-full` themselves. On `Halt`, exit cleanly with the saved plan path(s). On `Other`, revise + re-present.

This split keeps both consumers compliant with the single-owner todo rule: each skill owns its own todo for the duration of its own run; control returns to the user between skills.
