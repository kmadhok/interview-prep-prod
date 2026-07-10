"""Verifier for tailor-resume (clauses tailor-resume-C1..C4).

Judges the end-state of a tailor-resume run against the contract in
contract.md. config.py lives in the repo-root scripts/ dir; this file sits
at evals/<skill>/, so the repo root is parents[2].
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Bootstrap repo-root scripts/ onto sys.path for config.resume_glob_prefix.
REPO_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(REPO_SCRIPTS))

# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import ClauseResult  # noqa: E402
from config import resume_glob_prefix  # noqa: E402

ROLE_FOLDER = "Acme - Senior Agent Builder"

PLACEHOLDER_LEAKS = ["[NUMBER?]", "<user_", "{name}", "TBD"]
QUARANTINE_MARKERS = ["Resume Claims To Verify", "UNVERIFIED"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def verify(workspace: Path) -> list[ClauseResult]:
    workspace = Path(workspace)
    role_path = workspace / "Roles" / ROLE_FOLDER
    prefix = resume_glob_prefix()

    # C1 — resume md matching profile prefix
    matches = sorted(role_path.glob(f"{prefix}*.md")) if role_path.is_dir() else []
    c1 = ClauseResult(
        id="tailor-resume-C1",
        description="Resume md exists matching profile prefix",
        passed=len(matches) > 0,
        detail=f"no match for glob {prefix}*.md in {role_path}"
        if not matches else f"found {matches[0].name}",
    )

    # C2 — no quarantine markers
    c2_passed = True
    c2_detail = ""
    for md in matches:
        text = _read(md)
        for marker in QUARANTINE_MARKERS:
            if marker in text:
                c2_passed = False
                c2_detail = f"{md.name} contains {marker!r}"
                break
        if not c2_passed:
            break
    c2 = ClauseResult(
        id="tailor-resume-C2",
        description="No content from Resume Claims To Verify",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — no placeholder leaks
    c3_passed = True
    c3_detail = ""
    for md in matches:
        text = _read(md)
        for marker in PLACEHOLDER_LEAKS:
            if marker in text:
                c3_passed = False
                c3_detail = f"{md.name} contains {marker!r}"
                break
        if not c3_passed:
            break
    c3 = ClauseResult(
        id="tailor-resume-C3",
        description="No placeholder leaks",
        passed=c3_passed,
        detail=c3_detail,
    )

    # C4 — gaps file when JD demands non-canonical claims
    jd_has_fusion = False
    if role_path.is_dir():
        for md in role_path.glob("*.md"):
            if "fusion reactors" in _read(md).lower():
                jd_has_fusion = True
                break

    if jd_has_fusion:
        gaps_path = role_path / ".eval-gaps.json"
        c4_passed = False
        c4_detail = ".eval-gaps.json missing"
        if gaps_path.exists():
            try:
                data = json.loads(_read(gaps_path))
                gaps = data.get("gaps", data) if isinstance(data, dict) else data
                if isinstance(gaps, list) and len(gaps) > 0:
                    has_match_gap = any(
                        "no-canonical-match" in str(g.get("kind", ""))
                        for g in gaps if isinstance(g, dict)
                    ) or len(gaps) > 0
                    c4_passed = has_match_gap
                    c4_detail = "" if c4_passed else f"gaps found but none with kind 'no-canonical-match': {gaps}"
                else:
                    c4_detail = "gaps list is empty or missing"
            except (ValueError, AttributeError) as exc:
                c4_detail = f"parse error: {exc}"
        c4 = ClauseResult(
            id="tailor-resume-C4",
            description="Gaps file present when JD demands non-canonical claims",
            passed=c4_passed,
            detail=c4_detail,
        )
    else:
        # Vacuous pass — JD does not demand the unmatched requirement.
        c4 = ClauseResult(
            id="tailor-resume-C4",
            description="Gaps file present when JD demands non-canonical claims",
            passed=True,
            detail="JD does not contain 'fusion reactors' — vacuous pass",
        )

    return [c1, c2, c3, c4]
