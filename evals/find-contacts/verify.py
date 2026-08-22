"""Verifier for find-contacts (clauses find-contacts-C1..C3).

Parses the ledger via the shared evals/_ledger.py module (loaded by path via
importlib so neither verifier duplicates the parser and common.py stays
untouched).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Bootstrap evals/ parent for `from common import ClauseResult` + _ledger.py.
EVALS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS_DIR))

from common import ClauseResult, EvalContext  # noqa: E402

CONFIDENCE_TAGS = ("verified", "inferred", "flagged")


def _load_ledger_parser():
    """Import evals/_ledger.py by path so both find-contacts and enrich-contacts
    share one parser without touching common.py."""
    ledger_path = EVALS_DIR / "_ledger.py"
    spec = importlib.util.spec_from_file_location("_eval_ledger_fc", ledger_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_eval_ledger_fc"] = mod
    spec.loader.exec_module(mod)
    return mod


def verify(context: EvalContext) -> list[ClauseResult]:
    """Execute `verify`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    role = context.role
    ledger_path = role / ".contacts-ledger.md"
    ledger = _load_ledger_parser()
    parsed = ledger.read_ledger(ledger_path)

    # C1 — .contacts-ledger.md exists with >=1 scored row
    c1 = ClauseResult(
        id="find-contacts-C1",
        description=".contacts-ledger.md exists with >=1 scored row",
        passed=ledger_path.exists() and len(parsed["rows"]) >= 1,
        detail="ledger missing" if not ledger_path.exists()
        else f"0 scored rows" if not parsed["rows"] else "",
    )

    # C2 — table parses with the required ledger schema
    header = parsed["header"]
    c2_passed = False
    c2_detail = "no header parsed"
    if header is not None:
        has_name = "name" in header
        has_email = any("email" in h for h in header)
        has_conf = "confidence" in header
        c2_passed = has_name and has_email and has_conf
        c2_detail = "" if c2_passed else (
            f"header missing required cols; have {header}")
    c2 = ClauseResult(
        id="find-contacts-C2",
        description="Table parses with required columns (name, email, confidence)",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — every email cell carries a confidence tag
    c3_passed = True
    c3_detail = ""
    if parsed["rows"]:
        for i, row in enumerate(parsed["rows"]):
            conf = str(row.get("confidence", "")).lower()
            if not any(tag in conf for tag in CONFIDENCE_TAGS):
                c3_passed = False
                c3_detail = f"row {i} confidence={row.get('confidence')!r} lacks a tag"
                break
    else:
        c3_passed = False
        c3_detail = "no rows to check"
    c3 = ClauseResult(
        id="find-contacts-C3",
        description="Every email cell carries a confidence tag (verified|inferred|flagged)",
        passed=c3_passed,
        detail=c3_detail,
    )

    missing_source = [
        index for index, row in enumerate(parsed["rows"])
        if not str(row.get("source", "")).strip()
    ]
    c4 = ClauseResult(
        id="find-contacts-C4",
        description="Every ledger contact has source provenance",
        passed=bool(parsed["rows"]) and not missing_source,
        detail=f"rows missing source: {missing_source}" if missing_source else "",
    )
    c5 = ClauseResult(
        id="find-contacts-C5",
        description="Live LinkedIn identity and employer evidence",
        status="NOT_RUN" if context.live else "BLOCKED",
        tier="live",
        detail="LinkedIn MCP unavailable; live clause was not executed",
    )
    return [c1, c2, c3, c4, c5]
