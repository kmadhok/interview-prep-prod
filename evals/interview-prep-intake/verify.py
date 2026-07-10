"""Verifier for interview-prep-intake (clauses intake-C1..C4).

Judges the end-state of an intake run against the contract in contract.md.
Standalone: imports ClauseResult from evals/common.py via sys.path bootstrap.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap evals/ parent onto sys.path so `from common import ClauseResult`
# resolves whether invoked by run_eval.py or directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import ClauseResult  # noqa: E402

ROLE_FOLDER = "Acme - Senior Agent Builder"
PIPELINE_ROLE = "Acme — Senior Agent Builder"  # em-dash, as in Pipeline.md


def verify(workspace: Path) -> list[ClauseResult]:
    workspace = Path(workspace)
    roles_dir = workspace / "Roles"
    role_path = roles_dir / ROLE_FOLDER
    jd_path = role_path / "Job Description.md"
    pipeline_path = workspace / "Pipeline.md"

    # C1 — role folder exists
    c1 = ClauseResult(
        id="intake-C1",
        description="Role folder exists",
        passed=role_path.is_dir(),
        detail=str(role_path) if not role_path.is_dir() else "",
    )

    # C2 — Job Description.md non-empty
    jd_text = jd_path.read_text(encoding="utf-8-sig", errors="ignore") if jd_path.exists() else ""
    jd_nonempty = jd_path.exists() and len(jd_text.strip()) > 0
    c2 = ClauseResult(
        id="intake-C2",
        description="Job Description.md is non-empty",
        passed=jd_nonempty,
        detail="file missing" if not jd_path.exists()
        else f"empty ({len(jd_text)} chars)" if not jd_nonempty else "",
    )

    # C3 — Pipeline row under Considering
    c3_passed = False
    c3_detail = "Pipeline.md missing"
    if pipeline_path.exists():
        text = pipeline_path.read_text(encoding="utf-8-sig", errors="ignore")
        lines = text.splitlines()
        in_considering = False
        for line in lines:
            if line.strip().startswith("## Considering"):
                in_considering = True
                continue
            if in_considering and line.strip().startswith("## "):
                in_considering = False
            if in_considering and PIPELINE_ROLE in line:
                c3_passed = True
                break
        if not c3_passed:
            c3_detail = f"'{PIPELINE_ROLE}' not found under ## Considering"
    c3 = ClauseResult(
        id="intake-C3",
        description="Pipeline row under Considering",
        passed=c3_passed,
        detail="" if c3_passed else c3_detail,
    )

    # C4 — no other role folder
    other_roles = []
    if roles_dir.is_dir():
        other_roles = [
            d.name for d in sorted(roles_dir.iterdir())
            if d.is_dir() and d.name != ROLE_FOLDER
        ]
    c4 = ClauseResult(
        id="intake-C4",
        description="No other role folder created",
        passed=len(other_roles) == 0,
        detail=f"unexpected: {other_roles}" if other_roles else "",
    )

    return [c1, c2, c3, c4]
