"""Verifier for classify (clauses classify-C1..C4).

Imports THEME_VOCAB and check_classify from verify_artifacts.py so the
per-skill tier and the e2e tier share one authority on classification validity.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Bootstrap the e2e scripts dir so verify_artifacts is importable by path.
E2E_SCRIPTS = Path(__file__).resolve().parents[2] / ".claude/skills/two-orchestrator-e2e-test/scripts"

from common import ClauseResult  # noqa: E402

ROLE_FOLDER = "Acme - Senior Agent Builder"


def _load_verify_artifacts():
    """Import verify_artifacts.py from the e2e scripts dir by path."""
    va_path = E2E_SCRIPTS / "verify_artifacts.py"
    spec = importlib.util.spec_from_file_location("_eval_verify_artifacts", va_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_eval_verify_artifacts"] = mod
    spec.loader.exec_module(mod)
    return mod


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def verify(workspace: Path) -> list[ClauseResult]:
    workspace = Path(workspace)
    role = workspace / "Roles" / ROLE_FOLDER
    cls_path = role / ".classification.json"
    va = _load_verify_artifacts()
    THEME_VOCAB = va.THEME_VOCAB

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
                no_ev = [t for t in themes
                         if isinstance(t, dict) and not str(t.get("evidence", "")).strip()]
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

    # C4 — passes verify_artifacts.check_classify
    c4_passed = False
    c4_detail = "check_classify returned no checks"
    if role.is_dir():
        result = va.check_classify(role)
        checks = result.get("checks", [])
        failed = [c for c in checks if not c.get("ok")]
        c4_passed = len(failed) == 0 and len(checks) > 0
        c4_detail = "" if c4_passed else "; ".join(
            f"{c.get('name')}: {c.get('detail')}" for c in failed)
    c4 = ClauseResult(
        id="classify-C4",
        description="Passes verify_artifacts.check_classify",
        passed=c4_passed,
        detail=c4_detail,
    )

    return [c1, c2, c3, c4]
