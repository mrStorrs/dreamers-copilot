# Agent Failure Recovery (mandatory)

When a spawned agent hits a rate limit, crashes, or times out mid-run:
1. For a reviewer, check both copies using the review handoff contract before retrying. A complete report can survive a runtime failure. Inspect any partial workspace output to identify completed work, without treating an incomplete handoff as final.
2. Determine which steps completed and which remain (check workspace outputs, git log, test results).
3. Complete remaining steps directly or re-spawn the agent scoped to only the remaining work.
4. Do not re-run steps that already completed — build on partial progress.
