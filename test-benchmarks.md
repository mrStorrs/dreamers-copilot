# Test Benchmarks

This file records measured run times for test and validation commands in this project.

## Benchmark table

| Command | Last Run Time | Last Updated | Recommended Timeout | Notes |
|---|---|---|---|---|
| `python3 -m py_compile .github/dreamers/scripts/dreamers_stats.py tests/dreamers_stats_support.py tests/test_dreamers_stats.py tests/test_dreamers_stats_record.py tests/test_dreamers_stats_hooks_install.py tests/test_dreamers_stats_checkpoint.py tests/test_dreamers_stats_reports.py` | 0.03s | 2026-06-13 | 30s | Syntax validation for the Copilot shim and split stats suite. |
| `python3 -m unittest tests/test_dreamers_stats.py` | 0.25s | 2026-06-13 | 30s | 30s floor. |
| `scripts/sync-refs.sh -Verify` | 0.02s | 2026-06-13 | 30s | 30s floor. |
