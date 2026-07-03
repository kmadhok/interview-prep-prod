#!/usr/bin/env python3
"""Record subagent completion against the active jd-to-ready trace.

Claude Code delivers the hook payload as JSON on stdin. The legacy env-var
path (CLAUDE_SUBAGENT_NAME / SUBAGENT_NAME) is kept only as a fallback.
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


def main() -> int:
    payload = read_stdin_payload()
    agent_name = (
        payload.get("subagent_type")
        or payload.get("agent_name")
        or payload.get("agent_type")
        or os.environ.get("CLAUDE_SUBAGENT_NAME")
        or os.environ.get("SUBAGENT_NAME")
        or "subagent"
    )
    env = os.environ.copy()
    session_id = payload.get("session_id")
    if session_id and not env.get("CLAUDE_CODE_SESSION_ID"):
        env["CLAUDE_CODE_SESSION_ID"] = str(session_id)
    subprocess.run(
        [
            sys.executable,
            str(TRACE),
            "subagent-event",
            "--agent-name",
            str(agent_name),
            "--status",
            "completed",
            "--summary",
            "Subagent stopped during active jd-to-ready run.",
        ],
        env=env,
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
