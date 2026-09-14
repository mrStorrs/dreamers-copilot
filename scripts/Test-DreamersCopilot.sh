#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v pwsh >/dev/null 2>&1; then
  echo "PowerShell 7 (pwsh) is required; it also runs the package installer." >&2
  exit 1
fi
exec pwsh -NoLogo -NoProfile -File "$script_dir/Test-DreamersCopilot.ps1" "$@"
