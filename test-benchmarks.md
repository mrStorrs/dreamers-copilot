# Test Benchmarks

This file records measured run times for test and validation commands in this project.

## Benchmark table

| Command | Last Run Time | Last Updated | Recommended Timeout | Notes |
|---|---|---|---|---|
| `python3 -m py_compile .github/dreamers/scripts/dreamers_stats.py` | 0.02s | 2026-06-13 | 30s | Syntax validation for the stats writer. |
| `python3 -m unittest tests/test_dreamers_stats.py` | 0.13s | 2026-06-13 | 30s | 30s floor. |
| `scripts/sync-refs.sh -Verify` | 0.02s | 2026-06-13 | 30s | 30s floor. |
