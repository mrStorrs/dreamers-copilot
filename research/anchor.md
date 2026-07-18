# Code Commandments Research Anchor

Date started: 2026-07-03

## Original User Brief

> i want to make a solid list of "code commandments" these commandments should be general coding rules that apply to all code. they should be the highest most important rules of code. first lets do some research. create an md file called inital-rule-research.md. in there create a table. then research code improvement rules, systems, etc and extract from them these rules. for each table entry write the source. rate the source. and put 1/5 number 5 being the highest 1 being the lowest on how important you think the rule is. keep going until i stop you. search everywhere. reddit, coding websites, documetnations, whatever you can find. keep a running sources.md list of everything you checked, and the date you checked it. also turn this prompt into an "anchor.md" file that you can refer back to if the context compacts

Additional instruction added by user:

> one more thing. have agents do the seraching and report back to you. that way you can batch and do more faster

## Working Objective

Build a broad research base for universal "code commandments": high-level, generally applicable coding rules that apply across languages, stacks, and domains.

## Output Files

- `inital-rule-research.md`: running table of extracted candidate rules, source attribution, source rating, and rule importance rating.
- `sources.md`: running ledger of every source checked and the date checked.
- `anchor.md`: this file, preserving the task brief and operating constraints.

## Rating Scales

Source rating:

- 5: primary, canonical, or highly authoritative source with broad industry relevance.
- 4: strong expert, major organization, widely adopted guide, or well-supported technical article.
- 3: useful but narrower, more subjective, or less formal source.
- 2: anecdotal, lightly supported, or mainly useful as community signal.
- 1: weak, low-signal, outdated, or mostly noise.

Rule importance:

- 5: foundational rule that prevents major defects, security issues, maintainability collapse, or repeated delivery failure.
- 4: broadly important rule that strongly improves code quality in most systems.
- 3: useful rule with context-dependent exceptions.
- 2: narrow or situational guidance.
- 1: weak candidate for a universal commandment.

## Research Method

- Use parallel agents for source-family research when possible.
- Include canonical engineering practices, secure coding standards, testing guidance, reliability/operations guidance, style guides, community discussion, and influential books/articles.
- Keep source quotes short or paraphrased.
- Prefer deduplicated rule wording in the research table, but preserve source-specific evidence.
- Continue expanding until the user stops or redirects.

## Current Progress

- Latest validated research row: 1124.
- Latest validation date: 2026-07-03.
- Current workflow: spawn parallel Sage agents for source-family research, deduplicate their findings against `inital-rule-research.md`, append new rules, append checked sources to `sources.md`, then validate table numbering and column counts before the next batch.

## Last Completed Agent Batch

Started: 2026-07-03
Completed: 2026-07-03

- `019f298c-db0c-7c31-92c6-ad5b5592d3a1` / Hooke the 2nd: cryptography and authentication protocol engineering.
- `019f298c-dbaa-7b53-a417-66d3e33d885a` / Hume the 2nd: privacy, data governance, retention, deletion, consent, and auditability.
- `019f298c-dc48-7d52-95d3-6c0dd9c1bf6f` / Confucius the 2nd: AI/ML production engineering, RAG/LLM safety, reproducibility, and monitoring.
- `019f298c-dce2-71b0-992b-2d91c01454c6` / Turing the 2nd: embedded, realtime, and safety-critical software.
- `019f298c-dd9c-7ee1-bdca-c7e7a83307b8` / Cicero the 2nd: open-source maintainer, dependency governance, releases, and security response.
- `019f298c-de38-77b2-af0a-1a516db397ec` / Aquinas the 2nd: numerical, scientific, data-analysis, and reproducible-research computing.

## Completed Agent Batch

Started: 2026-07-03
Completed: 2026-07-03

- `019f299b-0d77-7043-a181-4f58d9f0ca9f` / Helmholtz the 2nd: mobile/native app platform rules.
- `019f299b-0e0c-7032-b3ac-4f43282d3e58` / Singer the 2nd: cloud infrastructure, Kubernetes, containers, IaC, and platform operations.
- `019f299b-0eb9-7d33-b0ba-20e08decf258` / Godel the 2nd: API design, protocol design, schema contracts, GraphQL/gRPC/OpenAPI, compatibility, pagination, errors, and deprecation.
- `019f299b-0f52-77f0-815a-bfa7907b90c2` / Kierkegaard the 2nd: databases, migrations, data engineering, warehouses/lakehouses, CDC, data quality, and analytics platforms.
- `019f299b-0fdc-7121-a010-31d0c7099a60` / Beauvoir the 2nd: security vulnerability patterns and incident lessons beyond the obvious basics.
- `019f299b-109d-7ed3-8bdf-bcc1d79cd1a0` / Nash the 2nd: developer tools, CLI UX, error-message design, onboarding, documentation usability, migration guides, code review ergonomics, and operational handoffs.

## Completed Agent Batch

Started: 2026-07-03
Completed: 2026-07-03
Stop condition honored: user asked to stop after this active batch; do not launch another batch.

- `019f29a9-009e-7513-a0fe-db3498342264` / Dewey the 2nd: community and practitioner consensus on universal coding rules.
- `019f29a9-013e-77c0-a2de-f35f39ff0a3d` / Maxwell the 2nd: frontend framework and UI application architecture.
- `019f29a9-01cf-7e10-b65e-b70a000813c4` / Poincare the 2nd: network protocols, DNS, CDN/edge, email, HTTP caching, and protocol operations.
- `019f29a9-0282-7a03-9441-1a8067ac3c2b` / Boole the 2nd: game development, realtime interactive systems, simulation loops, and engine architecture.
- `019f29a9-0321-7920-b784-bff6911dc308` / Galileo the 2nd: IoT, edge devices, OTA updates, device identity, constrained/offline fleets, telemetry, and firmware lifecycle.
- `019f29a9-03b8-7df3-94e6-49a926f9bb8a` / Newton the 2nd: language runtime sharp edges and standard-library lessons across major languages.
