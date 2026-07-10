"""Verifier for verify-emails (clauses verify-emails-C1..C3).

C3 implements the derived-inferred rule: every address in Verified Emails.md
either appears verbatim in the ledger or ends with a domain present in the
ledger.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS_DIR))

from common import ClauseResult  # noqa: E402

ROLE_FOLDER = "Acme - Senior Agent Builder"
STATUSES = ("verified", "inferred", "flagged")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def _load_ledger_parser():
    ledger_path = EVALS_DIR / "_ledger.py"
    spec = importlib.util.spec_from_file_location("_eval_ledger_ve", ledger_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_eval_ledger_ve"] = mod
    spec.loader.exec_module(mod)
    return mod


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def _row_emails_and_status(line: str) -> tuple[list[str], str]:
    """Return (emails in line, status word in line) for a table row."""
    emails = _EMAIL_RE.findall(line)
    lowered = line.lower()
    status = next((s for s in STATUSES if s in lowered), "")
    return emails, status


def verify(workspace: Path) -> list[ClauseResult]:
    workspace = Path(workspace)
    role = workspace / "Roles" / ROLE_FOLDER
    verified_path = role / "Verified Emails.md"
    ledger_path = role / ".contacts-ledger.md"
    ledger = _load_ledger_parser()
    parsed = ledger.read_ledger(ledger_path)

    # C1 — Verified Emails.md exists
    c1 = ClauseResult(
        id="verify-emails-C1",
        description="Verified Emails.md exists",
        passed=verified_path.exists(),
        detail=str(verified_path) if not verified_path.exists() else "",
    )

    # C2 — every entry line has a status
    c2_passed = True
    c2_detail = ""
    entry_lines = []
    if verified_path.exists():
        for line in _read(verified_path).splitlines():
            if not line.strip().startswith("|"):
                continue
            emails, status = _row_emails_and_status(line)
            if emails and not status:
                c2_passed = False
                c2_detail = f"row with email(s) {emails} has no status"
                break
            if emails:
                entry_lines.append(line)
        if c2_passed and not entry_lines:
            c2_passed = False
            c2_detail = "no entry rows with emails found"
    else:
        c2_passed = False
        c2_detail = "Verified Emails.md missing"
    c2 = ClauseResult(
        id="verify-emails-C2",
        description="Every entry line has a status (verified|inferred|flagged)",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — every address appears in the ledger or ends with a ledger domain
    ledger_emails = set()
    ledger_domains = set()
    for row in parsed["rows"]:
        cell = str(row.get("email", ""))
        for e in _EMAIL_RE.findall(cell):
            ledger_emails.add(e.lower())
            if "@" in e:
                ledger_domains.add(e.split("@", 1)[1].lower())
        # Also scan the whole row text for emails (some ledgers put the email
        # in a column not named 'email' in the fixture).
        for h, v in row.items():
            for e in _EMAIL_RE.findall(str(v)):
                ledger_emails.add(e.lower())
                if "@" in e:
                    ledger_domains.add(e.split("@", 1)[1].lower())

    c3_passed = True
    c3_detail = ""
    for line in entry_lines:
        emails, _ = _row_emails_and_status(line)
        for e in emails:
            el = e.lower()
            in_ledger = el in ledger_emails
            domain = el.split("@", 1)[1] if "@" in el else ""
            domain_ok = domain in ledger_domains
            if not (in_ledger or domain_ok):
                c3_passed = False
                c3_detail = f"{e} not in ledger and domain {domain!r} not in ledger"
                break
        if not c3_passed:
            break
    if not entry_lines:
        c3_passed = False
        c3_detail = "no entry rows to check"
    c3 = ClauseResult(
        id="verify-emails-C3",
        description="Every address appears in the ledger or ends with a ledger domain",
        passed=c3_passed,
        detail=c3_detail,
    )

    return [c1, c2, c3]
