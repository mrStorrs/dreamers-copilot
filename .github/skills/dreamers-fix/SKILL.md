---
name: dreamers-fix
description: 'Lightweight bug-fix pipeline. Cuts a fresh branch from origin/<default>, implements inline, runs project tests + Sentinel review in parallel, optionally invokes Echo for docs, pushes + opens PR. Self-contained — does NOT call /dreamers-plan, /dreamers-implement, or /dreamers-close-out. Escalates to /dreamers-full on scope blowup. Triggers: /dreamers-fix, fix this bug, bug fix, address the bug.'
argument-hint: '<bug description> [--issue <#|url>]'
---

## What this skill does

Lightweight, self-contained pipeline for bug fixes:

1. Cuts `fix/<slug>` from fresh `origin/<default>`.
2. Surveys the scope before any edit. If scope blows up (new module / schema change / cross-cutting refactor / new exported symbols), halts and surfaces an escalation choice — does NOT auto-route to `/dreamers-full`.
3. Writes a failing regression test (if test infra exists), then implements the fix inline.
4. Spawns Sentinel review + runs the project test command in a single parallel batch.
5. Applies Sentinel findings inline; re-runs tests (hard cap: 3 fix attempts).
6. AI-judgment Echo gate — spawns Echo subagent inline only if the change touches user-facing behavior, public API, config/setup, or test commands.
7. User approval gate before push.
8. Commits, then follows `pr-procedure.md` inline for push + PR creation (with `--issue` forwarded if provided).

**No plan file is written.** No retro, no improvements append, no plan archive, no Probe spawn, no Hone spawn. This skill is the entire pipeline for trivial-to-moderate bug fixes.

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


Also load at runtime (not inlined — these are templates / project files):
- `.github/copilot-instructions.md` (root) — project conventions, **test commands** (binding).
- `.github/instructions/git.instructions.md` (root, if present) — commit message style.
- `./test-benchmarks.md` (project root, if present) — recommended test timeouts.

Follow the Dreamers Kernel and Output Discipline from `~/.copilot/copilot-instructions.md`.

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

<git-workflow>
<!-- GENERATED from .github/dreamers/refs/git-workflow.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Git Workflow (mandatory)

Every milestone uses a feature branch + PR — never work directly on the default branch.

## Startup verification (do this FIRST)
1. Detect the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT_BRANCH" ] && DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
   Store `$DEFAULT_BRANCH` — use it everywhere `main` would have been used.
2. `git fetch origin && git log origin/$DEFAULT_BRANCH --oneline -5` — anchor to remote truth before reading any `.dreamers/` files. Workspace files are local-only and may be stale. `origin/$DEFAULT_BRANCH` is the authoritative record of what is actually shipped.

## Branch setup (before invoking `/dreamers-implement`)
1. `git checkout $DEFAULT_BRANCH && git pull origin $DEFAULT_BRANCH` — never build off a stale local default branch.
2. Cut `feat/<slug>` from `$DEFAULT_BRANCH`.
3. Confirm `.dreamers/` is in the project's `.gitignore`. If not, add it before any further edits.
4. **Archive prior feature's plan directory** — check if the previous feature's PR is merged (`gh pr list --state merged` or `gh pr view <number>`):
   - **Merged:** move the entire feature directory from `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/` (create the archive dir if it doesn't exist). The PR description is the lasting public record; the archived feature directory is preserved locally for easy reference. Use `mv` (or `Move-Item`), not `rm` — never delete plan files. Mid-feature archive (file-by-file) is NOT allowed; only whole-feature-directory archive at the milestone-final PR merge.
   - **Not merged:** leave the feature directory in place.
   - **Note:** this step catches prior features not already archived by `/dreamers-close-out` Step 7 (the primary archive trigger). If close-out already ran on the prior feature, the source directory won't exist and the `mv` is a no-op — skip silently.
5. No init commit — the first commit for the milestone is the first thing in the PR diff.

## Commit discipline (non-negotiable)
1. **Commit at end of each cycle** — one commit per plan in the sequence (single-plan: one commit total; multi-plan: N commits, one per plan).
2. **Commit before PR creation** — a final commit capturing any last changes before opening the PR.
3. **No auto-commit after PR is created** — if changes are made after `gh pr create`, do NOT commit automatically. Ask the user first.

## Push discipline (non-negotiable)
`git push` happens EXACTLY ONCE — immediately before `gh pr create` at final close-out. Never push after intermediate commits, between cycles, or at any other point in the pipeline.

## Post-PR push discipline
If the user approves a post-PR commit, push with `git push` (no force). The PR will update automatically.

## Commit structure (one commit per cycle)
- Exactly **one** commit per plan/cycle, immediately after the reviewer findings have been applied and tests are green (and user testing, if required, is signed off).
- The orchestrator stages changes with `git add` throughout the cycle but does **not** run `git commit` until the cycle ends.
- Commit message format follows `.github/instructions/git.instructions.md` (if present). Pipeline-specific bits:
  - Subject: `feat: <plan-name>` (or `feat!: <plan-name>` for breaking changes — see git.instructions.md for the breaking-change footer rule)
  - Body: reference the plan file (e.g. `Plan: feature-auth/plan-01-login-flow`) — repo-relative path without `.md`, without `.dreamers/plans/` prefix

One commit per plan keeps each plan's contribution atomic. Reviewer-fix application is part of the same cycle (not separate commits).

## What gets committed
Nothing in `.dreamers/` is committed — all workspace files (plans, retros, improvements.md) are gitignored and stay local. Ensure `.dreamers/` is in the project's `.gitignore`.

## No worktrees
The orchestrator works directly on the feature branch. Worktrees previously caused reviewers to read stale default-branch code.

## Git history is the archive
No separate archive directories. `git log` and PR diffs are the record.
</git-workflow>

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

<delegation>
<!-- GENERATED from .github/dreamers/refs/delegation.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Delegation Protocol

Each Agent tool invocation must include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files to read
- **What is needed** — specific deliverable expected from this agent
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)

## MANDATORY — Agent mode

All agents MUST be invoked with `mode: "sync"`. The agent blocks until completion and returns its summary inline. The orchestrator gates on the result before firing anything else.

For the parallel reviewer triad in `/dreamers-implement` Step 5 and `/dreamers-pr-resolve` Step 5: spawn Sentinel + Probe + Hone in a single tool-call with 3 Agent sub-tool-uses. All three run concurrently; the orchestrator waits for all three before applying findings.

## MANDATORY — Reading templates and project files at runtime

Refs are inlined into every consumer at build time by `scripts/sync-refs.ps1`; they are part of the live prompt and do not require a runtime read. Templates (`.github/dreamers/templates/*.md` repo-local, primary; `~/.copilot/dreamers/templates/*.md` user-global, legacy) and project files (`.github/copilot-instructions.md`, `.github/instructions/*.md`) are NOT inlined and MUST be read in full using the `view` tool when a skill or agent reaches them. Never use shell commands (`cat`, `head`, `tail`, `Select-String`) to read templates or project files — they truncate. Every line matters.

## Subagent allowlist (HARD RULE — read this twice)

The ONLY subagent types a Dreamers skill may spawn are the five below. Any other agent type is FORBIDDEN. There is no fallback, no "general-purpose for when nothing fits" escape hatch.

### Allowed (the only types you may pass as `agent_type` in a `task` / Agent tool call)

- **`sentinel`** — read-only review of correctness, security, maintainability. Returns structured findings; the orchestrator applies fixes. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-review`.
- **`probe`** — read-only review of test coverage (AC matrix, layer audit, edge cases, regression risk). Returns structured findings. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-test`.
- **`hone`** — read-only review of simplicity, over-engineering, redundancy, bad architecture. May recommend full refactors. Returns structured findings. One of the three parallel reviewers per cycle. Also invokable standalone via `/dreamers-simplify`.
- **`echo`** — documentation. Updates Echo-owned sections of `.github/copilot-instructions.md` plus other project docs after a cycle. Spawned inline at `close-out-procedure.md` Step 2, and by the `/dreamers-docs` standalone skill for ad-hoc doc updates.
- **`sage`** — deep multi-perspective research. Used by `/dreamers-research`. Orthogonal to the pipeline.

### Forbidden (must NEVER appear as `agent_type` from a Dreamers skill)

- **`general-purpose`** — NEVER. If you reach for general-purpose to "implement," "edit a file," "run a test," or "do git work," that is a bug. Implementation is INLINE by the orchestrator. There is no fallback.
- **`claude`**, **`claude-code-guide`**, **`Explore`**, **`Plan`** (capital-P architect agent), **`statusline-setup`**, **`vercel:*`** — host-runtime agents from other systems. NEVER spawn from a Dreamers skill.
- **`forge`**, **`nova`** — these are USER-ENTERED personas (via `/agents forge` or `/agents nova`). Skills do NOT spawn them as subagents.
- **`bolt`** — does not exist as a subagent in this Dreamers system. Implementation, git ops, and PR creation are done INLINE by the orchestrator.
- **Anything not in the 5-item allowlist above** — NEVER.

### Runtime hard stop

Before EVERY `task` / Agent tool call, check the `agent_type` argument:

- ✅ If `agent_type` is one of `sentinel` / `probe` / `hone` / `echo` / `sage` → proceed.
- ❌ If `agent_type` is anything else → STOP. Do not spawn. The action you're about to delegate either:
  - (a) belongs to the orchestrator INLINE (writing code, writing tests, running tests, git operations, doc updates, file edits, PR creation), OR
  - (b) needs the right Dreamers agent — re-evaluate which of Sentinel / Probe / Hone / Echo / Sage fits.

There is no third option. There is no "general-purpose because I'm not sure which agent to use" path.

## What implementation looks like (NO subagent)

Implementation (writing production code, writing tests, running tests, type-checking, running build / lint / format, git operations including `add` / `commit` / `push` / `mv` / `rm`, branch setup, doc updates, PR creation via `gh`) is the orchestrator's lane — done inline using the orchestrator's Edit / Write / Bash tools. The five allowed subagents are read-only reporters (Sentinel / Probe / Hone return findings) or scoped doc-writers (Echo edits docs only) — none of them write production code or run the build.

## Read-only reviewer lanes

The three reviewer agents (Sentinel, Probe, Hone) have **`tools: Read, Glob, Grep, Bash`** in their frontmatter — no Write or Edit. They cannot modify files. They return structured findings per the spec in `orchestrator-discipline.md`; the orchestrator applies fixes inline.

## Conflict resolution between reviewers

When two reviewers' findings touch the same `file:line` with contradicting fixes (e.g., Sentinel `[correctness] add defensive check` vs Hone `[simplicity] remove this as over-engineering`):

- **Correctness > simplicity always.** When in conflict, the correctness/security/maintainability finding wins.
- **Genuine ambiguity surfaces to user.** If both arguments are equally strong (rare), present the conflict before applying either.

See `orchestrator-discipline.md` § "Orchestrator-as-fixer behavior" for the full handling rules.
</delegation>

<agent-recovery>
<!-- GENERATED from .github/dreamers/refs/agent-recovery.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>

<pr-procedure>
<!-- GENERATED from .github/dreamers/refs/pr-procedure.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# PR-Creation Procedure (canonical)

This ref is the SOLE source of truth for the push + PR-creation step in the Dreamers pipeline. Consumers:

- `close-out-procedure.md` Step 6 (FULL or LIGHT close-out).
- `/dreamers-fix` Step 8.
- `/dreamers-pr-resolve` does NOT use this — it pushes updates to an existing PR, not creates a new one.

---

## Inputs

The orchestrator running this procedure must have these inputs ready (passed in the prompt context or already captured from earlier phases):

- **Branch name** — current feature branch (`fix/<slug>` for bug-fix flow, `feat/<slug>` for feature flow).
- **Default branch name** — `$DEFAULT` from earlier branch setup.
- **Plan file paths** — list of plan paths shipped this PR. Pass:
  - For milestone close-out (FULL): all plans in the feature directory.
  - For per-plan PR (LIGHT close-out, INCREMENTAL ship strategy): the single plan just completed.
  - For bug-fix flow (`/dreamers-fix`): the sentinel string `none — bug fix, no plan file` (literal value; the procedure handles the absence via the Summary fallback rule below).
- **Retro file path** — from FULL close-out Step 3. Omitted in LIGHT close-out and bug-fix flow.
- **Sentinel summary string** — concatenated reviewer outputs across cycles (FULL) or single cycle (LIGHT, bug-fix).
- **Issue reference** (optional) — number or URL. If provided, the procedure closes the issue after PR open.
- **Final commit hash** — from the most recent commit on the branch (the one being pushed).

## Outputs

- Branch pushed to origin with upstream tracking.
- PR opened against the default branch.
- Optionally: issue closed with a comment referencing the PR URL.
- PR URL returned to the caller.

The orchestrator's todo records each step's completion. This procedure does not touch the todo.

---

## Mandatory pre-push verification

Before pushing, verify:

1. **Branch identity** — `git branch --show-current` must NOT be the default branch. If on default, halt with error: "Refuse to push: working tree is on $DEFAULT, not a feature branch."
2. **Working tree clean** — `git status --porcelain` must be empty. If not, halt: "Working tree has uncommitted changes; commit them before opening the PR." (If invoked from close-out, this should already be handled by close-out Step 4 final commit; if not, surface the discrepancy.)
3. **Branch is ahead of remote** — `git log origin/$(git branch --show-current)..HEAD` should have commits, or the branch should not yet exist on remote. If the branch exists on remote and is up-to-date with local, halt: "Nothing to push." (Edge case: re-running this procedure on an already-pushed branch.)
4. **No force-push intent** — never use `--force` or `--force-with-lease` for the initial push. If a previous push exists and there's divergence, halt and ask the user.

---

## Step 1 — Push

```bash
git push -u origin <branch-name>
```

This is the ONLY push in the milestone pipeline. If push fails:
- **Rejected (non-fast-forward):** halt; surface the error. Ask the user how to proceed. Do not auto-force.
- **Network / auth error:** halt; surface; the user resolves credentials.
- **Hook failure:** halt; surface the pre-push hook output; do not skip hooks.

## Step 2 — Draft PR body

Use `~/.copilot/dreamers/templates/pr-description.md` as the base template. Fill in:

- **Summary** — one paragraph: plan title + 1–3 bullets of what was delivered + why.
  - **Bug-fix fallback (plan paths sentinel = `none — bug fix, no plan file`, OR plan paths absent):** derive the Summary from the most recent commit's body — specifically the `Bug:` line written by `/dreamers-fix` — plus 1–2 bullets drawn from the Sentinel summary string describing what changed and why. Do NOT attempt to read the sentinel string as a filesystem path. Do NOT scan `.dreamers/plans/` looking for a matching file.
- **Test counts** — only if test platforms are touched. Otherwise omit the section.
- **Fixes applied** — severity-graded list from the Sentinel summary string.

Title format: short (under 70 chars). Body details, not the title. Bug-fix invocations use the `fix:` prefix; milestone / plan invocations use the appropriate prefix per `.github/instructions/git.instructions.md` (if present).

### Co-authored attribution (mandatory)

Any co-author trailer in commit messages MUST use the standard git trailer key + this exact author identity:

```
Co-authored-by: The Dreamers System <noreply@dreamers.local>
```

Notes:
- Key must be exactly `Co-authored-by:` (git's standard trailer key) so `git interpret-trailers` and GitHub recognize the line.
- Author name is always `The Dreamers System` — never a specific model name. The system is the contributor; model identity ages poorly.
- The `<noreply@dreamers.local>` email is a placeholder — it won't link to a GitHub profile, but it satisfies the trailer's required `Name <email>` format.

The PR body should NOT include a `Co-authored-by:` line — co-author trailers belong on commits, not on PR descriptions.

## Step 3 — Open the PR

```bash
gh pr create \
  --title "<short title>" \
  --body "<drafted body>" \
  --base <DEFAULT_BRANCH>
```

Capture the returned PR URL.

If `gh pr create` fails:
- **Authentication:** halt; ask user to `gh auth login`.
- **PR already exists for this branch:** halt; surface the existing URL.
- **Repo permission denied:** halt; surface.

## Step 4 — Issue close (if applicable)

If an issue number/URL was provided as an input:

```bash
gh issue close <number> --comment "Resolved in <PR URL>"
```

If the issue close fails, surface the error but do not roll back the PR — the PR is valid even if the issue close has problems.

---

## What happens after this procedure ends

Return the PR URL to the caller (close-out procedure, `/dreamers-fix`, etc.). The caller continues with whatever step follows in its own procedure (post-PR discipline for FULL close-out, exit-with-PR-URL for bug-fix flow, etc.).

This procedure does not touch the orchestrator's todo. The caller maintains it.
</pr-procedure>

$ARGUMENTS

---

## Argument parsing

Parse `$ARGUMENTS`:

- Bare text up to (but not including) any `--<flag>` token → **bug description** (required).
- `--issue <#|url>` → **issue reference**; forwarded verbatim into `pr-procedure.md` Step 4 at Step 8. Accepts a bare issue number or a full GitHub issue URL.
- If `$ARGUMENTS` is empty or contains only flags → halt: "Usage: /dreamers-fix <bug description> [--issue <#|url>]." Do not invent a description.

Derive **slug** from the bug description: lowercase, kebab-case, drop articles and trailing punctuation, truncate to ~5–7 meaningful words. Example: "navbar misaligned on mobile after rotation" → `navbar-misaligned-mobile-rotation`.

**Slug sanitization (mandatory).** After transformation, strip every character not matching `[a-z0-9-]`. The slug must contain no spaces, slashes (beyond the `fix/` prefix added at branch creation), backticks, dollar signs, semicolons, parentheses, or any other shell metacharacter. If the sanitized slug is empty (e.g., bug description was non-ASCII-only), halt with: "Bug description does not yield a usable slug; rephrase using ASCII keywords."

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Step 1 — branch setup
- [ ] Step 2 — scope survey + escalation check
- [ ] Step 3 — implement fix inline + regression test
- [ ] Step 4 — parallel Sentinel review + test run
- [ ] Step 5 — apply Sentinel findings + re-run tests
- [ ] Step 6 — Echo gate (docs if applicable)
- [ ] Step 7 — user approval gate
- [ ] Step 8 — commit + push + PR

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Step 1 — Branch setup (inline)

Per `git-workflow.md`:

1. **Dirty-tree check FIRST (before any git write command).** Run `git status --porcelain`. If output is non-empty, halt and surface: "Working tree has uncommitted changes on `<current branch>`; resolve before invoking `/dreamers-fix`." Do not stash or discard without user approval.
2. **Current-branch check.** Run `git branch --show-current`. If the current branch is neither the default branch nor empty (i.e., user is on an unrelated feature branch), surface a confirmation via `request_information`: "Current branch is `<name>` (not default). Continuing will check out the default branch and cut a new `fix/<slug>` branch from it. Confirm to proceed." Choices: `["Continue", "Halt", "Other"]`. On Halt → stop. On Other → freeform redirect, halt.
3. Detect default branch (canonical two-step):
   ```bash
   DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
   [ -z "$DEFAULT" ] && DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
   ```
4. **Anchor to remote truth:** `git fetch origin && git log origin/$DEFAULT --oneline -5`. Never build off a stale local default.
5. `git checkout $DEFAULT && git pull origin $DEFAULT`.
6. `git checkout -b fix/<slug>` — cut from the now-fresh default. Branch name MUST be passed quoted to git to defeat any residual metacharacter (slug is already sanitized per the Argument parsing section, but quoting is defense in depth).
7. Confirm `.dreamers/` is in `.gitignore`. If not, add it before any further edit.
8. `git log --oneline -3` and confirm branch + recent commits match expectation.

---

## Step 2 — Scope survey + escalation check (BEFORE any code edit)

Survey the codebase to locate the bug and identify the minimum set of files that need to change. Use Read / Glob / Grep — no Edit / Write yet.

**Escalation criteria (mandatory check — if ANY hold, HALT before any edit):**

- Needs a new module or new top-level directory.
- Requires a schema or data-model change (migration, table alter, persisted shape change).
- Requires a cross-cutting refactor across unrelated subsystems (multiple disjoint feature areas).
- Introduces new public exported symbols (functions / classes / types / API endpoints).

If any criterion hits, call `request_information`:

```
**Scope analysis — this exceeds bug-fix scope.**

Bug: <description>

Triggered criterion: <one-line citing which of the four it hit, and why>.
Survey notes: <one or two lines on what the survey found — affected files / proposed shape>.

Lightweight fix is not appropriate here. Recommended path: `/dreamers-full <bug description>` to run the full plan + implement + close-out flow.

Options:
- Continue lightweight anyway — proceed with the fix on this branch (you accept the absence of planning + multi-reviewer review)
- Restart on /dreamers-full — abandon this branch; re-invoke as /dreamers-full
- Other — freeform redirect
```

Choices: `["Continue lightweight anyway", "Restart on /dreamers-full", "Other"]`.

- **Continue lightweight anyway** → proceed to Step 3 with user-acknowledged risk; note the escalation skip in the final Step 7 summary.
- **Restart on /dreamers-full** → output: `Branch fix/<slug> is unused. Delete with: git checkout $DEFAULT && git branch -D fix/<slug>. Re-invoke as: /dreamers-full <bug description>.` Then stop. Do not auto-invoke `/dreamers-full` — user re-runs.
- **Other** → surface the freeform back to the user as a redirect; halt (no auto-resume, no auto-commit).

If NO escalation criterion holds, proceed directly to Step 3.

---

## Step 3 — Implement fix inline + regression test

**HARD STOP — implementation is inline.** The orchestrator (this skill, running in your context) edits files directly using Edit / Write / Bash tools. **Do NOT spawn any subagent to write code, write tests, or run tests for the fix.** Specifically:
- ❌ `agent_type: "general-purpose"` → FORBIDDEN. There is no general-purpose fallback for implementation.
- ❌ `agent_type: "claude"` or any other host-runtime agent → FORBIDDEN.
- ❌ `agent_type: "forge"` / `"nova"` / `"bolt"` → FORBIDDEN (these are not subagents in this system — see `delegation.md`).
- ✅ The only `agent_type` values you may spawn from this skill are `sentinel` in Step 4 (parallel with the inline test run) and `echo` in Step 6 (only if the Echo gate fires). Nothing else.

If you reach the implementation step and find yourself thinking "let me delegate this to an agent," that's the bug. The orchestrator does the implementation. Write the regression test inline, edit the file inline, run the test command inline, stage with `git add`.

Follow the **Implementation discipline** rules from `orchestrator-discipline.md`.

1. **Regression test first** (if test infra exists per `.github/copilot-instructions.md`):
   - Write a failing test that captures the buggy behavior. The test should fail on the current (broken) code.
   - Stage with `git add`.
   - If no test infra is available for the affected surface (UI-only with no harness, etc.), skip and note the absence — this fact surfaces in Step 7's user approval block.

2. **Implement the fix** following discipline rules:
   - Only edit files in the bug's scope. No while-I'm-here cleanup, no unrelated refactors mixed in.
   - All `import` statements at the top of each file.
   - Method-signature changes: grep the full codebase for every call site before staging.
   - No spec-arguing comments in source.
   - No dependency installs without explicit user approval — if a new dependency is required, surface and ask first.
   - Stage with `git add` as work progresses.

3. **Type-check.** Run the project's type-check command (from `.github/copilot-instructions.md`). Fix any errors before Step 4. Do not proceed to review with type errors outstanding.

---

## Step 4 — Parallel Sentinel review + test run

Spawn the Sentinel review and run the test command **in a single batched tool call** — one Agent sub-tool-use + one Bash sub-tool-use, both fired concurrently. Wait for both to complete before Step 5.

**Sentinel** (`agent_type: "sentinel"`, `mode: "sync"`):
- Lenses: correctness, security, maintainability.
- Out of scope: test coverage (no Probe in this pipeline; orchestrator covers it via the regression test in Step 3), simplicity (no Hone in this pipeline).
- Prompt context (per `delegation.md`):
  - **Context:** lightweight bug fix; bug description verbatim.
  - **Prior work:** files changed (output of `git status`), regression test path (or "skipped — no harness"), type-check result.
  - **What is needed:** structured findings per `orchestrator-discipline.md` format. Focus on whether the fix actually resolves the bug, side-effects, and security/maintainability impact.
  - **Constraints:** read-only; no Write/Edit; report only.
  - **Definition of Done:** structured findings block returned (status line + findings + optional observations/open questions).

**Test run** (Bash):
- Use the test command from `.github/copilot-instructions.md`. If `./test-benchmarks.md` has a row for that command, set the timeout per the file's `max(last_run_time × 2, 30s)` formula. After the run, update the benchmark row with the new duration.
- Scope to the new + nearby tests if the runner supports it; otherwise run the full suite.

**Subagent failure recovery (Sentinel):** per `agent-recovery.md`, if Sentinel crashes or times out, read whatever it managed to write, determine the gap, and either complete inline (orchestrator has Read access to the diff) or re-spawn Sentinel scoped to the remaining check.

---

## Step 5 — Apply Sentinel findings + re-run tests

Per the **Orchestrator-as-fixer** rules in `orchestrator-discipline.md`:

1. **If Sentinel returns `Approved — no findings`** AND tests passed in Step 4 → skip fix application; proceed to Step 6.
2. **If Sentinel returns `Findings reported — N items`:**
   - Sort findings by severity (critical → high → medium → low).
   - **Evaluate each finding against the Major-refactor finding gate** per `orchestrator-discipline.md` § "Major-refactor finding gate." If ANY criterion fires for a finding (new module / schema change / cross-cutting refactor / new exported symbols / files outside the bug-fix surface / Hone-style "tear out X" scope language), call `request_information` with the 3-choice template (`Apply now — refactor in this cycle` / `Defer — create follow-up plan` / `Other`) and route per the user's answer. On `Defer`, create the stub plan file at `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md` per the canonical stub template; do NOT apply the deferred fix. The bug-fix surface is the set of files identified during Step 2 scope survey + any file the regression test touches.
   - Apply each (non-deferred) fix as a targeted Edit. Stage with `git add`.
   - Re-run the test command after all fixes applied. Update the benchmark row.
   - If tests regress after fix application → diagnose + re-fix inline. **Hard cap: 3 fix attempts total.** On the 3rd failure, halt and surface to the user — do not auto-loop.
3. **If Sentinel returns `Blocked — <reason>`** → halt the cycle; surface the block; resolve (user input if needed); re-spawn Sentinel scoped only to the affected area.
4. **If Sentinel surfaces open questions** → present each to the user before proceeding. Apply decisions; if the fix changes meaningfully, re-run tests once before moving on.

Tests must be green before Step 6. If they cannot be made green within 3 attempts, the skill stops at Step 5 and waits for user direction.

---

## Step 6 — Echo gate (judgment-based docs invocation)

Inspect `git diff --cached` (the staged change). Decide whether to spawn Echo as a subagent inline.

**Invoke Echo if ANY of these hold:**

- **User-facing behavior changed** — UI copy, layout, navigation, error messages the user sees, fixed user-visible flows.
- **Public API / interface contract changed** — exported function signatures, request / response shapes, CLI flags, public type definitions.
- **Setup / config / install steps changed** — `.env` keys, install commands, build commands, runtime environment requirements.
- **Test commands changed** — anything Bolt-style git agents or Probe rely on.
- **Significant new file or exported symbol** — rare in fix scope (usually caught by Step 2 escalation), but possible.

**Skip Echo if NONE hold** — cosmetic-only fixes, internal logic fixes with no surface change, error-log-string adjustments not user-visible, etc.

If invoking, spawn Echo via the `task` tool (`agent_type: "echo"`, `mode: "sync"`). Pass in the prompt (per `delegation.md`):
- Plan file paths: `none — bug fix, no plan file; use changed-files list as sole signal`.
- Changed files: output of `git diff --name-only origin/$DEFAULT...HEAD`.
- Diff base: `origin/$DEFAULT`.
- Sentinel summary string: the chat output from Step 4 (with severity counts).

Echo's prompt MUST include: "Do NOT call `manage_todo_list`. The orchestrator owns the todo." (per `orchestration-flow.md` § "Single-owner todo").

Wait for Echo to signal completion. Capture Echo's doc-changes log + any open questions. Resolve open questions before proceeding.

Stage any new doc edits with `git add`.

If skipping, record the decision (one-line: "Echo skipped — <reason>") for the Step 7 summary.

---

## Step 7 — User approval gate (MANDATORY)

Before following `pr-procedure.md` inline, present this block:

```
**Bug fix ready to ship.**

Bug: <description>
Branch: fix/<slug>

Files changed (<N>):
- <file 1> — one-line summary
- <file 2> — one-line summary
- ...

Regression test: <path, or "skipped — no harness for this surface">
Test run: <pass/fail + duration; e.g. "pass in 18s">
Sentinel: <"Approved — no findings" | "Findings reported — N items applied (severity breakdown)">
Echo: <"invoked — N docs touched (paths)" | "skipped — <reason>">
Escalation note: <"none" | "user opted Continue lightweight anyway despite scope-blowup signal">

Issue reference: <number/URL, or "none">

Options:
- Approved — push + PR (proceed to Step 8)
- Halt for now (stop here; branch preserved on fix/<slug>; no push)
- Other (freeform corrections)
```

Call `request_information` with choices `["Approved — push + PR", "Halt for now", "Other"]`.

- **Approved — push + PR** → proceed to Step 8.
- **Halt for now** → output: `Stopping before push. Branch fix/<slug> is preserved with all current edits and commits. To continue, re-invoke /dreamers-fix with the same bug description — note that Step 1 will re-cut the branch from a fresh origin/<default>, so cherry-pick or merge work from the preserved branch onto the new one before continuing.` Stop.
- **Other** → treat as not-yet-approved. Apply corrections inline. If code touched, re-run tests. If logic changed materially, re-spawn Sentinel. Re-present this gate. Loop until approved.

This is the last point where the user can halt before the PR goes live.

---

## Step 8 — Commit, push, PR

1. **Stage any remaining working-tree changes.**
   - `git status` to inspect.
   - If the working tree shows unstaged changes (orphaned edits from inline work, Echo doc edits not yet staged, etc.), stage them explicitly with `git add <files>` — list each file, never `-A` blanket. This is the last chance before the commit; do NOT skip even if Steps 3 / 5 / 6 are believed to have staged everything.
   - After staging, re-run `git status` to confirm a clean working tree (only staged content remaining).

2. **Final commit (inline).**
   - `git commit` with message per `.github/instructions/git.instructions.md` (if present) or conventional-commits style. Subject: `fix: <one-line summary derived from bug description>`. Body MUST include `Bug: <description>` line so the fix is traceable without a plan file (downstream `pr-procedure.md` reads this).
   - Commit trailer (mandatory per `orchestrator-discipline.md` git rules): `Co-authored-by: The Dreamers System <noreply@dreamers.local>`.

3. **Follow `~/.copilot/dreamers/refs/pr-procedure.md` inline** (the ref is inlined above in this skill body — refer to that block, not a runtime `view`). Pass these inputs to the procedure:
   - Branch name: `fix/<slug>` (from `git branch --show-current`).
   - Default branch name: `$DEFAULT`.
   - Plan file paths: explicit `none — bug fix, no plan file` — this is a recognized sentinel value that `pr-procedure.md` Step 2 handles via its bug-fix Summary fallback (derived from the commit body's `Bug:` line + Sentinel summary instead of a plan title).
   - Retro file path: **omitted** (no retro in fix flow).
   - Sentinel summary string: the structured-findings output from Step 4 (with severity counts and the fixes applied).
   - Issue reference: forwarded from `$ARGUMENTS`'s `--issue` flag if provided; else omitted.
   - Final commit hash: from the commit just created.

The procedure runs inline (pre-push verification → Step 1 push → Step 2 draft body → Step 3 open PR → Step 4 issue close if applicable). Capture the PR URL it returns.

This skill does NOT invoke any other skill — the PR-creation procedure runs inline from `pr-procedure.md`.

---

## Exit behavior

Return in chat output:
- PR URL.
- Issue closed (yes / no / n/a).
- Files changed (count + path list).
- Test result (pass + duration).
- Sentinel summary (one line: findings count + severity breakdown).
- Echo verdict (invoked + docs touched, or skipped + reason).
- Escalation note (if user opted Continue lightweight anyway).

Tell the user: post-PR discipline applies — no auto-commit of further changes (review comments, CI failures); ask first before any post-PR push. This skill does NOT run the `/dreamers-close-out` post-PR project-state scan; that scan lives in `/dreamers-close-out` for milestone flows. For a single fix, the user reviews the PR and merges manually.

---

## What this skill does NOT do

- Does NOT write a plan file. The bug description is the only input artifact; the commit body's `Bug:` line is the durable record.
- Does NOT invoke `/dreamers-plan`, `/dreamers-implement`, or `/dreamers-close-out`. It is a complete, self-contained pipeline.
- Does NOT spawn Probe or Hone. Sentinel is the only reviewer; the regression test (Step 3) covers what Probe would have spawned for.
- Does NOT auto-escalate to `/dreamers-full`. On scope blowup, Step 2 surfaces the choice and stops — user re-invokes the other skill themselves.
- Does NOT touch `.dreamers/improvements.md` or write a retro file. Lightweight by design.
- Does NOT push between steps — there is only one push, via `pr-procedure.md` Step 1 (invoked inline at Step 8).

---

## When this skill is NOT the right tool

- **A genuine new feature** masquerading as a "bug" → use `/dreamers-full <feature description>` directly.
- **Multi-plan refactor** → use `/dreamers-full` with variadic plan paths or manifest mode.
- **Doc-only typo fix** → just edit the doc and commit. Don't spin up a pipeline.
- **Question about existing behavior** (not a real bug) → answer in chat; no pipeline.
- **Bug that triggers Step 2 escalation criteria and the user chooses to plan it properly** → `/dreamers-full` is the right tool, not this one.
