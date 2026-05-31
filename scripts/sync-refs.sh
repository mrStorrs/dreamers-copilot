#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync-refs.sh -Sync | -Verify

  -Sync    Regenerate inlined ref content in consumer files.
  -Verify  Exit non-zero if any consumer is out of sync.

An explicit mode flag is required.
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

case "$1" in
  -Sync|--sync) mode="sync" ;;
  -Verify|--verify) mode="verify" ;;
  *) usage; exit 1 ;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

python3 - "$mode" "$repo_root" <<'PY'
from pathlib import Path
import re
import sys

mode = sys.argv[1]
repo = Path(sys.argv[2])
refs_dir = repo / ".github/dreamers/refs"

if not refs_dir.exists():
    print(f"ERROR: refs directory not found at {refs_dir}", file=sys.stderr)
    sys.exit(2)


def read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n")


refs = {
    path.stem: read_text(path).rstrip("\n")
    for path in sorted(refs_dir.glob("*.md"))
}

open_re = re.compile(r"^<([a-zA-Z][a-zA-Z0-9_-]*)>$")
close_re = re.compile(r"^</([a-zA-Z][a-zA-Z0-9_-]*)>$")

errors: list[str] = []
plan: list[tuple[Path, str, str, list[str], list[tuple[str, int, int]]]] = []

github_dir = repo / ".github"
for consumer in sorted(github_dir.rglob("*.md")):
    rel = consumer.relative_to(repo).as_posix()
    if rel.startswith(".github/dreamers/refs/"):
        continue

    text = read_text(consumer)
    lines = text.split("\n")
    pairs: list[tuple[str, int, int]] = []
    open_stack: dict[str, int] = {}
    has_markers = False

    for index, line in enumerate(lines):
        open_match = open_re.match(line)
        close_match = close_re.match(line)

        if open_match:
            name = open_match.group(1)
            if name not in refs:
                continue
            has_markers = True
            if name in open_stack:
                errors.append(
                    f"  {rel} line {index + 1}: duplicate opening tag <{name}> "
                    f"(previous opening at line {open_stack[name] + 1} not closed)."
                )
                continue
            open_stack[name] = index
            continue

        if close_match:
            name = close_match.group(1)
            if name not in refs:
                continue
            has_markers = True
            if name not in open_stack:
                errors.append(
                    f"  {rel} line {index + 1}: closing tag </{name}> without matching opening tag."
                )
                continue
            if any(pair_name == name for pair_name, _, _ in pairs):
                existing = next(open_line for pair_name, open_line, _ in pairs if pair_name == name)
                errors.append(
                    f"  {rel}: ref '{name}' appears in more than one marker pair "
                    f"(lines {existing + 1} and {open_stack[name] + 1}). Same-name duplication is forbidden."
                )
                del open_stack[name]
                continue
            pairs.append((name, open_stack[name], index))
            del open_stack[name]

    for name, open_line in open_stack.items():
        errors.append(f"  {rel} line {open_line + 1}: opening tag <{name}> without matching closing tag.")

    if has_markers and pairs:
        pairs.sort(key=lambda pair: pair[1])
        plan.append((consumer, rel, text, lines, pairs))

if errors:
    print("ERROR: malformed markers detected:", file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    print("\nNo files modified.", file=sys.stderr)
    sys.exit(3)

updated: list[str] = []
stale: list[tuple[str, list[str]]] = []

for path, rel, text, lines, pairs in plan:
    new_lines: list[str] = []
    cursor = 0
    stale_refs: list[str] = []

    for name, open_line, close_line in pairs:
        new_lines.extend(lines[cursor : open_line + 1])
        expected_lines = refs[name].split("\n")
        current = "\n".join(lines[open_line + 1 : close_line])
        expected = "\n".join(expected_lines)
        if current != expected:
            stale_refs.append(name)
        new_lines.extend(expected_lines)
        new_lines.append(lines[close_line])
        cursor = close_line + 1

    new_lines.extend(lines[cursor:])
    new_text = "\n".join(new_lines)

    if new_text == text:
        continue

    if mode == "sync":
        path.write_text(new_text, encoding="utf-8", newline="\n")
        updated.append(rel)
    else:
        stale.append((rel, sorted(set(stale_refs or [name for name, _, _ in pairs]))))

if mode == "sync":
    if not updated:
        print("sync-refs: no changes (tree already in sync).")
    else:
        print(f"sync-refs: updated {len(updated)} file(s):")
        for rel in updated:
            print(f"  {rel}")
    sys.exit(0)

if not stale:
    print("verify-refs: clean. All inlined refs match source.")
    sys.exit(0)

print(f"verify-refs: DRIFT detected in {len(stale)} file(s):", file=sys.stderr)
for rel, ref_names in stale:
    print(f"  {rel} ({', '.join(ref_names)})", file=sys.stderr)
print("Run: scripts/sync-refs.sh -Sync", file=sys.stderr)
sys.exit(1)
PY
