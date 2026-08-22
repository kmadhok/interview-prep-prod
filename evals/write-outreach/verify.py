"""Verifier for write-outreach (clauses write-outreach-C1..C3).

C1 checks Cold Outreach.md has two intro sections; C2 checks every To:
address is in Verified Emails.md; C3 checks zero placeholder leaks.
"""
from __future__ import annotations

import re
import json
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS_DIR))

from common import ClauseResult, EvalContext  # noqa: E402
PLACEHOLDER_LEAKS = ["[NUMBER?]", "<user_", "{name}", "[slot", "TBD"]
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_INTRO_HEADING_RE = re.compile(r"^#{1,2}\s+.*intro", re.IGNORECASE)
_TO_RE = re.compile(r"^To:\s*(.*)", re.IGNORECASE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def _verified_emails(role: Path) -> set[str]:
    verified_path = role / "Verified Emails.md"
    if not verified_path.exists():
        return set()
    return {e.lower() for e in _EMAIL_RE.findall(_read(verified_path))}


def verify(context: EvalContext) -> list[ClauseResult]:
    """Execute `verify`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    role = context.role
    outreach_path = role / "Cold Outreach.md"

    # C1 — Cold Outreach.md exists with two intro sections
    c1_passed = False
    c1_detail = "Cold Outreach.md missing"
    if outreach_path.exists():
        text = _read(outreach_path)
        intros = [ln for ln in text.splitlines() if _INTRO_HEADING_RE.match(ln.strip())]
        c1_passed = len(intros) >= 2
        c1_detail = "" if c1_passed else f"only {len(intros)} intro section(s)"
    c1 = ClauseResult(
        id="write-outreach-C1",
        description="Cold Outreach.md exists with two intro sections",
        passed=c1_passed,
        detail=c1_detail,
    )

    # C2 — every To: address appears in Verified Emails.md
    verified = _verified_emails(role)
    to_addresses: list[str] = []
    if outreach_path.exists():
        for line in _read(outreach_path).splitlines():
            m = _TO_RE.match(line.strip())
            if m:
                to_addresses.extend(_EMAIL_RE.findall(m.group(1)))
    c2_passed = True
    c2_detail = ""
    if not to_addresses:
        c2_passed = False
        c2_detail = "no To: addresses found in Cold Outreach.md"
    else:
        missing = [a for a in to_addresses if a.lower() not in verified]
        c2_passed = len(missing) == 0
        c2_detail = "" if c2_passed else f"addresses not in Verified Emails.md: {missing}"
    c2 = ClauseResult(
        id="write-outreach-C2",
        description="Every To: address appears in Verified Emails.md",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — zero placeholder leaks
    c3_passed = True
    c3_detail = ""
    if outreach_path.exists():
        text = _read(outreach_path)
        for marker in PLACEHOLDER_LEAKS:
            if marker in text:
                c3_passed = False
                c3_detail = f"contains {marker!r}"
                break
    else:
        c3_passed = False
        c3_detail = "Cold Outreach.md missing"
    c3 = ClauseResult(
        id="write-outreach-C3",
        description="Zero placeholder leaks",
        passed=c3_passed,
        detail=c3_detail,
    )

    drafts_path = next(
        (path for path in (role / ".drafts.json", role / "_draft.json") if path.exists()),
        role / ".drafts.json",
    )
    drafts = []
    if drafts_path.exists():
        try:
            value = json.loads(_read(drafts_path))
            drafts = value if isinstance(value, list) else [value]
        except ValueError:
            drafts = []
    c4_passed = bool(drafts) and all(
        isinstance(draft, dict) and draft.get("id") and not draft.get("sent", False)
        for draft in drafts
    )
    c4 = ClauseResult(
        id="write-outreach-C4",
        description="Fixture draft artifacts are present and unsent",
        passed=c4_passed,
        detail="" if c4_passed else "missing/invalid .drafts.json or a draft is marked sent",
    )
    c5 = ClauseResult(
        id="write-outreach-C5",
        description="Live Gmail Drafts and Sent-state evidence",
        status="NOT_RUN" if context.live else "BLOCKED",
        tier="live",
        detail="external Gmail execution disabled; fixture never-send clause evaluated",
    )
    return [c1, c2, c3, c4, c5]
