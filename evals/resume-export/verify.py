"""Verifier for resume-export (clauses resume-export-C1..C3).

C1 reuses verify_artifacts.check_pdf for the PDF-present check; C2 reuses
the same stdlib page-count technique build_resume_pdf._count_pdf_pages uses
(regex over PDF bytes — no pypdf); C3 reuses the title-leak detection logic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Bootstrap repo-root scripts/ onto sys.path for config.resume_glob_prefix.
REPO_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(REPO_SCRIPTS))
# Bootstrap evals/ parent for `from common import ClauseResult`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ClauseResult, EvalContext  # noqa: E402
from config import load_profile, resume_glob_prefix  # noqa: E402


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


def verify(context: EvalContext) -> list[ClauseResult]:
    """Execute `verify`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    role = context.role
    prefix = resume_glob_prefix(load_profile(context.profile) if context.profile else None)

    # C1 — PDF exists next to a matching resume md.
    pdfs = sorted(role.glob(f"{prefix}*.pdf")) if role.is_dir() else []
    mds = sorted(role.glob(f"{prefix}*.md")) if role.is_dir() else []
    if not pdfs and not mds and context.profile is None and role.is_dir():
        pdfs = sorted(role.glob("* Resume - *.pdf"))
        mds = sorted(role.glob("* Resume - *.md"))
    pdf_present = bool(pdfs) and any(pdf.with_suffix(".md") in mds for pdf in pdfs)
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
