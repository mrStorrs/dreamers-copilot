# Implementation workflow

Apply the embedded `dreamers-kernel`, `git-workflow`, `testing-mandate`, `comment-rules`, `logging-discipline` standards.

Execute this workflow inline with the supplied input. Keep the active skill's todo, gates, and delivery state.

## Todo
- When used standalone, a todo is optional. When used as a delivery phase, complete these steps under the active skill's existing todo.

## 1: Implement
- Implement the task or approved plan in the supplied input per `comment-rules` + `logging-discipline` + `testing-mandate` (Kernel). For tasks, use the stated requirements as acceptance criteria; no plan file is needed. Stage as you go.

## 2: Type-check + run tests
- Run the project's type-check + test command (from `.github/copilot-instructions.md`). Fix inline (max 3 attempts) then halt.
- Update `./test-benchmarks.md` row after passing (if the project uses one).

## Exit
- Return requirement/AC coverage and validation results at green tests.
