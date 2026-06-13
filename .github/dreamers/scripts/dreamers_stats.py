#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, TextIO


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

ALLOWED_EVENT_TYPES = {
    "session_started",
    "session_completed",
    "prompt_submitted",
    "turn_completed",
    "tool_requested",
    "tool_completed",
    "tool_failed",
    "subagent_started",
    "subagent_completed",
    "error_occurred",
    "compaction_started",
    "skill_started",
    "skill_completed",
    "skill_halted",
    "phase_started",
    "gate_presented",
    "gate_decided",
    "validation_attempt",
    "review_pass_started",
    "review_pass_completed",
    "review_findings_applied",
    "rerun_decision",
    "cycle_completed",
    "pr_created",
    "retro_written",
    "token_usage_recorded",
}

ALLOWED_SOURCES = {"hook", "skill", "summary"}
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

HOOK_EVENT_SPECS: dict[str, HookSpec] = {
    "sessionStart": {
        "event_type": "session_started",
        "status": "started",
        "metrics": lambda payload: {
            "session_source": hook_value(payload, "source"),
            "initial_input_present": bool(hook_value(payload, "initialPrompt")),
        },
    },
    "sessionEnd": {
        "event_type": "session_completed",
        "status": "completed",
        "metrics": lambda payload: {
            "reason": hook_value(payload, "reason"),
        },
    },
    "userPromptSubmitted": {
        "event_type": "prompt_submitted",
        "status": "submitted",
        "metrics": lambda payload: {
            "prompt_count": 1,
            "input_char_count": len(hook_value(payload, "prompt", default="")),
            "starts_with_slash": hook_value(payload, "prompt", default="").lstrip().startswith("/"),
        },
    },
    "postToolUse": {
        "event_type": "tool_completed",
        "status": "completed",
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
        "status": "failed",
        "metrics": lambda payload: {
            "tool_name": hook_value(payload, "toolName", "tool_name"),
            "error_present": bool(hook_value(payload, "error")),
        },
    },
    "agentStop": {
        "event_type": "turn_completed",
        "status": "completed",
        "metrics": lambda payload: {
            "stop_reason": hook_value(payload, "stopReason", "stop_reason"),
        },
    },
    "subagentStart": {
        "event_type": "subagent_started",
        "status": "started",
        "metrics": lambda payload: {
            "agent_name": hook_value(payload, "agentName", "agent_name"),
            "agent_display_name": hook_value(payload, "agentDisplayName", "agent_display_name"),
        },
    },
    "subagentStop": {
        "event_type": "subagent_completed",
        "status": "completed",
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
        "status": "started",
        "metrics": lambda payload: {
            "trigger": hook_value(payload, "trigger"),
            "instructions_present": bool(
                hook_value(payload, "customInstructions", "custom_instructions")
            ),
        },
    },
}


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

    if event["event_type"] not in ALLOWED_EVENT_TYPES:
        raise StatsValidationError("invalid_event_type", "event_type is not recognized")

    if event["source"] not in ALLOWED_SOURCES:
        raise StatsValidationError("invalid_source", "source must be hook, skill, or summary")

    if not isinstance(event["metrics"], dict):
        raise StatsValidationError("invalid_metrics", "metrics must be a JSON object")

    for field in OPTIONAL_FIELDS:
        if field in event and event[field] is not None and not isinstance(event[field], str):
            raise StatsValidationError("invalid_optional_field", f"{field} must be a string when present")

    _validate_timestamp(event["timestamp"])


def _require_string(event: dict[str, Any], field: str) -> None:
    if not isinstance(event[field], str) or not event[field].strip():
        raise StatsValidationError("invalid_field_type", f"{field} must be a non-empty string")


def _validate_event_id(value: str) -> None:
    if len(value) > 96 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}", value):
        raise StatsValidationError("invalid_event_id", "event_id must be a compact identifier")


def _validate_timestamp(value: str) -> None:
    parse_iso_timestamp(value)


def build_hook_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    spec = HOOK_EVENT_SPECS.get(event_name)
    if spec is None:
        raise StatsValidationError("invalid_hook_event", "hook event is not supported")
    event = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": hook_timestamp(payload),
        "event_type": resolve_hook_spec_value(spec["event_type"], payload),
        "repo_path": hook_value(payload, "cwd"),
        "session_id": hook_value(payload, "sessionId", "session_id"),
        "source": "hook",
        "status": resolve_hook_spec_value(spec["status"], payload),
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

    hook_parser = subcommands.add_parser("hook")
    hook_parser.add_argument("--copilot-home")
    hook_parser.add_argument("--event-name", required=True)

    return parser


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

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
