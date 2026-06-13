import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WRITER_PATH = REPO_ROOT / ".github" / "dreamers" / "scripts" / "dreamers_stats.py"


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


if __name__ == "__main__":
    unittest.main()
