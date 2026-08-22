"""Shared ledger parser for find-contacts and enrich-contacts verifiers.

Both verifiers need to parse the `.contacts-ledger.md` table into structured
rows (columns: Name, Email, Confidence, Source, etc.). Kept here as a
standalone module so neither verifier duplicates the parsing, and
evals/common.py stays untouched (the runner's contract).

Each verify.py loads this via importlib (path-based) rather than a package
import, so the module resolves whether run via run_eval.py or directly.
"""
from __future__ import annotations

import re
from pathlib import Path

# Column names this parser recognizes. The fixture ledger at
# evals/fixtures/contacts-ledger.md uses these headers:
#   Name | Category | Practice (0-3) | Practice evidence | Loc (0-2) |
#   Title (0-2) | Tenure (0-1) | Snr (0-1) | Total | Conn-degree |
#   Source | Provenance | Rank | Email (inferred) | Confidence
HEADER_KEYS = {
    "name", "category", "source", "provenance", "rank", "email",
    "confidence", "total", "conn-degree",
}


def _split_row(line: str) -> list[str]:
    """Split a markdown table row into stripped cells, dropping leading/trailing pipes."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_divider(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", (c or "-")) for c in cells)


def parse_ledger(text: str) -> dict:
    """Parse a contacts-ledger markdown table.

    Returns:
      {
        "header": [col_name_lower, ...] | None,
        "rows":   [ {col_lower: cell_value, ...}, ... ],   # data rows only
        "raw_rows": [ "full line", ... ],                   # every non-empty | line
      }
    """
    header = None
    rows: list[dict] = []
    raw_rows: list[str] = []
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _split_row(line)
        raw_rows.append(line.strip())
        if len(cells) < 3:
            continue
        if _is_divider(cells):
            continue
        lowered = {c.lower() for c in cells}
        # Header row: contains "name" and one of the other known column words.
        if header is None and "name" in lowered and len(lowered & HEADER_KEYS) >= 2:
            header = [c.lower() for c in cells]
            continue
        if header is not None:
            # Pad/truncate to header length so dict zip never misaligns.
            padded = cells + [""] * (len(header) - len(cells))
            rows.append(dict(zip(header, padded[:len(header)])))
    return {"header": header, "rows": rows, "raw_rows": raw_rows}


def read_ledger(path: Path) -> dict:
    """Execute `read_ledger`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not path.exists():
        return {"header": None, "rows": [], "raw_rows": []}
    return parse_ledger(path.read_text(encoding="utf-8-sig", errors="ignore"))
