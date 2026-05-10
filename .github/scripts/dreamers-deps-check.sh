#!/usr/bin/env bash
# Verify the system dependencies required by the dreamers-*.sh scripts.
# Reports OK / MISSING per tool and exits non-zero if any required dep is missing.
# Usage: dreamers-deps-check.sh
#
# The script set is intentionally small (only the LLM-error-prone routines were extracted).
# Most pipeline work still runs as inline bash inside the skills/refs.
set -uo pipefail

ok=0
fail=0

print_ok()    { printf '  OK:       %-12s %s\n' "$1" "$2"; ok=$((ok + 1)); }
print_miss()  { printf '  MISSING:  %-12s — needed by: %s\n' "$1" "$2" >&2; fail=$((fail + 1)); }

check_tool() {
  local tool="$1" needed_by="$2" path
  path=$(command -v "$tool" 2>/dev/null || true)
  if [ -z "$path" ] || [ ! -x "$path" ]; then
    print_miss "$tool" "$needed_by"
    return 1
  fi
  print_ok "$tool" "-> $path"
}

# Locate a real python3 (skip the Microsoft Store launcher stub on Windows).
check_python() {
  local needed_by="dreamers-catalog-lint.sh (dev-time only)" found="" cand p
  for cand in python3 python; do
    p=$(command -v "$cand" 2>/dev/null || true)
    if [ -n "$p" ] && [ -x "$p" ] && [[ "$p" != *"WindowsApps"* ]]; then
      found="$p"
      break
    fi
  done
  if [ -z "$found" ]; then
    print_miss "python3" "$needed_by"
    return 1
  fi
  print_ok "python3" "-> $found"
}

# Check `gh` is authenticated (separate from the binary being on PATH).
check_gh_auth() {
  if gh auth status >/dev/null 2>&1; then
    print_ok "gh-auth" "authenticated"
  else
    print_miss "gh-auth" "dreamers-pr-unresolved.sh, dreamers-pr-resolve-thread.sh — run \`gh auth login\`"
  fi
}

echo "Dreamers dependency check"
echo "-------------------------"

# Always required (every script + nearly all inline bash in skills/refs).
check_tool bash "every script + inline bash in skills/refs"
check_tool git  "dreamers-catalog-lint.sh + nearly all skills/refs"
check_tool gh   "dreamers-pr-unresolved.sh, dreamers-pr-resolve-thread.sh + several skills"

# POSIX coreutils used by the kept scripts (plan-lint, catalog-lint).
for t in sed awk grep; do
  check_tool "$t" "dreamers-plan-lint.sh + inline bash in skills/refs" || true
done

# Python — only catalog-lint needs it, and only for this repo's dev work.
check_python

# Auth — only checked if gh exists.
if command -v gh >/dev/null 2>&1; then
  check_gh_auth
fi

echo "-------------------------"
printf 'Tools OK: %d\nMissing:  %d\n' "$ok" "$fail"

if [ "$fail" -gt 0 ]; then
  exit 1
fi
