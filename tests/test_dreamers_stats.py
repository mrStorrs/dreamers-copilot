import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WRITER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_stats.py"
HOOK_CONFIG_PATH = REPO_ROOT / ".github" / "dreamers" / "hooks" / "dreamers-stats.json"
HOOK_BASH_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.sh"
HOOK_POWERSHELL_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.ps1"
INSTALLER_PATH = REPO_ROOT / "Install-Dreamers.ps1"
REMOVER_PATH = REPO_ROOT / "Remove-Dreamers.ps1"
RUNTIME_INSTALL_STATE_RELATIVE = Path("dreamers") / "install-state" / "runtime-hooks.txt"
STATS_CHECKPOINTS_REF_PATH = REPO_ROOT / ".github" / "dreamers" / "refs" / "stats-checkpoints.md"
SKILL_PATHS = {
    "dreamers-full": REPO_ROOT / ".github" / "skills" / "dreamers-full" / "SKILL.md",
    "dreamers-lite": REPO_ROOT / ".github" / "skills" / "dreamers-lite" / "SKILL.md",
    "dreamers-review": REPO_ROOT / ".github" / "skills" / "dreamers-review" / "SKILL.md",
    "dreamers-pr-resolve": REPO_ROOT / ".github" / "skills" / "dreamers-pr-resolve" / "SKILL.md",
}


def load_writer():
    spec = importlib.util.spec_from_file_location("dreamers_stats", WRITER_PATH)
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


class DreamersStatsWriterTests(unittest.TestCase):
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

    def test_record_event_creates_stats_dir_and_appends_jsonl_line(self):
        event_id = self.stats.record_event(valid_event(), copilot_home=self.home)

        self.assertEqual("evt_01", event_id)
        self.assertTrue(self.events_file.exists())
        events = self.read_events()
        self.assertEqual(1, len(events))
        self.assertEqual("skill_started", events[0]["event_type"])

    def test_missing_required_envelope_fields_are_rejected_without_append(self):
        required_fields = (
            "schema_version",
            "event_id",
            "timestamp",
            "event_type",
            "repo_path",
            "source",
            "metrics",
        )

        for field in required_fields:
            with self.subTest(field=field):
                home = Path(self.tmp.name) / f"missing-{field}"
                payload = valid_event()
                payload.pop(field)

                code, stdout, stderr = self.invoke(
                    ["record", "--copilot-home", str(home), "--event-json", json.dumps(payload)]
                )

                self.assertEqual(2, code)
                self.assertEqual("", stdout)
                self.assertIn("missing_required_field", stderr)
                self.assertFalse((home / "dreamers" / "stats" / "events.jsonl").exists())

    def test_secret_like_values_are_redacted_before_writing(self):
        event = valid_event(
            event_type="session_started",
            source="hook",
            status="started",
            metrics={
                "authorization": "Bearer abc1234567890",
                "api_key": "sk-abc1234567890abc1234567890",
                "db_password": "correct horse battery staple",
                "nested": {"password": "correct horse battery staple"},
                "note": "contains github_pat_1234567890abcdef",
            }
        )

        self.stats.record_event(event, copilot_home=self.home)

        metrics = self.read_events()[0]["metrics"]
        self.assertEqual("[REDACTED]", metrics["authorization"])
        self.assertEqual("[REDACTED]", metrics["api_key"])
        self.assertEqual("[REDACTED]", metrics["db_password"])
        self.assertEqual("[REDACTED]", metrics["nested"]["password"])
        self.assertEqual("[REDACTED]", metrics["note"])

    def test_prohibited_content_fields_are_redacted_before_writing(self):
        event = valid_event(
            event_type="session_started",
            source="hook",
            status="started",
            metrics={
                "prompt": "full user prompt must not be stored",
                "response_body": "raw response must not be stored",
                "git_diff": "diff --git a/secret b/secret",
                "nested": {"tool_output": "verbose command output"},
                "prompt_count": 3,
                "token_source": "unavailable",
            }
        )

        self.stats.record_event(event, copilot_home=self.home)

        metrics = self.read_events()[0]["metrics"]
        self.assertEqual("[REDACTED]", metrics["prompt"])
        self.assertEqual("[REDACTED]", metrics["response_body"])
        self.assertEqual("[REDACTED]", metrics["git_diff"])
        self.assertEqual("[REDACTED]", metrics["nested"]["tool_output"])
        self.assertEqual(3, metrics["prompt_count"])
        self.assertEqual("unavailable", metrics["token_source"])

    def test_token_metrics_require_source_quality_and_keep_unavailable_values_null(self):
        event = valid_event(
            event_type="token_usage_recorded",
            source="summary",
            status="completed",
            metrics={
                "token_source": "unavailable",
                "input_tokens": 100,
                "output_tokens": 20,
                "total_tokens": 120,
            },
        )

        self.stats.record_event(event, copilot_home=self.home)

        metrics = self.read_events()[0]["metrics"]
        self.assertEqual("unavailable", metrics["token_source"])
        self.assertIsNone(metrics["input_tokens"])
        self.assertIsNone(metrics["output_tokens"])
        self.assertIsNone(metrics["total_tokens"])

    def test_exact_and_estimated_token_sources_preserve_numeric_values(self):
        for source in ("exact", "estimated"):
            with self.subTest(source=source):
                home = Path(self.tmp.name) / f"tokens-{source}"
                event = valid_event(
                    event_type="token_usage_recorded",
                    source="summary",
                    status="completed",
                    metrics={
                        "token_source": source,
                        "input_tokens": 100,
                        "output_tokens": 20,
                        "total_tokens": 120,
                        "ai_credits": 1.5,
                    },
                )

                self.stats.record_event(event, copilot_home=home)

                events_file = home / "dreamers" / "stats" / "events.jsonl"
                metrics = json.loads(events_file.read_text(encoding="utf-8"))["metrics"]
                self.assertEqual(source, metrics["token_source"])
                self.assertEqual(100, metrics["input_tokens"])
                self.assertEqual(20, metrics["output_tokens"])
                self.assertEqual(120, metrics["total_tokens"])
                self.assertEqual(1.5, metrics["ai_credits"])

    def test_invalid_token_source_is_rejected(self):
        event = valid_event(
            event_type="token_usage_recorded",
            source="summary",
            status="completed",
            metrics={"token_source": "guessed", "total_tokens": 10},
        )

        with self.assertRaises(self.stats.StatsValidationError) as raised:
            self.stats.record_event(event, copilot_home=self.home)

        self.assertEqual("invalid_token_source", raised.exception.category)
        self.assertFalse(self.events_file.exists())

    def test_optional_best_effort_metadata_can_be_missing(self):
        event = valid_event()

        self.stats.record_event(event, copilot_home=self.home)

        stored = self.read_events()[0]
        self.assertIsNone(stored["session_id"])
        self.assertIsNone(stored["run_id"])
        self.assertIsNone(stored["branch"])
        self.assertIsNone(stored["skill"])
        self.assertEqual("example", stored["repo_name"])

    def test_available_best_effort_metadata_is_preserved(self):
        event = valid_event(
            repo_path="/tmp/example-repo",
            session_id="sess_01",
            run_id="run_01",
            branch="stats-testing",
            skill="dreamers-full",
        )

        self.stats.record_event(event, copilot_home=self.home)

        stored = self.read_events()[0]
        self.assertEqual("sess_01", stored["session_id"])
        self.assertEqual("run_01", stored["run_id"])
        self.assertEqual("stats-testing", stored["branch"])
        self.assertEqual("dreamers-full", stored["skill"])
        self.assertEqual("example-repo", stored["repo_name"])

    def test_multiple_appends_keep_each_line_parseable_and_preserve_prior_lines(self):
        self.stats.record_event(valid_event(event_id="evt_01"), copilot_home=self.home)
        first_line = self.events_file.read_text(encoding="utf-8").splitlines()[0]

        self.stats.record_event(
            valid_event(
                event_id="evt_02",
                event_type="skill_completed",
                status="completed",
                metrics={"plan_count": 1, "final_status": "completed"},
            ),
            copilot_home=self.home,
        )

        lines = self.events_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(first_line, lines[0])
        self.assertEqual(["evt_01", "evt_02"], [json.loads(line)["event_id"] for line in lines])

    def test_successful_record_cli_is_quiet_by_default(self):
        code, stdout, stderr = self.invoke(
            ["record", "--copilot-home", str(self.home)],
            stdin_text=json.dumps(valid_event()),
        )

        self.assertEqual(0, code)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

    def test_print_event_id_success_path_outputs_one_short_line(self):
        code, stdout, stderr = self.invoke(
            ["record", "--copilot-home", str(self.home), "--print-event-id"],
            stdin_text=json.dumps(valid_event(event_id="evt_short-01")),
        )

        self.assertEqual(0, code)
        self.assertEqual("evt_short-01\n", stdout)
        self.assertEqual("", stderr)
        self.assertEqual(1, len(self.read_events()))

    def test_long_event_id_is_rejected_before_printing_or_appending(self):
        payload = valid_event(event_id=f"evt_{'x' * 200}")

        code, stdout, stderr = self.invoke(
            ["record", "--copilot-home", str(self.home), "--print-event-id"],
            stdin_text=json.dumps(payload),
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_event_id", stderr)
        self.assertFalse(self.events_file.exists())

    def test_doctor_reports_writable_stats_dir_without_creating_event_or_prompt_logs(self):
        code, stdout, stderr = self.invoke(["doctor", "--copilot-home", str(self.home), "--json"])

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertTrue(report["writable"])
        self.assertEqual(str(self.events_file), report["events_file"])
        self.assertFalse(self.events_file.exists())
        self.assertEqual([], list((self.home / "dreamers" / "stats").glob("*prompt*")))
        self.assertEqual([], list((self.home / "dreamers" / "stats").glob("*transcript*")))
        self.assertEqual([], list((self.home / "dreamers" / "stats").glob("*tool-output*")))

    def test_doctor_counts_malformed_historical_lines_without_rewriting_log(self):
        stats_dir = self.home / "dreamers" / "stats"
        stats_dir.mkdir(parents=True)
        self.events_file.write_text('{"event_id":"evt_01"}\nnot-json\n\n', encoding="utf-8")

        code, stdout, stderr = self.invoke(["doctor", "--copilot-home", str(self.home), "--json"])

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertTrue(report["writable"])
        self.assertEqual(1, report["event_count"])
        self.assertEqual(1, report["malformed_line_count"])
        self.assertEqual('{"event_id":"evt_01"}\nnot-json\n\n', self.events_file.read_text(encoding="utf-8"))

    def test_doctor_reports_unwritable_stats_dir(self):
        dreamers_path = self.home / "dreamers"
        dreamers_path.parent.mkdir(parents=True)
        dreamers_path.write_text("not a directory\n", encoding="utf-8")

        code, stdout, stderr = self.invoke(["doctor", "--copilot-home", str(self.home), "--json"])

        self.assertEqual(1, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertFalse(report["writable"])
        self.assertIsNotNone(report["error"])

    def test_hook_command_records_supported_runtime_events_with_safe_metadata(self):
        cases = (
            (
                "sessionStart",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_400_000,
                    "cwd": "/tmp/example",
                    "source": "new",
                    "initialPrompt": "do not store this prompt",
                },
                "session_started",
                {
                    "session_id": "sess_01",
                    "status": "started",
                    "metrics": {
                        "session_source": "new",
                        "initial_input_present": True,
                    },
                },
            ),
            (
                "sessionEnd",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_460_000,
                    "cwd": "/tmp/example",
                    "reason": "complete",
                },
                "session_completed",
                {
                    "session_id": "sess_01",
                    "status": "completed",
                    "metrics": {
                        "reason": "complete",
                    },
                },
            ),
            (
                "postToolUse",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_420_000,
                    "cwd": "/tmp/example",
                    "toolName": "functions.exec_command",
                    "toolArgs": {"cmd": "cat secret.txt"},
                    "toolResult": {
                        "resultType": "success",
                        "textResultForLlm": "do not store this tool output",
                    },
                },
                "tool_completed",
                {
                    "session_id": "sess_01",
                    "status": "completed",
                    "metrics": {
                        "tool_name": "functions.exec_command",
                        "result_type": "success",
                    },
                },
            ),
            (
                "postToolUseFailure",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_430_000,
                    "cwd": "/tmp/example",
                    "toolName": "functions.exec_command",
                    "toolArgs": {"cmd": "cat secret.txt"},
                    "error": "Permission denied: do not store this error body",
                },
                "tool_failed",
                {
                    "session_id": "sess_01",
                    "status": "failed",
                    "metrics": {
                        "tool_name": "functions.exec_command",
                        "error_present": True,
                    },
                },
            ),
            (
                "subagentStart",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_440_000,
                    "cwd": "/tmp/example",
                    "transcriptPath": "/tmp/transcripts/subagent.md",
                    "agentName": "probe",
                    "agentDisplayName": "Probe",
                    "agentDescription": "coverage reviewer",
                },
                "subagent_started",
                {
                    "session_id": "sess_01",
                    "status": "started",
                    "metrics": {
                        "agent_name": "probe",
                        "agent_display_name": "Probe",
                    },
                },
            ),
            (
                "subagentStop",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_450_000,
                    "cwd": "/tmp/example",
                    "transcriptPath": "/tmp/transcripts/subagent.md",
                    "agentName": "probe",
                    "agentDisplayName": "Probe",
                    "stopReason": "end_turn",
                },
                "subagent_completed",
                {
                    "session_id": "sess_01",
                    "status": "completed",
                    "metrics": {
                        "agent_name": "probe",
                        "stop_reason": "end_turn",
                    },
                },
            ),
            (
                "agentStop",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_455_000,
                    "cwd": "/tmp/example",
                    "transcriptPath": "/tmp/transcripts/session.md",
                    "stopReason": "end_turn",
                },
                "turn_completed",
                {
                    "session_id": "sess_01",
                    "status": "completed",
                    "metrics": {
                        "stop_reason": "end_turn",
                    },
                },
            ),
            (
                "errorOccurred",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_456_000,
                    "cwd": "/tmp/example",
                    "error": {
                        "message": "do not store the full stack or message",
                        "name": "ToolExecutionError",
                        "stack": "stack trace",
                    },
                    "errorContext": "tool_execution",
                    "recoverable": True,
                },
                "error_occurred",
                {
                    "session_id": "sess_01",
                    "status": "recoverable",
                    "metrics": {
                        "error_name": "ToolExecutionError",
                        "error_context": "tool_execution",
                        "recoverable": True,
                    },
                },
            ),
            (
                "preCompact",
                {
                    "sessionId": "sess_01",
                    "timestamp": 1_718_302_457_000,
                    "cwd": "/tmp/example",
                    "transcriptPath": "/tmp/transcripts/session.md",
                    "trigger": "auto",
                    "customInstructions": "do not store compaction instructions",
                },
                "compaction_started",
                {
                    "session_id": "sess_01",
                    "status": "started",
                    "metrics": {
                        "trigger": "auto",
                        "instructions_present": True,
                    },
                },
            ),
        )

        for event_name, payload, expected_type, expected in cases:
            with self.subTest(event_name=event_name):
                code, stdout, stderr = self.invoke_hook(event_name, payload)

                self.assertEqual(0, code)
                self.assertEqual("", stdout)
                self.assertEqual("", stderr)

                stored = self.read_events()[-1]
                self.assertEqual(expected_type, stored["event_type"])
                self.assertEqual("hook", stored["source"])
                self.assertEqual(expected["session_id"], stored["session_id"])
                self.assertEqual(expected["status"], stored["status"])
                for key, value in expected["metrics"].items():
                    self.assertEqual(value, stored["metrics"][key])

                raw_line = self.events_file.read_text(encoding="utf-8").splitlines()[-1]
                self.assertNotIn("do not store", raw_line)
                self.assertNotIn("secret.txt", raw_line)
                self.assertNotIn("stack trace", raw_line)

    def test_user_prompt_hook_records_metadata_without_prompt_text(self):
        code, stdout, stderr = self.invoke_hook(
            "userPromptSubmitted",
            {
                "sessionId": "sess_prompt",
                "timestamp": 1_718_302_410_000,
                "cwd": "/tmp/example",
                "prompt": "/dreamers-full investigate hooks",
            },
        )

        self.assertEqual(0, code)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

        stored = self.read_events()[0]
        self.assertEqual("prompt_submitted", stored["event_type"])
        self.assertEqual("hook", stored["source"])
        self.assertEqual("submitted", stored["status"])
        self.assertEqual(1, stored["metrics"]["prompt_count"])
        self.assertEqual(len("/dreamers-full investigate hooks"), stored["metrics"]["input_char_count"])
        self.assertTrue(stored["metrics"]["starts_with_slash"])

        raw_line = self.events_file.read_text(encoding="utf-8")
        self.assertNotIn("/dreamers-full investigate hooks", raw_line)

    def test_hook_rejects_unsupported_event_name_without_append(self):
        code, stdout, stderr = self.invoke(
            ["hook", "--copilot-home", str(self.home), "--event-name", "preToolUse"],
            stdin_text=json.dumps(
                {
                    "sessionId": "sess_invalid",
                    "timestamp": 1_718_302_400_000,
                    "cwd": "/tmp/example",
                }
            ),
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_hook_event", stderr)
        self.assertFalse(self.events_file.exists())

    def test_hook_rejects_invalid_timestamp_without_append(self):
        code, stdout, stderr = self.invoke_hook(
            "sessionStart",
            {
                "sessionId": "sess_bad_time",
                "timestamp": {"not": "valid"},
                "cwd": "/tmp/example",
            },
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_timestamp", stderr)
        self.assertFalse(self.events_file.exists())

    def test_hook_requires_object_payload(self):
        code, stdout, stderr = self.invoke(
            ["hook", "--copilot-home", str(self.home), "--event-name", "sessionStart"],
            stdin_text=json.dumps(["not", "an", "object"]),
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_event", stderr)
        self.assertFalse(self.events_file.exists())

    def test_hook_config_uses_notification_command_hooks_and_installed_paths(self):
        config = json.loads(HOOK_CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(1, config["version"])
        self.assertEqual(
            {
                "sessionStart",
                "sessionEnd",
                "userPromptSubmitted",
                "postToolUse",
                "postToolUseFailure",
                "agentStop",
                "subagentStart",
                "subagentStop",
                "errorOccurred",
                "preCompact",
            },
            set(config["hooks"]),
        )

        for event_name, entries in config["hooks"].items():
            with self.subTest(event_name=event_name):
                self.assertEqual(1, len(entries))
                entry = entries[0]
                self.assertEqual("command", entry["type"])
                self.assertNotIn("additionalContext", json.dumps(entry, sort_keys=True))
                self.assertIn("dreamers/scripts/dreamers_hook.sh", entry["bash"])
                self.assertIn("dreamers/scripts/dreamers_hook.ps1", entry["powershell"])
                self.assertIn(event_name, entry["bash"])
                self.assertIn(event_name, entry["powershell"])
                self.assertGreaterEqual(entry["timeoutSec"], 5)

        self.assertFalse(({"preToolUse"} & set(config["hooks"])))

    def test_bash_hook_wrapper_reports_failures_without_blocking(self):
        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)
        env["DREAMERS_HOOK_PYTHON"] = "/does/not/exist/python"

        completed = subprocess.run(
            ["bash", str(HOOK_BASH_WRAPPER_PATH), "sessionStart"],
            input=json.dumps(
                {
                    "sessionId": "sess_wrapper",
                    "timestamp": 1_718_302_400_000,
                    "cwd": "/tmp/example",
                    "source": "new",
                }
            ),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertIn("dreamers hook warning", completed.stderr)
        self.assertFalse(self.events_file.exists())

    def test_powershell_hook_wrapper_reports_failures_without_blocking(self):
        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)
        env["DREAMERS_HOOK_PYTHON"] = "/does/not/exist/python"

        completed = self.run_powershell_script(
            HOOK_POWERSHELL_WRAPPER_PATH,
            "sessionStart",
            input_text=json.dumps(
                {
                    "sessionId": "sess_wrapper_ps",
                    "timestamp": 1_718_302_400_000,
                    "cwd": "/tmp/example",
                    "source": "new",
                }
            ),
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertIn("dreamers hook warning", completed.stderr)
        self.assertFalse(self.events_file.exists())

    def test_install_and_remove_manage_runtime_assets_without_touching_unrelated_hooks(self):
        hook_path = self.home / "hooks" / HOOK_CONFIG_PATH.name
        bash_path = self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name
        powershell_path = self.home / "dreamers" / "scripts" / HOOK_POWERSHELL_WRAPPER_PATH.name
        writer_path = self.home / "dreamers" / "scripts" / WRITER_PATH.name
        runtime_install_state = self.home / RUNTIME_INSTALL_STATE_RELATIVE
        unrelated_hook = self.home / "hooks" / "user-hook.json"

        unrelated_hook.parent.mkdir(parents=True, exist_ok=True)
        unrelated_hook.write_text('{"version":1,"hooks":{"sessionStart":[]}}\n', encoding="utf-8")
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        self.events_file.write_text('{"event_id":"historic"}\n', encoding="utf-8")

        what_if = self.run_powershell_script(INSTALLER_PATH, "-CopilotHome", str(self.home), "-WhatIf")
        self.assertEqual(0, what_if.returncode)
        self.assertFalse(hook_path.exists())
        self.assertFalse(writer_path.exists())

        installed = self.run_powershell_script(INSTALLER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, installed.returncode)
        self.assertTrue(hook_path.exists())
        self.assertTrue(bash_path.exists())
        self.assertTrue(powershell_path.exists())
        self.assertTrue(writer_path.exists())
        self.assertTrue(runtime_install_state.exists())
        manifest_entries = runtime_install_state.read_text(encoding="utf-8").splitlines()
        self.assertIn("dreamers/scripts/dreamers_hook.sh", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_hook.ps1", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_stats.py", manifest_entries)
        self.assertIn("hooks/dreamers-stats.json", manifest_entries)
        self.assertTrue(unrelated_hook.exists())

        dry_run = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home), "-DryRun")
        self.assertEqual(0, dry_run.returncode)
        self.assertTrue(hook_path.exists())
        self.assertTrue(writer_path.exists())
        self.assertEqual('{"event_id":"historic"}\n', self.events_file.read_text(encoding="utf-8"))

        removed = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, removed.returncode)
        self.assertFalse(hook_path.exists())
        self.assertFalse(bash_path.exists())
        self.assertFalse(powershell_path.exists())
        self.assertFalse(writer_path.exists())
        self.assertFalse(runtime_install_state.exists())
        self.assertTrue(unrelated_hook.exists())
        self.assertEqual('{"event_id":"historic"}\n', self.events_file.read_text(encoding="utf-8"))

    def test_remove_preserves_preexisting_same_name_assets_that_install_skips(self):
        hook_path = self.home / "hooks" / HOOK_CONFIG_PATH.name
        user_script_path = self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name
        managed_writer_path = self.home / "dreamers" / "scripts" / WRITER_PATH.name

        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text('{"user_owned":true}\n', encoding="utf-8")
        user_script_path.parent.mkdir(parents=True, exist_ok=True)
        user_script_path.write_text("#!/usr/bin/env bash\necho user-owned\n", encoding="utf-8")

        installed = self.run_powershell_script(INSTALLER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, installed.returncode)
        self.assertEqual('{"user_owned":true}\n', hook_path.read_text(encoding="utf-8"))
        self.assertEqual("#!/usr/bin/env bash\necho user-owned\n", user_script_path.read_text(encoding="utf-8"))
        self.assertTrue(managed_writer_path.exists())

        removed = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, removed.returncode)
        self.assertTrue(hook_path.exists())
        self.assertTrue(user_script_path.exists())
        self.assertFalse(managed_writer_path.exists())

    def test_remove_deletes_prior_version_runtime_assets_listed_in_install_state(self):
        hook_path = self.home / "hooks" / HOOK_CONFIG_PATH.name
        bash_path = self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name
        unrelated_hook = self.home / "hooks" / "user-hook.json"
        runtime_install_state = self.home / RUNTIME_INSTALL_STATE_RELATIVE

        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text('{"version":1,"hooks":{"sessionStart":[{"type":"command","bash":"old"}]}}\n', encoding="utf-8")
        bash_path.parent.mkdir(parents=True, exist_ok=True)
        bash_path.write_text("#!/usr/bin/env bash\necho old-dreamers\n", encoding="utf-8")
        unrelated_hook.write_text('{"version":1,"hooks":{"sessionEnd":[]}}\n', encoding="utf-8")
        runtime_install_state.parent.mkdir(parents=True, exist_ok=True)
        runtime_install_state.write_text(
            "hooks/dreamers-stats.json\ndreamers/scripts/dreamers_hook.sh\n",
            encoding="utf-8",
        )

        removed = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home))

        self.assertEqual(0, removed.returncode)
        self.assertFalse(hook_path.exists())
        self.assertFalse(bash_path.exists())
        self.assertTrue(unrelated_hook.exists())
        self.assertFalse(runtime_install_state.exists())

    def test_checkpoint_command_records_skill_event_with_defaults_and_short_output(self):
        code, stdout, stderr = self.invoke_checkpoint(
            "skill_started",
            status="started",
            metrics={"mode": "plan-path", "plan_count": 1},
            extra_args=["--print-event-id"],
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        self.assertRegex(stdout, r"^skill_skill_started_[0-9a-f]{16}\n$")

        stored = self.read_events()[0]
        self.assertEqual("skill_started", stored["event_type"])
        self.assertEqual("skill", stored["source"])
        self.assertEqual("dreamers-full", stored["skill"])
        self.assertEqual("run_01", stored["run_id"])
        self.assertEqual("started", stored["status"])
        self.assertEqual("plan-path", stored["metrics"]["mode"])
        self.assertEqual(1, stored["metrics"]["plan_count"])
        self.assertEqual(str(REPO_ROOT), stored["repo_path"])
        self.assertTrue(stored["timestamp"].endswith("Z"))

    def test_checkpoint_rejects_unknown_rerun_trigger_without_append(self):
        code, stdout, stderr = self.invoke_checkpoint(
            "rerun_decision",
            status="skipped",
            metrics={"trigger": "freeform_reason", "decision": "skip"},
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_metric_enum", stderr)
        self.assertFalse(self.events_file.exists())

    def test_checkpoint_rejects_unknown_review_count_categories_without_append(self):
        code, stdout, stderr = self.invoke_checkpoint(
            "review_pass_completed",
            metrics={
                "review_pass_id": "review_01",
                "lane": "full",
                "reviewers": ["sentinel", "probe", "hone"],
                "artifact_paths": [".dreamers/reviews/sentinel-skill-checkpoints-20260613-000000.md"],
                "findings_by_severity": {"custom": 1},
                "findings_by_lens": {"correctness": 1},
                "blocked": False,
                "open_question_count": 0,
            },
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_metric_enum", stderr)
        self.assertFalse(self.events_file.exists())

    def test_checkpoint_rejects_gate_freeform_explanation_without_append(self):
        code, stdout, stderr = self.invoke_checkpoint(
            "gate_decided",
            status="approved",
            metrics={
                "gate_type": "user-testing",
                "decision": "approved",
                "user_explanation": "the bug came from a long prompt the stats log must not keep",
            },
        )

        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("invalid_metric_key", stderr)
        self.assertFalse(self.events_file.exists())

    def test_checkpoint_review_findings_allows_follow_up_plan_path_without_user_text(self):
        follow_up_plan = ".dreamers/plans/feature-review-rerun/plan-01-vigil-follow-up.md"

        code, stdout, stderr = self.invoke_checkpoint(
            "review_findings_applied",
            status="completed",
            metrics={
                "applied_count": 2,
                "deferred_count": 1,
                "follow_up_plan_path": follow_up_plan,
            },
        )

        self.assertEqual(0, code)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

        stored = self.read_events()[0]
        self.assertEqual("review_findings_applied", stored["event_type"])
        self.assertEqual(2, stored["metrics"]["applied_count"])
        self.assertEqual(1, stored["metrics"]["deferred_count"])
        self.assertEqual(follow_up_plan, stored["metrics"]["follow_up_plan_path"])

    def test_checkpoint_gate_decided_defer_records_follow_up_plan_without_user_text(self):
        follow_up_plan = ".dreamers/plans/feature-review-rerun/plan-01-vigil-follow-up.md"

        code, stdout, stderr = self.invoke_checkpoint(
            "gate_decided",
            status="decided",
            metrics={
                "gate_type": "major-refactor",
                "decision": "defer_follow_up_plan",
                "follow_up_plan_path": follow_up_plan,
                "follow_up_plan_count": 1,
            },
        )

        self.assertEqual(0, code)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)

        stored = self.read_events()[0]
        self.assertEqual("gate_decided", stored["event_type"])
        self.assertEqual("defer_follow_up_plan", stored["metrics"]["decision"])
        self.assertEqual(1, stored["metrics"]["follow_up_plan_count"])
        self.assertEqual(follow_up_plan, stored["metrics"]["follow_up_plan_path"])

    def test_checkpoint_rejects_freeform_halt_or_completion_metrics(self):
        cases = (
            (
                "skill_halted",
                {
                    "halt_reason_category": "user_halt",
                    "halt_detail": "user asked to stop after a long explanation",
                },
            ),
            (
                "skill_completed",
                {
                    "completion_note": "this freeform close-out note should never be stored",
                },
            ),
        )

        for event_type, metrics in cases:
            with self.subTest(event_type=event_type):
                code, stdout, stderr = self.invoke_checkpoint(event_type, metrics=metrics)

                self.assertEqual(2, code)
                self.assertEqual("", stdout)
                self.assertIn("invalid_metric_key", stderr)
                self.assertFalse(self.events_file.exists())

    def test_full_skill_checkpoint_sequence_reuses_run_id_across_boundaries(self):
        plan_path = ".dreamers/plans/feature-dreamers-stats/plan-03-skill-checkpoints.md"
        events = (
            {
                "event_type": "skill_started",
                "status": "started",
                "metrics": {"mode": "plan-path", "plan_count": 1},
            },
            {
                "event_type": "phase_started",
                "status": "started",
                "metrics": {"phase_name": "implementation-start-gate", "phase_index": 1},
            },
            {
                "event_type": "gate_presented",
                "metrics": {
                    "gate_type": "implementation-start",
                    "option_categories": ["approved_start_implementation", "revise_plan", "halt", "other"],
                },
            },
            {
                "event_type": "gate_decided",
                "metrics": {
                    "gate_type": "implementation-start",
                    "decision": "approved_start_implementation",
                },
            },
            {
                "event_type": "phase_started",
                "status": "started",
                "metrics": {
                    "phase_name": "plan-cycle",
                    "phase_index": 2,
                    "plan_path": plan_path,
                    "plan_position": 1,
                },
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "typecheck",
                    "command_label": "stats writer syntax",
                    "attempt_number": 1,
                    "result": "pass",
                },
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "stats test suite",
                    "attempt_number": 1,
                    "result": "pass",
                },
            },
            {
                "event_type": "review_pass_started",
                "metrics": {
                    "review_pass_id": "review_01",
                    "lane": "full",
                    "reviewers": ["sentinel", "probe", "hone"],
                    "is_rereview": False,
                    "plan_path": plan_path,
                },
            },
            {
                "event_type": "review_pass_completed",
                "metrics": {
                    "review_pass_id": "review_01",
                    "lane": "full",
                    "reviewers": ["sentinel", "probe", "hone"],
                    "is_rereview": False,
                    "artifact_paths": [
                        ".dreamers/reviews/sentinel-skill-checkpoints-20260613-010000.md",
                        ".dreamers/reviews/probe-skill-checkpoints-20260613-010000.md",
                        ".dreamers/reviews/hone-skill-checkpoints-20260613-010000.md",
                    ],
                    "findings_by_severity": {"critical": 0, "high": 1, "medium": 2, "low": 0},
                    "findings_by_lens": {"correctness": 1, "test-coverage": 2, "simplicity": 0},
                    "blocked": False,
                    "open_question_count": 0,
                },
            },
            {
                "event_type": "review_findings_applied",
                "metrics": {
                    "review_pass_id": "review_01",
                    "applied_count": 2,
                    "deferred_count": 1,
                    "follow_up_plan_path": ".dreamers/plans/feature-review-rerun/plan-01-follow-up.md",
                },
            },
            {
                "event_type": "rerun_decision",
                "status": "decided",
                "metrics": {
                    "trigger": "skipped_small_fix",
                    "decision": "skip",
                    "reason_category": "validation-covered-change",
                    "user_selected": False,
                    "plan_path": plan_path,
                },
            },
            {
                "event_type": "phase_started",
                "status": "started",
                "metrics": {"phase_name": "close-out", "phase_index": 3},
            },
            {
                "event_type": "cycle_completed",
                "metrics": {
                    "plan_path": plan_path,
                    "cycle_status": "completed",
                    "validation_status": "pass",
                    "review_count": 1,
                    "rereview_count": 0,
                    "bug_count": 0,
                },
            },
            {
                "event_type": "retro_written",
                "metrics": {
                    "retro_path": ".dreamers/retros/retro-04-skill-checkpoints.md",
                    "cycle_count": 1,
                },
            },
            {
                "event_type": "pr_created",
                "metrics": {
                    "pr_url": "https://github.com/example/repo/pull/42",
                    "target_branch": "stats-testing",
                },
            },
            {
                "event_type": "skill_completed",
                "metrics": {
                    "plan_count": 1,
                    "final_status": "completed",
                },
            },
        )

        stored_events = self.record_checkpoint_sequence(
            skill="dreamers-full",
            run_id="run_full_01",
            events=events,
        )

        self.assertEqual([event["event_type"] for event in events], [event["event_type"] for event in stored_events])
        self.assertEqual({"run_full_01"}, {event["run_id"] for event in stored_events})
        self.assertEqual("completed", stored_events[-1]["status"])

    def test_lite_skill_checkpoint_sequence_covers_docs_pr_and_bug_loop(self):
        plan_path = ".dreamers/plans/feature-dreamers-stats/plan-03-skill-checkpoints.md"
        events = (
            {
                "event_type": "skill_started",
                "metrics": {"mode": "plan-path", "plan_count": 1},
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "lite validation",
                    "attempt_number": 1,
                    "result": "pass",
                },
            },
            {
                "event_type": "review_pass_started",
                "metrics": {
                    "review_pass_id": "vigil_01",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "is_rereview": False,
                    "plan_path": plan_path,
                },
            },
            {
                "event_type": "review_pass_completed",
                "metrics": {
                    "review_pass_id": "vigil_01",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "is_rereview": False,
                    "artifact_paths": [".dreamers/reviews/vigil-skill-checkpoints-20260613-010000.md"],
                    "findings_by_severity": {"critical": 0, "high": 0, "medium": 1, "low": 0},
                    "findings_by_lens": {"maintainability": 1},
                    "blocked": False,
                    "open_question_count": 0,
                },
            },
            {
                "event_type": "review_findings_applied",
                "metrics": {"review_pass_id": "vigil_01", "applied_count": 1, "deferred_count": 0},
            },
            {
                "event_type": "gate_presented",
                "metrics": {
                    "gate_type": "user-testing",
                    "option_categories": ["approved", "bug_found", "other"],
                },
            },
            {
                "event_type": "gate_decided",
                "metrics": {
                    "gate_type": "user-testing",
                    "decision": "bug_found",
                    "bug_count": 1,
                },
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "lite validation retry",
                    "attempt_number": 2,
                    "result": "pass",
                },
            },
            {
                "event_type": "rerun_decision",
                "metrics": {
                    "trigger": "user_testing_bug",
                    "decision": "run_vigil",
                    "reason_category": "bug-fix-loop",
                    "user_selected": False,
                    "plan_path": plan_path,
                },
            },
            {
                "event_type": "phase_started",
                "metrics": {"phase_name": "close-out", "phase_index": 4},
            },
            {
                "event_type": "pr_created",
                "metrics": {
                    "pr_url": "https://github.com/example/repo/pull/43",
                    "target_branch": "stats-testing",
                },
            },
            {
                "event_type": "cycle_completed",
                "metrics": {
                    "plan_path": plan_path,
                    "cycle_status": "completed",
                    "validation_status": "pass",
                    "review_count": 1,
                    "rereview_count": 1,
                    "bug_count": 1,
                },
            },
            {
                "event_type": "skill_completed",
                "metrics": {
                    "docs_status": "updated",
                    "docs_updated": True,
                    "final_status": "completed",
                    "plan_count": 1,
                },
            },
        )

        stored_events = self.record_checkpoint_sequence(
            skill="dreamers-lite",
            run_id="run_lite_01",
            events=events,
        )

        self.assertEqual({"run_lite_01"}, {event["run_id"] for event in stored_events})
        self.assertEqual("close-out", stored_events[9]["metrics"]["phase_name"])
        self.assertTrue(stored_events[-1]["metrics"]["docs_updated"])
        self.assertEqual("updated", stored_events[-1]["metrics"]["docs_status"])

    def test_review_skill_checkpoint_sequence_records_review_metrics(self):
        events = (
            {
                "event_type": "skill_started",
                "metrics": {"lane": "full", "invocation_source": "dreamers-full"},
            },
            {
                "event_type": "review_pass_started",
                "metrics": {
                    "review_pass_id": "review_02",
                    "lane": "full",
                    "reviewers": ["sentinel", "probe", "hone"],
                    "invocation_source": "dreamers-full",
                    "is_rereview": False,
                },
            },
            {
                "event_type": "review_pass_completed",
                "metrics": {
                    "review_pass_id": "review_02",
                    "lane": "full",
                    "reviewers": ["sentinel", "probe", "hone"],
                    "invocation_source": "dreamers-full",
                    "is_rereview": False,
                    "artifact_paths": [
                        ".dreamers/reviews/sentinel-skill-checkpoints-20260613-020000.md",
                        ".dreamers/reviews/probe-skill-checkpoints-20260613-020000.md",
                        ".dreamers/reviews/hone-skill-checkpoints-20260613-020000.md",
                    ],
                    "findings_by_severity": {"critical": 0, "high": 1, "medium": 0, "low": 1},
                    "findings_by_lens": {"correctness": 1, "simplicity": 1},
                    "blocked": False,
                    "open_question_count": 0,
                },
            },
            {
                "event_type": "skill_completed",
                "metrics": {"review_count": 1, "final_status": "completed"},
            },
        )

        stored_events = self.record_checkpoint_sequence(
            skill="dreamers-review",
            run_id="run_review_01",
            events=events,
        )

        completed = stored_events[2]
        self.assertEqual("full", completed["metrics"]["lane"])
        self.assertEqual(1, completed["metrics"]["findings_by_severity"]["high"])
        self.assertEqual(1, completed["metrics"]["findings_by_lens"]["correctness"])
        self.assertFalse(completed["metrics"]["blocked"])

    def test_pr_resolve_skill_checkpoint_sequence_records_pr_feedback_metrics(self):
        events = (
            {
                "event_type": "skill_started",
                "metrics": {
                    "pr_number": 42,
                    "pr_url": "https://github.com/example/repo/pull/42",
                    "unresolved_thread_count": 5,
                },
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "typecheck",
                    "command_label": "pr resolve typecheck",
                    "attempt_number": 1,
                    "result": "pass",
                },
            },
            {
                "event_type": "validation_attempt",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "pr resolve tests",
                    "attempt_number": 1,
                    "result": "pass",
                },
            },
            {
                "event_type": "review_pass_started",
                "metrics": {
                    "review_pass_id": "vigil_pr_01",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "is_rereview": True,
                    "trigger": "pr_feedback",
                },
            },
            {
                "event_type": "review_pass_completed",
                "metrics": {
                    "review_pass_id": "vigil_pr_01",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "is_rereview": True,
                    "trigger": "pr_feedback",
                    "artifact_paths": [".dreamers/reviews/vigil-pr-resolve-20260613-030000.md"],
                    "findings_by_severity": {"critical": 0, "high": 0, "medium": 1, "low": 0},
                    "findings_by_lens": {"correctness": 1},
                    "blocked": False,
                    "open_question_count": 0,
                },
            },
            {
                "event_type": "review_findings_applied",
                "metrics": {
                    "review_pass_id": "vigil_pr_01",
                    "accepted_count": 2,
                    "rejected_count": 3,
                    "applied_count": 1,
                },
            },
            {
                "event_type": "gate_presented",
                "metrics": {
                    "gate_type": "push-decision",
                    "option_categories": ["push_to_pr", "hold", "other"],
                },
            },
            {
                "event_type": "gate_decided",
                "metrics": {
                    "gate_type": "push-decision",
                    "decision": "hold",
                    "user_selected": True,
                },
            },
            {
                "event_type": "skill_completed",
                "metrics": {
                    "commit_hash": "abc1234",
                    "resolved_thread_count": 2,
                    "accepted_count": 2,
                    "rejected_count": 3,
                    "push_status": "held",
                    "final_status": "resolved",
                },
            },
        )

        stored_events = self.record_checkpoint_sequence(
            skill="dreamers-pr-resolve",
            run_id="run_pr_resolve_01",
            events=events,
        )

        self.assertEqual(5, stored_events[0]["metrics"]["unresolved_thread_count"])
        self.assertEqual(2, stored_events[5]["metrics"]["accepted_count"])
        self.assertEqual("held", stored_events[-1]["metrics"]["push_status"])
        self.assertEqual(2, stored_events[-1]["metrics"]["resolved_thread_count"])

    def test_user_testing_bug_loop_records_retries_and_rerun_decision(self):
        events = (
            {
                "event_type": "gate_presented",
                "metrics": {
                    "gate_type": "user-testing",
                    "option_categories": ["approved", "bug_found", "other"],
                },
            },
            {
                "event_type": "gate_decided",
                "metrics": {
                    "gate_type": "user-testing",
                    "decision": "bug_found",
                    "bug_count": 1,
                },
            },
            {
                "event_type": "validation_attempt",
                "status": "completed",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "retry one",
                    "attempt_number": 1,
                    "result": "fail",
                    "failure_category": "test-failure",
                },
            },
            {
                "event_type": "validation_attempt",
                "status": "completed",
                "metrics": {
                    "command_kind": "test",
                    "command_label": "retry two",
                    "attempt_number": 2,
                    "result": "pass",
                },
            },
            {
                "event_type": "rerun_decision",
                "metrics": {
                    "trigger": "user_testing_bug",
                    "decision": "run_vigil",
                    "reason_category": "bug-fix-loop",
                    "user_selected": False,
                },
            },
        )

        stored_events = self.record_checkpoint_sequence(
            skill="dreamers-full",
            run_id="run_bug_loop_01",
            events=events,
        )

        self.assertEqual(1, stored_events[1]["metrics"]["bug_count"])
        self.assertEqual([1, 2], [event["metrics"]["attempt_number"] for event in stored_events[2:4]])
        self.assertEqual("user_testing_bug", stored_events[-1]["metrics"]["trigger"])

    def test_core_skill_files_record_expected_checkpoint_boundaries(self):
        expected_events = {
            "dreamers-full": (
                "skill_started",
                "phase_started",
                "gate_presented",
                "gate_decided",
                "validation_attempt",
                "review_pass_started",
                "review_pass_completed",
                "review_findings_applied",
                "rerun_decision",
                "cycle_completed",
                "retro_written",
                "pr_created",
                "skill_halted",
                "skill_completed",
            ),
            "dreamers-lite": (
                "skill_started",
                "phase_started",
                "gate_presented",
                "gate_decided",
                "validation_attempt",
                "review_pass_started",
                "review_pass_completed",
                "review_findings_applied",
                "cycle_completed",
                "pr_created",
                "skill_completed",
            ),
            "dreamers-review": (
                "skill_started",
                "review_pass_started",
                "review_pass_completed",
                "skill_halted",
                "skill_completed",
            ),
            "dreamers-pr-resolve": (
                "skill_started",
                "gate_presented",
                "gate_decided",
                "validation_attempt",
                "review_pass_started",
                "review_pass_completed",
                "review_findings_applied",
                "skill_halted",
                "skill_completed",
            ),
        }

        for skill_name, event_names in expected_events.items():
            with self.subTest(skill_name=skill_name):
                text = SKILL_PATHS[skill_name].read_text(encoding="utf-8")
                self.assertIn("Stats checkpoints", text)
                self.assertIn("<stats-checkpoints>", text)
                self.assertIn("run ID", text)
                for event_name in event_names:
                    self.assertIn(event_name, text)

    def test_core_skill_files_require_critical_metric_fragments(self):
        required_fragments = {
            "dreamers-full": ("findings_by_severity", "findings_by_lens"),
            "dreamers-lite": ("docs_status", "docs_updated"),
            "dreamers-review": ("findings_by_severity", "findings_by_lens"),
            "dreamers-pr-resolve": (
                "unresolved_thread_count",
                "accepted_count",
                "rejected_count",
                "resolved_thread_count",
                "commit_hash",
                "push_status",
            ),
        }

        for skill_name, fragments in required_fragments.items():
            with self.subTest(skill_name=skill_name):
                text = SKILL_PATHS[skill_name].read_text(encoding="utf-8")
                for fragment in fragments:
                    self.assertIn(fragment, text)

    def test_core_skill_files_keep_checkpoint_text_compact_and_hook_free(self):
        prohibited_fragments = (
            "schema_version",
            "design-dreamers-stats-tracking.md",
            "tool_requested",
            "tool_completed",
            "tool_failed",
            "prompt_submitted",
        )

        for skill_name, path in SKILL_PATHS.items():
            with self.subTest(skill_name=skill_name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("```json", text)
                self.assertNotIn("shared event envelope", text)
                for fragment in prohibited_fragments:
                    self.assertNotIn(fragment, text)

    def test_checkpoint_boilerplate_is_ref_synced_once_and_full_guidance_stays_boundary_only(self):
        self.assertTrue(STATS_CHECKPOINTS_REF_PATH.exists())

        full_text = SKILL_PATHS["dreamers-full"].read_text(encoding="utf-8")
        stats_section = full_text.split("## Stats checkpoints", 1)[1].split("## Phase 1", 1)[0]

        self.assertLessEqual(stats_section.count("- Record `"), 11)
        self.assertIn("phase_started", stats_section)
        self.assertIn("review_pass_completed", stats_section)
        self.assertNotIn("every tool", stats_section)
        self.assertNotIn("per-tool", stats_section)
        self.assertNotIn("sub-step", stats_section)
        self.assertNotIn("tool_requested", stats_section)

    def test_runs_report_groups_current_repo_runs_by_skill_status_duration_and_range(self):
        self.record_fixture_event(
            self.fixture_event(
                "skill_started",
                event_id="evt_run_full_start",
                timestamp="2026-06-13T10:00:00Z",
                run_id="run_full_01",
                skill="dreamers-full",
                metrics={"mode": "plan-path", "plan_count": 1},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "skill_completed",
                event_id="evt_run_full_end",
                timestamp="2026-06-13T10:30:00Z",
                run_id="run_full_01",
                skill="dreamers-full",
                metrics={"plan_count": 1, "final_status": "completed"},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "skill_started",
                event_id="evt_run_lite_start",
                timestamp="2026-06-13T11:00:00Z",
                run_id="run_lite_01",
                skill="dreamers-lite",
                metrics={"mode": "plan-path", "plan_count": 1},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "skill_halted",
                event_id="evt_run_lite_end",
                timestamp="2026-06-13T11:05:00Z",
                run_id="run_lite_01",
                skill="dreamers-lite",
                metrics={"halt_reason_category": "user_halt"},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "skill_completed",
                event_id="evt_other_repo_end",
                timestamp="2026-06-13T12:00:00Z",
                repo="other",
                run_id="run_other_01",
                skill="dreamers-review",
                metrics={"plan_count": 1, "final_status": "completed"},
            )
        )

        code, stdout, stderr = self.invoke(
            [
                "runs",
                "--copilot-home",
                str(self.home),
                "--repo",
                "current",
                "--since",
                "2026-06-13T00:00:00Z",
                "--until",
                "2026-06-14T00:00:00Z",
                "--json",
            ],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("runs", report["report_type"])
        self.assertEqual(2, report["run_count"])
        self.assertEqual(0, report["warning_count"])
        groups = {(group["skill"], group["status"]): group for group in report["groups"]}
        self.assertEqual(1800, groups[("dreamers-full", "completed")]["total_duration_seconds"])
        self.assertEqual(1800, groups[("dreamers-full", "completed")]["average_duration_seconds"])
        self.assertEqual(300, groups[("dreamers-lite", "halted")]["total_duration_seconds"])
        self.assertEqual("2026-06-13T10:00:00Z", groups[("dreamers-full", "completed")]["first_timestamp"])
        self.assertEqual("2026-06-13T11:05:00Z", report["range"]["last_timestamp"])

    def test_reviews_report_counts_rereviews_and_detects_artifact_mismatches(self):
        sentinel_name = "sentinel-plan-04-20260613-100000.md"
        probe_name = "probe-plan-04-20260613-100000.md"
        hone_name = "hone-plan-04-20260613-100000.md"
        vigil_name = "vigil-plan-04-20260613-103000.md"
        mismatch_name = "vigil-plan-04-20260613-104500.md"
        self.write_review_artifact(
            self.fixture_repo,
            sentinel_name,
            "\n".join(
                [
                    "Status: Findings reported - 1 items",
                    "",
                    "Findings",
                    "- [high] [correctness] .github/dreamers/scripts/dreamers_stats.py:10 - issue -> fix",
                    "",
                    "Open Questions",
                    "none",
                ]
            )
            + "\n",
        )
        self.write_review_artifact(
            self.fixture_repo,
            probe_name,
            "\n".join(
                [
                    "Approved — no findings",
                    "",
                    "Open Questions",
                    "- should this be rerun after the bug fix?",
                ]
            )
            + "\n",
        )
        self.write_review_artifact(
            self.fixture_repo,
            hone_name,
            "Approved — no findings\n\nOpen Questions\nnone\n",
        )
        self.write_review_artifact(
            self.fixture_repo,
            vigil_name,
            "Status: Findings reported - 1 items\n\nFindings\n- [low] [simplicity] README.md:10 - issue -> fix\n\nOpen Questions\nnone\n",
        )
        self.write_review_artifact(
            self.fixture_repo,
            mismatch_name,
            "Status: Findings reported - 1 items\n\nFindings\n- [medium] [test-coverage] tests/test_dreamers_stats.py:10 - issue -> fix\n\nOpen Questions\nnone\n",
        )

        self.record_fixture_event(
            self.fixture_event(
                "review_pass_completed",
                event_id="evt_review_full",
                timestamp="2026-06-13T10:15:00Z",
                run_id="run_review_01",
                skill="dreamers-full",
                metrics={
                    "review_pass_id": "review_full_01",
                    "lane": "full",
                    "reviewers": ["sentinel", "probe", "hone"],
                    "artifact_paths": [
                        f".dreamers/reviews/{sentinel_name}",
                        f".dreamers/reviews/{probe_name}",
                        f".dreamers/reviews/{hone_name}",
                    ],
                    "findings_by_severity": {"critical": 0, "high": 1, "medium": 0, "low": 0},
                    "findings_by_lens": {"correctness": 1, "security": 0, "maintainability": 0, "test-coverage": 0, "simplicity": 0},
                    "blocked": False,
                    "open_question_count": 1,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "review_pass_completed",
                event_id="evt_review_vigil",
                timestamp="2026-06-13T10:35:00Z",
                run_id="run_review_01",
                skill="dreamers-full",
                metrics={
                    "review_pass_id": "review_vigil_01",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "artifact_paths": [f".dreamers/reviews/{vigil_name}"],
                    "findings_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 1},
                    "findings_by_lens": {"correctness": 0, "security": 0, "maintainability": 0, "test-coverage": 0, "simplicity": 1},
                    "blocked": False,
                    "open_question_count": 0,
                    "is_rereview": True,
                    "trigger": "user_testing_bug",
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "review_pass_completed",
                event_id="evt_review_mismatch",
                timestamp="2026-06-13T10:45:00Z",
                run_id="run_review_01",
                skill="dreamers-full",
                metrics={
                    "review_pass_id": "review_vigil_02",
                    "lane": "vigil",
                    "reviewers": ["vigil"],
                    "artifact_paths": [f".dreamers/reviews/{mismatch_name}"],
                    "findings_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                    "findings_by_lens": {"correctness": 0, "security": 0, "maintainability": 0, "test-coverage": 0, "simplicity": 0},
                    "blocked": False,
                    "open_question_count": 0,
                    "is_rereview": True,
                    "trigger": "post_triad_fixes",
                },
            )
        )

        code, stdout, stderr = self.invoke(
            ["reviews", "--copilot-home", str(self.home), "--json"],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("reviews", report["report_type"])
        self.assertEqual(3, report["review_count"])
        self.assertEqual(1, report["initial_review_count"])
        self.assertEqual(2, report["rereview_count"])
        self.assertEqual({"full": 1, "vigil": 2}, report["lane_counts"])
        self.assertEqual({"sentinel": 1, "probe": 1, "hone": 1, "vigil": 2}, report["reviewer_counts"])
        self.assertEqual(1, report["open_question_count"])
        self.assertEqual({"critical": 0, "high": 1, "medium": 1, "low": 1}, report["findings_by_severity"])
        self.assertEqual(1, report["rereview_trigger_counts"]["user_testing_bug"])
        self.assertEqual(1, report["rereview_trigger_counts"]["post_triad_fixes"])
        self.assertEqual(1, report["artifact_summary"]["mismatch_count"])
        self.assertEqual(5, report["artifact_summary"]["parsed_count"])

    def test_validation_report_counts_attempts_failures_retries_and_final_results(self):
        self.record_fixture_event(
            self.fixture_event(
                "validation_attempt",
                event_id="evt_validation_typecheck_01",
                timestamp="2026-06-13T10:00:00Z",
                run_id="run_validate_01",
                skill="dreamers-full",
                metrics={
                    "command_kind": "typecheck",
                    "command_label": "py_compile",
                    "attempt_number": 1,
                    "result": "pass",
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "validation_attempt",
                event_id="evt_validation_test_01",
                timestamp="2026-06-13T10:01:00Z",
                run_id="run_validate_01",
                skill="dreamers-full",
                metrics={
                    "command_kind": "test",
                    "command_label": "unittest",
                    "attempt_number": 1,
                    "result": "fail",
                    "failure_category": "test-failure",
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "validation_attempt",
                event_id="evt_validation_test_02",
                timestamp="2026-06-13T10:02:00Z",
                run_id="run_validate_01",
                skill="dreamers-full",
                metrics={
                    "command_kind": "test",
                    "command_label": "unittest",
                    "attempt_number": 2,
                    "result": "pass",
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "validation_attempt",
                event_id="evt_validation_test_03",
                timestamp="2026-06-13T10:03:00Z",
                run_id="run_validate_02",
                skill="dreamers-lite",
                metrics={
                    "command_kind": "test",
                    "command_label": "unittest",
                    "attempt_number": 1,
                    "result": "fail",
                    "failure_category": "test-failure",
                },
            )
        )

        code, stdout, stderr = self.invoke(
            ["validation", "--copilot-home", str(self.home), "--json"],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("validation", report["report_type"])
        self.assertEqual(4, report["attempt_count"])
        self.assertEqual(2, report["command_kinds"]["test"]["failure_count"])
        self.assertEqual(1, report["command_kinds"]["test"]["retry_count"])
        self.assertEqual(1, report["command_kinds"]["test"]["final_pass_count"])
        self.assertEqual(1, report["command_kinds"]["test"]["final_fail_count"])
        self.assertEqual(1, report["command_kinds"]["typecheck"]["attempt_count"])

    def test_gates_report_counts_gate_types_and_selected_option_categories(self):
        self.record_fixture_event(
            self.fixture_event(
                "gate_decided",
                event_id="evt_gate_plan",
                timestamp="2026-06-13T09:00:00Z",
                run_id="run_gate_01",
                skill="dreamers-full",
                metrics={"gate_type": "plan-approval", "decision": "approved"},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "gate_decided",
                event_id="evt_gate_bug",
                timestamp="2026-06-13T09:05:00Z",
                run_id="run_gate_01",
                skill="dreamers-full",
                metrics={"gate_type": "user-testing", "decision": "bug_found", "bug_count": 1},
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "gate_decided",
                event_id="evt_gate_defer",
                timestamp="2026-06-13T09:10:00Z",
                run_id="run_gate_01",
                skill="dreamers-full",
                metrics={
                    "gate_type": "major-refactor",
                    "decision": "defer_follow_up_plan",
                    "follow_up_plan_count": 1,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "gate_decided",
                event_id="evt_gate_other_repo",
                timestamp="2026-06-13T09:15:00Z",
                repo="other",
                run_id="run_gate_other",
                skill="dreamers-lite",
                metrics={"gate_type": "user-testing", "decision": "approved"},
            )
        )

        code, stdout, stderr = self.invoke(
            ["gates", "--copilot-home", str(self.home), "--json"],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("gates", report["report_type"])
        self.assertEqual({"major-refactor": 1, "plan-approval": 1, "user-testing": 1}, report["gate_type_counts"])
        self.assertEqual({"approved": 1}, report["decision_counts"]["plan-approval"])
        self.assertEqual({"bug_found": 1}, report["decision_counts"]["user-testing"])
        self.assertEqual({"defer_follow_up_plan": 1}, report["decision_counts"]["major-refactor"])

    def test_tokens_report_separates_exact_estimated_and_unavailable_sources(self):
        self.record_fixture_event(
            self.fixture_event(
                "token_usage_recorded",
                event_id="evt_tokens_exact_01",
                timestamp="2026-06-13T10:20:00Z",
                run_id="run_tokens_01",
                session_id="sess_exact_01",
                skill="dreamers-full",
                source="summary",
                metrics={
                    "token_source": "exact",
                    "model": "gpt-5",
                    "attribution_scope": "session",
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "total_tokens": 120,
                    "ai_credits": 1.25,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "token_usage_recorded",
                event_id="evt_tokens_exact_02",
                timestamp="2026-06-13T10:25:00Z",
                run_id="run_tokens_01",
                session_id="sess_exact_01",
                skill="dreamers-full",
                source="summary",
                metrics={
                    "token_source": "exact",
                    "model": "gpt-5",
                    "attribution_scope": "session",
                    "input_tokens": 20,
                    "output_tokens": 10,
                    "total_tokens": 30,
                    "ai_credits": 0.25,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "token_usage_recorded",
                event_id="evt_tokens_estimated_01",
                timestamp="2026-06-13T10:30:00Z",
                run_id="run_tokens_02",
                session_id="sess_est_01",
                skill="dreamers-review",
                source="summary",
                metrics={
                    "token_source": "estimated",
                    "model": "gpt-5-mini",
                    "attribution_scope": "session",
                    "input_tokens": 60,
                    "output_tokens": 30,
                    "total_tokens": 90,
                    "ai_credits": 0.5,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "token_usage_recorded",
                event_id="evt_tokens_unavailable_01",
                timestamp="2026-06-13T10:35:00Z",
                run_id="run_tokens_03",
                session_id="sess_unavailable_01",
                skill="dreamers-full",
                source="summary",
                metrics={
                    "token_source": "unavailable",
                    "model": None,
                    "attribution_scope": "session",
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "ai_credits": None,
                },
            )
        )
        self.record_fixture_event(
            self.fixture_event(
                "token_usage_recorded",
                event_id="evt_tokens_other_repo",
                timestamp="2026-06-13T10:40:00Z",
                repo="other",
                run_id="run_tokens_04",
                session_id="sess_other_01",
                skill="dreamers-full",
                source="summary",
                metrics={
                    "token_source": "exact",
                    "model": "gpt-5",
                    "attribution_scope": "session",
                    "input_tokens": 999,
                    "output_tokens": 1,
                    "total_tokens": 1000,
                    "ai_credits": 2.0,
                },
            )
        )

        code, stdout, stderr = self.invoke(
            ["tokens", "--copilot-home", str(self.home), "--json"],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("tokens", report["report_type"])
        self.assertEqual("exact", report["exact"]["source_quality"])
        self.assertEqual(150, report["exact"]["totals"]["total_tokens"])
        self.assertEqual(1, report["exact"]["session_count"])
        self.assertEqual(150, report["exact"]["sessions"][0]["total_tokens"])
        self.assertEqual(150, report["exact"]["skills"]["dreamers-full"]["total_tokens"])
        self.assertEqual(150, report["exact"]["models"]["gpt-5"]["total_tokens"])
        self.assertEqual("estimated", report["estimated"]["source_quality"])
        self.assertEqual(90, report["estimated"]["totals"]["total_tokens"])
        self.assertEqual("unavailable", report["unavailable"]["source_quality"])
        self.assertEqual(1, report["unavailable"]["row_count"])

    def test_summary_report_skips_malformed_historical_lines_with_warning_count(self):
        self.record_fixture_event(
            self.fixture_event(
                "skill_completed",
                event_id="evt_summary_ok",
                timestamp="2026-06-13T10:00:00Z",
                run_id="run_summary_01",
                skill="dreamers-full",
                metrics={"plan_count": 1, "final_status": "completed"},
            )
        )
        self.write_fixture_lines(['{"not":"valid"', '{"event_id":"missing_fields"}'])

        code, stdout, stderr = self.invoke(
            ["summarize", "--copilot-home", str(self.home), "--json"],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        report = json.loads(stdout)
        self.assertEqual("summarize", report["report_type"])
        self.assertEqual(2, report["warning_count"])
        self.assertEqual(1, report["runs"]["run_count"])

    def test_summary_report_default_output_is_human_readable_and_bounded(self):
        for index in range(15):
            start = datetime(2026, 6, 13, 10, 0, tzinfo=UTC)
            start = start.replace(minute=index)
            end = start.replace(second=30)
            self.record_fixture_event(
                self.fixture_event(
                    "skill_started",
                    event_id=f"evt_summary_start_{index}",
                    timestamp=start.isoformat().replace("+00:00", "Z"),
                    run_id=f"run_summary_{index}",
                    skill="dreamers-full",
                    metrics={"mode": "plan-path", "plan_count": 1},
                )
            )
            self.record_fixture_event(
                self.fixture_event(
                    "skill_completed",
                    event_id=f"evt_summary_end_{index}",
                    timestamp=end.isoformat().replace("+00:00", "Z"),
                    run_id=f"run_summary_{index}",
                    skill="dreamers-full",
                    metrics={"plan_count": 1, "final_status": "completed"},
                )
            )

        code, stdout, stderr = self.invoke(
            ["summarize", "--copilot-home", str(self.home)],
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        self.assertIn("Dreamers stats summary", stdout)
        self.assertIn("Skill runs", stdout)
        self.assertIn("Reviews", stdout)
        self.assertIn("Validation", stdout)
        self.assertIn("Tokens", stdout)
        self.assertNotIn("evt_summary_start_0", stdout)
        self.assertLessEqual(len(stdout.splitlines()), 30)
        self.assertIsNone(re.search(r'^\s*\{', stdout, flags=re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
