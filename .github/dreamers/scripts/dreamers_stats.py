#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO


SCHEMA_VERSION = 1

REQUIRED_FIELDS = (
    "schema_version",
    "event_id",
    "timestamp",
    "event_type",
    "repo_path",
    "source",
    "metrics",
)

OPTIONAL_FIELDS = (
    "session_id",
    "run_id",
    "repo_name",
    "branch",
    "skill",
    "status",
)

TOKEN_SOURCES = {"exact", "estimated", "unavailable"}
TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "ai_credits",
)

SENSITIVE_KEY_NAMES = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "credential",
    "credentials",
    "authorization",
    "auth_header",
    "bearer_token",
    "token",
}

SENSITIVE_KEY_EXCEPTIONS = {
    "token_source",
}

SAFE_CONTENT_KEYS = {
    "diff_count",
    "prompt_count",
    "prompt_counts",
    "prompt_id",
    "prompt_ids",
    "tool_output_count",
    "transcript_count",
}

PROHIBITED_CONTENT_KEYS = {
    "diff",
    "diff_text",
    "full_prompt",
    "patch",
    "prompt",
    "prompt_text",
    "request_body",
    "response_body",
    "tool_output",
    "tool_outputs",
    "tool_result",
    "tool_results",
    "transcript",
    "transcript_text",
}

SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9_]{10,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{10,}"),
    re.compile(r"sk-[A-Za-z0-9]{10,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE),
)

HookSpecValue = str | Callable[[dict[str, Any]], Any]
HookSpec = dict[str, HookSpecValue]
MetricSpec = dict[str, Any]
EventSpec = dict[str, Any]

SKILL_MODES = {"task-description", "plan-path", "manifest"}
GATE_TYPES = {
    "plan-approval",
    "implementation-start",
    "major-refactor",
    "review-rerun",
    "user-testing",
    "pre-pr",
    "pr-selection",
    "push-decision",
}
GATE_DECISIONS = {
    "approved",
    "approved_start_implementation",
    "approved_start_incremental",
    "approved_start_atomic",
    "revise",
    "revise_plan",
    "halt",
    "other",
    "apply_now",
    "defer",
    "defer_follow_up_plan",
    "continue_lite_scope",
    "run_vigil",
    "run_full_triad",
    "run_selected_lane",
    "skip",
    "skip_reviewer_rerun",
    "bug_found",
    "push_to_pr",
    "hold",
}
REVIEW_LANES = {"full", "standard", "sentinel", "probe", "hone", "vigil"}
VALIDATION_COMMAND_KINDS = {"typecheck", "test", "build", "lint", "manual"}
VALIDATION_RESULTS = {"pass", "fail", "skipped"}
VALIDATION_FAILURE_CATEGORIES = {
    "type-error",
    "test-failure",
    "timeout",
    "missing-command",
    "unknown",
}
RERUN_TRIGGERS = {
    "post_triad_fixes",
    "user_testing_bug",
    "major_change_gate",
    "user_selected_full",
    "user_selected_lane",
    "validation_risk",
    "pr_feedback",
    "optional_maintenance_review",
    "skipped_small_fix",
    "skipped_user_approved",
}
RERUN_DECISIONS = {"run_vigil", "run_full_triad", "run_selected_lane", "skip", "not_needed"}
INVOCATION_SOURCES = {"standalone", "dreamers-full", "dreamers-lite", "dreamers-pr-resolve"}
HALT_REASON_CATEGORIES = {
    "blocked_reviewer",
    "user_halt",
    "validation_failure",
    "missing_pr",
    "missing_artifact",
    "graphql_failure",
    "push_held",
    "other_safe",
}
CYCLE_STATUSES = {"completed", "halted", "blocked"}
DOCS_STATUSES = {"updated", "skipped", "not-needed"}
PUSH_STATUSES = {"pushed", "held", "not-requested"}
FINAL_STATUSES = {"completed", "resolved", "approved"}
FINDING_SEVERITIES = {"critical", "high", "medium", "low"}
FINDING_LENSES = {"correctness", "security", "maintainability", "test-coverage", "simplicity"}
FINDING_SEVERITY_ORDER = ("critical", "high", "medium", "low")
FINDING_LENS_ORDER = ("correctness", "security", "maintainability", "test-coverage", "simplicity")
ARTIFACT_SECTION_HEADINGS = {
    "findings",
    "plan alignment",
    "ac coverage",
    "full refactor findings",
    "observations",
    "open questions",
}
RELATIVE_RANGE_PATTERN = re.compile(r"^(?P<amount>\d+)(?P<unit>[dhm])$")
FINDING_LINE_PATTERN = re.compile(
    r"^- \[(?P<severity>critical|high|medium|low)\] "
    r"\[(?P<lens>correctness|security|maintainability|test-coverage|simplicity)\] "
)

HOOK_EVENT_SPECS: dict[str, HookSpec] = {
    "sessionStart": {
        "event_type": "session_started",
        "metrics": lambda payload: {
            "session_source": hook_value(payload, "source"),
            "initial_input_present": bool(hook_value(payload, "initialPrompt")),
        },
    },
    "sessionEnd": {
        "event_type": "session_completed",
        "metrics": lambda payload: {
            "reason": hook_value(payload, "reason"),
        },
    },
    "userPromptSubmitted": {
        "event_type": "prompt_submitted",
        "metrics": lambda payload: {
            "prompt_count": 1,
            "input_char_count": len(hook_value(payload, "prompt", default="")),
            "starts_with_slash": hook_value(payload, "prompt", default="").lstrip().startswith("/"),
        },
    },
    "postToolUse": {
        "event_type": "tool_completed",
        "metrics": lambda payload: {
            "tool_name": hook_value(payload, "toolName", "tool_name"),
            "result_type": hook_nested_value(
                payload,
                ("toolResult", "tool_result"),
                "resultType",
                "result_type",
                default="success",
            ),
        },
    },
    "postToolUseFailure": {
        "event_type": "tool_failed",
        "metrics": lambda payload: {
            "tool_name": hook_value(payload, "toolName", "tool_name"),
            "error_present": bool(hook_value(payload, "error")),
        },
    },
    "agentStop": {
        "event_type": "turn_completed",
        "metrics": lambda payload: {
            "stop_reason": hook_value(payload, "stopReason", "stop_reason"),
        },
    },
    "subagentStart": {
        "event_type": "subagent_started",
        "metrics": lambda payload: {
            "agent_name": hook_value(payload, "agentName", "agent_name"),
            "agent_display_name": hook_value(payload, "agentDisplayName", "agent_display_name"),
        },
    },
    "subagentStop": {
        "event_type": "subagent_completed",
        "metrics": lambda payload: {
            "agent_name": hook_value(payload, "agentName", "agent_name"),
            "agent_display_name": hook_value(payload, "agentDisplayName", "agent_display_name"),
            "stop_reason": hook_value(payload, "stopReason", "stop_reason"),
        },
    },
    "errorOccurred": {
        "event_type": "error_occurred",
        "status": lambda payload: "recoverable" if bool(hook_value(payload, "recoverable")) else "terminal",
        "metrics": lambda payload: {
            "error_name": hook_nested_value(payload, ("error",), "name", default="unknown"),
            "error_context": hook_value(payload, "errorContext", "error_context"),
            "recoverable": bool(hook_value(payload, "recoverable")),
        },
    },
    "preCompact": {
        "event_type": "compaction_started",
        "metrics": lambda payload: {
            "trigger": hook_value(payload, "trigger"),
            "instructions_present": bool(
                hook_value(payload, "customInstructions", "custom_instructions")
            ),
        },
    },
}

SKILL_EVENT_SPECS: dict[str, MetricSpec] = {
    "skill_started": {
        "enum_fields": {
            "mode": SKILL_MODES,
            "lane": REVIEW_LANES,
            "invocation_source": INVOCATION_SOURCES,
        },
        "int_fields": ("plan_count", "pr_number", "unresolved_thread_count"),
        "string_fields": ("strategy", "plan_path", "pr_url"),
    },
    "skill_completed": {
        "enum_fields": {
            "docs_status": DOCS_STATUSES,
            "push_status": PUSH_STATUSES,
            "final_status": FINAL_STATUSES,
        },
        "int_fields": (
            "accepted_count",
            "rejected_count",
            "resolved_thread_count",
            "review_count",
            "rereview_count",
            "plan_count",
        ),
        "string_fields": ("commit_hash", "plan_path", "pr_url"),
        "bool_fields": ("docs_updated",),
    },
    "skill_halted": {
        "required_fields": ("halt_reason_category",),
        "enum_fields": {
            "halt_reason_category": HALT_REASON_CATEGORIES,
            "gate_type": GATE_TYPES,
            "lane": REVIEW_LANES,
        },
        "int_fields": ("open_question_count", "unresolved_thread_count"),
        "string_fields": ("plan_path", "reviewer", "artifact_path"),
        "bool_fields": ("user_selected",),
    },
    "phase_started": {
        "required_fields": ("phase_name",),
        "string_fields": ("phase_name", "plan_path", "step_name", "strategy"),
        "int_fields": ("phase_index", "plan_position"),
    },
    "gate_presented": {
        "required_fields": ("gate_type",),
        "enum_fields": {"gate_type": GATE_TYPES},
        "string_fields": (
            "plan_path",
            "reviewer",
            "severity",
            "lens",
            "location",
            "breadth_estimate",
            "trigger_category",
            "requested_lane",
        ),
        "list_string_fields": ("option_categories",),
    },
    "gate_decided": {
        "required_fields": ("gate_type", "decision"),
        "enum_fields": {
            "gate_type": GATE_TYPES,
            "decision": GATE_DECISIONS,
        },
        "string_fields": (
            "plan_path",
            "follow_up_plan_path",
            "trigger_category",
            "requested_lane",
        ),
        "int_fields": ("bug_count", "follow_up_plan_count"),
        "bool_fields": ("user_selected",),
    },
    "validation_attempt": {
        "required_fields": ("command_kind", "command_label", "attempt_number", "result"),
        "enum_fields": {
            "command_kind": VALIDATION_COMMAND_KINDS,
            "result": VALIDATION_RESULTS,
            "failure_category": VALIDATION_FAILURE_CATEGORIES,
        },
        "string_fields": ("command_label", "scope", "plan_path"),
        "int_fields": ("attempt_number", "duration_ms"),
    },
    "review_pass_started": {
        "required_fields": ("lane", "reviewers"),
        "enum_fields": {"lane": REVIEW_LANES, "trigger": RERUN_TRIGGERS},
        "string_fields": ("review_pass_id", "plan_path", "invocation_source"),
        "bool_fields": ("is_rereview",),
        "list_string_fields": ("reviewers",),
    },
    "review_pass_completed": {
        "required_fields": ("lane", "reviewers", "artifact_paths", "blocked", "open_question_count"),
        "enum_fields": {"lane": REVIEW_LANES, "trigger": RERUN_TRIGGERS},
        "string_fields": ("review_pass_id", "plan_path", "invocation_source"),
        "bool_fields": ("is_rereview", "blocked"),
        "int_fields": ("open_question_count",),
        "list_string_fields": ("reviewers", "artifact_paths"),
        "count_object_fields": {
            "findings_by_severity": FINDING_SEVERITIES,
            "findings_by_lens": FINDING_LENSES,
        },
    },
    "review_findings_applied": {
        "string_fields": ("review_pass_id", "follow_up_plan_path", "plan_path"),
        "int_fields": (
            "applied_count",
            "deferred_count",
            "continued_count",
            "open_question_count",
            "accepted_count",
            "rejected_count",
        ),
        "bool_fields": ("rereview_needed",),
        "list_string_fields": ("follow_up_plan_paths",),
    },
    "rerun_decision": {
        "required_fields": ("trigger", "decision"),
        "enum_fields": {
            "trigger": RERUN_TRIGGERS,
            "decision": RERUN_DECISIONS,
        },
        "string_fields": ("reason_category", "requested_lane", "plan_path"),
        "bool_fields": ("user_selected",),
    },
    "cycle_completed": {
        "required_fields": ("plan_path",),
        "enum_fields": {
            "cycle_status": CYCLE_STATUSES,
            "validation_status": VALIDATION_RESULTS,
        },
        "string_fields": ("plan_path",),
        "int_fields": ("review_count", "rereview_count", "bug_count"),
    },
    "pr_created": {
        "string_fields": ("pr_url", "target_branch", "commit_hash"),
        "int_fields": ("pr_number",),
        "bool_fields": ("draft",),
    },
    "retro_written": {
        "required_fields": ("retro_path",),
        "string_fields": ("retro_path",),
        "int_fields": ("cycle_count",),
    },
}

EVENT_SPECS: dict[str, EventSpec] = {
    "session_started": {"allowed_sources": {"hook"}, "default_status": "started"},
    "session_completed": {"allowed_sources": {"hook"}, "default_status": "completed"},
    "prompt_submitted": {"allowed_sources": {"hook"}, "default_status": "submitted"},
    "turn_completed": {"allowed_sources": {"hook"}, "default_status": "completed"},
    "tool_requested": {"allowed_sources": {"hook"}, "default_status": "requested"},
    "tool_completed": {"allowed_sources": {"hook"}, "default_status": "completed"},
    "tool_failed": {"allowed_sources": {"hook"}, "default_status": "failed"},
    "subagent_started": {"allowed_sources": {"hook"}, "default_status": "started"},
    "subagent_completed": {"allowed_sources": {"hook"}, "default_status": "completed"},
    "error_occurred": {"allowed_sources": {"hook"}, "default_status": "terminal"},
    "compaction_started": {"allowed_sources": {"hook"}, "default_status": "started"},
    "skill_started": {
        "allowed_sources": {"skill"},
        "default_status": "started",
        "metric_spec": SKILL_EVENT_SPECS["skill_started"],
    },
    "skill_completed": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["skill_completed"],
    },
    "skill_halted": {
        "allowed_sources": {"skill"},
        "default_status": "halted",
        "metric_spec": SKILL_EVENT_SPECS["skill_halted"],
    },
    "phase_started": {
        "allowed_sources": {"skill"},
        "default_status": "started",
        "metric_spec": SKILL_EVENT_SPECS["phase_started"],
    },
    "gate_presented": {
        "allowed_sources": {"skill"},
        "default_status": "presented",
        "metric_spec": SKILL_EVENT_SPECS["gate_presented"],
    },
    "gate_decided": {
        "allowed_sources": {"skill"},
        "default_status": "decided",
        "metric_spec": SKILL_EVENT_SPECS["gate_decided"],
    },
    "validation_attempt": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["validation_attempt"],
    },
    "review_pass_started": {
        "allowed_sources": {"skill"},
        "default_status": "started",
        "metric_spec": SKILL_EVENT_SPECS["review_pass_started"],
    },
    "review_pass_completed": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["review_pass_completed"],
    },
    "review_findings_applied": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["review_findings_applied"],
    },
    "rerun_decision": {
        "allowed_sources": {"skill"},
        "default_status": "decided",
        "metric_spec": SKILL_EVENT_SPECS["rerun_decision"],
    },
    "cycle_completed": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["cycle_completed"],
    },
    "pr_created": {
        "allowed_sources": {"skill"},
        "default_status": "created",
        "metric_spec": SKILL_EVENT_SPECS["pr_created"],
    },
    "retro_written": {
        "allowed_sources": {"skill"},
        "default_status": "completed",
        "metric_spec": SKILL_EVENT_SPECS["retro_written"],
    },
    "token_usage_recorded": {"allowed_sources": {"summary", "skill"}, "default_status": "completed"},
}

ALLOWED_EVENT_TYPES = set(EVENT_SPECS)
ALLOWED_SOURCES = {source for spec in EVENT_SPECS.values() for source in spec["allowed_sources"]}


class StatsValidationError(ValueError):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


def default_copilot_home() -> Path:
    configured = os.environ.get("COPILOT_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".copilot"


def resolve_copilot_home(copilot_home: str | Path | None = None) -> Path:
    if copilot_home is None:
        return default_copilot_home()
    return Path(copilot_home).expanduser()


def stats_dir(copilot_home: str | Path | None = None) -> Path:
    return resolve_copilot_home(copilot_home) / "dreamers" / "stats"


def events_path(copilot_home: str | Path | None = None) -> Path:
    return stats_dir(copilot_home) / "events.jsonl"


def record_event(event: dict[str, Any], copilot_home: str | Path | None = None) -> str:
    normalized = normalize_event(event)
    destination = events_path(copilot_home)
    destination.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.write("\n")
    return normalized["event_id"]


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise StatsValidationError("invalid_event", "event must be a JSON object")

    normalized = event
    validate_event(normalized)
    normalize_token_metrics(normalized)
    fill_best_effort_metadata(normalized)
    return redact_event(normalized)


def validate_event(event: dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in event or event[field] in ("", None):
            raise StatsValidationError("missing_required_field", f"missing required field: {field}")

    if event["schema_version"] != SCHEMA_VERSION:
        raise StatsValidationError("unsupported_schema_version", "unsupported schema_version")

    _require_string(event, "event_id")
    _require_string(event, "timestamp")
    _require_string(event, "event_type")
    _require_string(event, "repo_path")
    _require_string(event, "source")
    _validate_event_id(event["event_id"])

    event_spec = EVENT_SPECS.get(event["event_type"])
    if event_spec is None:
        raise StatsValidationError("invalid_event_type", "event_type is not recognized")

    if event["source"] not in ALLOWED_SOURCES or event["source"] not in event_spec["allowed_sources"]:
        raise StatsValidationError("invalid_source", "source is not allowed for this event_type")

    if not isinstance(event["metrics"], dict):
        raise StatsValidationError("invalid_metrics", "metrics must be a JSON object")

    for field in OPTIONAL_FIELDS:
        if field in event and event[field] is not None and not isinstance(event[field], str):
            raise StatsValidationError("invalid_optional_field", f"{field} must be a string when present")

    _validate_timestamp(event["timestamp"])
    metric_spec = event_spec.get("metric_spec")
    if metric_spec is not None:
        validate_checkpoint_metrics(metric_spec, event["metrics"])


def _require_string(event: dict[str, Any], field: str) -> None:
    if not isinstance(event[field], str) or not event[field].strip():
        raise StatsValidationError("invalid_field_type", f"{field} must be a non-empty string")


def _validate_event_id(value: str) -> None:
    if len(value) > 96 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}", value):
        raise StatsValidationError("invalid_event_id", "event_id must be a compact identifier")


def _validate_timestamp(value: str) -> None:
    parse_iso_timestamp(value)


def validate_checkpoint_metrics(spec: MetricSpec, metrics: dict[str, Any]) -> None:
    allowed_keys: set[str] = set(spec.get("required_fields", ()))
    count_object_fields = spec.get("count_object_fields", {})
    for field_names in (
        spec.get("enum_fields", {}).keys(),
        spec.get("string_fields", ()),
        spec.get("int_fields", ()),
        spec.get("bool_fields", ()),
        spec.get("list_string_fields", ()),
        count_object_fields.keys(),
    ):
        allowed_keys.update(field_names)

    for field in spec.get("required_fields", ()):
        if field not in metrics or metrics[field] in ("", None):
            raise StatsValidationError("missing_metric", f"missing metric: {field}")

    for key in metrics:
        if key not in allowed_keys:
            raise StatsValidationError("invalid_metric_key", f"metric is not allowed for this event: {key}")

    for field, allowed_values in spec.get("enum_fields", {}).items():
        if field not in metrics or metrics[field] is None:
            continue
        if metrics[field] not in allowed_values:
            raise StatsValidationError("invalid_metric_enum", f"{field} is not recognized")

    for field in spec.get("string_fields", ()):
        if field in metrics and metrics[field] is not None:
            if not isinstance(metrics[field], str) or not metrics[field].strip():
                raise StatsValidationError("invalid_metric_type", f"{field} must be a non-empty string")

    for field in spec.get("int_fields", ()):
        if field in metrics:
            validate_metric_int(metrics[field], field)

    for field in spec.get("bool_fields", ()):
        if field in metrics and not isinstance(metrics[field], bool):
            raise StatsValidationError("invalid_metric_type", f"{field} must be a boolean")

    for field in spec.get("list_string_fields", ()):
        if field in metrics:
            validate_metric_string_list(metrics[field], field)

    for field, allowed_keys_for_field in count_object_fields.items():
        if field in metrics:
            validate_metric_count_object(metrics[field], field, allowed_keys_for_field)


def validate_metric_int(value: Any, field: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StatsValidationError("invalid_metric_type", f"{field} must be a non-negative integer or null")


def validate_metric_string_list(value: Any, field: str) -> None:
    if not isinstance(value, list):
        raise StatsValidationError("invalid_metric_type", f"{field} must be a list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise StatsValidationError("invalid_metric_type", f"{field} must contain non-empty strings")


def validate_metric_count_object(value: Any, field: str, allowed_keys: set[str] | None = None) -> None:
    if not isinstance(value, dict):
        raise StatsValidationError("invalid_metric_type", f"{field} must be a JSON object")
    for key, count in value.items():
        if not isinstance(key, str) or not key.strip():
            raise StatsValidationError("invalid_metric_type", f"{field} keys must be non-empty strings")
        if allowed_keys is not None and key not in allowed_keys:
            raise StatsValidationError("invalid_metric_enum", f"{field} key is not recognized")
        validate_metric_int(count, field)


def build_checkpoint_event(args: argparse.Namespace) -> dict[str, Any]:
    event_type = args.event_type
    event_spec = EVENT_SPECS.get(event_type)
    if event_spec is None or "skill" not in event_spec["allowed_sources"]:
        raise StatsValidationError("invalid_checkpoint_event", "checkpoint event is not supported")

    metrics = load_metrics_json(args.metrics_json)
    event = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": resolve_checkpoint_timestamp(args.timestamp),
        "event_type": event_type,
        "repo_path": args.repo_path or os.getcwd(),
        "session_id": args.session_id,
        "run_id": args.run_id,
        "branch": args.branch,
        "skill": args.skill,
        "source": "skill",
        "status": args.status or default_status_for_event(event_type),
        "metrics": metrics,
    }
    event["event_id"] = checkpoint_event_id(event)
    return event


def load_metrics_json(raw: str | None) -> dict[str, Any]:
    if raw in (None, ""):
        return {}
    metrics = json.loads(raw)
    if not isinstance(metrics, dict):
        raise StatsValidationError("invalid_metrics", "metrics must be a JSON object")
    return metrics


def resolve_checkpoint_timestamp(value: str | None) -> str:
    if value is None:
        return utc_now_iso()
    parsed = parse_iso_timestamp(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def checkpoint_event_id(event: dict[str, Any]) -> str:
    fingerprint = json.dumps(
        {
            "timestamp": event["timestamp"],
            "run_id": event["run_id"],
            "repo_path": event["repo_path"],
            "skill": event["skill"],
            "event_type": event["event_type"],
            "status": event["status"],
            "metrics": event["metrics"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]
    return f"skill_{event['event_type']}_{digest}"


def build_hook_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    spec = HOOK_EVENT_SPECS.get(event_name)
    if spec is None:
        raise StatsValidationError("invalid_hook_event", "hook event is not supported")
    event_type = resolve_hook_spec_value(spec["event_type"], payload)
    event = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": hook_timestamp(payload),
        "event_type": event_type,
        "repo_path": hook_value(payload, "cwd"),
        "session_id": hook_value(payload, "sessionId", "session_id"),
        "source": "hook",
        "status": resolve_hook_status(spec, payload, event_type),
        "metrics": resolve_hook_spec_value(spec["metrics"], payload),
    }
    event["event_id"] = hook_event_id(event_name, event)
    return event


def hook_event_id(event_name: str, event: dict[str, Any]) -> str:
    fingerprint = json.dumps(
        {
            "event_name": event_name,
            "timestamp": event["timestamp"],
            "session_id": event.get("session_id"),
            "repo_path": event["repo_path"],
            "event_type": event["event_type"],
            "metrics": event["metrics"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]
    return f"hook_{event['event_type']}_{digest}"


def hook_value(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def hook_nested_value(
    payload: dict[str, Any],
    parent_keys: tuple[str, ...],
    *child_keys: str,
    default: Any = None,
) -> Any:
    nested = hook_value(payload, *parent_keys, default={})
    if not isinstance(nested, dict):
        return default
    return hook_value(nested, *child_keys, default=default)


def resolve_hook_spec_value(value: HookSpecValue, payload: dict[str, Any]) -> Any:
    if callable(value):
        return value(payload)
    return value


def resolve_hook_status(spec: HookSpec, payload: dict[str, Any], event_type: str) -> str:
    status = spec.get("status", default_status_for_event(event_type))
    return resolve_hook_spec_value(status, payload)


def default_status_for_event(event_type: str) -> str:
    spec = EVENT_SPECS.get(event_type)
    if spec is None:
        raise StatsValidationError("invalid_event_type", "event_type is not recognized")
    return spec["default_status"]


def hook_timestamp(payload: dict[str, Any]) -> str:
    value = hook_value(payload, "timestamp")
    if isinstance(value, int | float):
        return datetime.fromtimestamp(value / 1000, tz=UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, str):
        parsed = parse_iso_timestamp(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
    raise StatsValidationError("invalid_timestamp", "timestamp must be a number or ISO 8601 string")


def parse_iso_timestamp(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise StatsValidationError("invalid_timestamp", "timestamp must be ISO 8601") from exc


def normalize_token_metrics(event: dict[str, Any]) -> None:
    metrics = event["metrics"]
    has_token_metrics = event["event_type"] == "token_usage_recorded"
    has_token_metrics = has_token_metrics or "token_source" in metrics
    has_token_metrics = has_token_metrics or any(field in metrics for field in TOKEN_FIELDS)
    if not has_token_metrics:
        return

    source = metrics.get("token_source", "unavailable")
    if source not in TOKEN_SOURCES:
        raise StatsValidationError("invalid_token_source", "token_source must be exact, estimated, or unavailable")

    metrics["token_source"] = source
    for field in TOKEN_FIELDS:
        if field not in metrics:
            continue
        if source == "unavailable":
            metrics[field] = None
            continue
        _validate_metric_number(metrics[field], field)

    if event["event_type"] == "token_usage_recorded":
        for field in TOKEN_FIELDS:
            metrics.setdefault(field, None)


def _validate_metric_number(value: Any, field: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise StatsValidationError("invalid_token_value", f"{field} must be a non-negative number or null")
    if value < 0:
        raise StatsValidationError("invalid_token_value", f"{field} must be non-negative")
    if field.endswith("_tokens") and not isinstance(value, int):
        raise StatsValidationError("invalid_token_value", f"{field} must be an integer or null")


def fill_best_effort_metadata(event: dict[str, Any]) -> None:
    for field in OPTIONAL_FIELDS:
        event.setdefault(field, None)

    if not event["repo_name"]:
        event["repo_name"] = derive_repo_name(event["repo_path"])


def derive_repo_name(repo_path: str) -> str | None:
    name = Path(repo_path).expanduser().name
    return name or None


def redact_event(value: Any, key: str | None = None) -> Any:
    if is_sensitive_key(key) or is_prohibited_content_key(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {item_key: redact_event(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [redact_event(item) for item in value]
    if isinstance(value, str) and contains_sensitive_value(value):
        return "[REDACTED]"
    return value


def is_sensitive_key(key: str | None) -> bool:
    normalized = normalize_key(key)
    if normalized is None or normalized in SENSITIVE_KEY_EXCEPTIONS:
        return False
    if normalized in SENSITIVE_KEY_NAMES:
        return True
    if any(token in SENSITIVE_KEY_NAMES for token in key_tokens(normalized)):
        return True
    return normalized.endswith("_secret") or normalized.endswith("_token")


def is_prohibited_content_key(key: str | None) -> bool:
    normalized = normalize_key(key)
    if normalized is None or normalized in SAFE_CONTENT_KEYS:
        return False
    tokens = set(key_tokens(normalized))
    if normalized in PROHIBITED_CONTENT_KEYS:
        return True
    if tokens.intersection({"diff", "prompt", "transcript"}):
        return True
    if {"request", "body"}.issubset(tokens):
        return True
    if {"response", "body"}.issubset(tokens):
        return True
    return "tool" in tokens and bool(tokens.intersection({"output", "outputs", "result", "results"}))


def normalize_key(key: str | None) -> str | None:
    if key is None:
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    return normalized or None


def key_tokens(normalized_key: str) -> list[str]:
    return [token for token in normalized_key.split("_") if token]


def contains_sensitive_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in SENSITIVE_VALUE_PATTERNS)


def doctor(copilot_home: str | Path | None = None) -> dict[str, Any]:
    directory = stats_dir(copilot_home)
    event_log = events_path(copilot_home)
    report: dict[str, Any] = {
        "stats_dir": str(directory),
        "events_file": str(event_log),
        "writable": False,
        "event_count": 0,
        "malformed_line_count": 0,
        "error": None,
    }

    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / ".doctor-write-test"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        report["writable"] = True
    except OSError as exc:
        report["error"] = exc.__class__.__name__

    if event_log.exists():
        for line in event_log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                report["malformed_line_count"] += 1
                continue
            report["event_count"] += 1

    return report


def load_report_events(copilot_home: str | Path | None = None) -> tuple[list[dict[str, Any]], int]:
    event_log = events_path(copilot_home)
    if not event_log.exists():
        return [], 0

    events: list[dict[str, Any]] = []
    warning_count = 0
    for line in event_log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            warning_count += 1
            continue
        normalized = normalize_report_event(payload)
        if normalized is None:
            warning_count += 1
            continue
        events.append(normalized)
    return events, warning_count


def normalize_report_event(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    if not isinstance(payload.get("metrics"), dict):
        return None
    if not isinstance(payload.get("repo_path"), str) or not payload["repo_path"].strip():
        return None
    if not isinstance(payload.get("event_type"), str) or not payload["event_type"].strip():
        return None
    if not isinstance(payload.get("timestamp"), str) or not payload["timestamp"].strip():
        return None

    try:
        parsed_timestamp = parse_iso_timestamp(payload["timestamp"])
    except StatsValidationError:
        return None

    if parsed_timestamp.tzinfo is None:
        parsed_timestamp = parsed_timestamp.replace(tzinfo=UTC)
    normalized = dict(payload)
    normalized["metrics"] = dict(payload["metrics"])
    normalized["_parsed_timestamp"] = parsed_timestamp.astimezone(UTC)
    return normalized


def build_report_filters(args: argparse.Namespace) -> dict[str, Any]:
    since = parse_report_boundary(args.since, is_end=False) if args.since else None
    until = parse_report_boundary(args.until, is_end=True) if args.until else None
    if since is not None and until is not None and since > until:
        raise StatsValidationError("invalid_date_range", "--since must be earlier than --until")

    current_repo = detect_repo_root(os.getcwd()) if args.repo == "current" else None
    return {
        "repo": args.repo,
        "skill": args.skill,
        "since": datetime_to_iso(since),
        "until": datetime_to_iso(until),
        "current_repo": str(current_repo) if current_repo is not None else None,
        "_since": since,
        "_until": until,
        "_current_repo": current_repo,
    }


def parse_report_boundary(value: str, *, is_end: bool) -> datetime:
    match = RELATIVE_RANGE_PATTERN.fullmatch(value)
    if match is not None:
        amount = int(match.group("amount"))
        unit = match.group("unit")
        delta = {
            "d": timedelta(days=amount),
            "h": timedelta(hours=amount),
            "m": timedelta(minutes=amount),
        }[unit]
        return datetime.now(UTC) - delta

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        parsed = datetime.fromisoformat(value).replace(tzinfo=UTC)
        if is_end:
            return parsed + timedelta(days=1) - timedelta(microseconds=1)
        return parsed

    parsed = parse_iso_timestamp(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def detect_repo_root(start: str | Path) -> Path:
    current = Path(start).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def filter_report_events(events: Iterable[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    since = filters["_since"]
    until = filters["_until"]
    current_repo = filters["_current_repo"]
    skill = filters["skill"]
    repo_mode = filters["repo"]

    for event in events:
        if repo_mode == "current" and current_repo is not None and not event_matches_repo(event, current_repo):
            continue
        if skill is not None and event.get("skill") != skill:
            continue
        timestamp = event["_parsed_timestamp"]
        if since is not None and timestamp < since:
            continue
        if until is not None and timestamp > until:
            continue
        filtered.append(event)
    return filtered


def event_matches_repo(event: dict[str, Any], current_repo: Path) -> bool:
    event_path = Path(event["repo_path"]).expanduser().resolve(strict=False)
    return event_path == current_repo or current_repo in event_path.parents or event_path in current_repo.parents


def datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def event_range(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    timestamps = [event["_parsed_timestamp"] for event in events]
    if not timestamps:
        return {"first_timestamp": None, "last_timestamp": None}
    return {
        "first_timestamp": datetime_to_iso(min(timestamps)),
        "last_timestamp": datetime_to_iso(max(timestamps)),
    }


def empty_count_dict(keys: Iterable[str]) -> dict[str, int]:
    return {key: 0 for key in keys}


def merge_count_dicts(target: dict[str, int], source: dict[str, Any], keys: Iterable[str]) -> None:
    for key in keys:
        target[key] += int(source.get(key, 0) or 0)


def build_runs_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    runs: dict[tuple[str, str, str], dict[str, Any]] = {}
    for event in events:
        run_id = event.get("run_id")
        skill = event.get("skill")
        if not run_id or not skill:
            continue
        run_key = (run_id, event["repo_path"], skill)

        run = runs.setdefault(
            run_key,
            {
                "run_id": run_id,
                "repo_path": event["repo_path"],
                "skill": skill,
                "status": "in_progress",
                "first_timestamp": event["_parsed_timestamp"],
                "last_timestamp": event["_parsed_timestamp"],
                "start_timestamp": None,
                "end_timestamp": None,
            },
        )
        run["first_timestamp"] = min(run["first_timestamp"], event["_parsed_timestamp"])
        run["last_timestamp"] = max(run["last_timestamp"], event["_parsed_timestamp"])
        if event["event_type"] == "skill_started":
            run["start_timestamp"] = event["_parsed_timestamp"]
        elif event["event_type"] == "skill_completed":
            run["end_timestamp"] = event["_parsed_timestamp"]
            run["status"] = event["metrics"].get("final_status") or event.get("status") or "completed"
        elif event["event_type"] == "skill_halted":
            run["end_timestamp"] = event["_parsed_timestamp"]
            run["status"] = event.get("status") or "halted"

    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for run in runs.values():
        start_timestamp = run["start_timestamp"] or run["first_timestamp"]
        end_timestamp = run["end_timestamp"] or run["last_timestamp"]
        duration_seconds = int((end_timestamp - start_timestamp).total_seconds())
        duration_seconds = max(duration_seconds, 0)
        key = (run["skill"], run["status"])
        group = grouped.setdefault(
            key,
            {
                "skill": run["skill"],
                "status": run["status"],
                "run_count": 0,
                "total_duration_seconds": 0,
                "first_timestamp": start_timestamp,
                "last_timestamp": end_timestamp,
            },
        )
        group["run_count"] += 1
        group["total_duration_seconds"] += duration_seconds
        group["first_timestamp"] = min(group["first_timestamp"], start_timestamp)
        group["last_timestamp"] = max(group["last_timestamp"], end_timestamp)

    groups = []
    for key in sorted(grouped):
        group = grouped[key]
        average_duration = 0
        if group["run_count"]:
            average_duration = int(group["total_duration_seconds"] / group["run_count"])
        groups.append(
            {
                "skill": group["skill"],
                "status": group["status"],
                "run_count": group["run_count"],
                "total_duration_seconds": group["total_duration_seconds"],
                "average_duration_seconds": average_duration,
                "first_timestamp": datetime_to_iso(group["first_timestamp"]),
                "last_timestamp": datetime_to_iso(group["last_timestamp"]),
            }
        )

    run_range = {"first_timestamp": None, "last_timestamp": None}
    if runs:
        run_range = {
            "first_timestamp": datetime_to_iso(min(run["first_timestamp"] for run in runs.values())),
            "last_timestamp": datetime_to_iso(max(run["last_timestamp"] for run in runs.values())),
        }

    return {
        "report_type": "runs",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "run_count": len(runs),
        "range": run_range,
        "groups": groups,
    }


def build_reviews_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    review_events = [event for event in events if event["event_type"] == "review_pass_completed"]
    lane_counts: Counter[str] = Counter()
    reviewer_counts: Counter[str] = Counter()
    trigger_counts: Counter[str] = Counter()
    findings_by_severity = empty_count_dict(FINDING_SEVERITY_ORDER)
    findings_by_lens = empty_count_dict(FINDING_LENS_ORDER)
    initial_review_count = 0
    rereview_count = 0
    blocked_count = 0
    open_question_count = 0
    artifact_cache: dict[str, dict[str, Any]] = {}
    parsed_artifact_paths: set[str] = set()
    missing_artifact_paths: set[str] = set()
    mismatches: list[dict[str, Any]] = []

    for event in review_events:
        metrics = event["metrics"]
        lane = metrics.get("lane")
        if isinstance(lane, str) and lane:
            lane_counts[lane] += 1
        reviewers = metrics.get("reviewers", [])
        if isinstance(reviewers, list):
            reviewer_counts.update([reviewer for reviewer in reviewers if isinstance(reviewer, str)])

        is_rereview = bool(metrics.get("is_rereview"))
        if is_rereview:
            rereview_count += 1
            trigger = metrics.get("trigger")
            if isinstance(trigger, str) and trigger:
                trigger_counts[trigger] += 1
        else:
            initial_review_count += 1

        event_artifacts = resolve_review_artifacts(event)
        event_missing = False
        parsed_summary = {
            "blocked": False,
            "open_question_count": 0,
            "findings_by_severity": empty_count_dict(FINDING_SEVERITY_ORDER),
            "findings_by_lens": empty_count_dict(FINDING_LENS_ORDER),
        }
        for artifact_path in event_artifacts:
            summary = artifact_cache.get(str(artifact_path))
            if summary is None:
                summary = parse_review_artifact(artifact_path)
                artifact_cache[str(artifact_path)] = summary
            if not summary["found"]:
                event_missing = True
                missing_artifact_paths.add(str(artifact_path))
                continue
            parsed_artifact_paths.add(str(artifact_path))
            if summary["blocked"]:
                parsed_summary["blocked"] = True
            parsed_summary["open_question_count"] += summary["open_question_count"]
            merge_count_dicts(
                parsed_summary["findings_by_severity"],
                summary["findings_by_severity"],
                FINDING_SEVERITY_ORDER,
            )
            merge_count_dicts(
                parsed_summary["findings_by_lens"],
                summary["findings_by_lens"],
                FINDING_LENS_ORDER,
            )

        count_source = parsed_summary if event_artifacts and not event_missing else metrics
        if bool(count_source.get("blocked")):
            blocked_count += 1
        open_question_count += int(count_source.get("open_question_count", 0) or 0)
        merge_count_dicts(findings_by_severity, count_source.get("findings_by_severity", {}), FINDING_SEVERITY_ORDER)
        merge_count_dicts(findings_by_lens, count_source.get("findings_by_lens", {}), FINDING_LENS_ORDER)

        if event_artifacts and not event_missing and review_event_has_artifact_mismatch(metrics, parsed_summary):
            mismatches.append(
                {
                    "review_pass_id": metrics.get("review_pass_id"),
                    "artifact_paths": [str(path) for path in event_artifacts],
                }
            )

    return {
        "report_type": "reviews",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "review_count": len(review_events),
        "initial_review_count": initial_review_count,
        "rereview_count": rereview_count,
        "lane_counts": dict(lane_counts),
        "reviewer_counts": dict(reviewer_counts),
        "blocked_count": blocked_count,
        "open_question_count": open_question_count,
        "findings_by_severity": findings_by_severity,
        "findings_by_lens": findings_by_lens,
        "rereview_trigger_counts": dict(trigger_counts),
        "artifact_summary": {
            "parsed_count": len(parsed_artifact_paths),
            "missing_count": len(missing_artifact_paths),
            "mismatch_count": len(mismatches),
            "mismatches": mismatches,
        },
    }


def resolve_review_artifacts(event: dict[str, Any]) -> list[Path]:
    repo_root = Path(event["repo_path"]).expanduser()
    seen: set[str] = set()
    resolved: list[Path] = []
    for artifact in event["metrics"].get("artifact_paths", []):
        if not isinstance(artifact, str) or not artifact.strip():
            continue
        candidate = Path(artifact)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        resolved.append(candidate)
    return resolved


def parse_review_artifact(path: Path) -> dict[str, Any]:
    summary = {
        "found": False,
        "blocked": False,
        "open_question_count": 0,
        "findings_by_severity": empty_count_dict(FINDING_SEVERITY_ORDER),
        "findings_by_lens": empty_count_dict(FINDING_LENS_ORDER),
    }
    if not path.exists():
        return summary

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return summary
    summary["found"] = True
    status_line = next((line.strip() for line in lines if line.strip()), "")
    normalized_status = status_line
    if normalized_status.lower().startswith("status:"):
        normalized_status = normalized_status.split(":", 1)[1].strip()
    summary["blocked"] = normalized_status.startswith("Blocked")

    sections = split_artifact_sections(lines)
    for line in sections.get("findings", []):
        match = FINDING_LINE_PATTERN.match(line.strip())
        if match is None:
            continue
        summary["findings_by_severity"][match.group("severity")] += 1
        summary["findings_by_lens"][match.group("lens")] += 1

    open_question_lines = [line.strip() for line in sections.get("open questions", []) if line.strip()]
    if open_question_lines and not (len(open_question_lines) == 1 and open_question_lines[0].lower() == "none"):
        summary["open_question_count"] = sum(
            1
            for line in open_question_lines
            if line.startswith("- ")
            or re.match(r"^\d+\.\s+", line) is not None
            or line.lower() != "none"
        )

    return summary


def split_artifact_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in lines:
        heading = line.strip().lower()
        if heading in ARTIFACT_SECTION_HEADINGS:
            current_section = heading
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return sections


def review_event_has_artifact_mismatch(metrics: dict[str, Any], parsed: dict[str, Any]) -> bool:
    stored_severity = empty_count_dict(FINDING_SEVERITY_ORDER)
    stored_lens = empty_count_dict(FINDING_LENS_ORDER)
    merge_count_dicts(stored_severity, metrics.get("findings_by_severity", {}), FINDING_SEVERITY_ORDER)
    merge_count_dicts(stored_lens, metrics.get("findings_by_lens", {}), FINDING_LENS_ORDER)
    if stored_severity != parsed["findings_by_severity"]:
        return True
    if stored_lens != parsed["findings_by_lens"]:
        return True
    if bool(metrics.get("blocked")) != parsed["blocked"]:
        return True
    return int(metrics.get("open_question_count", 0) or 0) != parsed["open_question_count"]


def build_validation_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    validation_events = [event for event in events if event["event_type"] == "validation_attempt"]
    command_kinds: dict[str, dict[str, int]] = {}
    final_attempts: dict[tuple[Any, ...], dict[str, Any]] = {}

    for event in validation_events:
        metrics = event["metrics"]
        command_kind = metrics.get("command_kind")
        command_label = metrics.get("command_label")
        if not isinstance(command_kind, str) or not isinstance(command_label, str):
            continue

        stats = command_kinds.setdefault(
            command_kind,
            {
                "attempt_count": 0,
                "failure_count": 0,
                "retry_count": 0,
                "final_pass_count": 0,
                "final_fail_count": 0,
            },
        )
        stats["attempt_count"] += 1
        if metrics.get("result") == "fail":
            stats["failure_count"] += 1
        if int(metrics.get("attempt_number", 0) or 0) > 1:
            stats["retry_count"] += 1

        key = (
            event.get("run_id"),
            event.get("repo_path"),
            command_kind,
            command_label,
            metrics.get("scope"),
            metrics.get("plan_path"),
        )
        previous = final_attempts.get(key)
        if previous is None or should_replace_validation_attempt(previous, event):
            final_attempts[key] = event

    for event in final_attempts.values():
        command_kind = event["metrics"]["command_kind"]
        result = event["metrics"].get("result")
        if result == "pass":
            command_kinds[command_kind]["final_pass_count"] += 1
        elif result == "fail":
            command_kinds[command_kind]["final_fail_count"] += 1

    return {
        "report_type": "validation",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "attempt_count": len(validation_events),
        "command_kinds": command_kinds,
    }


def should_replace_validation_attempt(previous: dict[str, Any], candidate: dict[str, Any]) -> bool:
    previous_attempt = int(previous["metrics"].get("attempt_number", 0) or 0)
    candidate_attempt = int(candidate["metrics"].get("attempt_number", 0) or 0)
    if candidate_attempt != previous_attempt:
        return candidate_attempt > previous_attempt
    return candidate["_parsed_timestamp"] > previous["_parsed_timestamp"]


def build_gates_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    gate_events = [event for event in events if event["event_type"] == "gate_decided"]
    gate_type_counts: Counter[str] = Counter()
    decision_counts: dict[str, Counter[str]] = {}

    for event in gate_events:
        gate_type = event["metrics"].get("gate_type")
        decision = event["metrics"].get("decision")
        if not isinstance(gate_type, str) or not gate_type:
            continue
        gate_type_counts[gate_type] += 1
        if isinstance(decision, str) and decision:
            decision_counts.setdefault(gate_type, Counter())[decision] += 1

    return {
        "report_type": "gates",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "gate_count": len(gate_events),
        "gate_type_counts": dict(gate_type_counts),
        "decision_counts": {gate_type: dict(counter) for gate_type, counter in decision_counts.items()},
    }


def build_tokens_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    token_events = [event for event in events if event["event_type"] == "token_usage_recorded"]
    by_source = {
        "exact": [event for event in token_events if event["metrics"].get("token_source") == "exact"],
        "estimated": [event for event in token_events if event["metrics"].get("token_source") == "estimated"],
        "unavailable": [event for event in token_events if event["metrics"].get("token_source") == "unavailable"],
    }

    return {
        "report_type": "tokens",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "exact": summarize_token_source("exact", by_source["exact"]),
        "estimated": summarize_token_source("estimated", by_source["estimated"]),
        "unavailable": summarize_token_source("unavailable", by_source["unavailable"]),
    }


def summarize_token_source(source_quality: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    totals = empty_token_totals()
    skills: dict[str, dict[str, Any]] = {}
    models: dict[str, dict[str, Any]] = {}
    sessions: dict[tuple[str | None, str | None, str | None], dict[str, Any]] = {}

    for event in events:
        metrics = event["metrics"]
        merge_token_totals(totals, metrics)

        skill = event.get("skill")
        model = metrics.get("model")
        session_id = event.get("session_id")
        session_key = (session_id, skill, model if isinstance(model, str) else None)
        session_summary = sessions.setdefault(
            session_key,
            {
                "session_id": session_id,
                "skill": skill,
                "model": model if isinstance(model, str) else None,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "cache_read_tokens": None,
                "cache_write_tokens": None,
                "ai_credits": None,
            },
        )
        merge_token_totals(session_summary, metrics)

        if isinstance(skill, str) and skill:
            merge_named_token_totals(skills, skill, metrics)
        if isinstance(model, str) and model:
            merge_named_token_totals(models, model, metrics)

    return {
        "source_quality": source_quality,
        "row_count": len(events),
        "session_count": len({event.get("session_id") for event in events if event.get("session_id") is not None}),
        "totals": totals,
        "sessions": sorted(sessions.values(), key=lambda item: (item["session_id"] or "", item["skill"] or "", item["model"] or "")),
        "skills": skills,
        "models": models,
    }


def empty_token_totals() -> dict[str, int | float | None]:
    return {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cache_read_tokens": None,
        "cache_write_tokens": None,
        "ai_credits": None,
    }


def merge_token_totals(target: dict[str, Any], metrics: dict[str, Any]) -> None:
    for field in TOKEN_FIELDS:
        value = metrics.get(field)
        if value is None:
            continue
        if target[field] is None:
            target[field] = value
        else:
            target[field] += value


def merge_named_token_totals(target: dict[str, dict[str, Any]], key: str, metrics: dict[str, Any]) -> None:
    summary = target.setdefault(key, empty_token_totals())
    merge_token_totals(summary, metrics)


def build_workflow_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    cycle_status_counts: Counter[str] = Counter()
    for event in events:
        if event["event_type"] == "cycle_completed":
            cycle_status = event["metrics"].get("cycle_status")
            if isinstance(cycle_status, str) and cycle_status:
                cycle_status_counts[cycle_status] += 1

    return {
        "cycle_status_counts": dict(cycle_status_counts),
        "pr_count": sum(1 for event in events if event["event_type"] == "pr_created"),
        "retro_count": sum(1 for event in events if event["event_type"] == "retro_written"),
    }


def build_summary_report(
    events: list[dict[str, Any]],
    filters: dict[str, Any],
    *,
    warning_count: int = 0,
) -> dict[str, Any]:
    return {
        "report_type": "summarize",
        "filters": report_filters_public(filters),
        "warning_count": warning_count,
        "runs": build_runs_report(events, filters),
        "reviews": build_reviews_report(events, filters),
        "validation": build_validation_report(events, filters),
        "gates": build_gates_report(events, filters),
        "workflow_outputs": build_workflow_report(events),
        "tokens": build_tokens_report(events, filters),
    }


def report_filters_public(filters: dict[str, Any]) -> dict[str, Any]:
    return {
        "repo": filters["repo"],
        "skill": filters["skill"],
        "since": filters["since"],
        "until": filters["until"],
        "current_repo": filters["current_repo"],
    }


def format_runs_report(report: dict[str, Any]) -> str:
    lines = [f"Skill runs ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    if not report["groups"]:
        lines.append("- none")
        return "\n".join(lines)

    for group in report["groups"]:
        lines.append(
            "- "
            f"{group['skill']} {group['status']}: {group['run_count']} runs, "
            f"avg {format_duration(group['average_duration_seconds'])}, "
            f"total {format_duration(group['total_duration_seconds'])}, "
            f"window {group['first_timestamp']} .. {group['last_timestamp']}"
        )
    return "\n".join(lines)


def format_reviews_report(report: dict[str, Any]) -> str:
    lines = [f"Reviews ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    lines.append(
        "- "
        f"reviews={report['review_count']} initial={report['initial_review_count']} "
        f"rereviews={report['rereview_count']} blocked={report['blocked_count']} "
        f"open_questions={report['open_question_count']}"
    )
    lines.append(f"- lanes: {format_counter_map(report['lane_counts'])}")
    lines.append(f"- reviewers: {format_counter_map(report['reviewer_counts'])}")
    lines.append(f"- findings by severity: {format_counter_map(report['findings_by_severity'])}")
    lines.append(f"- findings by lens: {format_counter_map(report['findings_by_lens'])}")
    if report["rereview_trigger_counts"]:
        lines.append(f"- rereview triggers: {format_counter_map(report['rereview_trigger_counts'])}")
    lines.append(
        "- "
        f"artifacts parsed={report['artifact_summary']['parsed_count']} "
        f"missing={report['artifact_summary']['missing_count']} "
        f"mismatches={report['artifact_summary']['mismatch_count']}"
    )
    return "\n".join(lines)


def format_validation_report(report: dict[str, Any]) -> str:
    lines = [f"Validation ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    if not report["command_kinds"]:
        lines.append("- none")
        return "\n".join(lines)
    for command_kind in sorted(report["command_kinds"]):
        stats = report["command_kinds"][command_kind]
        lines.append(
            "- "
            f"{command_kind}: attempts={stats['attempt_count']} failures={stats['failure_count']} "
            f"retries={stats['retry_count']} final_pass={stats['final_pass_count']} "
            f"final_fail={stats['final_fail_count']}"
        )
    return "\n".join(lines)


def format_gates_report(report: dict[str, Any]) -> str:
    lines = [f"Gates ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    if not report["decision_counts"]:
        lines.append("- none")
        return "\n".join(lines)
    for gate_type in sorted(report["decision_counts"]):
        lines.append(f"- {gate_type}: {format_counter_map(report['decision_counts'][gate_type])}")
    return "\n".join(lines)


def format_tokens_report(report: dict[str, Any]) -> str:
    lines = [f"Tokens ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    for key in ("exact", "estimated", "unavailable"):
        source = report[key]
        total_tokens = source["totals"]["total_tokens"]
        total_label = "none" if total_tokens is None else str(total_tokens)
        lines.append(
            "- "
            f"Source quality: {source['source_quality']} rows={source['row_count']} "
            f"sessions={source['session_count']} total_tokens={total_label}"
        )
    return "\n".join(lines)


def format_summary_report(report: dict[str, Any]) -> str:
    lines = [f"Dreamers stats summary ({format_filter_header(report['filters'])})"]
    lines.extend(format_warning_lines(report["warning_count"]))
    lines.append("")
    lines.append("Skill runs")
    lines.extend(format_summary_block_from_runs(report["runs"]))
    lines.append("")
    lines.append("Reviews")
    lines.extend(format_summary_block_from_reviews(report["reviews"]))
    lines.append("")
    lines.append("Validation")
    lines.extend(format_summary_block_from_validation(report["validation"]))
    lines.append("")
    lines.append("Gates")
    lines.extend(format_summary_block_from_gates(report["gates"]))
    lines.append("")
    lines.append("Workflow outputs")
    lines.extend(format_summary_block_from_workflow(report["workflow_outputs"]))
    lines.append("")
    lines.append("Tokens")
    lines.extend(format_summary_block_from_tokens(report["tokens"]))
    return "\n".join(lines)


def format_summary_block_from_runs(report: dict[str, Any]) -> list[str]:
    if not report["groups"]:
        return ["- none"]
    return [
        "- "
        f"{group['skill']} {group['status']}: {group['run_count']} runs, "
        f"avg {format_duration(group['average_duration_seconds'])}, "
        f"total {format_duration(group['total_duration_seconds'])}"
        for group in report["groups"]
    ]


def format_summary_block_from_reviews(report: dict[str, Any]) -> list[str]:
    return [
        "- "
        f"reviews={report['review_count']} rereviews={report['rereview_count']} "
        f"blocked={report['blocked_count']} open_questions={report['open_question_count']}",
        f"- lanes: {format_counter_map(report['lane_counts'])}",
        f"- artifacts: parsed={report['artifact_summary']['parsed_count']} mismatches={report['artifact_summary']['mismatch_count']}",
    ]


def format_summary_block_from_validation(report: dict[str, Any]) -> list[str]:
    if not report["command_kinds"]:
        return ["- none"]
    return [
        "- "
        f"{kind}: attempts={stats['attempt_count']} failures={stats['failure_count']} retries={stats['retry_count']}"
        for kind, stats in sorted(report["command_kinds"].items())
    ]


def format_summary_block_from_gates(report: dict[str, Any]) -> list[str]:
    if not report["decision_counts"]:
        return ["- none"]
    return [f"- {gate_type}: {format_counter_map(decisions)}" for gate_type, decisions in sorted(report["decision_counts"].items())]


def format_summary_block_from_workflow(report: dict[str, Any]) -> list[str]:
    return [
        f"- cycles: {format_counter_map(report['cycle_status_counts'])}",
        f"- prs={report['pr_count']} retros={report['retro_count']}",
    ]


def format_summary_block_from_tokens(report: dict[str, Any]) -> list[str]:
    return [
        "- "
        f"{key}: rows={report[key]['row_count']} total_tokens="
        f"{'none' if report[key]['totals']['total_tokens'] is None else report[key]['totals']['total_tokens']}"
        for key in ("exact", "estimated", "unavailable")
    ]


def format_filter_header(filters: dict[str, Any]) -> str:
    parts = [f"repo={filters['repo']}"]
    if filters["skill"] is not None:
        parts.append(f"skill={filters['skill']}")
    if filters["since"] is not None:
        parts.append(f"since={filters['since']}")
    if filters["until"] is not None:
        parts.append(f"until={filters['until']}")
    return ", ".join(parts)


def format_warning_lines(warning_count: int) -> list[str]:
    if warning_count == 0:
        return []
    return [f"Warnings: skipped {warning_count} malformed or unreadable line(s)"]


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        if remainder:
            return f"{minutes}m {remainder}s"
        return f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    if minutes:
        return f"{hours}h {minutes}m"
    return f"{hours}h"


def format_counter_map(values: dict[str, Any]) -> str:
    if not values:
        return "none"
    items = []
    for key in sorted(values):
        items.append(f"{key}={values[key]}")
    return ", ".join(items)


REPORT_BUILDERS: dict[str, Callable[[list[dict[str, Any]], dict[str, Any]], dict[str, Any]]] = {
    "summarize": build_summary_report,
    "runs": build_runs_report,
    "reviews": build_reviews_report,
    "validation": build_validation_report,
    "gates": build_gates_report,
    "tokens": build_tokens_report,
}

REPORT_FORMATTERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "summarize": format_summary_report,
    "runs": format_runs_report,
    "reviews": format_reviews_report,
    "validation": format_validation_report,
    "gates": format_gates_report,
    "tokens": format_tokens_report,
}


def run_report_command(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    filters = build_report_filters(args)
    events, warning_count = load_report_events(args.copilot_home)
    filtered_events = filter_report_events(events, filters)
    report = REPORT_BUILDERS[args.command](filtered_events, filters, warning_count=warning_count)
    if args.json:
        return report, json.dumps(report, sort_keys=True)
    return report, REPORT_FORMATTERS[args.command](report)


def load_event(args: argparse.Namespace, stdin: TextIO) -> dict[str, Any]:
    event_json = getattr(args, "event_json", None)
    if event_json is not None:
        raw = event_json
    else:
        raw = stdin.read()
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise StatsValidationError("invalid_event", "event must be a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dreamers-stats")
    subcommands = parser.add_subparsers(dest="command", required=True)

    record_parser = subcommands.add_parser("record")
    record_parser.add_argument("--copilot-home")
    input_group = record_parser.add_mutually_exclusive_group()
    input_group.add_argument("--event-json")
    record_parser.add_argument("--print-event-id", action="store_true")

    doctor_parser = subcommands.add_parser("doctor")
    doctor_parser.add_argument("--copilot-home")
    doctor_parser.add_argument("--json", action="store_true")

    checkpoint_parser = subcommands.add_parser("checkpoint")
    checkpoint_parser.add_argument("--copilot-home")
    checkpoint_parser.add_argument("--event-type", required=True)
    checkpoint_parser.add_argument("--skill", required=True)
    checkpoint_parser.add_argument("--run-id", required=True)
    checkpoint_parser.add_argument("--status")
    checkpoint_parser.add_argument("--session-id")
    checkpoint_parser.add_argument("--branch")
    checkpoint_parser.add_argument("--repo-path")
    checkpoint_parser.add_argument("--timestamp")
    checkpoint_parser.add_argument("--metrics-json")
    checkpoint_parser.add_argument("--print-event-id", action="store_true")

    hook_parser = subcommands.add_parser("hook")
    hook_parser.add_argument("--copilot-home")
    hook_parser.add_argument("--event-name", required=True)

    for name in ("summarize", "runs", "reviews", "validation", "gates", "tokens"):
        report_parser = subcommands.add_parser(name)
        add_report_arguments(report_parser)

    return parser


def add_report_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--copilot-home")
    parser.add_argument("--repo", choices=("current", "all"), default="current")
    parser.add_argument("--skill")
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None, stdin: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_stream = stdin if stdin is not None else sys.stdin

    if args.command == "record":
        try:
            event = load_event(args, input_stream)
            event_id = record_event(event, copilot_home=args.copilot_home)
        except json.JSONDecodeError:
            print("invalid_json", file=sys.stderr)
            return 2
        except StatsValidationError as exc:
            print(exc.category, file=sys.stderr)
            return 2
        except OSError:
            print("write_failed", file=sys.stderr)
            return 1
        if args.print_event_id:
            print(event_id)
        return 0

    if args.command == "checkpoint":
        try:
            event = build_checkpoint_event(args)
            event_id = record_event(event, copilot_home=args.copilot_home)
        except json.JSONDecodeError:
            print("invalid_json", file=sys.stderr)
            return 2
        except StatsValidationError as exc:
            print(exc.category, file=sys.stderr)
            return 2
        except OSError:
            print("write_failed", file=sys.stderr)
            return 1
        if args.print_event_id:
            print(event_id)
        return 0

    if args.command == "doctor":
        report = doctor(copilot_home=args.copilot_home)
        if args.json:
            print(json.dumps(report, sort_keys=True))
        else:
            status = "ok" if report["writable"] else "error"
            print(
                f"{status} writable={str(report['writable']).lower()} "
                f"events={report['event_count']} malformed={report['malformed_line_count']} "
                f"path={report['events_file']}"
            )
        return 0 if report["writable"] else 1

    if args.command == "hook":
        try:
            payload = load_event(args, input_stream)
            event = build_hook_event(args.event_name, payload)
            record_event(event, copilot_home=args.copilot_home)
        except json.JSONDecodeError:
            print("invalid_json", file=sys.stderr)
            return 2
        except StatsValidationError as exc:
            print(exc.category, file=sys.stderr)
            return 2
        except OSError:
            print("write_failed", file=sys.stderr)
            return 1
        return 0

    if args.command in REPORT_BUILDERS:
        try:
            _report, output = run_report_command(args)
        except StatsValidationError as exc:
            print(exc.category, file=sys.stderr)
            return 2
        except OSError:
            print("read_failed", file=sys.stderr)
            return 1
        print(output)
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
