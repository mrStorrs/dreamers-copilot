from datetime import UTC, datetime
import json
import re

from tests.dreamers_stats_support import DreamersStatsTestCase


class DreamersStatsReportTests(DreamersStatsTestCase):
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
