### Phase 1A — Grill

For task descriptions, run Grill by default. Skip it only when the user supplies
--no-grill or unmistakable natural-language direction such as "do not grill"
or "skip the interview." Record the reason, remove control syntax from the task
description, and continue through proposal and plan-quality checks.

Plan path and manifest artifact modes skip Grill because the user supplied the
implementation specification. They still require artifact quality and drift
checks.

```
Interview me relentlessly about every aspect of this plan until
we reach a shared understanding. Walk down each branch of the design
tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore
the codebase instead.

When a decision still needs user input, use `request_information`.
Ask one blocking question at a time; do not dump a batch of questions
in chat. Each question must include exactly these choices:

1. Your recommended answer, labeled as recommended.
2. The strongest viable alternate.
3. `Other` for freeform direction.

After each answer, fold the decision into the shared understanding,
then continue to the next unresolved branch.
```
