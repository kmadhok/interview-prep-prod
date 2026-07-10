#!/usr/bin/env python3
"""Render runs/<run-id>/trace.jsonl into a human report (report.md).

The report is the user's repair manual: every step shows WHY it ran (reason)
and WHICH files shaped its output (sources) -- edit those files to change the
behavior. Tolerates schema v1 traces (missing reason/sources render as "—").
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


DASH = "—"


def read_events(trace: Path) -> list[dict[str, Any]]:
    """Parse a JSONL trace, skipping blank lines."""
    events: list[dict[str, Any]] = []
    for line in trace.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def fmt_tokens(tokens: dict[str, Any] | None) -> str:
    """Return the total token count from a token dict, or DASH when unknown."""
    if not isinstance(tokens, dict):
        return DASH
    total = tokens.get("total")
    if total is None:
        return DASH
    return str(total)


def _first_event(events: list[dict[str, Any]], event_name: str) -> dict[str, Any] | None:
    for event in events:
        if event.get("event") == event_name:
            return event
    return None


def _event_value(events: list[dict[str, Any]], key: str) -> Any:
    for event in events:
        value = event.get(key)
        if value not in (None, ""):
            return value
    return None


def _step_key(event: dict[str, Any]) -> str:
    return str(event.get("step", DASH))


def _table_cell(value: Any) -> str:
    if value in (None, ""):
        return DASH
    text = str(value).replace("\n", "<br>")
    return text.replace("|", "\\|")


def _inline_code(value: Any) -> str:
    text = str(value).replace("`", "\\`")
    return f"`{text}`"


def _format_paths(paths: Any) -> str:
    if not isinstance(paths, list) or not paths:
        return DASH
    return ", ".join(_inline_code(path) for path in paths)


def _format_produced(paths: Any) -> str:
    if not isinstance(paths, list) or not paths:
        return "(no files)"
    return ", ".join(_inline_code(path) for path in paths)


def _final_status(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        if event.get("event") == "run_finish":
            return str(event.get("status") or "ok")
        if event.get("event") == "run_abort":
            return str(event.get("status") or "aborted")
    return "INCOMPLETE"


def _step_ends(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    ends: dict[str, dict[str, Any]] = {}
    for event in events:
        if event.get("event") == "step_end":
            ends[_step_key(event)] = event
    return ends


def render(run_dir: Path) -> Path:
    trace = run_dir / "trace.jsonl"
    events = read_events(trace)
    run_start = _first_event(events, "run_start") or {}
    run_id = run_start.get("run_id") or _event_value(events, "run_id") or run_dir.name
    skill = run_start.get("skill") or run_id
    company = run_start.get("company") or _event_value(events, "company") or DASH
    role = run_start.get("role") or _event_value(events, "role") or DASH
    schema_version = run_start.get("schema_version", DASH)
    tool_call_count = sum(1 for event in events if event.get("event") == "tool_event")
    begins = [event for event in events if event.get("event") == "step_begin"]
    ends = _step_ends(events)

    abort = _first_event(events, "run_abort")

    lines = [
        f"# Run report — {skill}",
        "",
        f"- Run ID: {run_id}",
        f"- Status: {_final_status(events)}",
        f"- Company/role: {company} / {role}",
        f"- Schema version: {schema_version}",
        f"- Tool-call count: {tool_call_count}",
    ]
    if abort is not None:
        lines.append(f"- Abort reason: {abort.get('reason') or DASH}")
    lines += [
        "",
        "## Steps",
        "",
        "| Step | Status | Reason | Tokens |",
        "| --- | --- | --- | --- |",
    ]

    for begin in begins:
        step = _step_key(begin)
        end = ends.get(step)
        status = end.get("status") if end else "OPEN"
        reason = begin.get("reason") or DASH
        tokens = fmt_tokens(end.get("tokens") if end else None)
        lines.append(
            f"| {_table_cell(step)} | {_table_cell(status)} | {_table_cell(reason)} | {_table_cell(tokens)} |"
        )

    if not begins:
        lines.append(f"| {DASH} | {DASH} | {DASH} | {DASH} |")

    lines.extend(["", "## How to change an output", ""])

    if begins:
        for begin in begins:
            step = _step_key(begin)
            end = ends.get(step) or {}
            produced = _format_produced(end.get("produced"))
            sources = _format_paths(begin.get("sources"))
            reason = begin.get("reason") or DASH
            lines.append(
                f"- {step}: {produced} — shaped by: {sources}. "
                f"Don't like it? Edit those files and re-run. Why it ran: {reason}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Gaps", ""])

    # step_end gaps plus terminal run_abort gaps (deduped: abort-run receives the
    # merged array, so most of its entries repeat step gaps)
    gaps: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any, Any]] = set()
    for event in events:
        if event.get("event") not in ("step_end", "run_abort"):
            continue
        event_gaps = event.get("gaps")
        if not isinstance(event_gaps, list):
            continue
        for gap in event_gaps:
            if not isinstance(gap, dict):
                continue
            key = (gap.get("kind"), gap.get("source"), gap.get("detail"))
            if key in seen:
                continue
            seen.add(key)
            gaps.append(gap)

    if gaps:
        for gap in gaps:
            kind = gap.get("kind") or DASH
            source = gap.get("source") or DASH
            detail = gap.get("detail") or DASH
            lines.append(f"- {_inline_code(kind)} ({source}): {detail}")
    else:
        lines.append("- none")

    report_path = run_dir / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: render_run_report.py <run-dir>", file=sys.stderr)
        return 2
    run_dir = Path(args[0])
    trace = run_dir / "trace.jsonl"
    if not trace.exists():
        print(f"no trace.jsonl found in {run_dir}", file=sys.stderr)
        return 1
    print(render(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
