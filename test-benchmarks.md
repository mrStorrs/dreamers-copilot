# Test benchmarks

Measured in Debian 13 on ai-test-01 using a temporary PowerShell 7.6.6 runtime and isolated package copies. Recommended timeout is max(last duration × 2, 30 seconds).

| Command | Last run | Updated | Recommended timeout | Notes |
| --- | --- | --- | --- | --- |
| pwsh -File scripts/Test-DreamersCopilot.ps1 | 1.341s | 2026-09-13 | 30s | Full package and installer behavior checks. |
| scripts/Test-DreamersCopilot.sh -Root <repo> | 1.278s | 2026-09-13 | 30s | Full checks through the Bash launcher, including argument forwarding. |
