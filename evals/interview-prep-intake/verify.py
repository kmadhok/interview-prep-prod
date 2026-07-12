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

from common import ClauseResult, EvalContext  # noqa: E402


def verify(context: EvalContext) -> list[ClauseResult]:
    workspace = context.workspace
    role_path = context.role
    isolated_clone = workspace.resolve() == role_path.resolve()
    role_folder = role_path.name
    pipeline_role = role_folder.replace(" - ", " — ", 1)
    jd_path = role_path / "Job Description.md"
    pipeline_path = (role_path / "_pipeline-fixture.md") if isolated_clone else workspace / "Pipeline.md"

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
            if in_considering and pipeline_role in line:
                c3_passed = True
                break
        if not c3_passed:
            c3_detail = f"'{pipeline_role}' not found under ## Considering"
    c3 = ClauseResult(
        id="intake-C3",
        description="Pipeline row under Considering",
        passed=c3_passed,
        detail="" if c3_passed else c3_detail,
    )

    # C4 — idempotent row/path correspondence.
    matching_rows = []
    if pipeline_path.exists():
        matching_rows = [
            line for line in pipeline_path.read_text(
                encoding="utf-8-sig", errors="ignore"
            ).splitlines()
            if line.lstrip().startswith("|") and pipeline_role in line
        ]
    folder_linked = len(matching_rows) == 1 and role_folder in matching_rows[0]
    c4 = ClauseResult(
        id="intake-C4",
        description="Exactly one Pipeline row links the selected role path",
        passed=folder_linked,
        detail=f"matching rows={len(matching_rows)}; expected one row linking {role_folder!r}"
        if not folder_linked else "",
    )

    return [c1, c2, c3, c4]
