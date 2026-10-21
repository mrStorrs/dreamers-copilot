# Implementation workflow

Execute this workflow inline with the supplied input. Resolve links relative to this ref. Read the linked standards before acting. Keep the active skill's todo, gates, and delivery state.

## Todo
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## 1: Implement
- Implement the task or approved plan in the supplied input per `comment-rules` + `logging-discipline` + `testing-mandate` (Kernel). For tasks, use the stated requirements as acceptance criteria; no plan file is needed. Stage as you go.

## 2: Type-check + run tests
- Run the project's type-check + test command (from `.github/copilot-instructions.md`). Fix inline (max 3 attempts) then halt.
- Update `./test-benchmarks.md` row after passing (if the project uses one).

## Exit
- Return requirement/AC coverage and validation results at green tests.

Read and apply [dreamers-kernel](dreamers-kernel.md).

Read and apply [git-workflow](git-workflow.md).

Read and apply [testing-mandate](testing-mandate.md).

Read and apply [comment-rules](comment-rules.md).

Read and apply [logging-discipline](logging-discipline.md).
