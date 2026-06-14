from tests.dreamers_stats_support import (
    DreamersStatsTestCase,
    REPO_ROOT,
    SKILL_PATHS,
    STATS_CHECKPOINTS_REF_PATH,
)


class DreamersStatsCheckpointTests(DreamersStatsTestCase):
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
