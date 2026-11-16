---
name: dreamers-issue
description: 'Investigate code and propose a short issue with acceptance criteria for approval. Triggers: /dreamers-issue, create an issue, open a GitHub issue, file an issue.'
argument-hint: '<goal>'
---

$ARGUMENTS

<proposal>
Follow YAGNI principles.

Look into how code works today. Propose the requested change for [goal], built around clear acceptance criteria. Ask questions if needed. Before presenting the proposal, review the code for potential concerns or unintended behaviours. Report them to the user with suggested acceptance criteria to address them. Present the proposal for approval before creating the requested artifact.

```markdown
## Goal
What should improve, for whom, and why?

## Acceptance criteria
- [ ] Observable outcome.
```
</proposal>

After approval, create the GitHub issue (or ADO story if specifically asked, using Goal as its description) and return its URL.
