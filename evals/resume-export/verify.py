"""Verifier for resume-export (clauses resume-export-C1..C3).

C1 reuses verify_artifacts.check_pdf for the PDF-present check; C2 reuses
the same stdlib page-count technique build_resume_pdf._count_pdf_pages uses
(regex over PDF bytes — no pypdf); C3 reuses the title-leak detection logic.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

# Bootstrap repo-root scripts/ onto sys.path for config.resume_glob_prefix.
REPO_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(REPO_SCRIPTS))
# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Bootstrap the e2e scripts dir for verify_artifacts.
E2E_SCRIPTS = Path(__file__).resolve().parents[2] / ".claude/skills/two-orchestrator-e2e-test/scripts"

from common import ClauseResult  # noqa: E402
from config import resume_glob_prefix  # noqa: E402

ROLE_FOLDER = "Acme - Senior Agent Builder"


def _load_verify_artifacts():
    va_path = E2E_SCRIPTS / "verify_artifacts.py"
    spec = importlib.util.spec_from_file_location("_eval_verify_artifacts_re", va_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_eval_verify_artifacts_re"] = mod
    spec.loader.exec_module(mod)
    return mod


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def _count_pdf_pages(pdf_path: Path) -> int:
    """Stdlib page count — same regex as build_resume_pdf._count_pdf_pages."""
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_path.read_bytes()))


def _detect_title_leak(md_text: str) -> int:
    """Re-implemented from build_resume_pdf._detect_title_leak so this verifier
    stays standalone (importing build_resume_pdf would pull in reportlab)."""
    saw_resume_title = False
    for ln in md_text.splitlines():
        stripped = ln.strip()
        if not stripped:
            continue
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", stripped)
        title_text = heading.group(1).strip() if heading else stripped
        if title_text.lower() == "resume":
            saw_resume_title = True
            continue
        if stripped.startswith("# "):
            return 1 if saw_resume_title else 0
    return 1 if saw_resume_title else 0


def verify(workspace: Path) -> list[ClauseResult]:
    workspace = Path(workspace)
    role = workspace / "Roles" / ROLE_FOLDER
    prefix = resume_glob_prefix()
    va = _load_verify_artifacts()

    # C1 — PDF exists next to the resume md (reuse check_pdf's present check)
    pdf_result = va.check_pdf(role, pages=None, title_leak=None, prefix=prefix)
    pdf_present = any(c.get("name") == "resume-pdf-present" and c.get("ok")
                      for c in pdf_result.get("checks", []))
    pdfs = sorted(role.glob(f"{prefix}*.pdf")) if role.is_dir() else []
    c1 = ClauseResult(
        id="resume-export-C1",
        description="PDF exists next to the resume md",
        passed=pdf_present,
        detail=f"no match for glob {prefix}*.pdf" if not pdf_present else f"found {pdfs[0].name}",
    )

    # C2 — one page
    c2_passed = False
    c2_detail = "no PDF to check"
    if pdfs:
        try:
            pages = _count_pdf_pages(pdfs[0])
            c2_passed = pages == 1
            c2_detail = "" if c2_passed else f"PAGES={pages}"
        except Exception as exc:
            c2_detail = f"read error: {exc}"
    c2 = ClauseResult(
        id="resume-export-C2",
        description="One page",
        passed=c2_passed,
        detail=c2_detail,
    )

    # C3 — no title leak (on the backing resume md)
    mds = sorted(role.glob(f"{prefix}*.md")) if role.is_dir() else []
    c3_passed = False
    c3_detail = "no resume md to check"
    if mds:
        leak = _detect_title_leak(_read(mds[0]))
        c3_passed = leak == 0
        c3_detail = "" if c3_passed else f"TITLE_LEAK={leak}"
    c3 = ClauseResult(
        id="resume-export-C3",
        description="No title leak",
        passed=c3_passed,
        detail=c3_detail,
    )

    return [c1, c2, c3]
