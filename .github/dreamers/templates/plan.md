<plan-format>
Use the same Goal and Acceptance criteria body as GitHub issue proposals. Keep the metadata needed by the delivery workflow.

```markdown
# Plan-NN: <short title>

**Date:** YYYY-MM-DD
**Status:** Draft
**Plan-type:** <lite|standard|complex>
**Branch:** <feat/slug|fix/slug>
**User-testing-required:** <yes|no>
**Grilling transcript:** [grilling-transcript.md](./grilling-transcript.md)

## Goal
What should improve, for whom, and why?

## Acceptance criteria
- [ ] Observable outcome.
```

Include the transcript link only when the sibling artifact exists. For manual checks, include the steps, expected result, and why automation cannot cover them; set `User-testing-required: yes`.
</plan-format>
