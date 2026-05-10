---
name: dreamers-pr-resolve
description: 'Resolve unresolved PR review comments via Forge and Probe pipeline. Triggers: /dreamers-pr-resolve, resolve PR comments, address review comments, fix PR feedback.'
---

Resolve unresolved PR review comments. Route: Forge → Probe → resolve threads.

Read these refs:
- `~/.copilot/dreamers/refs/delegation.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

**Step 1 — Discover open PRs**
Run `gh pr list --state open` to find all live PRs. If a specific PR is provided in the arguments, use that one. If multiple are open and none is specified, ask the user which PR to target before proceeding.

$ARGUMENTS

**Step 2 — Pull unresolved review threads**
Use the helper (REST `resolved` is unreliable — the script wraps the canonical GraphQL query):
```bash
~/.copilot/dreamers/scripts/dreamers-pr-unresolved.sh <PR_NUMBER>
```
Output is a JSON array of `{threadId, path, body}` for unresolved threads only. If empty, report that back to the user and stop.

**Step 3 — Invoke Forge**
Pass all unresolved threads to Forge (follow delegation.md) with this framing:
- Forge is the implementation expert and has full authority to accept or reject each comment.
- For each thread: decide accept or reject, implement if accepted, include a brief rationale per decision in Forge's chat output (per `forge.agent.md` Output discipline — the chat output replaces the dropped `implementation.md`).
- Forge should not feel obligated to accept every comment — if a suggestion conflicts with the plan, the architecture, or is simply wrong, reject it and say why.

**Step 4 — Invoke Probe**
After Forge completes, route to Probe to verify that accepted changes pass tests and nothing regressed.

**Step 5 — Resolve comments (Bolt)**
After Probe passes, invoke **Bolt** to resolve each accepted thread:
```bash
~/.copilot/dreamers/scripts/dreamers-pr-resolve-thread.sh <THREAD_ID>
```
Pass Bolt the list of accepted-thread IDs and have it call the script once per ID. Leave rejected threads open — they represent active disagreements the reviewer should see.

Bolt reports back: threads resolved. Then report to the user: how many comments were accepted, how many rejected, and which threads remain open (with a one-line reason per rejection).

