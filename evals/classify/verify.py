"""Verifier for classify (clauses classify-C1..C4).

Imports THEME_VOCAB and check_classify from verify_artifacts.py so the
per-skill tier and the e2e tier share one authority on classification validity.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ClauseResult, EvalContext, THEME_VOCAB, ARCHETYPE_VOCAB  # noqa: E402


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def verify(context: EvalContext) -> list[ClauseResult]:
    role = context.role
    cls_path = role / ".classification.json"
    jd_text = _normalize(_read(role / "Job Description.md"))

    # C1 — .classification.json exists
    c1 = ClauseResult(
        id="classify-C1",
        description=".classification.json exists in role folder",
        passed=cls_path.exists(),
        detail=str(cls_path) if not cls_path.exists() else "",
    )

    # C2 — JSON with non-empty themes + archetype + evidence
    c2_passed = False
    c2_detail = "file missing or unparseable"
    data = None
    if cls_path.exists():
        try:
            data = json.loads(_read(cls_path))
            themes = data.get("themes", [])
            if not isinstance(themes, list) or len(themes) == 0:
                c2_detail = "themes missing or empty"
            elif not isinstance(data.get("archetype"), str) or not data["archetype"].strip():
                c2_detail = "archetype missing or not a string"
            else:
                no_ev = [
                    t for t in themes
                    if not isinstance(t, dict) or not str(t.get("evidence", "")).strip()
                ]
                if no_ev:
                    c2_detail = f"{len(no_ev)} theme(s) missing evidence"
                else:
                    c2_passed = True
                    c2_detail = ""
        except ValueError as exc:
            c2_detail = f"parse error: {exc}"
    c2 = ClauseResult(
        id="classify-C2",
        description="JSON with non-empty themes + archetype + evidence",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — themes within the vocab
    c3_passed = False
    c3_detail = "no themes to check (see C2)"
    if data is not None:
        themes = data.get("themes", [])
        tags = [t.get("tag") for t in themes if isinstance(t, dict)]
        off = [t for t in tags if t not in THEME_VOCAB]
        c3_passed = len(off) == 0 and len(tags) > 0
        c3_detail = "" if c3_passed else f"off-vocab: {off}"
    c3 = ClauseResult(
        id="classify-C3",
        description="Themes within the vocab (THEME_VOCAB in verify_artifacts.py)",
        passed=c3_passed,
        detail=c3_detail,
    )

    # C4 — archetype is stable vocabulary
    archetype = data.get("archetype") if isinstance(data, dict) else None
    c4_passed = archetype in ARCHETYPE_VOCAB
    c4_detail = "" if c4_passed else f"off-vocab archetype: {archetype!r}"
    c4 = ClauseResult(
        id="classify-C4",
        description="Archetype is within stable vocabulary",
        passed=c4_passed,
        detail=c4_detail,
    )

    themes = data.get("themes", []) if isinstance(data, dict) else []
    c5 = ClauseResult(
        id="classify-C5",
        description="Classification contains 4–6 themes",
        passed=isinstance(themes, list) and 4 <= len(themes) <= 6,
        detail="" if isinstance(themes, list) and 4 <= len(themes) <= 6
        else f"theme count={len(themes) if isinstance(themes, list) else 'invalid'}",
    )

    unresolved = []
    if isinstance(themes, list) and jd_text:
        unresolved = [
            str(theme.get("evidence", ""))
            for theme in themes if isinstance(theme, dict)
            and _normalize(str(theme.get("evidence", ""))) not in jd_text
        ]
    c6_passed = (
        bool(jd_text) and isinstance(themes, list) and bool(themes)
        and all(isinstance(theme, dict) for theme in themes) and not unresolved
    )
    c6 = ClauseResult(
        id="classify-C6",
        description="Every theme evidence quote resolves against Job Description.md",
        passed=c6_passed,
        detail="Job Description.md missing/empty" if not jd_text
        else f"unresolved evidence: {unresolved}" if unresolved else "",
    )

    rationale = data.get("archetype_rationale") if isinstance(data, dict) else None
    c7 = ClauseResult(
        id="classify-C7",
        description="Archetype rationale is present",
        passed=isinstance(rationale, str) and bool(rationale.strip()),
        detail="" if isinstance(rationale, str) and rationale.strip()
        else "archetype_rationale missing or empty",
    )

    classified_ts = data.get("classified_ts") if isinstance(data, dict) else None
    ts_valid = False
    if isinstance(classified_ts, str) and classified_ts.strip():
        try:
            datetime.fromisoformat(classified_ts.replace("Z", "+00:00"))
            ts_valid = True
        except ValueError:
            pass
    c8 = ClauseResult(
        id="classify-C8",
        description="classified_ts is a valid ISO timestamp/date",
        passed=ts_valid,
        detail="" if ts_valid else f"classified_ts={classified_ts!r}",
    )
    return [c1, c2, c3, c4, c5, c6, c7, c8]
