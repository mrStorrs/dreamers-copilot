---
name: dreamers-review
description: 'Canonical review phase. Spawns Sentinel + Probe + Hone in parallel, applies findings inline, gates major-refactor findings to the user, re-runs tests. Called by /dreamers-implement, /dreamers-fix, /dreamers-pr-resolve; invokable standalone with --lens for ad-hoc single-lens audit. Triggers: /dreamers-review, review my code, audit.'
argument-hint: '[--lens sentinel|probe|hone] [--paths <glob>] [--branch] [--no-apply]'
---

$ARGUMENTS

---

## Modes

| Flag | Behavior |
|---|---|
| (default) | Triad: Sentinel + Probe + Hone in parallel + apply findings + major-refactor gate + re-run tests. |
| `--lens <name>` | Single-lens audit (`sentinel` / `probe` / `hone`). No fix application; surface findings only. |
| `--no-apply` | Triad runs but findings are surfaced without applying (read-only). |

Scope flags: `--paths <glob>` (specific files), `--branch` (feature-branch diff vs default), default = staged + unstaged.

---

## Phase 1 — Spawn

Triad: one batched `task()` call with three sub-invocations (Sentinel + Probe + Hone, all `mode: "sync"`).

Each prompt MUST include `Do NOT call manage_todo_list.`

Common context per reviewer:
- Plan file path (if invoked from `/dreamers-implement` or `/dreamers-fix` with a plan)
- Scope: file list from arg parsing
- Branch + default-branch names
- For manifest-mode runs: shared-context payload (constraints / design decisions / data models / end-to-end ACs) under "Feature context"

Per-lens prompt:
- **Sentinel** (`agent_type: "sentinel"`) — correctness / security / maintainability. Return findings + plan-alignment summary.
- **Probe** (`agent_type: "probe"`) — test coverage (AC matrix, layer audit, edge cases, gaps). Return findings + AC coverage table.
- **Hone** (`agent_type: "hone"`) — simplicity / over-engineering / redundancy / architecture. Return findings. **Mandate verbatim:** "Aggressively flag bad architecture, over-engineering, redundancy, and simpler alternatives. Refactor cost is NOT a moderating factor. When the suggested fix has architectural scope, state it explicitly. The major-refactor gate handles disposition."

Wait for all three to return. Single-lens mode: spawn only the chosen reviewer; skip Phase 2 (apply findings).

---

## Phase 2 — Apply findings (orchestrator-as-fixer)

1. **Concatenate** findings from all three reviewers; sort by severity (critical → low).
2. **Conflict resolution.** Same `file:line` with contradicting fixes: correctness > simplicity. Genuine ambiguity → `request_information` before applying.
3. **Major-refactor gate (see Phase 3).** For each finding, check the criteria checklist. If any criterion fires, route through the gate. Never silently apply a gate-triggering finding regardless of severity.
4. **Apply each non-deferred fix** as a targeted Edit. Stage with `git add`.
5. **Re-run type-check + tests** after applying. If regression appears, fix inline (max 3 attempts) before halting.

Non-finding outputs:
- Reviewer returns `Blocked` → halt; surface verbatim; resolve with user; re-spawn that reviewer only.
- Reviewer returns open questions → present each via `request_information`; capture; apply decisions; re-run tests once (no full re-spawn).
- All three return `Approved — no findings` → skip to Phase 4.

---

## Phase 3 — Major-refactor finding gate

A finding is "major-refactor scope" if its suggested fix meets **any** of:

1. **New module or top-level directory** not in the plan's scope.
2. **Schema / data-model change** (DB schema, persisted shape, migration, core data-model interface).
3. **Cross-cutting refactor** (touches multiple unrelated subsystems).
4. **New public exported symbols** not specified in the plan.
5. **Files outside the plan's scope** (or outside the bug-fix surface for `/dreamers-fix`).
6. **Hone-recommended full refactor** — scope language like "tear out X across N files," "rewrite Y module," "remove Z abstraction and inline at N call sites."

Closed checklist. Don't invent new criteria at runtime. Ambiguous → fire the gate.

### Gate prompt

For each gate-triggering finding (or batched group sharing the same refactor scope), `request_information`:

```
**Major-refactor finding surfaced.**

Reviewer: <sentinel | probe | hone>
Severity: <critical | high | medium | low>
Lens: <correctness | security | maintainability | test-coverage | simplicity>
Location: <file:line>

Finding:
<what was wrong>

Suggested fix:
<suggested fix verbatim>

Triggered criterion: <N — short label>
Rationale: <one sentence — why criterion N fired for THIS finding>
Breadth estimate: <files touched, ~LOC, in-plan-scope: yes/no>

Options:
- Apply now — refactor in this cycle
- Defer — create follow-up plan
- Other
```

### Routing

- **Apply now** → fix inline at Phase 2 step 4; stage; re-run tests at step 5.
- **Defer** → do NOT apply. Create a stub plan file at `.dreamers/plans/feature-<deferred-slug>/plan-01-<short-slug>.md` per `plan-writing-guide.md`. Stub captures the finding verbatim with TBD ACs/constraints/verification. Surface the stub path to the user and continue with remaining findings.
- **Other** → treat as freeform redirect. If user clarifies "yes apply" → Apply now; if "no defer" → Defer; otherwise follow their direction. Never silently apply/defer on Other.

### Batching

Multiple findings sharing the same refactor scope (e.g., 3 Hone findings on the same module) MAY combine into one gate call. User's single answer applies to all batched findings. When in doubt, don't batch.

### Severity does NOT bypass the gate

Critical/high findings still go through the gate when they meet criteria. The user disposes.

---

## Phase 4 — Re-verification after fixes

**Snapshot first (required before applying):** `git diff --cached --name-only` + `git diff --cached --stat`. This snapshot measures the fix-pass delta — without it, the significant-refactor criteria can't be evaluated.

After applying fixes, re-run the project's test command. No reviewer is re-spawned by default. A **second 3-parallel pass** runs ONLY if the significant-refactor criteria fire AND the user opts in via `request_information`.

### Significant-refactor criteria (fix-pass delta vs snapshot)

ANY ONE fires eligibility (not automatic — user opt-in required):

1. More than 5 production files touched in the fix pass.
2. More than 150 LOC of production code changed in the fix pass.
3. A new file was added by the fix pass.
4. A new exported/public symbol was introduced.
5. Code was moved between modules.

Test files are excluded from criteria 1–2. Structural criteria 3–5 apply to all file types.

### Second-pass prompt

If criteria fire, `request_information`:

```
Fix-pass delta exceeds significant-refactor threshold.
Triggered criterion: <N — measured values>
Reasoning: <one sentence — why a second pass is recommended>

Options:
- Run second 3-parallel pass
- Skip — commit as-is
- Other
```

- **Run second pass** → re-spawn Sentinel + Probe + Hone, re-apply findings, re-run tests.
- **Skip** → commit as-is (caller's commit step).
- **Other** → freeform redirect. Halt — do not auto-commit, do not auto-spawn.

---

## Output

Return chat output to caller:
- Triad status (Approved / Findings applied / Blocked / Open questions).
- Per-lens findings summary (counts by severity + lens).
- Files modified during apply-findings.
- Gate decisions (apply / defer / stub paths created).
- Test status (green / regression details).

Standalone mode (single-lens or `--no-apply`): pass reviewer chat output through verbatim; no fix application; no test re-run.

---

## Dreamers Kernel

Inlined by `scripts/sync-refs.ps1`. Do not edit between tags — edit source + re-sync.

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

## Subagent prompt — required content

Every `task()` invocation MUST include in the prompt:
- **Context** — what this agent is being asked to do and why
- **Prior work** — what was done previously, with absolute paths to any output files
- **What is needed** — specific deliverable
- **Constraints** — hard rules the agent must not violate
- **Definition of Done** — how to know the work is complete
- **Plan file path** — absolute path to the relevant plan file (if applicable)
- **Mandatory line:** `Do NOT call manage_todo_list. The skill that invoked you owns its todo.`

All `task()` calls use `mode: "sync"` — the call blocks until the agent returns.

## Continuation principle

At every natural pause between phases — where the skill has produced a meaningful result and the user could redirect — call `request_information` with three choices: `Continue` / `Halt for now` / `Other` (freeform). Never silently advance; never silently stop. On `Halt`, emit a one-line resume command and stop.

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

<reviewer-findings-format>
<!-- GENERATED from .github/dreamers/refs/reviewer-findings-format.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Reviewer Findings Format

All three reviewers (Sentinel, Probe, Hone) return chat output in this exact format. The caller (typically `/dreamers-review`) parses against this spec.

**Status line** (one of):
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

Reviewers are read-only / report-only. The caller applies fixes per its own orchestrator-as-fixer behavior.
</reviewer-findings-format>

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

<agent-recovery>
<!-- GENERATED from .github/dreamers/refs/agent-recovery.md -- do not edit between tags; edit the source file and re-run scripts/sync-refs.ps1 -->
# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. Read whatever workspace files the agent managed to write before failing.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly (you have Read, Write, Edit, Glob, Grep, Bash in the main conversation) or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
</agent-recovery>
