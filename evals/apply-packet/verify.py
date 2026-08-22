"""Verifier for apply-packet (clauses apply-packet-C1..C3).

C1 checks Application Answers.md exists + answers traceable to the fixture
Application Profile.md (pragmatic proxy: no digits/amounts in answers absent
from the profile). C2 reuses verify_artifacts.check_packet. C3 asserts the
recorded remote_dir contains "_test".
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ClauseResult, EvalContext  # noqa: E402
EVALS_DIR = Path(__file__).resolve().parents[1]
PROFILE_FIXTURE = EVALS_DIR / "fixtures" / "application-profile.md"

# Digits and dollar amounts — the pragmatic traceability proxy.
_AMOUNT_RE = re.compile(r"\$[\d,]+(?:\.\d+)?[kK]?")
_DIGIT_RE = re.compile(r"\d+")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def verify(context: EvalContext) -> list[ClauseResult]:
    """Execute `verify`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    role = context.role
    answers_path = role / "Application Answers.md"
    packet_path = role / ".apply-packet.json"
    profile_fixture = context.profile or PROFILE_FIXTURE

    # C1 — Application Answers.md exists + answers traceable to the profile fixture
    c1_passed = False
    c1_detail = "Application Answers.md missing"
    if answers_path.exists():
        answers_text = _read(answers_path)
        profile_text = _read(profile_fixture)
        if not answers_text.strip():
            c1_detail = "Application Answers.md is empty"
        else:
            amounts = _AMOUNT_RE.findall(answers_text)
            # "digits" as bare numbers excluding those already captured as amounts
            amount_digit_sets = set()
            for a in amounts:
                amount_digit_sets.update(_DIGIT_RE.findall(a))
            bare_digits = [d for d in _DIGIT_RE.findall(answers_text)
                           if d not in amount_digit_sets]
            missing = []
            for a in amounts:
                if a not in profile_text:
                    missing.append(a)
            for d in bare_digits:
                if d not in profile_text:
                    missing.append(d)
            c1_passed = len(missing) == 0
            c1_detail = "" if c1_passed else (
                f"{len(missing)} digit(s)/amount(s) in answers absent from profile: {missing}")
    c1 = ClauseResult(
        id="apply-packet-C1",
        description="Application Answers.md exists + answers traceable to profile fixture",
        passed=c1_passed,
        detail=c1_detail,
    )

    # C2 — runtime packet record is complete and queued.
    c2_passed = False
    c2_detail = ".apply-packet.json missing or invalid"
    if packet_path.exists():
        try:
            rec = json.loads(_read(packet_path))
            c2_passed = (
                rec.get("state") == "queued"
                and answers_path.exists()
                and bool(str(rec.get("remote_dir", "")).strip())
            )
            c2_detail = "" if c2_passed else f"incomplete packet record: {rec}"
        except ValueError as exc:
            c2_detail = f"parse error: {exc}"
    c2 = ClauseResult(
        id="apply-packet-C2",
        description=".apply-packet.json is complete and queued",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — recorded remote dir contains "_test"
    c3_passed = False
    c3_detail = ".apply-packet.json missing or unparseable"
    if packet_path.exists():
        try:
            rec = json.loads(_read(packet_path))
            remote = str(rec.get("remote_dir", ""))
            c3_passed = "_test" in remote
            c3_detail = "" if c3_passed else f"remote_dir={remote!r} lacks '_test'"
        except ValueError as exc:
            c3_detail = f"parse error: {exc}"
    c3 = ClauseResult(
        id="apply-packet-C3",
        description="Recorded remote dir contains '_test'",
        passed=c3_passed,
        detail=c3_detail,
    )

    return [c1, c2, c3]
