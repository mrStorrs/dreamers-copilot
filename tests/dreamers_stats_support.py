import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHARED_RUNTIME_REPO_ROOT = REPO_ROOT.parent / "dreamers-mcp"
WRITER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_stats.py"
HOOK_CONFIG_PATH = REPO_ROOT / ".github" / "dreamers" / "hooks" / "dreamers-stats.json"
HOOK_BASH_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.sh"
HOOK_POWERSHELL_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.ps1"
INSTALLER_PATH = REPO_ROOT / "Install-Dreamers.ps1"
REMOVER_PATH = REPO_ROOT / "Remove-Dreamers.ps1"
RUNTIME_INSTALL_STATE_RELATIVE = Path("dreamers") / "install-state" / "runtime-hooks.txt"
INSTALLED_RUNTIME_PACKAGE_RELATIVE = Path("dreamers") / "runtime" / "dreamers_stats"
STATS_CHECKPOINTS_REF_PATH = REPO_ROOT / ".github" / "dreamers" / "refs" / "stats-checkpoints.md"
SKILL_PATHS = {
    "dreamers-full": REPO_ROOT / ".github" / "skills" / "dreamers-full" / "SKILL.md",
    "dreamers-lite": REPO_ROOT / ".github" / "skills" / "dreamers-lite" / "SKILL.md",
    "dreamers-review": REPO_ROOT / ".github" / "skills" / "dreamers-review" / "SKILL.md",
    "dreamers-pr-resolve": REPO_ROOT / ".github" / "skills" / "dreamers-pr-resolve" / "SKILL.md",
}


def load_writer():
    spec = importlib.util.spec_from_file_location("dreamers_stats_shim", WRITER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_event(**overrides):
    event = {
        "schema_version": 1,
        "event_id": "evt_01",
        "timestamp": "2026-06-13T10:00:00-07:00",
        "event_type": "skill_started",
        "repo_path": "/tmp/example",
        "source": "skill",
        "status": "started",
        "metrics": {"mode": "plan-path"},
    }
    event.update(overrides)
    return event


class DreamersStatsTestCase(unittest.TestCase):
    def setUp(self):
        self.stats = load_writer()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "copilot-home"
        self.events_file = self.home / "dreamers" / "stats" / "events.jsonl"
        self.fixture_repo = Path(self.tmp.name) / "fixture-repo"
        (self.fixture_repo / ".git").mkdir(parents=True)
        (self.fixture_repo / ".dreamers" / "reviews").mkdir(parents=True)
        self.other_repo = Path(self.tmp.name) / "other-repo"
        (self.other_repo / ".git").mkdir(parents=True)

    def read_events(self):
        return [json.loads(line) for line in self.events_file.read_text(encoding="utf-8").splitlines()]

    def invoke(self, argv, stdin_text="", cwd=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        stdin = io.StringIO(stdin_text)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            if cwd is None:
                code = self.stats.main(argv, stdin=stdin)
            else:
                with contextlib.chdir(cwd):
                    code = self.stats.main(argv, stdin=stdin)
        return code, stdout.getvalue(), stderr.getvalue()

    def invoke_hook(self, event_name, payload):
        return self.invoke(
            ["hook", "--copilot-home", str(self.home), "--event-name", event_name],
            stdin_text=json.dumps(payload),
        )

    def invoke_checkpoint(
        self,
        event_type,
        *,
        skill="dreamers-full",
        run_id="run_01",
        status=None,
        metrics=None,
        extra_args=None,
    ):
        argv = [
            "checkpoint",
            "--copilot-home",
            str(self.home),
            "--event-type",
            event_type,
            "--skill",
            skill,
            "--run-id",
            run_id,
            "--metrics-json",
            json.dumps(metrics or {}),
        ]
        if status is not None:
            argv.extend(["--status", status])
        if extra_args:
            argv.extend(extra_args)
        return self.invoke(argv)

    def record_checkpoint_sequence(self, *, skill, run_id, events):
        for event in events:
            code, stdout, stderr = self.invoke_checkpoint(
                event["event_type"],
                skill=skill,
                run_id=run_id,
                status=event.get("status"),
                metrics=event.get("metrics"),
                extra_args=event.get("extra_args"),
            )

            self.assertEqual(0, code, event["event_type"])
            self.assertEqual("", stdout)
            self.assertEqual("", stderr)

        return self.read_events()

    def powershell_command(self):
        if shutil.which("pwsh"):
            return ["pwsh", "-NoLogo", "-NoProfile", "-File"]
        if shutil.which("powershell"):
            return ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
        self.skipTest("PowerShell is not available in this environment")

    def run_powershell_script(self, script_path, *args, input_text="", env=None):
        command = [*self.powershell_command(), str(script_path), *args]
        return subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
            cwd=REPO_ROOT,
            env=env,
        )

    def run_python_script(self, script_path, *args, input_text="", cwd=None, env=None):
        command = [sys.executable, str(script_path), *args]
        return subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
            cwd=REPO_ROOT if cwd is None else cwd,
            env=env,
        )

    def repo_path(self, which="current"):
        if which == "current":
            return self.fixture_repo
        if which == "other":
            return self.other_repo
        raise ValueError(which)

    def fixture_event(
        self,
        event_type,
        *,
        event_id,
        timestamp,
        metrics,
        source="skill",
        status=None,
        repo="current",
        run_id=None,
        session_id=None,
        skill=None,
        branch="stats-testing",
    ):
        repo_path = self.repo_path(repo)
        return {
            "schema_version": 1,
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "repo_path": str(repo_path),
            "repo_name": repo_path.name,
            "branch": branch,
            "run_id": run_id,
            "session_id": session_id,
            "skill": skill,
            "source": source,
            "status": status if status is not None else self.stats.default_status_for_event(event_type),
            "metrics": metrics,
        }

    def record_fixture_event(self, event):
        self.stats.record_event(event, copilot_home=self.home)

    def write_fixture_lines(self, lines):
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        with self.events_file.open("a", encoding="utf-8", newline="\n") as handle:
            for line in lines:
                handle.write(line)
                handle.write("\n")

    def write_review_artifact(self, repo_path, name, body):
        artifact_path = repo_path / ".dreamers" / "reviews" / name
        artifact_path.write_text(body, encoding="utf-8")
        return artifact_path
