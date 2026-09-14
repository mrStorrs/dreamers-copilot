# /dreamers-implement

Implement a supplied approved proposal or detailed plan in the main session. An approved proposal is enough to start; detailed planning and tests-first are optional.

Standalone runs inspect git state and create/resume the appropriate feature branch; calls from /dreamers reuse its branch. Verify branch identity before editing, resolve stale or incomplete plan inputs, and obtain direction before expanding scope.

Execution, git, code, comment, verification, and logging rules are embedded as synchronized XML blocks. The skill needs no runtime reads of Dreamers reference or template files. Project instructions and the approved work artifacts remain runtime inputs.

Reuse sufficient tests or add meaningful behavior coverage. Run applicable checks, record successful test timings, inspect the final diff, and return each required outcome's evidence and gaps. Required failing or blocked checks prevent a verified result.

Stage explicit changes and stop before review, user testing, commits, or PR creation. The caller owns those phases.

See [the workflow](SKILL.md).
