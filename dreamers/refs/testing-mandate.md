# Testing Coverage Mandate (MANDATORY)

Every plan — umbrella, sub-plan, or standalone — **must** include test cases that give Probe a complete picture of what to verify. The planner specifies *what* to test, not *how* to implement the tests — that is Probe's domain.

## Test case format
- **Non-trivial cases:** Given/When/Then:
  `Given [precondition] / When [action] / Then [expected outcome]`
- **Simple assertions:** one-liner acceptable (e.g. "null input returns empty list")

## Coverage requirement
Every plan must include test cases across all three layers. Think through each layer explicitly — do not skip a layer without a written reason.

**Unit tests**
- Each significant function, method, or class in isolation
- All branches: happy path, edge cases (boundary values, empty/null/max), negative cases (invalid input, error states)
- Any pure logic that does not require a real device, network, or database

**Integration tests**
- Interactions between layers: repository ↔ data source, ViewModel ↔ repository, service ↔ external API
- Database reads/writes (real or in-memory, not mocked)
- Auth flows end-to-end within the backend
- Cloud function triggers and side-effects

**UI / E2E tests**
- Full user journeys through the UI: screen load → interaction → outcome visible on screen
- Navigation flows between screens
- Error and empty states rendered correctly in the UI
- Any flow that requires a real device or emulator
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), the plan must include explicit E2E test cases — not just unit tests. Probe must independently verify E2E coverage for nav changes and block if missing.

**Regression risks**
- Anything touching existing behavior that could break — call out the specific existing test or flow at risk

If a layer cannot be covered automatically, flag it explicitly as a manual verification requirement with a reason.

## Why this matters
Writing explicit test cases prevents Probe from guessing intent. The Given/When/Then format forces specificity about preconditions and expected outcomes — reducing ambiguity at the handoff boundary.
