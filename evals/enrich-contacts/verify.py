"""Verifier for enrich-contacts (clauses enrich-contacts-C1..C3).

Reuses the shared evals/_ledger.py parser (same importlib load as
find-contacts) so the two verifiers never duplicate ledger parsing.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS_DIR))

from common import ClauseResult, EvalContext  # noqa: E402


def _load_ledger_parser():
    ledger_path = EVALS_DIR / "_ledger.py"
    spec = importlib.util.spec_from_file_location("_eval_ledger_ec", ledger_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_eval_ledger_ec"] = mod
    spec.loader.exec_module(mod)
    return mod


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def _hooks_section(text: str) -> list[str]:
    """Return the non-empty lines under a '## hooks' (case-insensitive) heading."""
    lines = text.splitlines()
    in_hooks = False
    body = []
    for line in lines:
        if re.match(r"^##\s+hooks", line.strip(), re.IGNORECASE):
            in_hooks = True
            continue
        if in_hooks and line.strip().startswith("## "):
            in_hooks = False
        if in_hooks and line.strip():
            body.append(line.strip())
    return body


def _has_no_hook_gap(context: EvalContext) -> bool:
    roots = [context.workspace / "runs", context.role / "runs"]
    for root in roots:
        if not root.is_dir():
            continue
        for trace in root.glob("*/trace.jsonl"):
            for line in _read(trace).splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                for gap in event.get("gaps", []) if isinstance(event, dict) else []:
                    if (
                        isinstance(gap, dict)
                        and gap.get("kind") in {"no-activity", "no-hook"}
                        and all(str(gap.get(field, "")).strip() for field in ("source", "detail"))
                    ):
                        return True
    return False


def verify(context: EvalContext) -> list[ClauseResult]:
    role = context.role
    ledger_path = role / ".contacts-ledger.md"
    ledger = _load_ledger_parser()
    parsed = ledger.read_ledger(ledger_path)

    # C1 — ledger parses after enrichment
    c1 = ClauseResult(
        id="enrich-contacts-C1",
        description="Ledger parses after enrichment",
        passed=parsed["header"] is not None and len(parsed["rows"]) > 0,
        detail="ledger missing or unparsable" if parsed["header"] is None else "",
    )

    # C2 — >=1 row marked with an activity source when enriched
    enrich_rows = [r for r in parsed["rows"]
                   if "enrich" in str(r.get("source", "")).lower()]
    c2_passed = len(enrich_rows) >= 1
    c2_detail = "" if c2_passed else "no rows with source containing 'enrich'"
    c2 = ClauseResult(
        id="enrich-contacts-C2",
        description=">=1 row records enrichment provenance",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — every hook line references a person already in the table
    names = [str(r.get("name", "")).strip() for r in parsed["rows"]
             if str(r.get("name", "")).strip()]
    hooks = _hooks_section(_read(ledger_path))
    if not hooks:
        c3_passed = _has_no_hook_gap(context)
        c3_detail = "" if c3_passed else (
            "hooks section missing and no structured no-activity/no-hook trace gap found"
        )
    else:
        bad = []
        for line in hooks:
            # Skip markdown table rows / bullet scaffolding; only check lines that
            # look like hook references (contain a name token or a pipe row).
            if not any(name and name.lower() in line.lower() for name in names):
                bad.append(line)
        c3_passed = len(bad) == 0
        c3_detail = "" if c3_passed else f"{len(bad)} hook line(s) reference no ledger person: {bad}"
    c3 = ClauseResult(
        id="enrich-contacts-C3",
        description="Every hook line references a person already in the table",
        passed=c3_passed,
        detail=c3_detail,
    )

    c4 = ClauseResult(
        id="enrich-contacts-C4",
        description="Live LinkedIn activity evidence resolves",
        status="NOT_RUN" if context.live else "BLOCKED",
        tier="live",
        detail="LinkedIn MCP unavailable; live clause was not executed",
    )
    return [c1, c2, c3, c4]
