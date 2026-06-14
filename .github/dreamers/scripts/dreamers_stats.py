#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, TextIO


class StatsValidationError(Exception):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


_SHARED_RUNTIME = None


def _runtime_candidate(path: Path) -> Path | None:
    candidate = path.expanduser()
    for root in (candidate, candidate / "runtime"):
        runtime_path = root / "dreamers_stats" / "runtime.py"
        if runtime_path.is_file():
            return root
    return None


def _find_shared_runtime_root() -> Path:
    configured = os_environ("DREAMERS_MCP_HOME")
    if configured is not None:
        resolved = _runtime_candidate(Path(configured))
        if resolved is None:
            raise RuntimeError(
                f"shared dreamers-mcp runtime not found at '{Path(configured).expanduser()}'"
            )
        return resolved

    script_path = Path(__file__).resolve()
    candidates = [script_path.parent.parent / "runtime"]
    if len(script_path.parents) > 3:
        candidates.append(script_path.parents[3].parent / "dreamers-mcp")

    for candidate in candidates:
        resolved = _runtime_candidate(candidate)
        if resolved is not None:
            return resolved

    raise RuntimeError(
        "shared dreamers-mcp runtime not found; reinstall Dreamers or set DREAMERS_MCP_HOME"
    )


def _format_counter_map(values: dict[str, Any]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{key}={values[key]}" for key in sorted(values))


def _format_warning_lines(warning_count: int) -> list[str]:
    if warning_count == 0:
        return []
    return [f"Warnings: skipped {warning_count} malformed or unreadable line(s)"]


def _format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {remainder}s" if remainder else f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if minutes else f"{hours}h"


def _build_workflow_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    cycle_status_counts: Counter[str] = Counter()
    for event in events:
        if event["event_type"] != "cycle_completed":
            continue
        cycle_status = event["metrics"].get("cycle_status")
        if isinstance(cycle_status, str) and cycle_status:
            cycle_status_counts[cycle_status] += 1

    return {
        "cycle_status_counts": dict(cycle_status_counts),
        "pr_count": sum(1 for event in events if event["event_type"] == "pr_created"),
        "retro_count": sum(1 for event in events if event["event_type"] == "retro_written"),
    }


def _summary_block_from_runs(report: dict[str, Any]) -> list[str]:
    if not report["groups"]:
        return ["- none"]
    return [
        "- "
        f"{group['skill']} {group['status']}: {group['run_count']} runs, "
        f"avg {_format_duration(group['average_duration_seconds'])}, "
        f"total {_format_duration(group['total_duration_seconds'])}"
        for group in report["groups"]
    ]


def _summary_block_from_reviews(report: dict[str, Any]) -> list[str]:
    return [
        "- "
        f"reviews={report['review_count']} rereviews={report['rereview_count']} "
        f"blocked={report['blocked_count']} open_questions={report['open_question_count']}",
        f"- lanes: {_format_counter_map(report['lane_counts'])}",
        f"- artifacts: parsed={report['artifact_summary']['parsed_count']} mismatches={report['artifact_summary']['mismatch_count']}",
    ]


def _summary_block_from_validation(report: dict[str, Any]) -> list[str]:
    if not report["command_kinds"]:
        return ["- none"]
    return [
        "- "
        f"{kind}: attempts={stats['attempt_count']} failures={stats['failure_count']} retries={stats['retry_count']}"
        for kind, stats in sorted(report["command_kinds"].items())
    ]


def _summary_block_from_gates(report: dict[str, Any]) -> list[str]:
    if not report["decision_counts"]:
        return ["- none"]
    return [
        f"- {gate_type}: {_format_counter_map(decisions)}"
        for gate_type, decisions in sorted(report["decision_counts"].items())
    ]


def _summary_block_from_workflow(report: dict[str, Any]) -> list[str]:
    return [
        f"- cycles: {_format_counter_map(report['cycle_status_counts'])}",
        f"- prs={report['pr_count']} retros={report['retro_count']}",
    ]


def _summary_block_from_tokens(report: dict[str, Any]) -> list[str]:
    return [
        "- "
        f"{source_quality}: rows={report[source_quality]['row_count']} total_tokens="
        f"{'none' if report[source_quality]['totals']['total_tokens'] is None else report[source_quality]['totals']['total_tokens']}"
        for source_quality in ("exact", "estimated", "unavailable")
    ]


def _compat_build_summary_report(
    runtime: Any,
    events: list[dict[str, Any]],
    warning_count: int,
    filters: dict[str, Any],
) -> dict[str, Any]:
    report = runtime.build_summary_report(events, warning_count, filters)
    report["workflow_outputs"] = _build_workflow_report(events)
    return report


def _format_filter_header(runtime: Any, filters: dict[str, Any]) -> str:
    parts = [f"repo={filters['repo']}"]
    if filters["skill"] is not None:
        parts.append(f"skill={filters['skill']}")
    if filters["since"] is not None:
        parts.append(f"since={filters['since']}")
    if filters["until"] is not None:
        parts.append(f"until={filters['until']}")
    return ", ".join(parts)

def _compat_format_summary_report(runtime: Any, report: dict[str, Any]) -> str:
    workflow_outputs = report.get(
        "workflow_outputs",
        {"cycle_status_counts": {}, "pr_count": 0, "retro_count": 0},
    )
    lines = [f"Dreamers stats summary ({_format_filter_header(runtime, report['filters'])})"]
    lines.extend(_format_warning_lines(report["warning_count"]))
    lines.append("")
    lines.append("Skill runs")
    lines.extend(_summary_block_from_runs(report["runs"]))
    lines.append("")
    lines.append("Reviews")
    lines.extend(_summary_block_from_reviews(report["reviews"]))
    lines.append("")
    lines.append("Validation")
    lines.extend(_summary_block_from_validation(report["validation"]))
    lines.append("")
    lines.append("Gates")
    lines.extend(_summary_block_from_gates(report["gates"]))
    lines.append("")
    lines.append("Workflow outputs")
    lines.extend(_summary_block_from_workflow(workflow_outputs))
    lines.append("")
    lines.append("Tokens")
    lines.extend(_summary_block_from_tokens(report["tokens"]))
    return "\n".join(lines)


def _patch_runtime(runtime: Any) -> None:
    if getattr(runtime, "_dreamers_copilot_compat", False):
        return

    runtime.REPORT_BUILDERS["summarize"] = (
        lambda events, warning_count, filters: _compat_build_summary_report(
            runtime,
            events,
            warning_count,
            filters,
        )
    )
    runtime.REPORT_FORMATTERS["summarize"] = (
        lambda report: _compat_format_summary_report(runtime, report)
    )
    runtime._dreamers_copilot_compat = True


def _load_shared_runtime() -> Any:
    global _SHARED_RUNTIME
    if _SHARED_RUNTIME is not None:
        return _SHARED_RUNTIME

    runtime_root = _find_shared_runtime_root()
    runtime_path = runtime_root / "dreamers_stats" / "runtime.py"
    spec = importlib.util.spec_from_file_location("dreamers_shared_runtime", runtime_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load shared runtime from '{runtime_path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    _patch_runtime(module)
    _SHARED_RUNTIME = module
    return module


def _normalize_argv(argv: list[str] | None) -> list[str]:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return args
    if args[0].startswith("-"):
        return args

    option_args = args[1:]
    if any(flag in option_args for flag in ("--client", "--copilot-home", "--codex-home")):
        return args
    return [args[0], "--client", "copilot", *option_args]


def default_status_for_event(event_type: str) -> str:
    runtime = _load_shared_runtime()
    return runtime.default_status_for_event(event_type)


def record_event(event: dict[str, Any], copilot_home: str | Path | None = None) -> str:
    runtime = _load_shared_runtime()
    try:
        return runtime.record_event(event, client="copilot", home=copilot_home)
    except runtime.StatsValidationError as exc:
        raise StatsValidationError(exc.category, str(exc)) from None


def main(argv: list[str] | None = None, stdin: TextIO | None = None) -> int:
    try:
        runtime = _load_shared_runtime()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return runtime.main(_normalize_argv(argv), stdin=stdin)


def os_environ(key: str) -> str | None:
    value = os.environ.get(key)
    if value is None or not value.strip():
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["StatsValidationError", "default_status_for_event", "main", "record_event", "TextIO"]
