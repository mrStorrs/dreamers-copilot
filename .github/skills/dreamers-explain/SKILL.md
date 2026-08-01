---
name: dreamers-explain
description: 'Thoroughly explain any topic, code, document, system, or decision using layered explanations, concrete examples, local evidence, and authoritative sources when needed. Triggers: /dreamers-explain, explain this, help me understand, walk me through, teach me.'
argument-hint: '<question, topic, path, code, or URL>'
---

$ARGUMENTS

---

## User overrides

- Explicit user instructions control audience, depth, format, source use, and whether to include a comprehension check.

## Boundary

- Default to read-only work. Inspect relevant files, history, documentation, and external sources; do not modify the subject being explained.
- Answer in the conversation unless the user explicitly requests a durable artifact.
- Use `/dreamers-research` instead when the requested outcome is a durable, multi-perspective research report with scoped sub-topics and review loops. Do not turn a focused explanation into that pipeline.
- If no subject or question was provided, halt and ask what to explain.

## Resolve the request

Identify:

- **Subject** — the topic, claim, code, file, diff, document, system, decision, or URL to explain.
- **Goal** — what the user is trying to understand or do afterward.
- **Audience** — use an explicit level when supplied; otherwise infer it from the request and conversation. Default to an intelligent non-specialist and introduce prerequisites just in time.
- **Depth** — honor explicit requests such as quick, standard, deep, first-principles, ELI5, or expert. Default to standard.

Ask one concise question only when the subject is missing or ambiguity would materially change the explanation. Otherwise state a small assumption and proceed.

## Ground the explanation

Use the narrowest evidence route that can answer accurately:

1. For local code or documents, inspect the named material and enough surrounding context to explain purpose, data flow, dependencies, and consequences. Cite file paths and line numbers for material claims.
2. For supplied text or links, ground the explanation in that material. Distinguish what it states from interpretation or inference.
3. Search or retrieve external sources when:
   - the user asks for sources, verification, quotes, or current information;
   - facts may have changed;
   - the topic is niche, disputed, uncertain, or high-stakes;
   - a named page, paper, standard, dataset, product, or API must be inspected.
4. Do not browse by default for stable foundational knowledge when external verification would not improve the answer.

Source priority:

1. User-provided material and repository evidence for claims about that material or repository.
2. First-party documentation, specifications, standards, primary research, and original datasets.
3. High-quality secondary sources for context, comparison, or independent analysis.

Cross-check consequential or disputed claims with independent sources when practical. Never invent a citation or imply that a source supports more than it does. If reliable support remains unavailable, state the uncertainty and explain its effect on the answer.

## Build the explanation

Choose only the layers that help this request; do not force every heading into every response.

1. **Direct answer** — open with the simplest accurate statement of what the subject is, does, or means.
2. **Orientation** — explain why it exists, what problem it addresses, and where it fits.
3. **Mental model** — give the central intuition before detail. Use an analogy only when it preserves the important mechanics; label its limits.
4. **Mechanics** — walk through the causal sequence, data flow, argument, or procedure in a logical order. Explain why each important step follows from the previous one.
5. **Concrete example** — use toy data, a minimal scenario, a worked example, or a traced execution. For code, connect the example back to specific symbols and files.
6. **Edges and alternatives** — cover assumptions, failure modes, tradeoffs, common misconceptions, and meaningful alternatives.
7. **Takeaway** — close with the few ideas the user should retain or the next practical step.

For deep explanations, also surface prerequisites, hidden assumptions, connections to adjacent concepts, and the strongest reasonable counterpoint. Thorough means covering the causal chain and important boundaries, not maximizing length.

## Presentation

- Lead with the outcome. Use clear language and define jargon on first use.
- Adapt structure and density to the user. Prefer cohesive prose; use lists, tables, code, equations, or diagrams only when they materially improve understanding.
- Use the smallest useful visual. Label components and show example values when they clarify flow.
- Separate sourced fact, local observation, inference, and analogy when a reader could confuse them.
- Place citations next to the claims they support. Use descriptive links for web sources and clickable file-and-line references for local evidence.
- Cite enough to verify externally checkable claims without attaching citations to every stable or purely explanatory sentence.
- Quote sparingly; prefer faithful paraphrase.
- Do not expose hidden reasoning. Present concise derivations, evidence, checks, and conclusions instead.

## Comprehension

Do not force a quiz or Socratic exchange. If the user asks to learn, practice, be quizzed, or work interactively:

- explain one coherent unit at a time;
- ask prediction, comparison, or application questions that test the mental model rather than trivia;
- give graduated hints before revealing an answer when requested;
- adjust depth from the user's responses.

For a normal explanation, end cleanly. Offer a comprehension check or a deeper follow-up only when it would be useful.

## Final check

Before responding, verify:

- the answer addresses the user's actual goal, not only the surface noun;
- the core explanation appears before detail;
- examples match the mechanics described;
- important assumptions, caveats, and uncertainty are visible;
- every citation supports its nearby claim and the best available source type was used;
- the explanation is thorough without avoidable repetition.
