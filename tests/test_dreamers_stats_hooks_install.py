import json
import os
from pathlib import Path
import shutil
import subprocess

from tests.dreamers_stats_support import (
    DreamersStatsTestCase,
    HOOK_BASH_WRAPPER_PATH,
    HOOK_CONFIG_PATH,
    HOOK_POWERSHELL_WRAPPER_PATH,
    INSTALLER_PATH,
    INSTALLED_RUNTIME_PACKAGE_RELATIVE,
    REMOVER_PATH,
    RUNTIME_INSTALL_STATE_RELATIVE,
    SHARED_RUNTIME_REPO_ROOT,
    WRITER_PATH,
    valid_event,
)


class DreamersStatsHookInstallTests(DreamersStatsTestCase):
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
        runtime_package = self.home / INSTALLED_RUNTIME_PACKAGE_RELATIVE
        runtime_install_state = self.home / RUNTIME_INSTALL_STATE_RELATIVE
        unrelated_hook = self.home / "hooks" / "user-hook.json"

        unrelated_hook.parent.mkdir(parents=True, exist_ok=True)
        unrelated_hook.write_text('{"version":1,"hooks":{"sessionStart":[]}}\n', encoding="utf-8")
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        self.events_file.write_text('{"event_id":"historic"}\n', encoding="utf-8")

        what_if = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
            "-WhatIf",
        )
        self.assertEqual(0, what_if.returncode)
        self.assertFalse(hook_path.exists())
        self.assertFalse(writer_path.exists())
        self.assertFalse(runtime_package.exists())

        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)
        self.assertTrue(hook_path.exists())
        self.assertTrue(bash_path.exists())
        self.assertTrue(powershell_path.exists())
        self.assertTrue(writer_path.exists())
        self.assertTrue((runtime_package / "__init__.py").exists())
        self.assertTrue((runtime_package / "cli.py").exists())
        self.assertTrue((runtime_package / "runtime.py").exists())
        self.assertTrue(runtime_install_state.exists())
        manifest_entries = runtime_install_state.read_text(encoding="utf-8").splitlines()
        self.assertIn("dreamers/scripts/dreamers_hook.sh", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_hook.ps1", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_stats.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/__init__.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/cli.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/runtime.py", manifest_entries)
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
        self.assertFalse(runtime_package.exists())
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

        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)
        self.assertEqual('{"user_owned":true}\n', hook_path.read_text(encoding="utf-8"))
        self.assertEqual("#!/usr/bin/env bash\necho user-owned\n", user_script_path.read_text(encoding="utf-8"))
        self.assertTrue(managed_writer_path.exists())

        removed = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, removed.returncode)
        self.assertTrue(hook_path.exists())
        self.assertTrue(user_script_path.exists())
        self.assertFalse(managed_writer_path.exists())

    def test_reinstall_without_force_preserves_manifest_ownership_for_remove(self):
        hook_path = self.home / "hooks" / HOOK_CONFIG_PATH.name
        bash_path = self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name
        powershell_path = self.home / "dreamers" / "scripts" / HOOK_POWERSHELL_WRAPPER_PATH.name
        writer_path = self.home / "dreamers" / "scripts" / WRITER_PATH.name
        runtime_package = self.home / INSTALLED_RUNTIME_PACKAGE_RELATIVE
        runtime_install_state = self.home / RUNTIME_INSTALL_STATE_RELATIVE

        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)
        self.assertTrue(runtime_install_state.exists())

        reinstalled = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, reinstalled.returncode)
        self.assertTrue(runtime_install_state.exists())

        manifest_entries = runtime_install_state.read_text(encoding="utf-8").splitlines()
        self.assertIn("dreamers/scripts/dreamers_hook.sh", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_hook.ps1", manifest_entries)
        self.assertIn("dreamers/scripts/dreamers_stats.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/__init__.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/cli.py", manifest_entries)
        self.assertIn("dreamers/runtime/dreamers_stats/runtime.py", manifest_entries)
        self.assertIn("hooks/dreamers-stats.json", manifest_entries)

        removed = self.run_powershell_script(REMOVER_PATH, "-CopilotHome", str(self.home))
        self.assertEqual(0, removed.returncode)
        self.assertFalse(hook_path.exists())
        self.assertFalse(bash_path.exists())
        self.assertFalse(powershell_path.exists())
        self.assertFalse(writer_path.exists())
        self.assertFalse(runtime_package.exists())
        self.assertFalse(runtime_install_state.exists())

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

    def test_install_fails_with_clear_error_when_shared_runtime_checkout_is_missing(self):
        missing_runtime = Path(self.tmp.name) / "missing-dreamers-mcp"

        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(missing_runtime),
        )

        self.assertNotEqual(0, installed.returncode)
        self.assertIn("dreamers-mcp", installed.stderr)
        self.assertFalse((self.home / "dreamers" / "scripts" / WRITER_PATH.name).exists())

    def test_installed_hook_wrapper_records_event_with_shared_runtime_and_safe_metadata(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)

        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)

        completed = subprocess.run(
            ["bash", str(self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name), "userPromptSubmitted"],
            input=json.dumps(
                {
                    "sessionId": "sess_installed_wrapper",
                    "timestamp": 1_718_302_400_000,
                    "cwd": str(self.fixture_repo),
                    "source": "new",
                    "prompt": "/dreamers-full investigate hooks",
                }
            ),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertEqual("", completed.stderr)
        stored = self.read_events()[0]
        self.assertEqual("prompt_submitted", stored["event_type"])
        self.assertEqual("hook", stored["source"])
        self.assertEqual(len("/dreamers-full investigate hooks"), stored["metrics"]["input_char_count"])
        raw_line = self.events_file.read_text(encoding="utf-8")
        self.assertNotIn("/dreamers-full investigate hooks", raw_line)

    def test_installed_powershell_hook_wrapper_records_event_with_shared_runtime_and_safe_metadata(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)

        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)

        completed = self.run_powershell_script(
            self.home / "dreamers" / "scripts" / HOOK_POWERSHELL_WRAPPER_PATH.name,
            "userPromptSubmitted",
            input_text=json.dumps(
                {
                    "sessionId": "sess_installed_wrapper_ps",
                    "timestamp": 1_718_302_400_000,
                    "cwd": str(self.fixture_repo),
                    "source": "new",
                    "prompt": "/dreamers-full investigate hooks",
                }
            ),
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertEqual("", completed.stderr)
        stored = self.read_events()[0]
        self.assertEqual("prompt_submitted", stored["event_type"])
        self.assertEqual("hook", stored["source"])
        self.assertEqual(len("/dreamers-full investigate hooks"), stored["metrics"]["input_char_count"])
        raw_line = self.events_file.read_text(encoding="utf-8")
        self.assertNotIn("/dreamers-full investigate hooks", raw_line)

    def test_installed_hook_wrapper_warns_when_shared_runtime_is_missing(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)
        shutil.rmtree(self.home / "dreamers" / "runtime")

        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)

        completed = subprocess.run(
            ["bash", str(self.home / "dreamers" / "scripts" / HOOK_BASH_WRAPPER_PATH.name), "sessionStart"],
            input=json.dumps(
                {
                    "sessionId": "sess_missing_runtime",
                    "timestamp": 1_718_302_400_000,
                    "cwd": str(self.fixture_repo),
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

    def test_installed_powershell_hook_wrapper_warns_when_shared_runtime_is_missing(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)
        shutil.rmtree(self.home / "dreamers" / "runtime")

        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)

        completed = self.run_powershell_script(
            self.home / "dreamers" / "scripts" / HOOK_POWERSHELL_WRAPPER_PATH.name,
            "sessionStart",
            input_text=json.dumps(
                {
                    "sessionId": "sess_missing_runtime_ps",
                    "timestamp": 1_718_302_400_000,
                    "cwd": str(self.fixture_repo),
                    "source": "new",
                }
            ),
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertIn("dreamers hook warning", completed.stderr)
        self.assertFalse(self.events_file.exists())

    def test_installed_compatibility_shim_preserves_legacy_report_command_path(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)

        self.stats.record_event(
            valid_event(
                event_id="evt_compat_summary",
                event_type="skill_completed",
                status="completed",
                repo_path=str(self.fixture_repo),
                run_id="run_compat_01",
                skill="dreamers-full",
                metrics={"plan_count": 1, "final_status": "completed"},
            ),
            copilot_home=self.home,
        )

        completed = self.run_python_script(
            self.home / "dreamers" / "scripts" / WRITER_PATH.name,
            "summarize",
            "--copilot-home",
            str(self.home),
            cwd=self.fixture_repo,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        self.assertIn("Dreamers stats summary", completed.stdout)

    def test_installed_compatibility_shim_injects_copilot_defaults_for_json_report_commands(self):
        installed = self.run_powershell_script(
            INSTALLER_PATH,
            "-CopilotHome",
            str(self.home),
            "-DreamersMcpPath",
            str(SHARED_RUNTIME_REPO_ROOT),
        )
        self.assertEqual(0, installed.returncode)

        self.stats.record_event(
            valid_event(
                event_id="evt_runs_start",
                event_type="skill_started",
                status="started",
                repo_path=str(self.fixture_repo),
                run_id="run_compat_default_01",
                skill="dreamers-full",
                metrics={"mode": "plan-path", "plan_count": 1},
            ),
            copilot_home=self.home,
        )
        self.stats.record_event(
            valid_event(
                event_id="evt_runs_end",
                event_type="skill_completed",
                status="completed",
                repo_path=str(self.fixture_repo),
                run_id="run_compat_default_01",
                skill="dreamers-full",
                metrics={"plan_count": 1, "final_status": "completed"},
            ),
            copilot_home=self.home,
        )

        env = os.environ.copy()
        env["COPILOT_HOME"] = str(self.home)

        completed = self.run_python_script(
            self.home / "dreamers" / "scripts" / WRITER_PATH.name,
            "runs",
            "--repo",
            "current",
            "--json",
            cwd=self.fixture_repo,
            env=env,
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("runs", report["report_type"])
        self.assertEqual(1, report["run_count"])
