### Phase 1A — Grill

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

Record the Grill exchange verbatim while it happens. Preserve every planner
question and every user response in chronological order, exactly as sent or
received. Do not summarize, paraphrase, normalize, combine, correct, or omit
text. For `request_information`, include the complete presented question,
choice labels, and choice descriptions. Preserve separate responses as
separate entries.

In Step 2, when the feature plan directory is known, write the accumulated
exchange to `.dreamers/plans/feature-<slug>/grilling-transcript.md` with only
speaker/sequence headings added around the unchanged message text. If no Grill
question and response occurred, do not create an empty transcript.
