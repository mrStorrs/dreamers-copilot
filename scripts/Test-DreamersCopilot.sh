#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: Test-DreamersCopilot.sh [--root <path>]

Validates synchronized refs, package inventory, skill contracts, catalog
integrity, and retired-pipeline references using Bash and Python.
EOF
}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd -- "$script_dir/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || { usage; exit 1; }
      root="$(cd -- "$2" && pwd)"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

"$root/scripts/sync-refs.sh" -Verify

python3 - "$root" <<'PY'
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
errors: list[str] = []


def add_error(message: str) -> None:
    errors.append(message)


def assert_exact(label: str, expected: list[str], actual: list[str]) -> None:
    expected_set = set(expected)
    actual_set = set(actual)
    for item in sorted(expected_set - actual_set):
        add_error(f"Missing {label} item: {item}")
    for item in sorted(actual_set - expected_set):
        add_error(f"Unexpected {label} item: {item}")


def assert_path(path: Path, label: str) -> None:
    if not path.exists():
        add_error(f"Missing {label}: {path}")


def assert_patterns(path: Path, patterns: list[tuple[str, str]]) -> None:
    if not path.exists():
        add_error(f"Missing contract file: {path}")
        return
    content = path.read_text(encoding="utf-8")
    for label, pattern in patterns:
        if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            add_error(f"Missing {label} contract in {path.relative_to(root)}")


def assert_no_patterns(path: Path, patterns: list[tuple[str, str]]) -> None:
    if not path.exists():
        add_error(f"Missing contract file: {path}")
        return
    content = path.read_text(encoding="utf-8")
    for label, pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            add_error(f"Unexpected {label} contract in {path.relative_to(root)}")


def assert_pattern_count(path: Path, label: str, pattern: str, expected: int) -> None:
    if not path.exists():
        add_error(f"Missing contract file: {path}")
        return
    content = path.read_text(encoding="utf-8")
    actual = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
    if actual != expected:
        add_error(
            f"Expected {expected} {label} contract(s) in {path.relative_to(root)}, found {actual}"
        )


expected_agents = [
    "echo",
    "forge",
    "hone",
    "nova",
    "probe",
    "sage",
    "sentinel",
    "vigil",
]
expected_skills = [
    "dreamers",
    "dreamers-add-logging",
    "dreamers-clean-work",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-docs",
    "dreamers-find-refactors",
    "dreamers-fix",
    "dreamers-help",
    "dreamers-implement",
    "dreamers-issue",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-plan-verify",
    "dreamers-pr",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review",
    "dreamers-simplify",
    "dreamers-test",
    "dreamers-update",
]
expected_refs = [
    "agent-recovery.md",
    "comment-rules.md",
    "dreamers-kernel.md",
    "git-workflow.md",
    "hone-architecture-rubric.md",
    "logging-discipline.md",
    "planning-grill.md",
    "project-bootstrap.md",
    "review-selection.md",
    "reviewer-findings-format.md",
    "testing-mandate.md",
]
expected_templates = [
    "discovery-questions.md",
    "github-issue.md",
    "logging-standards.md",
    "manifest.md",
    "plan-guide-complex.md",
    "plan-guide-lite.md",
    "plan-guide-selector.md",
    "plan-guide-standard.md",
    "plan.md",
    "pr-description.md",
    "project-brief.md",
    "shell-plan.md",
    "test-benchmarks.md",
    "user-testing-gate.md",
]
expected_instructions = [
    "comment-rules.instructions.md",
    "dreamers.instructions.md",
    "git.instructions.md",
]
expected_skill_readmes = [
    "dreamers",
    "dreamers-add-logging",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-find-refactors",
    "dreamers-fix",
    "dreamers-implement",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review",
]

agent_root = root / ".github/agents"
skill_root = root / ".github/skills"
dreamers_root = root / ".github/dreamers"
instructions_root = root / ".github/instructions"

for path, label in [
    (agent_root, "agents directory"),
    (skill_root, "skills directory"),
    (dreamers_root, "dreamers directory"),
    (instructions_root, "instructions directory"),
]:
    assert_path(path, label)

if agent_root.exists():
    actual_agents = [
        path.name.removesuffix(".agent.md")
        for path in agent_root.glob("*.agent.md")
    ]
    assert_exact("agent", expected_agents, actual_agents)

if skill_root.exists():
    actual_skills = [path.name for path in skill_root.iterdir() if path.is_dir()]
    assert_exact("skill", expected_skills, actual_skills)
    for skill_name in expected_skills:
        skill_file = skill_root / skill_name / "SKILL.md"
        if not skill_file.exists():
            add_error(f"Missing SKILL.md: {skill_file}")
            continue
        content = skill_file.read_text(encoding="utf-8")
        match = re.search(r"(?s)^---\s*\n(.*?)\n---", content)
        if not match:
            add_error(f"Invalid frontmatter: {skill_file}")
            continue
        frontmatter = match.group(1)
        name_match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", frontmatter)
        if not name_match or name_match.group(1).strip() != skill_name:
            add_error(f"Skill name does not match directory: {skill_file}")
        if not re.search(r"(?m)^description:\s*.+$", frontmatter):
            add_error(f"Skill missing description: {skill_file}")
    for skill_name in expected_skill_readmes:
        readme = skill_root / skill_name / "readme.md"
        if not readme.exists():
            add_error(f"Missing skill readme: {readme}")

for label, directory, expected in [
    ("ref", dreamers_root / "refs", expected_refs),
    ("template", dreamers_root / "templates", expected_templates),
    ("instruction", instructions_root, expected_instructions),
]:
    if not directory.exists():
        continue
    assert_exact(label, expected, [path.name for path in directory.iterdir() if path.is_file()])

catalog_path = root / ".github/catalog.json"
assert_path(catalog_path, "catalog")
if catalog_path.exists():
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        items = catalog.get("items", [])
        item_keys = {(item.get("type"), item.get("slug")) for item in items}
        for key in [("skill", "dreamers"), ("skill", "dreamers-help")]:
            if key not in item_keys:
                add_error(f"Catalog missing item: {key[1]}")
        for key in [("skill", "dreamers-full"), ("skill", "dreamers-lite")]:
            if key in item_keys:
                add_error(f"Catalog retains retired item: {key[1]}")
        for item in items:
            item_path = item.get("path")
            if item_path and not (root / item_path).exists():
                add_error(f"Catalog item path does not exist: {item_path}")
        for collection in catalog.get("collections", []):
            member_keys = {
                (member.get("type"), member.get("slug"))
                for member in collection.get("members", [])
            }
            for key in [("skill", "dreamers"), ("skill", "dreamers-help")]:
                if key not in member_keys:
                    add_error(f"Collection missing member: {key[1]}")
            for key in [("skill", "dreamers-full"), ("skill", "dreamers-lite")]:
                if key in member_keys:
                    add_error(f"Collection retains retired member: {key[1]}")
            readme_path = collection.get("readmePath")
            if readme_path and not (root / readme_path).exists():
                add_error(f"Catalog readmePath does not exist: {readme_path}")
    except Exception as exc:
        add_error(f"Invalid catalog JSON: {exc}")

assert_patterns(
    skill_root / "dreamers/SKILL.md",
    [
        ("input routing", r"empty|whitespace.*help|--help|-h"),
        ("read-only help delegation", r"/dreamers-help.*read.only|read.only.*/dreamers-help"),
        ("default Grill", r"task description.*Grill.*default|Grill.*default.*task description"),
        ("explicit Grill opt-out", r"--no-grill.*do not grill|--no-grill.*skip the interview"),
        ("artifact mode", r"plan path.*manifest.*skip.*Grill|artifact mode.*skip.*Grill"),
        ("startup contract loading", r"load and apply.*dreamers/refs/git-workflow\.md.*startup verification.*before reading \.dreamers.*branch.*commit.*push"),
        ("branch setup", r"git-workflow branch setup.*checkout.*pull.*feature branch"),
        ("plan quality", r"plan-guide-selector.*plan-guide-(?:lite|standard|complex)"),
        ("approval authorizes implementation", r"plan approval authorizes implementation"),
        ("task planning before implementation", r"### Planning mode.*invoke\s+(?:\x60)?/dreamers-plan.*## Run each plan.*invoke\s+(?:\x60)?/dreamers-plan-verify.*invoke\s+(?:\x60)?/dreamers-implement"),
        ("artifact verification timing", r"### Plan and manifest modes.*single verification call at cycle entry before implementation"),
        ("verification before implementation", r"For every plan in sequence:.*1\.\s*Invoke\s+(?:\x60)?/dreamers-plan-verify exactly once.*2\.\s*Invoke\s+(?:\x60)?/dreamers-implement"),
        ("plan verification delegation", r"invoke\s+(?:\x60)?/dreamers-plan-verify"),
        ("implementation delegation", r"invoke\s+(?:\x60)?/dreamers-implement"),
        ("review delegation", r"invoke\s+(?:\x60)?/dreamers-review"),
        ("specialist call order", r"invoke\s+(?:\x60)?/dreamers-implement.*invoke\s+(?:\x60)?/dreamers-review.*invoke\s+(?:\x60)?/dreamers-docs.*invoke\s+(?:\x60)?/dreamers-pr"),
        ("review selection ref", r"<review-selection>.*</review-selection>"),
        ("visible adaptive decision", r"selected.*rationale.*without.*confirmation"),
        ("explicit review override", r"explicit user override"),
        ("major scope gate", r"major.*scope.*gate|scope expansion.*gate"),
        ("triggered user testing", r"user.testing.*trigger"),
        ("pre-PR approval", r"pre-PR approval"),
        ("independent decisions", r"independent.*ship strategy.*reviewer rerun.*documentation.*retrospective"),
        ("triggered retrospective", r"retrospective.*trigger|retro.*trigger"),
        ("PR close-out", r"/dreamers-pr"),
    ],
)
assert_pattern_count(
    skill_root / "dreamers/SKILL.md",
    "executable plan verification",
    r"\binvoke\s+(?:`)?/dreamers-plan-verify\b",
    1,
)
assert_no_patterns(
    skill_root / "dreamers/SKILL.md",
    [
        ("inline implementation heading", r"## Implement each plan inline"),
        ("implementation-only synchronized refs", r"<(?:planning-grill|testing-mandate|comment-rules|logging-discipline|reviewer-findings-format|agent-recovery)>"),
    ],
)
assert_patterns(
    skill_root / "dreamers-implement/SKILL.md",
    [
        ("tests-first implementation", r"failing tests.*implement|tests.first"),
        ("green-validation exit", r"exit.*green|green validation"),
        ("complete project validation", r"every type-check, test, build, and lint command required by project instructions"),
        ("bounded validation attempts", r"at most three attempts"),
        ("validation result reporting", r"record every command and result"),
        ("benchmark updates", r"test-benchmarks\.md.*after passing"),
        ("no review boundary", r"does not review|does NOT review"),
        ("no user-testing boundary", r"does not.*user.testing|does NOT.*user.testing"),
    ],
)
assert_no_patterns(
    skill_root / "dreamers-implement/SKILL.md",
    [("stale seven-step todo", r"Step 5 \(review\).*Step 6 \(user test\).*Step 7 \(commit\)")],
)
assert_patterns(
    skill_root / "dreamers-review/SKILL.md",
    [
        ("Vigil execution mode", r"--vigil.*Vigil|Vigil.*--vigil"),
        ("conditional todo ownership", r"when standalone.*todo.*when invoked by an outer delivery skill.*existing todo"),
        ("project-file read-only boundary", r"read.only.*project (?:code|files)|project (?:code|files).*read.only"),
        ("reviewer artifact-only writes", r"reviewer.*(?:only|sole).*write.*artifact|reviewer.*write.*exactly one.*artifact"),
    ],
)
assert_no_patterns(
    skill_root / "dreamers-plan-verify/SKILL.md",
    [("standalone-only composition prohibition", r"always invoked standalone|no composed mode|skills do not invoke other skills")],
)
assert_patterns(
    instructions_root / "dreamers.instructions.md",
    [
        ("same-context skill invocation", r"skill.*same orchestrator context|same orchestrator context.*skill"),
        ("outermost todo ownership", r"outermost skill.*owns.*todo|todo.*owned by.*outermost skill"),
    ],
)
assert_no_patterns(
    skill_root / "dreamers-update/SKILL.md",
    [("implementation mirror rule", r"dreamers-implement mirror")],
)
assert_patterns(
    skill_root / "dreamers-help/SKILL.md",
    [
        ("read-only boundary", r"read.only"),
        ("system orientation", r"Dreamers system"),
        ("delivery example", r"/dreamers\s+"),
        ("specialized choices", r"specialized"),
        ("Grill override", r"--no-grill"),
        ("review override", r"Vigil|Sentinel"),
        ("migration note", r"retired|removed|migration"),
        ("next-command prompt", r"describe.*goal|next command"),
    ],
)
assert_patterns(
    dreamers_root / "refs/review-selection.md",
    [
        ("complex triad", r"complex.*Sentinel.*Probe.*Hone"),
        ("low-risk Vigil", r"lite.*standard.*Vigil"),
        ("danger escalation", r"security.*schema.*public.*API"),
        ("visible rationale", r"rationale.*without.*confirmation"),
        ("override precedence", r"explicit user override.*wins|user override.*authoritative"),
        ("ambiguity handling", r"ambigu.*ask"),
        ("rerun policy", r"rerun"),
    ],
)
assert_patterns(
    dreamers_root / "refs/planning-grill.md",
    [
        ("default-on task Grill", r"task description.*default"),
        ("flag opt-out", r"--no-grill"),
        ("natural-language opt-out", r"do not grill|skip the interview"),
        ("artifact boundary", r"plan path.*manifest.*skip|artifact.*skip"),
    ],
)

expected_review_selection_consumers = [
    skill_root / "dreamers/SKILL.md",
]
actual_review_selection_consumers = [
    path
    for path in (root / ".github").rglob("*.md")
    if re.search(
        r"<review-selection>.*</review-selection>",
        path.read_text(encoding="utf-8"),
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
]
assert_exact(
    "review-selection consumer",
    [path.relative_to(root).as_posix() for path in expected_review_selection_consumers],
    [path.relative_to(root).as_posix() for path in actual_review_selection_consumers],
)

scan_roots = [
    agent_root,
    skill_root,
    dreamers_root,
    instructions_root,
    root / "README.md",
    root / ".github/README.md",
    catalog_path,
]
legacy_pattern = re.compile(r"dreamers-(?:full|lite)")
migration_pattern = re.compile(
    r"retir|remov|legacy|migrat|cleanup|clean up|previous|old command|no longer",
    re.IGNORECASE,
)
for scan_root in scan_roots:
    if not scan_root.exists():
        continue
    files = [scan_root] if scan_root.is_file() else [
        path
        for path in scan_root.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".ps1"}
    ]
    for path in files:
        if path.name.startswith("Test-DreamersCopilot"):
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1,
        ):
            if legacy_pattern.search(line) and not migration_pattern.search(line):
                add_error(
                    f"Active retired-pipeline reference in "
                    f"{path.relative_to(root)}:{line_number}"
                )

workflow_path = root / ".github/workflows/verify-refs.yml"
assert_patterns(
    workflow_path,
    [
        ("Bash validator CI", r"Test-DreamersCopilot\.sh"),
        ("PowerShell validator CI", r"Test-DreamersCopilot\.ps1"),
        ("package surface paths", r"Install-Dreamers\.ps1.*catalog\.json"),
    ],
)

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    sys.exit(1)

print("Dreamers Copilot validation passed.")
PY
