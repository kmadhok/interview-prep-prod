"""Verifier for tailor-resume (clauses tailor-resume-C1..C4).

Judges the end-state of a tailor-resume run against the contract in
contract.md. config.py lives in the repo-root scripts/ dir; this file sits
at evals/<skill>/, so the repo root is parents[2].
"""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap repo-root scripts/ onto sys.path for config.resume_glob_prefix.
REPO_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(REPO_SCRIPTS))

# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import ClauseResult, EvalContext  # noqa: E402
from config import load_profile, resume_glob_prefix  # noqa: E402

PLACEHOLDER_LEAKS = ["[NUMBER?]", "<user_", "{name}", "TBD"]
QUARANTINE_MARKERS = ["Resume Claims To Verify", "UNVERIFIED"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def verify(context: EvalContext) -> list[ClauseResult]:
    """Execute `verify`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    role_path = context.role
    profile = load_profile(context.profile) if context.profile else load_profile()
    prefix = resume_glob_prefix(profile)

    # C1 — resume md matching profile prefix
    matches = sorted(role_path.glob(f"{prefix}*.md")) if role_path.is_dir() else []
    if not matches and context.profile is None and role_path.is_dir():
        # Legacy isolated clones predate --profile; accept their sole
        # profile-shaped resume while explicit profiles remain fail-closed.
        matches = sorted(role_path.glob("* Resume - *.md"))
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

    # C4 — the owned resume artifact is substantive and carries profile contact.
    resume_text = _read(matches[0]) if matches else ""
    email = profile.get("user_email", "")
    c4_passed = len(resume_text.strip()) > 400 and bool(email) and email in resume_text
    c4_detail = "" if c4_passed else (
        f"resume chars={len(resume_text.strip())}; profile email present={bool(email and email in resume_text)}"
    )
    c4 = ClauseResult(
        id="tailor-resume-C4",
        description="Resume is nontrivial and contains profile contact email",
        passed=c4_passed,
        detail=c4_detail,
    )

    return [c1, c2, c3, c4]
