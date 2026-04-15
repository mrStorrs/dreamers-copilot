---
name: dreamers-research
description: 'Deep research with phased workflow: scoping, parallel sub-topic research, synthesis, final report. Triggers: /dreamers-research, research, deep research, investigate, find out about.'
argument-hint: '$ARGUMENTS'
---

Deep research skill with phased workflow: preliminary scoping → user selection → parallel research/review loops.

$ARGUMENTS

---

## Phase 1 — Preliminary Research (Scoping)

**Objective:** Identify sub-topics within the main research topic before committing to deep research.

Invoke **Sage** (subagent_type: `sage`) with:
- **Mode:** preliminary
- **Task:** Identify 5-10 distinct sub-topics/dimensions of the research question
- **Output:** `scope.md` with numbered sub-topics, each with:
  - Short title
  - One-sentence description
  - Why it matters to the overall question
  - Estimated research depth needed (quick/moderate/deep)

**Prompt template for Sage:**
```
Mode: preliminary
Topic: [user's topic]

Conduct preliminary research to identify the key sub-topics within this domain.

1. Do 3-5 broad web searches to understand the landscape
2. Identify 5-10 distinct sub-topics or dimensions worth researching
3. For each sub-topic, note: title, description, relevance, recommended depth
4. Write findings to .dreamers/sage/scope.md

Do NOT do deep research yet. This is scoping only.
```

After Sage returns, present the sub-topics to the user in chat:
```
## Research Scope: [Topic]

Sage identified the following sub-topics:

1. **[Title]** — [description] (recommended: [depth])
2. **[Title]** — [description] (recommended: [depth])
...

**Select which to research:**
- "all" — research all sub-topics
- "1, 3, 5" — research specific numbers
- "1-4" — research a range
- "none" — cancel

Which sub-topics should I research?
```

**Do not proceed to Phase 2 until user explicitly selects sub-topics.**

---

## Phase 2 — Deep Research Loop (Parallel)

For each selected sub-topic, run two sequential agent calls:
1. **Research** — Sage deep-dives on the sub-topic
2. **Review** — Sage reviews and verifies the research

**These sub-topic pipelines can run in parallel** — launch up to 6 concurrent research/review pairs.

### Step 2a: Research (per sub-topic)

Invoke **Sage** with:
```
Mode: deep
Topic: [sub-topic title]
Parent topic: [original topic]
Depth: [recommended depth from scope.md]

Conduct deep research on this sub-topic.

Follow the full 5-phase pipeline:
1. SCOPE — define boundaries for this sub-topic
2. DISCOVER — generate perspectives and queries
3. GATHER — search and collect sources
4. VERIFY — cross-reference and fact-check
5. SYNTHESIZE — write sub-topic report

Output files (use sub-topic slug in paths):
- .dreamers/sage/[slug]/scope.md
- .dreamers/sage/[slug]/perspectives.md
- .dreamers/sage/[slug]/sources.md
- .dreamers/sage/[slug]/verified-claims.md
- .dreamers/sage/[slug]/report.md
```

### Step 2b: Review (per sub-topic)

After research completes, invoke **Sage** again with:
```
Mode: review
Sub-topic: [sub-topic title]
Research path: .dreamers/sage/[slug]/

Review the research for this sub-topic:

1. Read all files in the research directory
2. Check citation accuracy — do URLs resolve? Are claims supported?
3. Check for gaps — any obvious perspectives missing?
4. Check for bias — is coverage balanced?
5. Check confidence ratings — are they appropriate?
6. Write review findings to .dreamers/sage/[slug]/review.md

If critical issues found, flag them. Otherwise mark as verified.
```

### Parallel Execution Pattern

```
Sub-topic 1: [Research] → [Review] ─┐
Sub-topic 2: [Research] → [Review] ─┤
Sub-topic 3: [Research] → [Review] ─┼─→ All complete → Phase 3
Sub-topic 4: [Research] → [Review] ─┤
Sub-topic 5: [Research] → [Review] ─┘
```

Launch all research calls in parallel (single message with multiple Agent tool invocations).
When a research call completes, immediately launch its review call.
Track completion status for each sub-topic.

---

## Phase 3 — Synthesis

Once all sub-topic pipelines complete, invoke **Sage** one final time:

```
Mode: synthesis
Topic: [original topic]
Sub-topics researched: [list]
Research paths: [list of .dreamers/sage/[slug]/ paths]

Synthesize all sub-topic research into a comprehensive final report.

1. Read all sub-topic report.md files
2. Read all review.md files for quality notes
3. Create unified outline covering all sub-topics
4. Write executive summary
5. Synthesize findings, noting where sub-topics connect
6. Include full source list with all citations
7. Write to .dreamers/sage/final-report.md
```

---

## Phase 4 — Delivery

Present the final report to the user:

```
## Research Complete: [Topic]

**Sub-topics researched:** [count]
**Total sources consulted:** [count from all sources.md files]
**Confidence:** [overall assessment]

### Executive Summary
[paste executive summary from final-report.md]

**Full report:** .dreamers/sage/final-report.md
**Sub-topic reports:** .dreamers/sage/[slug]/report.md (x[count])

Would you like me to:
- Expand any sub-topic further
- Research additional sub-topics
- Export to a different format
```

---

## Error Handling

**If Sage fails on a sub-topic:**
1. Log the failure in `.dreamers/sage/errors.md`
2. Continue with other sub-topics
3. Report failed sub-topics at delivery

**If review finds critical issues:**
1. Flag the sub-topic as needing revision
2. Optionally re-run research with tighter constraints
3. Report issues at delivery

---

## Workspace Structure

```
.dreamers/sage/
├── scope.md                    # Phase 1 output
├── errors.md                   # Any failures logged
├── final-report.md             # Phase 3 output
├── [sub-topic-1-slug]/
│   ├── scope.md
│   ├── perspectives.md
│   ├── sources.md
│   ├── verified-claims.md
│   ├── report.md
│   └── review.md
├── [sub-topic-2-slug]/
│   └── ...
└── ...
```

