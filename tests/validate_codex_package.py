"""Package contracts migrated from the former Codex repository validator."""

from pathlib import Path
import json
import re
import sys
import tomllib

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


def assert_patterns(path: Path, patterns: dict[str, str]) -> None:
    if not path.exists():
        add_error(f"Missing contract file: {path}")
        return
    content = path.read_text(encoding="utf-8")
    for label, pattern in patterns.items():
        if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            add_error(f"Missing {label} contract in {path}")


def assert_no_patterns(path: Path, patterns: dict[str, str]) -> None:
    if not path.exists():
        add_error(f"Missing contract file: {path}")
        return
    content = path.read_text(encoding="utf-8")
    for label, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            add_error(f"Unexpected {label} contract in {path}")


expected_agents = [
    "echo",
    "hone",
    "probe",
    "sentinel",
    "vigil"
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
    "dreamers-implement",
    "dreamers-issue",
    "dreamers-lite",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-plan-verify",
    "dreamers-pr",
    "dreamers-pr-resolve",
    "dreamers-review",
    "dreamers-simplify",
    "dreamers-test",
    "dreamers-update"
]
expected_refs = [
    "agent-recovery.md",
    "codex-runtime.md",
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
    "user-testing-gate.md"
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
    "user-testing-gate.md"
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
    "dreamers-implement",
    "dreamers-lite",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-pr-resolve",
    "dreamers-review"
]

agent_root = root / "agents"
skill_root = root / "skills"
dreamers_root = root / "dreamers"

assert_path(agent_root, "agents directory")
assert_path(skill_root, "skills directory")
assert_path(dreamers_root, "dreamers directory")

if (dreamers_root / "agents").exists():
    add_error(f"Legacy role prompt directory should not exist: {dreamers_root / 'agents'}")

if agent_root.exists():
    actual_agents = [path.stem for path in agent_root.glob("*.toml")]
    assert_exact("agent", expected_agents, actual_agents)
    for name in expected_agents:
        path = agent_root / f"{name}.toml"
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        try:
            tomllib.loads(content)
        except Exception as exc:
            add_error(f"Invalid agent TOML: {path} ({exc})")
        if not re.search(rf'(?m)^name\s*=\s*"{re.escape(name)}"\s*$', content):
            add_error(f"Agent name does not match basename: {path}")
        if not re.search(r'(?m)^description\s*=\s*".+"\s*$', content):
            add_error(f"Agent missing non-empty description: {path}")
        if not re.search(r"(?s)developer_instructions\s*=\s*'''(.+)'''", content):
            add_error(f"Agent missing developer_instructions literal block: {path}")
        if name in {"sentinel", "probe", "hone", "vigil"} and re.search(
            r"(?m)^model(?:_reasoning_effort)?\s*=", content
        ):
            add_error(f"Reviewer agent pins model configuration: {path}")

if skill_root.exists():
    actual_skills = [path.name for path in skill_root.iterdir() if path.is_dir()]
    assert_exact("skill", expected_skills, actual_skills)
    for skill_name in expected_skills:
        path = skill_root / skill_name / "SKILL.md"
        if not path.exists():
            add_error(f"Missing SKILL.md: {path}")
            continue
        content = path.read_text(encoding="utf-8")
        if not re.search(r"(?s)^---\s*\nname:\s*([^\n]+)\ndescription:\s*([^\n]+)\n---", content):
            add_error(f"Invalid frontmatter: {path}")
        if "argument-hint:" in content:
            add_error(f"Copilot argument-hint remains: {path}")
    for skill_name in expected_skill_readmes:
        path = skill_root / skill_name / "readme.md"
        if not path.exists():
            add_error(f"Missing skill readme copied from source: {path}")

for label, directory, expected in [
    ("ref", dreamers_root / "refs", expected_refs),
    ("template", dreamers_root / "templates", expected_templates),
    ("instruction", dreamers_root / "instructions", expected_instructions),
]:
    if not directory.exists():
        add_error(f"Missing {label} directory: {directory}")
        continue
    assert_exact(label, expected, [path.name for path in directory.iterdir() if path.is_file()])

for rel in [".codex-plugin/plugin.json", ".github/catalog.json"]:
    path = root / rel
    if not path.exists():
        add_error(f"Missing JSON file: {path}")
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add_error(f"Invalid JSON: {path} ({exc})")

catalog_path = root / ".github/catalog.json"
if catalog_path.exists():
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        items = {f"{item.get('type')}:{item.get('slug')}" for item in catalog.get("items", [])}
        for required in ["skill:dreamers", "skill:dreamers-help"]:
            if required not in items:
                add_error(f"Catalog missing item: {required}")
        for retired in ["skill:dreamers-full", "skill:dreamers-research", "agent:forge", "agent:nova", "agent:sage"]:
            if retired in items:
                add_error(f"Catalog retains retired item: {retired}")
        for item in catalog.get("items", []):
            item_path = item.get("path")
            if not item_path:
                continue
            if item_path.startswith(".github/") or item_path.startswith("skillsdreamers-"):
                add_error(f"Catalog path is not Codex-layout: {item_path}")
                continue
            if not (root / item_path).exists():
                add_error(f"Catalog item path does not exist: {item_path}")
        for collection in catalog.get("collections", []):
            readme_path = collection.get("readmePath")
            if readme_path and not (root / readme_path).exists():
                add_error(f"Catalog readmePath does not exist: {readme_path}")
            members = {
                f"{member.get('type')}:{member.get('slug')}"
                for member in collection.get("members", [])
            }
            for required in ["skill:dreamers", "skill:dreamers-help"]:
                if required not in members:
                    add_error(f"Collection missing member: {required}")
            for retired in ["skill:dreamers-full", "skill:dreamers-research", "agent:forge", "agent:nova", "agent:sage"]:
                if retired in members:
                    add_error(f"Collection retains retired member: {retired}")
        for folder in catalog.get("folderTargets", []):
            source_path = folder.get("sourcePath")
            if not source_path:
                continue
            if source_path.startswith(".github/"):
                add_error(f"Catalog folder sourcePath is not Codex-layout: {source_path}")
                continue
            if not (root / source_path).exists():
                add_error(f"Catalog folder sourcePath does not exist: {source_path}")
    except Exception as exc:
        add_error(f"Unable to validate catalog paths: {exc}")

assert_patterns(
    skill_root / "dreamers/SKILL.md",
    {
        "help route before inspection": r"Empty input.*`help`.*`--help`.*`-h`.*dreamers-help.*stop before inspecting",
        "artifact authorization": r"Supplied artifacts are implementation authorization.*do not re-plan.*ask to start",
        "task planning and start gate": r"Phase 1:.*Invoke `dreamers-plan.*Approved — start implementation.*start INCREMENTAL.*start ATOMIC",
        "implementation then selected review": r"### Implement and review.*dreamers-implement.*dreamers-review --branch",
        "capped Vigil fixes": r"dreamers-review --vigil.*up to 3 times.*Ask before major refactors.*defered\.md",
        "blocked or unresolved review stops": r"Halt.*blocked review or unresolved findings at the cap",
        "triggered user testing": r"### User testing.*manual verification.*user-testing-gate.*Bug reports resume.*step 1",
        "ship strategies": r"ATOMIC.*commit.*do not push.*INCREMENTAL.*dreamers-docs --branch.*confirm merge",
        "close-out order": r"Phase 3.*dreamers-docs --branch.*commit remaining changes.*Approved.*dreamers-pr",
    },
)
assert_patterns(
    skill_root / "dreamers-help/SKILL.md",
    {
        "Codex runtime preamble": r"## Codex runtime.*codex-runtime\.md.*user's message as skill input",
        "read-only boundary": r"## Boundary.*read-only guidance.*Do not inspect or change",
        "primary examples": r"dreamers add offline export.*dreamers feature-search/plan-01-indexing\.md.*dreamers feature-search/manifest\.md",
        "review lanes": r"lite plans use Vigil.*standard plans use Sentinel \+ Probe.*complex plans use Sentinel \+ Probe \+ Hone",
        "specialized choices": r"dreamers-plan.* dreamers-implement.* dreamers-review.* dreamers-lite",
        "mandatory gates": r"plan approval.*major scope expansion.*triggered user testing.*final pre-PR approval",
        "invitation": r"Describe your goal and I can suggest the next command",
    },
)
assert_patterns(
    skill_root / "dreamers-pr-resolve/SKILL.md",
    {
        "deferred Vigil findings ledger": r"Defer — save to defered\.md.*do NOT apply.*create a follow-up plan.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`",
        "deferred ledger commit": r"If any fixes landed or Step 5 added deferred entries",
        "deferred ledger report": r"Deferred Vigil findings recorded in `defered\.md`",
    },
)
assert_no_patterns(
    skill_root / "dreamers/SKILL.md",
    {
        "retired pipeline name": r"dreamers-full",
        "Grill opt-out": r"--no-grill|do not grill|skip the interview",
        "inline implementation refs": r"<(?:planning-grill|testing-mandate|comment-rules|logging-discipline|reviewer-findings-format|agent-recovery)>",
    },
)
assert_patterns(
    skill_root / "dreamers-implement/SKILL.md",
    {
        "task or plan implementation": r"Implement the task or approved plan.*stated requirements as acceptance criteria; no plan file is needed",
        "bounded validation": r"Type-check \+ run tests.*max 3 attempts.*halt",
        "green coverage handoff": r"Return requirement/AC coverage and validation results at green tests",
        "optional standalone progress": r"When standalone, a todo is optional.*outer delivery skill.*existing todo",
    },
)
assert_patterns(
    skill_root / "dreamers-review/SKILL.md",
    {
        "Vigil mode": r"--vigil.*Vigil|Vigil.*--vigil",
        "full mode": r"--full.*Sentinel \+ Probe \+ Hone",
        "selection precedence": r"explicit lane flag or explicit user direction.*explicit reviewer requirement.*Plan-type",
        "lite selection": r"lite` = Vigil",
        "standard selection": r"standard` = Sentinel \+ Probe",
        "complex selection": r"complex` = Sentinel \+ Probe \+ Hone",
        "planless intent inference": r"infer the intended behavior.*explicit user direction.*PR title/body.*commits and diff.*changed tests.*changed code",
        "planless ambiguity question": r"one reliable interpretation.*ask the user one concise question",
        "planless reviewer basis": r"review basis.*absolute plan path.*inferred-intent summary",
        "Grill transcript resolution": r"Grilling transcript:.*sibling `grilling-transcript\.md`.*read it in full",
        "Grill transcript reviewer context": r"absolute path and full verbatim contents.*plan/transcript conflict",
        "parallel spawning": r"launch every selected reviewer concurrently.*Never spawn or await reviewers sequentially",
        "caller owns fix loop": r"caller owns all finding disposition, gates, fixes, revalidation, and user testing",
        "artifact-only reviewer writes": r"sole write is exactly one.*artifact",
    },
)
assert_patterns(
    dreamers_root / "refs/planning-grill.md",
    {
        "explore before asking": r"Explore the codebase for answers before asking the user",
        "single blocking question": r"one blocking question at a time",
        "verbatim transcript": r"every question and response verbatim.*complete tool questions, choice labels, and descriptions.*never summarize, paraphrase, normalize, or omit",
        "transcript storage": r"\.dreamers/plans/feature-<slug>/grilling-transcript\.md.*Do not create an empty transcript",
    },
)
assert_patterns(
    skill_root / "dreamers-plan/SKILL.md",
    {
        "planning write boundary": r"write only `\.dreamers/plans/` artifacts; do not change project files or git state",
        "proposal before writing": r"Propose to user.*until approved.*Write plan",
        "review gate": r"Review gate.*Approved.*Minor edit.*Major rewrite.*Halt",
    },
)
assert_patterns(
    agent_root / "vigil.toml",
    {
        "planless Vigil review basis": r"If no plan is bound.*inferred-intent summary.*evidence",
        "planless Vigil requirements": r"plan AC or inferred requirement",
    },
)
assert_patterns(
    agent_root / "probe.toml",
    {
        "planless Probe review basis": r"no plan is bound.*inferred requirements",
        "planless Probe findings": r"report missing or weak coverage as findings",
    },
)
assert_patterns(
    skill_root / "dreamers-new-project/SKILL.md",
    {
        "existing-solutions opt-in gate": r"Phase 1\.5.*ask the user.*Research similar existing solutions.*Skip research",
        "research blocked before approval": r"Do not perform research before the user explicitly approves it",
        "research remains conversation-only": r"Keep this phase conversation-only: no subagent and no disk writes",
        "research informs downstream artifacts": r"existing-solutions research.*stack recommendation.*project brief",
    },
)
assert_patterns(
    dreamers_root / "instructions/dreamers.instructions.md",
    {
        "same-context composition": r"skill.*same orchestrator context",
        "outermost progress ownership": r"outermost skill.*owns.*todo",
        "durable delivery state": r"Delivery continuation.*goal, owning skill, branch/PR, next phase, and review count.*confirmed outcomes",
        "follow-ups preserve caps": r"resume the pending phase.*detours do not reset an active review count",
        "open PR corrections": r"open PR, reuse its branch.*dreamers-review --vigil.*staged \+ unstaged.*dreamers-docs --staged.*approval for the current changes before committing and pushing.*Reuse approval already given",
        "global deferred ledger": r"explicitly chooses `Defer`.*defered\.md.*never overwrite existing entries",
    },
)
assert_patterns(
    dreamers_root / "refs/codex-runtime.md",
    {
        "same-context composition": r"invoke it in the same orchestrator context",
        "parallel reviewer runtime": r"launch every selected reviewer concurrently.*Never spawn and await reviewers sequentially",
    },
)
assert_no_patterns(
    skill_root / "dreamers-update/SKILL.md",
    {"implementation mirror rule": r"dreamers-implement mirror"},
)
assert_patterns(
    skill_root / "dreamers-explain/SKILL.md",
    {
        "Codex runtime preamble": r"## Codex runtime.*codex-runtime\.md.*user's message as skill input",
        "read-only boundary": r"Default to read-only work.*do not modify the subject",
        "conditional source retrieval": r"Search or retrieve external sources when:.*facts may have changed.*niche, disputed, uncertain, or high-stakes",
        "source priority": r"Source priority:.*repository evidence.*First-party documentation.*High-quality secondary sources",
        "layered explanation": r"Direct answer.*Orientation.*Mental model.*Mechanics.*Concrete example.*Edges and alternatives.*Takeaway",
        "optional comprehension": r"Do not force a quiz or Socratic exchange",
    },
)
assert_patterns(
    root / ".codex-plugin/plugin.json",
    {"unified default prompt": r"Use dreamers to plan and ship"},
)

assert_patterns(
    skill_root / "dreamers-lite/SKILL.md",
    {
        "direct task implementation": r"dreamers-implement <task description and agreed scope>",
        "capped Vigil fixes": r"dreamers-review --vigil --branch.*up to 2 times.*Ask before major refactors.*defered\.md",
        "blocked or unresolved review stops": r"Halt on a blocked review or unresolved findings at the cap",
        "uncommitted docs before commit": r"Phase 3.*dreamers-docs --staged.*commit remaining changes.*Approved.*dreamers-pr",
        "continuation routing": r"Delivery continuation.*resume the pending phase",
    },
)

assert_patterns(
    dreamers_root / "refs/plan-format.md",
    {
        "unified plan body": r"## Goal.*## Scope and context.*## Acceptance Criteria",
        "complexity metadata": r"Plan-type:.*lite\|standard\|complex",
        "optional transcript link": r"Grilling transcript:.*grilling-transcript\.md.*Include the transcript link only when the sibling artifact exists",
        "checks with ACs": r"Under the relevant AC, add a test command or check.*manual checks.*steps, expected result.*User-testing-required: yes",
        "useful visuals": r"Mermaid diagrams.*UI layouts/wireframes",
    },
)

scan_roots = [
    root / "agents",
    root / "skills",
    root / "dreamers",
    root / "README.md",
    root / "Install-DreamersCodex.ps1",
    root / "Remove-DreamersCodex.ps1",
    root / ".github/catalog.json",
]
scan_files: list[Path] = []
for path in scan_roots:
    if not path.exists():
        continue
    if path.is_dir():
        scan_files.extend(
            child
            for child in path.rglob("*")
            if child.is_file() and child.suffix in {".md", ".toml", ".ps1", ".json"}
        )
    else:
        scan_files.append(path)

stale_patterns = [
    r"Atlas",
    r"WebSearch",
    r"WebFetch",
    r"C:\\Users\\cjsto\\.Codex",
    r"~/.Codex",
    r"\.github/agents/",
    r"\.github/skills/",
    r"\.github/dreamers/",
    r"dreamers/agents/<role>",
    r"dreamers/agents/sentinel",
    r"dreamers/agents/probe",
    r"dreamers/agents/hone",
    r"manage_todo_list",
    r"request_information",
    r"task\(",
    r"mode:\s*[\"']?sync",
]

for path in scan_files:
    rel = path.relative_to(root).as_posix()
    if rel in {"dreamers/refs/codex-runtime.md", "skills/dreamers-update/SKILL.md"}:
        continue
    content = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in stale_patterns:
        if re.search(pattern, content):
            add_error(f"Stale Copilot/legacy token '{pattern}' remains in {rel}")

legacy_pattern = re.compile(r"dreamers-full|dreamers-research|\b(?:forge|nova|sage)\b|plan-quality|plan-selection|plan-guide-(?:selector|lite|standard|complex)|hone-architecture-rubric", re.IGNORECASE)
migration_pattern = re.compile(
    r"retir|remov|legacy|migrat|cleanup|clean up|previous|old command|no longer",
    re.IGNORECASE,
)
for path in [agent_root, skill_root, dreamers_root, root / "README.md", catalog_path, root / ".codex-plugin/plugin.json"]:
    if not path.exists():
        continue
    files = (
        [child for child in path.rglob("*") if child.is_file()]
        if path.is_dir()
        else [path]
    )
    for file in files:
        if file.name.startswith("Test-DreamersCodex"):
            continue
        for line_number, line in enumerate(
            file.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
        ):
            if legacy_pattern.search(line) and not migration_pattern.search(line):
                add_error(f"Active retired-pipeline reference in {file}:{line_number}")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    sys.exit(1)
print("Dreamers Codex package validation passed.")
