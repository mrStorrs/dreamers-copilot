#!/usr/bin/env bash
# Verify .github/catalog.json matches the actual filesystem layout.
# Checks:
#   - every catalog agent has a corresponding .github/agents/<slug>.agent.md
#   - every catalog skill has a corresponding .github/skills/<slug>/SKILL.md
#   - every catalog item's `path` exists on disk
#   - every .agent.md / SKILL.md on disk appears in the catalog
# Exits 0 on success, 1 on mismatch.
#
# Uses Python 3 for JSON parsing (no jq dependency).
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
catalog="$repo_root/.github/catalog.json"

if [ ! -f "$catalog" ]; then
  echo "catalog.json not found at $catalog" >&2
  exit 1
fi

python_bin=""
for cand in python3 python; do
  p=$(command -v "$cand" 2>/dev/null || true)
  # Skip the Microsoft Store python stub on Windows (no execute permission, just a launcher).
  if [ -n "$p" ] && [ -x "$p" ] && [[ "$p" != *"WindowsApps"* ]]; then
    python_bin="$p"
    break
  fi
done
if [ -z "$python_bin" ]; then
  echo "python3 not found — required for catalog sync check" >&2
  exit 1
fi

# Have Python emit two TSV streams to a temp file: items, then a separator, then
# expected-on-disk slugs grouped by type.
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

"$python_bin" - "$catalog" > "$tmp" <<'PY'
import json, sys, io
# Force LF line endings so bash `read` doesn't see CR on Windows.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
with open(sys.argv[1], encoding='utf-8') as fh:
    data = json.load(fh)
for item in data.get('items', []):
    print('ITEM', item.get('type', ''), item.get('slug', ''), item.get('path', ''), sep='\t')
PY

fail=0

# Catalog -> filesystem
while IFS=$'\t' read -r marker kind slug path; do
  [ "$marker" = "ITEM" ] || continue
  case "$kind" in
    agent)
      expected="$repo_root/.github/agents/$slug.agent.md"
      if [ ! -f "$expected" ]; then
        printf '  MISSING FILE for catalog agent "%s": %s\n' "$slug" "$expected" >&2
        fail=1
      fi
      ;;
    skill)
      expected="$repo_root/.github/skills/$slug/SKILL.md"
      if [ ! -f "$expected" ]; then
        printf '  MISSING FILE for catalog skill "%s": %s\n' "$slug" "$expected" >&2
        fail=1
      fi
      ;;
  esac
  if [ -n "$path" ] && [ ! -f "$repo_root/$path" ]; then
    printf '  CATALOG path does not exist: %s\n' "$path" >&2
    fail=1
  fi
done < "$tmp"

# Filesystem -> catalog
catalog_agents=$(awk -F'\t' '$1=="ITEM" && $2=="agent" {print $3}' "$tmp" | sort -u)
catalog_skills=$(awk -F'\t' '$1=="ITEM" && $2=="skill" {print $3}' "$tmp" | sort -u)

for f in "$repo_root"/.github/agents/*.agent.md; do
  [ -f "$f" ] || continue
  slug=$(basename "$f" .agent.md)
  if ! grep -qx "$slug" <<< "$catalog_agents"; then
    printf '  AGENT not in catalog: %s\n' "$slug" >&2
    fail=1
  fi
done

for d in "$repo_root"/.github/skills/*/; do
  [ -d "$d" ] || continue
  slug=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  if ! grep -qx "$slug" <<< "$catalog_skills"; then
    printf '  SKILL not in catalog: %s\n' "$slug" >&2
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "catalog: OK"
else
  echo "catalog: MISMATCH" >&2
  exit 1
fi
