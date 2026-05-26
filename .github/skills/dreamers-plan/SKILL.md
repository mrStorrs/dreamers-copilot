---
name: dreamers-plan
description: 'Planning-only entry point. Runs the canonical planning procedure (`planning-procedure.md`) and exits at the implementation-start approval gate. Does NOT invoke implementation. Triggers: /dreamers-plan, plan this, create a plan, plan only.'
argument-hint: '<task description>'
---

## What this skill does

Standalone entry point for the planning phase. The user invokes this when they want plan files written but are NOT yet ready to ship — they'll run `/dreamers-full` themselves later when ready.

This skill follows `~/.copilot/dreamers/refs/planning-procedure.md` end-to-end (Phase 1a → 1g) and exits cleanly at the approval gate. It does NOT invoke any other skill (no `Invoke /dreamers-full`, no chained-skill invocation). The user is in control of what runs next.

If the user wants planning + implementation + close-out in one go, they should run `/dreamers-full <task description>` instead — that skill follows the same planning procedure but continues into implementation automatically.

---

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


Also load at runtime (not inlined — these are templates / project files):
- `~/.copilot/dreamers/templates/plan.md` — plan template
- `~/.copilot/dreamers/templates/manifest.md` — manifest template (when multi-plan with shared context)
- `.github/copilot-instructions.md` (root) — project conventions, tech stack, test commands, source roots.

<orchestration-flow>
<!-- GENERATED from .github/dreamers/refs/orchestration-flow.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Orchestration flow — single-owner todo, continuation principle

Single source of truth for the orchestration principles that apply across all Dreamers skills.

---

## Single-owner todo rule (HARD RULE)

There is exactly ONE todo list per user-invoked skill run. The skill the user invoked at the top level (`/dreamers-full`, `/dreamers-plan`, `/dreamers-implement`, `/dreamers-fix`, `/dreamers-close-out`, etc.) owns the todo for the duration of its run. No other entity touches it.

### What the orchestrator does

At skill entry:
- Declare the todo via `manage_todo_list`. Each item corresponds to one major phase or step. Declare all items upfront; do not add items mid-run.

During the run:
- Mark the active item `in_progress` when starting.
- Mark it `completed` when done.
- Never batch completions at the end. The todo is a live progress indicator, not a retrospective log.
- Before every meaningful step, re-read the todo to confirm position — the todo is the authoritative "where am I" signal, not chat context.

At skill exit:
- All items should be `completed` (or explicitly noted as deferred/skipped, with reason).

### What subagents do NOT do

Subagents spawned by the orchestrator (Sentinel, Probe, Hone, Echo, Sage) do NOT touch the todo. Their prompts MUST include the line:

> "Do NOT call `manage_todo_list`. The orchestrator owns the todo."

A subagent that creates its own todo creates a parallel state that drifts from the orchestrator's. Don't do it.

### No composed-mode handoff

There is no "composed mode" for the todo. Skills do not invoke other skills as runtime sub-routines in this system. Each user-invoked skill runs end-to-end with its own todo. When a user wants the full pipeline, they run `/dreamers-full`; when they want only planning, they run `/dreamers-plan`; etc. Each run has one owner, one todo, one exit.

This rule replaces the previous "composed vs standalone — sub-skill updates parent's matching item" pattern, which created multi-owner todo state and was the root cause of mid-pipeline progress lapses.

### Granularity

One todo item per major phase or clearly distinct step. Not one per line of work. Not one per sub-step within a phase. Scannable overview, not micro-log.

---

## Continuation principle

### Definition

The orchestrator MUST NOT silently halt mid-feature. At every natural pause — where a phase ends and a meaningful choice about what to do next exists — the orchestrator calls `request_information` with a structured choice block. The user picks `Continue`, `Halt for now`, or `Other (freeform)`. No silent forward progress; no silent stops.

### Pause-point list

The following are the canonical natural pauses where a continuation prompt is required:

1. Between ATOMIC cycles in a multi-plan loop, after each plan's commit and drift check, before the next cycle starts — only when more plans remain.
2. Between LIGHT close-outs in INCREMENTAL multi-plan mode, after each per-plan PR opens, before the next cycle starts — only when more plans remain.

**Approval gates are NOT continuation prompts.** Phase 1c (proposal approval), Phase 1g (plan-file approval), and close-out Step 5 (push approval) each carry their own decision. They do not need a follow-up "do you want to continue?" prompt after they fire. Phase 1g's `Approved — start implementation` answer is itself the proceed signal — no second gate fires between Phase 1g and Phase 1.5 / Phase 2.

### Prompt template

Use this shape for every continuation prompt:

```
<status summary — one sentence stating what just completed>

<concrete next action — one sentence stating what will happen if the user says Continue>

Options:
- label: Continue — <specific yes-action label>
- label: Halt for now — No (halt; resume later)
- label: Other — freeform redirect
```

Call `request_information` with at minimum these three choices. The `Continue` label must name the concrete next action (e.g., "start next cycle for feature-auth/plan-02-logout.md").

### Halt behavior

On `Halt for now` at any continuation prompt: halt cleanly. Output one line stating the resume command:

```
Resume by re-invoking `/dreamers-full` with the remaining plan paths: <paths>
```

(Adapt the resume command to whichever skill the user was running.)

Do not leave partial state dangling. Stage nothing new. Do not proceed.

On `Other`: treat the freeform input as a redirect instruction. Acknowledge it, confirm the new direction, and proceed accordingly.

---

## Tool naming convention

Skills in this system reference two tools by pseudonym. Runtime resolves the pseudonym to whatever Copilot CLI surfaces as the actual tool name at the time of invocation.

| Pseudonym | Tool | What it does |
|-----------|------|--------------|
| `request_information` | Copilot CLI user-prompt tool | Pauses the orchestrator, presents a message and structured choices, waits for the user's response |
| `manage_todo_list` | Copilot CLI todo tool | Creates, updates, and marks items in a persistent todo list visible to the user |

When a skill says "call `request_information`" or "declare via `manage_todo_list`", it means: invoke the tool Copilot CLI has bound to that function at runtime. The pseudonym names are stable across skill files regardless of CLI version.

### Legacy convention note

The `.github/agents/nova.agent.md` file retains the older `ask_user` pseudonym (predates this ref). It is functionally equivalent to `request_information`. Out of scope for the current alignment pass; tracked as a follow-up to harmonize agent files with the skill convention.
</orchestration-flow>

<dreamers-kernel>
<!-- GENERATED from .github/dreamers/refs/dreamers-kernel.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Dreamers Kernel

Universal rules. Inlined at the bottom of every Dreamers skill + agent by `scripts/sync-refs.ps1`.

## Subagent allowlist (HARD RULE)

The only `agent_type` values a skill may pass to `task()`:
- `sentinel`, `probe`, `hone`, `echo`, `sage`

Forbidden: `general-purpose`, `claude`, `claude-code-guide`, `Explore`, `Plan`, `bolt`, or any non-Dreamers agent. Exception: only if the user explicitly authorizes a fallback in the current run.

## Single-owner todo

Each user-invoked skill owns its own todo for its run. When skills compose (e.g., `/dreamers-full` invokes `/dreamers-implement`), the called skill creates its own todo on entry and closes it on exit. Sub-skills do not touch the caller's todo.

## Mandatory subagent prompt line

Every `task()` invocation MUST include this line in the prompt:

```
Do NOT call `manage_todo_list`. The skill that invoked you owns its todo.
```

## Implementation discipline

- **Plan adherence:** edit only files in the plan's scope. No while-I'm-here cleanup, no unrelated refactors mixed with feature work.
- **No spec-arguing comments:** never add a code comment that argues the spec permits a pattern.
- **Branch identity check:** before the first edit, `git log --oneline -3`. Confirm the branch and recent commits match the expected feature. If not, halt and surface.
- **No dependency installs without permission.** Don't run `npm install`, `pip install`, etc. without explicit user approval.
- **Type-check before declaring implementation done.** Run the project's type-check command from `.github/copilot-instructions.md` and fix errors before moving on.

## Commit trailer

Every commit body includes:

```
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```
</dreamers-kernel>

<planning-procedure>
<!-- GENERATED from .github/dreamers/refs/planning-procedure.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
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
</planning-procedure>

<testing-mandate>
<!-- GENERATED from .github/dreamers/refs/testing-mandate.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Testing Coverage Mandate (MANDATORY)

Every plan must express its test coverage intent through the Acceptance Criteria's Layer annotations. The planner specifies *what observable outcome* the AC requires and *which test layer* covers it. The implementer (orchestrator at `/dreamers-implement` Step 1) writes the actual tests from each AC's Given/When/Then.

## How test coverage is expressed in plans (new format)

Plan ACs are numbered Given/When/Then statements with a Layer annotation per AC. See `plan-writing-guide.md` § "Acceptance Criteria format" for the canonical spec.

```
<acceptance_criteria>
1. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: unit.*
2. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: integration.*
3. Given <state>, when <trigger>, then <observable outcome>.
   *Layer: E2E.*
</acceptance_criteria>
```

Layer label set (closed): `unit` / `integration` / `E2E` / `perf`. Compound labels allowed when one assertion serves two purposes (e.g., `*Layer: integration / perf.*`).

**Test coverage intent is expressed via the `*Layer: ...*` annotation on each Acceptance Criterion — not via a standalone Test Cases section.** Do not write a separate Test Cases section in a plan; embed the test layer directly in the AC. This keeps ACs and test specification in one place so they never drift.

## Coverage requirement (every plan)

Across all of a plan's ACs, the layer mix must cover the following whenever applicable to the work — think through each layer explicitly:

**Unit layer**
- Each significant function, method, or class in isolation.
- All branches: happy path, edge cases (boundary values, empty/null/max), negative cases (invalid input, error states).
- Any pure logic that does not require a real device, network, or database.

**Integration layer**
- Interactions between layers: repository ↔ data source, ViewModel ↔ repository, service ↔ external API.
- Database reads/writes (real or in-memory, not mocked).
- Auth flows end-to-end within the backend.
- Cloud function triggers and side-effects.

**UI / E2E layer**
- Full user journeys through the UI: screen load → interaction → outcome visible on screen.
- Navigation flows between screens.
- Error and empty states rendered correctly in the UI.
- Any flow that requires a real device or emulator.
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), the plan must include at least one AC with `*Layer: E2E.*` — not just unit/integration. Probe enforces this in the layer audit and blocks if missing.

**Regression risks**
- Anything touching existing behavior that could break — call out the specific existing test or flow at risk in the plan's Context section.

If a layer cannot be covered automatically (e.g., camera permission flows), flag it explicitly as a manual-verification requirement in the plan's Verification section with a reason.

## Probe's layer audit (consumes the new format)

In `/dreamers-implement` Step 4 (coverage sweep) and Step 5 (parallel review with Probe), the layer audit reads each AC's `*Layer: ...*` annotation to verify coverage at each layer was implemented. Probe blocks the cycle if any AC's annotated layer lacks a corresponding green test.

## Test benchmarks

Each project that uses `/dreamers-implement` maintains a `./test-benchmarks.md` file at the project root. The file records measured run times per test command so the orchestrator can set realistic timeouts.

- **File path:** `./test-benchmarks.md` at the project root (committed to version control).
- **Recommended-timeout formula:** `max(last_run_time × 2, 30s)` — the 2× multiplier accounts for machine variance; 30s is a non-negotiable floor.
- **Orchestrator updates** the row for each test command after every successful test run. **Humans may edit** the `Notes` column to capture CI environment factors or known flakiness.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).

## Why this matters

Layer-annotated ACs prevent Probe from guessing intent. The Given/When/Then format forces specificity about preconditions and expected outcomes; the Layer annotation forces specificity about which test layer covers each AC. Together they reduce ambiguity at the planning → implementation handoff without duplicating content across multiple plan sections.
</testing-mandate>

$ARGUMENTS

---

## Todo list (single owner: this skill)

At skill entry, declare via `manage_todo_list`:

- [ ] Read planning-procedure.md
- [ ] Phase 1a — hash it out
- [ ] Phase 1b — user input audit
- [ ] Phase 1c — approval gate
- [ ] Phase 1d — decide plan count (and manifest backfill check)
- [ ] Phase 1e — write plan file(s)
- [ ] Phase 1f — plan quality self-check
- [ ] Phase 1g — implementation-start approval gate

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

This skill is the sole owner of the todo. No subagents are spawned in this skill, so no subagent prompts need the "do NOT touch todo" reminder. But the rule still applies if any subagent IS spawned in the future.

---

## Procedure

Follow `~/.copilot/dreamers/refs/planning-procedure.md` Phase 1a through Phase 1g, exactly as written. The procedure handles its own approval gates (Phase 1c, Phase 1g) and quality self-check (Phase 1f). Update this skill's todo as each phase is completed.

At Phase 1g, the user picks one of three options. Handle each per the planning-procedure.md "What happens after Phase 1g approval" section:

- **`Approved — start implementation`** — exit this skill with success. Surface the saved plan path(s) to the user and the next-step command:
  - Single plan: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md`
  - Multiple plans, no manifest: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/plan-01-<name>.md .dreamers/plans/feature-<slug>/plan-02-<name>.md ...`
  - Multiple plans with manifest: `Plans saved. To begin implementation, run: /dreamers-full .dreamers/plans/feature-<slug>/manifest.md`

  This skill does NOT itself invoke `/dreamers-full`. Skill-calls-skill chaining is forbidden under the new architecture (see `orchestration-flow.md` § "Single-owner todo rule"). The user invokes the next skill themselves.

- **`Halt — planning only`** — exit cleanly. Output: `Planning complete. Plan file(s) saved at <paths>. To begin implementation later, run /dreamers-full with the plan paths.` Stop. Do not invoke any further skill.

- **`Other` / corrections** — apply inline per the planning-procedure.md guidance. Revise plan files, re-run Phase 1f, re-present the Phase 1g gate. Loop until the user picks Approved or Halt.

---

## Exit behavior

On Phase 1g approval (any approval choice or Halt): exit with success. Tell the user:
- The approved plan file path(s).
- If a manifest was produced: the manifest path.
- Next step: run `/dreamers-full <plan-paths>` (or `/dreamers-full <manifest-path>` for manifest mode) when ready to begin implementation.

---

## What this skill does NOT do

- Does NOT proceed to implementation. That's `/dreamers-full`'s job.
- Does NOT auto-invoke `/dreamers-full` or any other skill. The user invokes the next step themselves.
- Does NOT spawn any subagent. Planning is entirely inline by the orchestrator (this skill, running in your context).
- Does NOT write code or test files. Plan files only.

## HARD STOP after Phase 1g

When plan files are written and the approval gate clears, the skill exits. No edits beyond plan files. No invocations of other skills. The user is in control of what happens next.

If the user asks "now start implementing" in the same session: surface the `/dreamers-full <plan-paths>` command to them and stop. They run it.
