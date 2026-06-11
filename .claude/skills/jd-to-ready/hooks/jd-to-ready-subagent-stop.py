#!/usr/bin/env python3
"""Record subagent completion against the active jd-to-ready trace."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


TRACE = Path.home() / ".claude" / "skills" / "jd-to-ready" / "scripts" / "trace_step.py"


def main() -> int:
    agent_name = os.environ.get("CLAUDE_SUBAGENT_NAME") or os.environ.get("SUBAGENT_NAME") or "subagent"
    subprocess.run(
        [
            sys.executable,
            str(TRACE),
            "subagent-event",
            "--agent-name",
            agent_name,
            "--status",
            "completed",
            "--summary",
            "Subagent stopped during active jd-to-ready run.",
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
