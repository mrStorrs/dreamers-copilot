# Orchestration flow — continuation principle + todo-list protocol

Single source of truth for two orchestration principles that apply across all Dreamers skills.

---

## Continuation principle

### Definition

The orchestrator MUST NOT silently halt mid-feature. At every natural pause — where a phase ends and a meaningful choice about what to do next exists — the orchestrator calls `request_information` with a structured choice block. The user picks `Yes`, `No`, or `Other (freeform)`. No silent forward progress; no silent stops.

### Pause-point list

The following are the canonical natural pauses where a continuation prompt is required:

1. After Phase 1g approval (Mode 1), before entering Phase 2 implementation.
2. Between ATOMIC cycles in a multi-plan loop, after each plan's commit and drift check, before the next cycle starts — only when more plans remain.
3. Between LIGHT close-outs in INCREMENTAL multi-plan mode, after each per-plan PR opens, before the next cycle starts — only when more plans remain.

Existing approval gates (Phase 1c proposal approval, Phase 1g plan-file approval, close-out Step 5 push approval) are separate from continuation prompts. They remain unchanged. Continuation prompts fire around them, not instead of them.

### Prompt template

Use this shape for every continuation prompt:

```
<status summary — one sentence stating what just completed>

<concrete next action — one sentence stating what will happen if the user says Yes>

Options:
- label: Continue — <specific yes-action label>
- label: Halt for now — No (halt; resume later)
- label: Other — freeform redirect
```

Call `request_information` with at minimum these three choices. The `Yes` label must name the concrete next action (e.g., "start Phase 2", "start next cycle for plan-auth.md", "wait for merge and start plan-b.md").

### Halt behavior

On `No` at any continuation prompt: halt cleanly. Output one line:

```
Resume by re-invoking `/dreamers-full` with the remaining plan paths: <paths>
```

Do not leave partial state dangling. Stage nothing new. Do not proceed.

On `Other`: treat the freeform input as a redirect instruction. Acknowledge it, confirm the new direction, and proceed accordingly.

---

## Todo-list protocol

### Declare at orchestrator entry

At skill entry, declare the todo list via `manage_todo_list`. Each item corresponds to one major phase or step in the skill. Declare all items upfront — do not add items mid-run.

### Mark in-progress + completed as you go

When starting an item: mark it `in_progress`.
When completing it: mark it `completed`.
Never batch completions at the end of the run. The todo list is a live progress indicator, not a retrospective log.

### Composed vs standalone

When a skill is invoked in **composed mode** (called by `/dreamers-full` or another orchestrator skill), it MUST NOT declare a new todo list. Instead, it updates the parent orchestrator's matching items:

- Mark the parent's item `in_progress` when starting.
- Mark it `completed` when done.

This keeps one coherent list visible end-to-end. Nested lists produce duplicate, confusing progress views.

When a skill is invoked **standalone** (user invokes directly), it declares its own list.

### One item per major phase

Granularity: one item per major phase or clearly distinct step. Not one item per line of work. Not one item per sub-step within a phase. The goal is a scannable overview, not a micro-log.

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
