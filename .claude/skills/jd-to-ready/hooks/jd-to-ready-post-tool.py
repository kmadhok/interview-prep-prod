#!/usr/bin/env python3
"""Append compact tool telemetry to the active jd-to-ready trace."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


TRACE = Path.home() / ".claude" / "skills" / "jd-to-ready" / "scripts" / "trace_step.py"


def summarize_tool_input(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:240]
    if isinstance(value, dict):
        for key in ("file_path", "path", "pattern", "command", "cmd"):
            if key in value:
                return f"{key}={str(value[key])[:220]}"
        return ",".join(sorted(value.keys()))[:240]
    return str(value)[:240]


def main() -> int:
    tool_name = os.environ.get("TOOL_NAME") or os.environ.get("CLAUDE_TOOL_NAME") or "unknown"
    summary = summarize_tool_input(os.environ.get("CLAUDE_TOOL_INPUT"))
    subprocess.run(
        [
            sys.executable,
            str(TRACE),
            "tool-event",
            "--tool-name",
            tool_name,
            "--status",
            "completed",
            "--summary",
            summary or "",
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
