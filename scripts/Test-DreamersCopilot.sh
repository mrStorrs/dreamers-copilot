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


expected_agents = [
    "echo",
    "hone",
    "probe",
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
    "dreamers-explain",
    "dreamers-find-refactors",
    "dreamers-help",
    "dreamers-lite",
    "dreamers-implement",
    "dreamers-issue",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-plan-verify",
    "dreamers-pr",
    "dreamers-pr-resolve",
    "dreamers-review",
    "dreamers-simplify",
    "dreamers-test",
    "dreamers-update",
]
expected_refs = [
    "comment-cleanup-workflow.md",
    "documentation-workflow.md",
    "help-workflow.md",
    "implementation-workflow.md",
    "planning-workflow.md",
    "pr-workflow.md",
    "review-workflow.md",
    "agent-recovery.md",
    "comment-rules.md",
    "dreamers-kernel.md",
    "git-workflow.md",
    "logging-discipline.md",
    "manifest-format.md",
    "plan-format.md",
    "planning-grill.md",
    "project-bootstrap.md",
    "reviewer-findings-format.md",
    "shell-plan.md",
    "testing-mandate.md",
    "user-testing-gate.md",
]
expected_templates = [
    "discovery-questions.md",
    "github-issue.md",
    "logging-standards.md",
    "manifest.md",
    "plan.md",
    "pr-description.md",
    "project-brief.md",
    "shell-plan.md",
    "test-benchmarks.md",
    "user-testing-gate.md",
]
expected_instructions = [
    "dreamers.comment-rules.instructions.md",
    "dreamers.instructions.md",
    "dreamers.laws.md",
]
expected_skill_readmes = [
    "dreamers",
    "dreamers-add-logging",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-explain",
    "dreamers-find-refactors",
    "dreamers-lite",
    "dreamers-implement",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-pr-resolve",
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

workflow_consumers = {
    "dreamers": ["help", "planning", "implementation", "review", "documentation", "pr"],
    "dreamers-lite": ["implementation", "review", "documentation", "pr"],
    "dreamers-help": ["help"],
    "dreamers-plan": ["planning"],
    "dreamers-implement": ["implementation"],
    "dreamers-review": ["review"],
    "dreamers-docs": ["documentation"],
    "dreamers-pr": ["pr"],
    "dreamers-update": ["pr"],
    "dreamers-cleanup-comments": ["comment-cleanup"],
    "dreamers-cleanup-comments-branch": ["comment-cleanup"],
}

for skill, workflows in workflow_consumers.items():
    path = skill_root / skill / "SKILL.md"
    if not path.exists():
        continue
    content = path.read_text(encoding="utf-8")
    for workflow in workflows:
        target = f"../../dreamers/refs/{workflow}-workflow.md"
        if f"]({target})" not in content:
            add_error(f"Missing direct workflow ref in {path.relative_to(root)}: {target}")

link_pattern = re.compile(r"\[[^\]\n]+\]\(([^)\s]+\.md)\)")
instruction_files = list(skill_root.glob("*/SKILL.md")) + list(instructions_root.glob("*.md"))
workflow_files = list((dreamers_root / "refs").glob("*-workflow.md"))
for path in instruction_files + workflow_files:
    content = path.read_text(encoding="utf-8")
    for target in link_pattern.findall(content):
        if target.endswith("/SKILL.md"):
            add_error(f"Skill-to-skill file dependency in {path.relative_to(root)}: {target}")
        elif path in workflow_files or "dreamers/refs/" in target:
            if not (path.parent / target).is_file():
                add_error(f"Broken workflow ref link in {path.relative_to(root)}: {target}")
    if re.search(r"(?im)^(?:\d+[.)]\s+|-\s+)?(?:on success,\s*|upon approval\s+)?(?:invoke|call|run|prefer)\s+`?/dreamers(?:-|\b)", content):
        add_error(f"Skill-to-skill invocation in {path.relative_to(root)}")

catalog_path = root / ".github/catalog.json"
assert_path(catalog_path, "catalog")
if catalog_path.exists():
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        items = catalog.get("items", [])
        refs_target = next((item for item in catalog.get("folderTargets", []) if item.get("slug") == "dreamers-refs"), {})
        if refs_target.get("sourcePath") != ".github/dreamers/refs" or refs_target.get("destSubpath") != "dreamers/refs":
            add_error("Catalog must install shared workflow refs at dreamers/refs")
        item_keys = {(item.get("type"), item.get("slug")) for item in items}
        for key in [("skill", "dreamers")]:
            if key not in item_keys:
                add_error(f"Catalog missing item: {key[1]}")
        for key in [("skill", "dreamers-full"), ("skill", "dreamers-research"), ("agent", "sage")]:
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
            if ("folder", "dreamers-refs") not in member_keys:
                add_error("Collection missing member: dreamers-refs")
            for key in [("skill", "dreamers-full"), ("skill", "dreamers-research"), ("agent", "sage")]:
                if key in member_keys:
                    add_error(f"Collection retains retired member: {key[1]}")
            readme_path = collection.get("readmePath")
            if readme_path and not (root / readme_path).exists():
                add_error(f"Catalog readmePath does not exist: {readme_path}")
    except Exception as exc:
        add_error(f"Invalid catalog JSON: {exc}")

assert_patterns(
    dreamers_root / "refs/help-workflow.md",
    [
        ("read-only boundary", r"## Boundary.*read-only guidance.*Do not inspect or change"),
        ("primary examples", r"/dreamers add offline export.*feature-search/plan-01-indexing\.md.*feature-search/manifest\.md"),
        ("review lanes", r"lite plans use Vigil.*standard plans use Sentinel \+ Probe.*complex plans use Sentinel \+ Probe \+ Hone"),
        ("specialized choices", r"/dreamers-plan.* /dreamers-implement.* /dreamers-review.* /dreamers-lite"),
        ("mandatory gates", r"plan approval.*major scope expansion.*triggered user testing.*final pre-PR approval"),
        ("invitation", r"Describe your goal and I can suggest the next command"),
    ],
)
assert_patterns(
    skill_root / "dreamers-pr-resolve/SKILL.md",
    [
        ("deferred Vigil findings ledger", r"Defer — save to defered\.md.*do NOT apply.*create a follow-up plan.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`"),
        ("deferred ledger commit", r"If any fixes landed or Step 5 added deferred entries"),
        ("deferred ledger report", r"Deferred Vigil findings recorded in `defered\.md`"),
    ],
)
assert_patterns(
    dreamers_root / "refs/review-workflow.md",
    [
        ("Vigil execution mode", r"--vigil.*Vigil|Vigil.*--vigil"),
        ("full execution mode", r"--full.*Sentinel \+ Probe \+ Hone"),
        ("selection precedence", r"explicit lane flag or explicit user direction.*explicit reviewer requirement.*Plan-type"),
        ("lite selection", r"lite` = Vigil"),
        ("standard selection", r"standard` = Sentinel \+ Probe"),
        ("complex selection", r"complex` = Sentinel \+ Probe \+ Hone"),
        ("planless intent inference", r"infer the intended behavior.*explicit user direction.*PR title/body.*commits and diff.*changed tests.*changed code"),
        ("planless ambiguity question", r"one reliable interpretation.*ask the user one concise question"),
        ("planless reviewer basis", r"review basis.*absolute plan path.*inferred-intent summary"),
        ("Grill transcript resolution", r"Grilling transcript:.*sibling `grilling-transcript\.md`.*read it in full"),
        ("Grill transcript reviewer context", r"absolute path and full verbatim contents.*plan/transcript conflict"),
        ("conditional todo ownership", r"when used standalone.*todo.*when used as a delivery phase.*existing todo"),
        ("project-file read-only boundary", r"read.only.*project (?:code|files)|project (?:code|files).*read.only"),
        ("reviewer artifact-only writes", r"reviewer.*(?:only|sole).*write.*artifact|reviewer.*write.*exactly one.*artifact"),
        ("caller owns fix loop", r"caller owns all finding disposition, gates, fixes, revalidation, and user testing"),
    ],
)
assert_patterns(
    agent_root / "vigil.agent.md",
    [
        ("planless Vigil review basis", r"If no plan is bound.*inferred-intent summary.*evidence"),
        ("planless Vigil requirements", r"plan AC or inferred requirement"),
    ],
)
assert_patterns(
    agent_root / "probe.agent.md",
    [
        ("planless Probe review basis", r"no plan is bound.*inferred requirements"),
        ("planless Probe findings", r"report missing or weak coverage as findings"),
    ],
)
assert_patterns(
    instructions_root / "dreamers.instructions.md",
    [
        ("independent skills", r"Do not invoke another skill or load another skill.*SKILL\.md.*Execute shared workflow refs inline"),
        ("active skill todo ownership", r"active skill owns the todo and end-to-end state"),
        ("global deferred suggestions ledger", r"Deferred suggestions.*explicitly chooses `Defer`.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`"),
    ],
)
assert_no_patterns(
    skill_root / "dreamers-update/SKILL.md",
    [("implementation mirror rule", r"dreamers-implement mirror")],
)
assert_patterns(
    skill_root / "dreamers-explain/SKILL.md",
    [
        ("read-only boundary", r"Default to read-only work.*do not modify the subject"),
        ("conditional source retrieval", r"Search or retrieve external sources when:.*facts may have changed.*niche, disputed, uncertain, or high-stakes"),
        ("source priority", r"Source priority:.*repository evidence.*First-party documentation.*High-quality secondary sources"),
        ("layered explanation", r"Direct answer.*Orientation.*Mental model.*Mechanics.*Concrete example.*Edges and alternatives.*Takeaway"),
        ("optional comprehension", r"Do not force a quiz or Socratic exchange"),
    ],
)
assert_patterns(
    skill_root / "dreamers-new-project/SKILL.md",
    [
        ("existing-solutions opt-in gate", r"Phase 1\.5.*request_information.*Research similar existing solutions.*Skip research"),
        ("research blocked before approval", r"Do not perform research before the user explicitly approves it"),
        ("research remains conversation-only", r"Keep this phase conversation-only: no subagent and no disk writes"),
        ("research informs downstream artifacts", r"existing-solutions research.*stack recommendation.*project brief"),
    ],
)

for path in [
    skill_root / "dreamers/SKILL.md",
    skill_root / "dreamers-plan/SKILL.md",
    skill_root / "dreamers-plan/readme.md",
    dreamers_root / "refs/planning-grill.md",
    dreamers_root / "refs/planning-workflow.md",
    root / "README.md",
    root / ".github/README.md",
]:
    assert_no_patterns(
        path,
        [
            ("Grill opt-out policy", r"--no-grill|do not grill|skip the interview"),
        ],
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
legacy_pattern = re.compile(r"dreamers-full|dreamers-research|\bsage\b|plan-quality|plan-selection|plan-guide-selector", re.IGNORECASE)
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
