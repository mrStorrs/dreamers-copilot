import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WRITER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_stats.py"
HOOK_CONFIG_PATH = REPO_ROOT / ".github" / "dreamers" / "hooks" / "dreamers-stats.json"
HOOK_BASH_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.sh"
HOOK_POWERSHELL_WRAPPER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_hook.ps1"
INSTALLER_PATH = REPO_ROOT / "Install-Dreamers.ps1"
REMOVER_PATH = REPO_ROOT / "Remove-Dreamers.ps1"
RUNTIME_INSTALL_STATE_RELATIVE = Path("dreamers") / "install-state" / "runtime-hooks.txt"


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

    def read_events(self):
        return [json.loads(line) for line in self.events_file.read_text(encoding="utf-8").splitlines()]

    def invoke(self, argv, stdin_text=""):
        stdout = io.StringIO()
        stderr = io.StringIO()
        stdin = io.StringIO(stdin_text)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.stats.main(argv, stdin=stdin)
        return code, stdout.getvalue(), stderr.getvalue()

    def invoke_hook(self, event_name, payload):
        return self.invoke(
            ["hook", "--copilot-home", str(self.home), "--event-name", event_name],
            stdin_text=json.dumps(payload),
        )

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
        event = valid_event(metrics={"token_source": "guessed", "total_tokens": 10})

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
            valid_event(event_id="evt_02", event_type="skill_completed", status="completed"),
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


if __name__ == "__main__":
    unittest.main()
