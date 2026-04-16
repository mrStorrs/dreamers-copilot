---
applyTo: "**"
---

# Comment Rules

Comments must add value that the code cannot express itself. Concise, no fluff, no separators — value only.

## When to comment
- Non-obvious logic: why a non-obvious approach was chosen, constraints, gotchas
- Public API documentation callers need to use the interface correctly
- TODO/FIXME with specific, actionable notes
- License headers

## When NOT to comment
- Code that reads naturally from well-named functions and variables
- Anything that restates what the code obviously does

## Strict prohibitions
- No plan/ticket references in source code
- No separator comments (`// ---`, `// ===`, `// ###`, blank-comment lines, visual dividers)
- No spec rationalization — never argue a spec permits a pattern
- No redundant JSDoc/KDoc that only repeats the function signature

## Style
- One line when possible; never exceed two lines for inline comments
- Write *why*, never *what*
- If a comment requires more than two lines, the code needs refactoring, not more words
