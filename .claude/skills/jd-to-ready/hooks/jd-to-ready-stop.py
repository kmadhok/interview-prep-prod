#!/usr/bin/env python3
"""Prevent silent completion when an active jd-to-ready trace is incomplete.

Reads the hook payload from stdin JSON and forwards the session_id to the
trace helper as CLAUDE_CODE_SESSION_ID so the owner-session scoping in
`trace_step.py check` works: only the session that started a run gets flagged
for its incomplete trace.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


# Repo-relative: hooks/<file> -> .claude/skills/jd-to-ready/hooks, repo root is parents[4].
TRACE = Path(__file__).resolve().parents[4] / "scripts" / "trace_step.py"


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
    """Block only an owner session whose active trace fails the strict completeness check."""
    payload = read_stdin_payload()
    env = os.environ.copy()
    session_id = payload.get("session_id")
    if session_id and not env.get("CLAUDE_CODE_SESSION_ID"):
        env["CLAUDE_CODE_SESSION_ID"] = str(session_id)
    result = subprocess.run(
        [sys.executable, str(TRACE), "check", "--strict"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode == 2:
        sys.stderr.write(result.stderr or result.stdout)
        return 2
    if result.stdout:
        sys.stdout.write(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
