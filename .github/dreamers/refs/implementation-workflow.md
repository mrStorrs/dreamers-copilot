**Input:** task requirements or an approved plan, agreed scope, and any shared context or accepted findings. Apply the embedded `dreamers-kernel`, `git-workflow`, `testing-mandate`, `comment-rules`, and `logging-discipline` rules.

1. **Implement.** Make the scoped code and test changes inline on the prepared feature branch. For tasks, use the stated requirements as acceptance criteria; no plan file is needed. Stage explicit paths as work progresses.
2. **Validate.** Run the project's type-check and test commands from `.github/copilot-instructions.md`. Fix failures inline, allowing at most 3 fix attempts; halt if validation still fails. After passing, update the corresponding `./test-benchmarks.md` row if the project uses one.

**Result:** requirement/AC coverage and validation results at green tests. Leave changes staged; review, commit, push, and PR creation are outside this operation.
