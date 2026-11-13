#!/usr/bin/env bash
set -euo pipefail

codex_home="${CODEX_HOME:-$HOME/.codex}"
force=0

usage() {
  cat <<'EOF'
Usage: ./Install-DreamersCodex.sh [--force] [--codex-home PATH]

Installs Dreamers Codex-managed files into CODEX_HOME, or ~/.codex when CODEX_HOME is not set.
EOF
}

while (($#)); do
  case "$1" in
    -f|--force)
      force=1
      ;;
    --codex-home)
      shift
      if (($# == 0)); then
        echo "Missing value for --codex-home" >&2
        exit 1
      fi
      codex_home="$1"
      ;;
    --codex-home=*)
      codex_home="${1#*=}"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(mktemp -d "${TMPDIR:-/tmp}/dreamers-codex.XXXXXXXX")"
trap 'rm -rf -- "$repo_root"' EXIT
python3 "$source_root/scripts/build-codex.py" --output "$repo_root"
python3 "$source_root/scripts/codex_global_instructions.py" check --codex-home "$codex_home"
legacy_agent_names=(echo forge hone nova probe sage sentinel)
legacy_agent_toml_names=(bolt forge nova sage)
obsolete_managed_files=(
  dreamers/instructions/comment-rules.instructions.md
  dreamers/instructions/git.instructions.md
  dreamers/templates/plan-writing-guide.md
  dreamers/refs/hone-architecture-rubric.md
  dreamers/refs/plan-quality.md
  dreamers/refs/plan-selection.md
  dreamers/templates/plan-guide-selector.md
  dreamers/templates/plan-guide-lite.md
  dreamers/templates/plan-guide-standard.md
  dreamers/templates/plan-guide-complex.md
)
legacy_skill_names=(dreamers-full dreamers-research)

copy_dreamers_files() {
  local from="$1"
  local to="$2"
  local label="$3"
  local count=0

  if [[ ! -d "$from" ]]; then
    printf '  WARN: source not found, skipping: %s\n' "$from" >&2
    echo 0
    return 0
  fi

  mkdir -p "$to"

  shopt -s nullglob
  for src in "$from"/*; do
    [[ -f "$src" ]] || continue
    local name
    name="$(basename "$src")"
    local dest="$to/$name"
    if [[ -e "$dest" && $force -eq 0 ]]; then
      printf '  SKIP (exists): %s/%s - use --force to overwrite\n' "$label" "$name" >&2
      continue
    fi
    cp -f "$src" "$dest"
    cmp -s "$src" "$dest" || { printf 'Verification failed: %s\n' "$dest" >&2; return 1; }
    printf '  OK: %s/%s\n' "$label" "$name" >&2
    count=$((count + 1))
  done
  shopt -u nullglob

  echo "$count"
}

remove_legacy_agent_files() {
  local target_dir="$1"
  local count=0

  if [[ ! -d "$target_dir" ]]; then
    echo 0
    return 0
  fi

  for name in "${legacy_agent_names[@]}"; do
    local target="$target_dir/$name.md"
    [[ -e "$target" ]] || continue
    rm -f "$target"
    printf '  REMOVED legacy: dreamers/agents/%s.md\n' "$name" >&2
    count=$((count + 1))
  done

  if [[ -d "$target_dir" ]] && ! find "$target_dir" -mindepth 1 -print -quit | grep -q .; then
    rmdir "$target_dir"
    printf '  REMOVED empty legacy dir: dreamers/agents\n' >&2
  fi

  echo "$count"
}

remove_legacy_agent_tomls() {
  local target_dir="$1"
  local count=0

  if [[ ! -d "$target_dir" ]]; then
    echo 0
    return 0
  fi

  for name in "${legacy_agent_toml_names[@]}"; do
    local target="$target_dir/$name.toml"
    [[ -e "$target" ]] || continue
    rm -f "$target"
    printf '  REMOVED legacy: agents/%s.toml\n' "$name" >&2
    count=$((count + 1))
  done

  echo "$count"
}

remove_obsolete_managed_files() {
  local count=0

  for rel in "${obsolete_managed_files[@]}"; do
    local target="$codex_home/$rel"
    [[ -e "$target" ]] || continue
    rm -f "$target"
    printf '  REMOVED obsolete managed file: %s\n' "$rel" >&2
    count=$((count + 1))
  done

  echo "$count"
}

remove_legacy_skill_files() {
  local target_root="$1"
  local count=0

  for skill_name in "${legacy_skill_names[@]}"; do
    local target_dir="$target_root/$skill_name"
    for file_name in SKILL.md readme.md; do
      local target="$target_dir/$file_name"
      [[ -e "$target" ]] || continue
      rm -f "$target"
      printf '  REMOVED legacy managed file: skills/%s/%s\n' "$skill_name" "$file_name" >&2
      count=$((count + 1))
    done
    if [[ -d "$target_dir" ]] && ! find "$target_dir" -mindepth 1 -print -quit | grep -q .; then
      rmdir "$target_dir"
      printf '  REMOVED empty legacy dir: skills/%s\n' "$skill_name" >&2
    fi
  done

  echo "$count"
}

printf '\nDreamers Codex Installer\n'
printf 'Source:  %s\n' "$repo_root"
printf 'Target:  %s\n\n' "$codex_home"

total=0
legacy_removed=0

printf '[agents]\n'
count="$(copy_dreamers_files "$repo_root/agents" "$codex_home/agents" "agents")"
total=$((total + count))

printf '[skills]\n'
if [[ -d "$repo_root/skills" ]]; then
  while IFS= read -r -d '' skill_dir; do
    skill_name="$(basename "$skill_dir")"
    if [[ "$skill_name" == "dreamers" || "$skill_name" == dreamers-* ]]; then
      count="$(copy_dreamers_files "$skill_dir" "$codex_home/skills/$skill_name" "skills/$skill_name")"
      total=$((total + count))
    fi
  done < <(find "$repo_root/skills" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
fi

printf '[dreamers]\n'
for name in refs templates instructions; do
  count="$(copy_dreamers_files "$repo_root/dreamers/$name" "$codex_home/dreamers/$name" "dreamers/$name")"
  total=$((total + count))
done

printf '[global instructions]\n'
instruction_args=()
if ((force)); then instruction_args+=(--force); fi
python3 "$source_root/scripts/codex_global_instructions.py" install --codex-home "$codex_home" --package-root "$repo_root" "${instruction_args[@]}"

printf '[legacy]\n'
count="$(remove_legacy_skill_files "$codex_home/skills")"
legacy_removed=$((legacy_removed + count))
count="$(remove_legacy_agent_tomls "$codex_home/agents")"
legacy_removed=$((legacy_removed + count))
count="$(remove_legacy_agent_files "$codex_home/dreamers/agents")"
legacy_removed=$((legacy_removed + count))
count="$(remove_obsolete_managed_files)"
legacy_removed=$((legacy_removed + count))

printf '\nInstalled %s Dreamers Codex file(s); removed %s legacy/obsolete file(s).\n\n' "$total" "$legacy_removed"
