# Planning workflow

Execute this workflow inline with the supplied input. Resolve links relative to this ref. Read the linked standards before acting. Keep the active skill's todo, gates, and delivery state.

If the task is missing, ask. Work inline and write only `.dreamers/plans/` artifacts; do not change project files or git state. When used standalone, own a planning todo; as a delivery phase, use the active skill's existing todo.

## 1: Grill
Read and apply [planning-grill](planning-grill.md).

## 2: Generate plan(s) proposal
- generate plans following `plan-format`
- plans should be the smallest shippable chunks. do not break up arbitrarily if doing so would cause more work.
- when more than one plans are needed generate a manifest.md

## 3: Propose to user
- If: change requires a single plan. then present the full plan to the user.
- Else: Then present the manifest when task requires multiple plans.

Present the proposal and any critiques through `request_information`: risks, assumptions, tradeoffs, and simpler alternatives. Answer questions and corrections with reasoning and a recommendation; revise and re-present until approved.

## 3: Write plan(s)
- Create `.dreamers/plans/feature-<slug>/`.
- Write numbered `plan-NN-<name>.md` files using `plan-format`; add `manifest.md` when multi-plan task

## 3: Review gate

Present plan paths through `request_information`: `Approved` / `Minor edit` / `Major rewrite` / `Halt` / `Other`.

- Minor edit: apply, repeat Step 2 checks, and re-present.
- Major rewrite: return to Step 1 with the correction.
- Halt: stop and surface paths.
- Other: follow the user's direction.

On approval, return plan paths. When used standalone, stop and suggest `/dreamers-implement <plan-path>` as a next command for the user. As a delivery phase, return to the active skill's implementation-start gate.

Read and apply [plan-format](plan-format.md).

Read and apply [manifest-format](manifest-format.md).
