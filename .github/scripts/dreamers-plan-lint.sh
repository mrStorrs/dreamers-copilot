#!/usr/bin/env bash
# Lint a single plan file (or every plan-*.md in .dreamers/plans/) against the
# mechanical subset of the plan quality checklist from refs/quality-gates.md.
# Usage:
#   test-plan-quality.sh <plan-path>          # check one file
#   test-plan-quality.sh                      # check every plan-*.md in .dreamers/plans/ (excluding archive/)
#
# Exits 0 if every plan passes the mechanical checks, 1 otherwise.
#
# Mechanical checks performed:
#   - filename matches plan-{slug}.md or plan-{slug}-[a-z].md
#   - has H1 starting with "Plan —"
#   - has Acceptance Criteria section
#   - has Status field with value in {Draft, Active, Completed, Superseded}
#   - sub-plans / standalones have Design Decisions, Rollback boundary, Test Cases for Probe
#   - umbrella plans have Sub-plans table
#   - no fenced code blocks outside of an Interface contracts / Type contracts section
#
# Judgment-based checks (sub-plan splits at "natural seams", "natural" decomposition,
# whether referenced paths exist) are NOT covered here — those remain the caller's job.
set -euo pipefail

valid_status_re='^(Draft|Active|Completed|Superseded)$'

check_one() {
  local file="$1"
  local fail=0
  local base
  base=$(basename "$file")

  if [[ ! "$base" =~ ^plan-[a-z0-9-]+(\-[a-z])?\.md$ ]]; then
    printf '  [%s] filename does not match plan-{slug}[-a..z].md\n' "$base" >&2
    fail=1
  fi

  if ! grep -qE '^# Plan —' "$file"; then
    printf '  [%s] missing H1 starting with "# Plan —"\n' "$base" >&2
    fail=1
  fi

  # Detect umbrella vs sub/standalone by H1 suffix "(Umbrella)".
  local is_umbrella=0
  if grep -qE '^# Plan —.*\(Umbrella\)' "$file"; then
    is_umbrella=1
  fi

  # Status field — accept any of: "Status: X", "**Status:** X", "- **Status:** X", "Status**: X"
  local status
  status=$(grep -m1 -iE '(^|[^a-z])Status\*{0,2}:\*{0,2}\s*[A-Za-z]+' "$file" \
    | sed -E 's/.*Status\*{0,2}:\*{0,2}[[:space:]]*//; s/[[:space:]]*\*+[[:space:]]*$//; s/[[:space:]]*$//' \
    | head -1 \
    || true)
  if [ -z "$status" ]; then
    printf '  [%s] missing Status field\n' "$base" >&2
    fail=1
  elif ! [[ "$status" =~ $valid_status_re ]]; then
    printf '  [%s] Status="%s" not in {Draft, Active, Completed, Superseded}\n' "$base" "$status" >&2
    fail=1
  fi

  # Section headings (## level)
  has_section() {
    grep -qE "^##+ +$1\b" "$file"
  }

  if ! has_section "Acceptance Criteria"; then
    printf '  [%s] missing "## Acceptance Criteria" section\n' "$base" >&2
    fail=1
  fi

  if [ "$is_umbrella" -eq 1 ]; then
    if ! has_section "Sub-plans"; then
      printf '  [%s] umbrella missing "## Sub-plans" section\n' "$base" >&2
      fail=1
    fi
  else
    if ! has_section "Design Decisions"; then
      printf '  [%s] missing "## Design Decisions" section\n' "$base" >&2
      fail=1
    fi
    if ! has_section "Rollback"; then
      printf '  [%s] missing Rollback section (e.g. "## Rollback boundary")\n' "$base" >&2
      fail=1
    fi
    if ! has_section "Test Cases"; then
      printf '  [%s] missing "## Test Cases for Probe" section\n' "$base" >&2
      fail=1
    fi
  fi

  # Code-block check: fenced blocks are forbidden except inside an
  # "Interface contracts" or "Type contracts" section.
  awk -v base="$base" '
    /^##+ / {
      section=$0
      in_contracts = (tolower(section) ~ /interface contracts|type contracts/) ? 1 : 0
    }
    /^```/ {
      in_fence = !in_fence
      if (in_fence && !in_contracts) {
        printf("  [%s] fenced code block outside Interface/Type contracts (line %d)\n", base, NR) > "/dev/stderr"
        bad=1
      }
    }
    END { exit bad ? 1 : 0 }
  ' "$file" || fail=1

  return "$fail"
}

overall=0

if [ "$#" -ge 1 ]; then
  for f in "$@"; do
    if ! check_one "$f"; then
      overall=1
    fi
  done
else
  shopt -s nullglob
  found=0
  for f in .dreamers/plans/plan-*.md; do
    [ -f "$f" ] || continue
    found=1
    if ! check_one "$f"; then
      overall=1
    fi
  done
  if [ "$found" -eq 0 ]; then
    echo "No plan-*.md files found in .dreamers/plans/" >&2
    exit 0
  fi
fi

if [ "$overall" -eq 0 ]; then
  echo "plan-quality: OK"
else
  echo "plan-quality: FAILED — see items above" >&2
  exit 1
fi
