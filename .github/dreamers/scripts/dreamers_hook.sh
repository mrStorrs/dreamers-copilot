#!/usr/bin/env bash
set -u

event_name="${1:-}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
copilot_home="${COPILOT_HOME:-$HOME/.copilot}"

resolve_python() {
  if [ -n "${DREAMERS_HOOK_PYTHON:-}" ]; then
    printf '%s\n' "$DREAMERS_HOOK_PYTHON"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

if [ -z "$event_name" ]; then
  printf 'dreamers hook warning: missing event name\n' >&2
  exit 0
fi

if ! python_bin="$(resolve_python)"; then
  printf 'dreamers hook warning: python runtime unavailable for %s\n' "$event_name" >&2
  exit 0
fi

if "$python_bin" "$script_dir/dreamers_stats.py" hook --client copilot --home "$copilot_home" --event-name "$event_name"; then
  :
else
  status=$?
  printf 'dreamers hook warning: %s stats write failed with exit %s\n' "$event_name" "$status" >&2
fi

exit 0
