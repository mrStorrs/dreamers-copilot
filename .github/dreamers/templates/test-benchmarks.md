# Test Benchmarks

This file records measured run times for each test command in the project. It lives at the project root so it is visible to the team and committed to version control for cross-machine reference.

## How it's used

**The orchestrator writes** a row (or updates the existing row) for each test command after a successful test run in `dreamers-implement` Step 3 and after post-fix re-runs in Step 6. The orchestrator also reads the `Recommended Timeout` column at pre-flight to set test-command timeouts. **Humans may edit** the `Notes` column to capture machine-specific variance, known flakiness, or CI environment factors.

If this file is absent when `dreamers-implement` starts, no timeout adjustment is made. The file is created automatically after the first successful test run.

## Recommended-timeout formula

```
Recommended Timeout = max(last_run_time × 2, 30s)
```

The 2× multiplier absorbs machine-variance and warm-cache vs cold-cache differences. The 30s floor prevents pathological single-digit timeouts on cold runs.

## Benchmark table

| Command | Last Run Time | Last Updated | Recommended Timeout | Notes |
|---|---|---|---|---|
| `pytest tests/unit` | 20s | 2026-05-23 | 40s | — |
