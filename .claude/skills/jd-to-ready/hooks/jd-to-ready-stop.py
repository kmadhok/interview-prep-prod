#!/usr/bin/env python3
"""Prevent silent completion when an active jd-to-ready trace is incomplete."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


TRACE = Path.home() / ".claude" / "skills" / "jd-to-ready" / "scripts" / "trace_step.py"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(TRACE), "check", "--strict"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 2:
        sys.stderr.write(result.stderr or result.stdout)
        return 2
    if result.stdout:
        sys.stdout.write(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
