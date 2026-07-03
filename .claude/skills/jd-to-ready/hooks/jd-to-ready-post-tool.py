#!/usr/bin/env python3
"""Append compact tool telemetry to the active jd-to-ready trace.

Claude Code delivers the hook payload as JSON on stdin (tool_name, tool_input,
session_id, ...). The legacy env-var path (TOOL_NAME / CLAUDE_TOOL_INPUT) is
kept only as a fallback — before the stdin fix, every tool_event logged
tool=unknown with an empty summary.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


TRACE = Path.home() / ".claude" / "skills" / "jd-to-ready" / "scripts" / "trace_step.py"


def read_stdin_payload() -> dict[str, Any]:
    """Parse the hook payload from stdin, tolerating a BOM or other prefix junk
    (PowerShell pipes prepend one during manual smoke tests)."""
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
    except OSError:
        return {}
    start = raw.find("{")
    if start < 0:
        return {}
    try:
        payload = json.loads(raw[start:])
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def summarize_tool_input(value: Any) -> str | None:
    """Compact one-line summary of a tool input (dict from stdin, or raw string)."""
    if not value:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value[:240]
    if isinstance(value, dict):
        for key in ("file_path", "path", "pattern", "command", "cmd"):
            if key in value:
                return f"{key}={str(value[key])[:220]}"
        return ",".join(sorted(value.keys()))[:240]
    return str(value)[:240]


def main() -> int:
    payload = read_stdin_payload()
    tool_name = (
        payload.get("tool_name")
        or os.environ.get("TOOL_NAME")
        or os.environ.get("CLAUDE_TOOL_NAME")
        or "unknown"
    )
    summary = summarize_tool_input(payload.get("tool_input") or os.environ.get("CLAUDE_TOOL_INPUT"))
    env = os.environ.copy()
    session_id = payload.get("session_id")
    if session_id and not env.get("CLAUDE_CODE_SESSION_ID"):
        env["CLAUDE_CODE_SESSION_ID"] = str(session_id)
    subprocess.run(
        [
            sys.executable,
            str(TRACE),
            "tool-event",
            "--tool-name",
            str(tool_name),
            "--status",
            "completed",
            "--summary",
            summary or "",
        ],
        env=env,
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
