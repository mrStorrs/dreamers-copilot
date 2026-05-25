---
name: dreamers-plan
description: 'Planning phase of the Dreamers pipeline. Three-phase requirements conversation → plan files in `.dreamers/plans/` → implementation-start approval gate. Invokable standalone (plan-only) or composed from `/dreamers-full` Phase 1. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '<task description>'
---

## What this skill does

Drives the three-phase planning conversation (Hash-it-out → Approval → Decompose) and writes plan files to `.dreamers/plans/`. Exits at the implementation-start approval gate (Phase 1g). Does NOT proceed to implementation — that's `/dreamers-implement`'s job. When called from `/dreamers-full`, the orchestrator captures the approved plan paths from this skill's chat output and forwards them.

## Pre-flight reads

Read these refs once at startup (full file, no truncation):

- `~/.copilot/dreamers/refs/orchestrator-discipline.md` — the shared discipline cited by all pipeline sub-skills
- `~/.copilot/dreamers/refs/plan-content.md` — plan section requirements
- `~/.copilot/dreamers/refs/plan-rules.md` — plan naming + numbering
- `~/.copilot/dreamers/refs/planning-protocol.md` — three-phase conversation rules
- `~/.copilot/dreamers/refs/citation-accuracy.md` — verify before citing existing artifacts
- `~/.copilot/dreamers/refs/testing-mandate.md` — coverage layer expectations the plan must capture
- `~/.copilot/dreamers/refs/feature-decomposition.md` — when to write multiple plans
- `~/.copilot/dreamers/templates/plan.md` — the single plan template
- `~/.copilot/dreamers/templates/manifest.md` — the feature manifest template (used in multi-plan work)
- `~/.copilot/dreamers/refs/orchestration-flow.md` — continuation principle, todo-list protocol, tool-name pseudonyms

Also check for project-level files:
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, test commands, source roots used by the component-usage check.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1a — hash it out (clarifying questions)
- [ ] Phase 1b — user input audit
- [ ] Phase 1c — approval gate
- [ ] Phase 1d — decide plan count (and manifest)
- [ ] Phase 1e — write plan file(s)
- [ ] Phase 1f — plan quality self-check
- [ ] Phase 1g — implementation-start approval gate

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

(When invoked in composed mode by `/dreamers-full`, do NOT declare a new list — update the parent's matching Phase 1 item instead. See `~/.copilot/dreamers/refs/orchestration-flow.md`.)

---

## Phase 1a — Hash it out

1. Write a one-paragraph **understanding summary** of the goal.
2. Identify all ambiguities, gaps, open decisions.
3. Ask every clarifying question in one round via `request_information`. Do not trickle questions across multiple message turns.

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

## Phase 1d — Decide plan count (one or multiple)

Default to ONE plan inside a feature directory. If the work's scope is too large to land cleanly in a single cycle, produce MULTIPLE independent plans inside the same feature directory per `feature-decomposition.md` (each shippable on its own; sequenced via `/dreamers-full feature-<slug>/plan-01-<name>.md feature-<slug>/plan-02-<name>.md ...` at invocation time, or via `/dreamers-full feature-<slug>/manifest.md` when a manifest is produced).

"Too large" thresholds:
- More than ~300 lines of new/changed code across the touched files.
- More than one data-layer change PLUS more than one UI surface in the same cycle.
- Crosses natural seams (model → repository → viewmodel → screen → cloud function) such that one cycle's review would be unwieldy.

When splitting, each plan MUST be:
- **Independently shippable** — can merge to main alone; no dependency on a later plan.
- **Testable in isolation** — at least one machine-verifiable assertion per plan.
- **Coherent scope** — touches at most one data-layer change + one UI surface (loose guideline).
- **At a natural seam** — split at model/repo/viewmodel/screen/function boundary, not arbitrary line cuts.

State your decision in chat: "Producing ONE plan: …" or "Producing N plans: …" with a one-sentence rationale.

### Phase 1d.1 — Decide whether to produce a feature manifest (multi-plan only)

If producing multiple plans, decide whether they warrant a `manifest.md` at `.dreamers/plans/feature-<slug>/manifest.md`. **Produce a manifest if ANY of these hold:**

- At least 2 shared constraints apply across all plans (e.g., "all plans must preserve API X's backward compat until plan-03 ships")
- Shared design decisions span plans (e.g., "all auth flows use the same state-machine abstraction")
- Shared data models referenced by multiple plans (interface / type contracts)
- End-to-end Acceptance Criteria exist (only verifiable after ALL plans ship)
- Cross-plan rollback rules (ordering dependencies, coordinated revert — folded into shared constraints)

**Skip the manifest if:** the multiple plans are essentially unrelated (e.g., 3 bug fixes shipped together but touching different subsystems). No shared context → manifest would be decorative.

When produced, the manifest is the cross-plan context anchor. It threads shared constraints / design / data / end-to-end ACs into each cycle's reviewer prompts.

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

The flat layout (`plan-{slug}.md` directly in `.dreamers/plans/`) and the lettered suffix (`plan-a-...`, `plan-b-...`) are RETIRED. Do not use either.

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

**XML escaping:** if literal `</acceptance_criteria>` or `</constraints>` text needs to appear inside a wrapped block (e.g., quoting another plan's structure), use HTML entity escapes: `&lt;` / `&gt;` / `&amp;`. Phase 1f's parser is entity-aware.

**Design Decisions format** (optional section, one entry per significant choice — include only when non-obvious):
- **Decision:** [what was chosen]
- **Rationale:** [why — one sentence]
- **Rejected:** [alternatives considered — one line each]

**User-testing required:** `yes` if a human must manually verify before the cycle completes (UI flows, push notifications, payments, camera, permissions). `no` for backend, data-layer, non-visible. Default to `yes` when in doubt.

**Plans MUST NOT include code snippets.** One exception: interface/type contracts where the signature itself is the design decision.

**Plans MUST NOT contain an "Open Questions" section.** Per `planning-protocol.md`, all open questions are resolved in Phase 1 (Hash it out) BEFORE plan generation. If you discover a new question during Phase 1e, halt, surface it to the user via `request_information`, get the answer, then resume.

**Plan length:** target 200–400 lines. Hard cap 600. If a plan exceeds 600 lines, split it into two plans within the feature directory.

### Phase 1e.1 — Component usage check (mandatory)

When a plan modifies a shared component, search for all references to it across the project's source root (from `.github/copilot-instructions.md`) before finalizing the scope file list — include all callers.

### Phase 1e.2 — Citation accuracy

Before citing the behavior, structure, content, or API of any existing artifact in the plan — test file, test method, repository method, ViewModel property, Maestro YAML, UI assertion pattern, or any other code artifact — read and verify the source during this planning session. Claiming "method X does Y" or "test Z asserts W" without reading the file is a planning error; the plan becomes a liability when implementation builds against a wrong assumption.

- **If the artifact cannot be read** (e.g., it belongs to a later plan in the same sequence and doesn't exist yet): state explicitly in the plan that the citation is an assumption pending verification. Do not present it as confirmed fact.
- **UI assertion-string collision check** (when applicable): when a plan asserts on visible text, verify no other persistent UI element shares that text. If a collision exists, specify a more-specific assertion that matches only the intended element. Project-specific assertion conventions (e.g., Maestro for mobile) live in `.github/copilot-instructions.md`.

## Phase 1f — Plan quality self-check (mandatory)

Before exiting Phase 1, verify each plan against:

**Structural checks:**
- [ ] File path matches `.dreamers/plans/feature-<slug>/plan-NN-<name>.md` (numbered, zero-padded; inside a feature directory)
- [ ] Metadata block present with Date / Status / Branch / User-testing-required
- [ ] All mandatory sections present in order: Goal, Context, Acceptance Criteria, Out of Scope, Constraints, Verification
- [ ] Verification section is at the bottom (Anthropic recency-bias rule)
- [ ] No "Open Questions" section exists (all questions resolved in Phase 1)
- [ ] No "Risks / Mitigations" section exists (real risks folded into Constraints)
- [ ] No standalone "Test Cases" section exists (test layer captured via `*Layer: ...*` annotation on each AC)

**Content checks:**
- [ ] Goal is one paragraph stating the done-state
- [ ] Context is ≤ 200 words, bullet links only (no motivation prose)
- [ ] At least 2 Acceptance Criteria (soft warning if fewer — overridable with user confirmation)
- [ ] Every AC has a Layer annotation (`*Layer: unit.*` / `integration` / `E2E` / `perf`, compounds allowed)
- [ ] ACs are XML-wrapped in `<acceptance_criteria>...</acceptance_criteria>`
- [ ] Constraints are XML-wrapped in `<constraints>...</constraints>`
- [ ] XML is structurally valid (parser is entity-aware — `&lt;`/`&gt;` in content is allowed; only unmatched STRUCTURAL tags fail)
- [ ] Out of Scope has explicit "Will NOT" bullets
- [ ] Verification is 5–8 lines: test command + type-check command + files to inspect + smoke check (no AC narrative restatement)
- [ ] References only files/paths that exist (no invented paths)
- [ ] No code snippets (exception: interface/type contracts only)
- [ ] Plan length ≤ 600 lines (hard cap)

**UI section checks (only when UI section exists):**
- [ ] Layer 1 ASCII layout in code-fenced block
- [ ] Layer 2 component spec (table OR per-component subsections)
- [ ] Layer 3 Mermaid (optional)

**Multi-plan checks (when multiple plans are produced):**
- [ ] Each plan is independently shippable (no plan depends on a later sibling)
- [ ] Each plan has at least one machine-verifiable AC testable in isolation
- [ ] Splits fall at natural seams (not arbitrary line-count cuts)
- [ ] All plans share the same `feature-<slug>/` directory

**Manifest checks (when a manifest is produced):**
- [ ] `feature-<slug>/manifest.md` exists at the feature directory root
- [ ] Manifest has a Plan sequence table listing all plans in the intended run order
- [ ] At least one of: shared constraints, shared design decisions, shared data models, or end-to-end ACs is populated (manifest with all sections empty = decorative; either populate or skip the manifest)
- [ ] Manifest does NOT have a separate "Risks / Mitigations (cross-plan)" or "Rollback strategy (cross-plan)" section (those are folded into Shared constraints)

Any failure → halt and prompt the user with the specific item(s) that failed. Soft-warning items (fewer than 2 ACs) may be overridden with explicit user confirmation; all other items are hard fails.

## Phase 1g — Implementation start approval gate (mandatory)

Phase 1c approved the high-level goal. Phase 1g approves the actual plan files before any implementation work begins.

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

### Approval handling

- **Approved — start implementation:**
  - **Standalone mode:** invoke `/dreamers-full <plan-paths>` directly to begin Phase 2 (implementation) — do NOT just tell the user to run it. Invoke it. The argument(s) to pass depend on what was produced:
    - Single plan → `/dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md`
    - Multiple plans, no manifest → `/dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md .dreamers/plans/feature-<slug>/plan-02-<name>.md ...`
    - Multiple plans WITH manifest → `/dreamers-full .dreamers/plans/feature-<slug>/manifest.md` (Mode 3 — threads shared context into reviewer prompts)
  - **Composed mode (called from `/dreamers-full`):** exit this skill with success status. The parent orchestrator already owns Phase 2 — do NOT re-invoke `/dreamers-full` from inside a `/dreamers-full` call (would create a recursion loop). The parent reads the approval status from this skill's chat output and proceeds.
- **Halt — planning only:** exit this skill with success status. Output: `Planning complete. Plan file(s) saved. To begin implementation later, invoke /dreamers-full <plan-paths>.` Do NOT invoke any further skill. Use this when the user wants the plan but is not ready to ship yet.
- **Corrections (Other):** revise plan files inline, re-run Phase 1f, re-present this gate. Loop until the user picks Approved or Halt.

---

## Exit behavior

### Standalone invocation

Three exit paths from Phase 1g (per the approval-handling rules above):

1. **Approved — start implementation:** the skill INVOKES `/dreamers-full <plan-paths>` directly. From the user's perspective, the planning skill hands off seamlessly to the full pipeline — no extra command typed, no extra step.
2. **Halt — planning only:** exit cleanly. Tell the user:
   - The approved plan file path(s) — `.dreamers/plans/feature-<slug>/plan-NN-<name>.md`.
   - If a manifest was produced: `.dreamers/plans/feature-<slug>/manifest.md`.
   - To resume later: invoke `/dreamers-full <plan-paths>` (single plan, multiple plans, or manifest path).
3. **Other / corrections:** does not exit. Loops back to revise the plan and re-present the gate.

### Composed invocation (called from `/dreamers-full`)

Exit on Phase 1g approval (or halt). Return in chat output:
- Plan count (one or multiple) + sequence order if multiple.
- Plan file path(s).
- Manifest file path (if a manifest was produced; omit if none).
- Approval status: `Approved` or `Halted`.

The parent orchestrator (`/dreamers-full`) reads this chat output and proceeds to Phase 2 if approved. This skill does NOT re-invoke `/dreamers-full` in composed mode — that would recurse.

## Phase 1g exit semantics — what this skill does and does NOT do

This skill writes plan files. It does NOT implement plan content. The Phase 1g approval gate determines what happens NEXT:

- **Approved (standalone):** invoke `/dreamers-full <plan-paths>` directly per the approval-handling rules above. The skill hands off; `/dreamers-full` takes over Phase 2 (implementation), Phase 3 (close-out), and PR. This skill does not write code, run tests, or commit beyond the plan files themselves — those actions belong to the skills `/dreamers-full` orchestrates.
- **Approved (composed mode, called from `/dreamers-full`):** exit with success status. The parent orchestrator owns Phase 2. Do NOT re-invoke `/dreamers-full` from inside `/dreamers-full` — that would recurse.
- **Halt — planning only:** exit cleanly without invoking the next phase. The user resumes later by invoking `/dreamers-full <plan-paths>` themselves.

The "lane" rule (this skill never makes production code edits, never runs tests, never commits) still applies — it just no longer prevents seamless handoff to `/dreamers-full` when the user explicitly says "start implementation."
