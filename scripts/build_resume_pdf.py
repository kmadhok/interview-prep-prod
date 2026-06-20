"""Convert a Kanu Madhok resume Markdown into a PDF matching the canonical layout.

Usage:
    python3 scripts/build_resume_pdf.py path/to/Resume.md
    python3 scripts/build_resume_pdf.py --all          # all .md without paired .pdf
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path("/Users/kanumadhok/Documents/Claude/Projects/Interview Prep")
LINK = HexColor("#1A6FB3")

EXP_HEADERS = {"PROFESSIONAL EXPERIENCE", "EXPERIENCE"}
SKILLS_HEADERS = {"SKILLS", "TECHNICAL SKILLS"}
PROJECT_HEADERS = {"SELECTED PROJECT", "SELECTED PROJECTS", "PROJECTS"}
EDU_HEADERS = {"EDUCATION"}
HONORS_HEADERS = {"HONORS", "AWARDS"}
SKIP_HEADERS_PREFIX = ("TAILORING NOTES",)

TIERS = [
    {"body_pt": 10.5, "margin_in": 0.65},
    {"body_pt": 10.0, "margin_in": 0.58},
    {"body_pt": 9.5, "margin_in": 0.50},
    {"body_pt": 9.25, "margin_in": 0.45},
    {"body_pt": 9.0, "margin_in": 0.42},
]


def _leading(font_size: float) -> float:
    return round(font_size * 1.24, 2)


def build_styles(body_pt: float) -> dict[str, ParagraphStyle]:
    name_pt = body_pt + 10.5
    section_pt = body_pt + 1
    meta_pt = body_pt - 0.5
    return {
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=name_pt, leading=_leading(name_pt),
            alignment=TA_CENTER, spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "contact", fontName="Helvetica", fontSize=meta_pt, leading=_leading(meta_pt),
            alignment=TA_CENTER, spaceAfter=8,
        ),
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=section_pt, leading=_leading(section_pt),
            alignment=TA_LEFT, spaceBefore=6, spaceAfter=2, textColor=black,
        ),
        "company": ParagraphStyle(
            "company", fontName="Helvetica-Bold", fontSize=section_pt, leading=_leading(section_pt),
            alignment=TA_LEFT,
        ),
        "city_date": ParagraphStyle(
            "city_date", fontName="Helvetica-Oblique", fontSize=meta_pt, leading=_leading(meta_pt),
            alignment=TA_RIGHT,
        ),
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Oblique", fontSize=meta_pt, leading=_leading(meta_pt),
            alignment=TA_LEFT, spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=body_pt, leading=_leading(body_pt),
            alignment=TA_LEFT, leftIndent=14, bulletIndent=2, spaceAfter=1.5,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=body_pt, leading=_leading(body_pt),
            alignment=TA_LEFT, spaceAfter=1.5,
        ),
    }


# ---------- markdown inline -> reportlab HTML ----------

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_BOLDU_RE = re.compile(r"__([^_]+)__")
_ITAL_AST_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_ITAL_UND_RE = re.compile(r"(?<!_)_([^_\n]+)_(?!_)")


def md_inline(text: str) -> str:
    """Convert basic markdown inline syntax to ReportLab miniHTML."""
    # Escape ReportLab-meaningful chars first
    out = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Re-allow the right-arrow that authors type literally as → already unicode-fine.
    # Links [text](url)
    out = _LINK_RE.sub(
        lambda m: f'<a href="{m.group(2)}" color="{LINK.hexval()}"><u>{m.group(1)}</u></a>',
        out,
    )
    # Bold
    out = _BOLD_RE.sub(r"<b>\1</b>", out)
    out = _BOLDU_RE.sub(r"<b>\1</b>", out)
    # Italic
    out = _ITAL_AST_RE.sub(r"<i>\1</i>", out)
    out = _ITAL_UND_RE.sub(r"<i>\1</i>", out)
    return out


# ---------- layout helpers ----------

def header_row(left_html: str, right_html: str, left_style, right_style,
               col_split: float = 4.7, frame_width_in: float = 7.2):
    # The table must fill the full frame width and left-align within it, or it
    # centers itself (reportlab default hAlign=CENTER) and the company name drifts
    # right by half the (frame - table) gap — an amount that varies per font/margin
    # tier. Track the real frame width and pin the right column to the right margin.
    right_w = frame_width_in - col_split
    t = Table(
        [[Paragraph(left_html, left_style), Paragraph(right_html, right_style)]],
        colWidths=[col_split * inch, right_w * inch],
        hAlign="LEFT",
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def section_header_flow(title: str, styles: dict[str, ParagraphStyle]):
    return [
        Spacer(1, 2),
        Paragraph(title, styles["section"]),
        HRFlowable(width="100%", thickness=0.6, color=black,
                   spaceBefore=0, spaceAfter=3),
    ]


def bullet_flow(text: str, styles: dict[str, ParagraphStyle]):
    return Paragraph(f"• {md_inline(text)}", styles["bullet"])


# ---------- markdown parser ----------

DATE_HINT_RE = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|\d{4}|Present)",
    re.IGNORECASE,
)


def split_company_line(header: str):
    """Parse `### Company — City, ST · Date – Date` into (company, city_date).

    Falls back to (header, "") when no ' — ' separator or no date hint on right side.
    """
    # Split on em-dash (— = U+2014)
    parts = header.split("—")
    if len(parts) < 2:
        return header.strip(), ""
    # Try last segment as city/date if it has a date marker or 'Present'
    last = parts[-1].strip()
    if DATE_HINT_RE.search(last):
        company = "—".join(parts[:-1]).strip()
        return company, last
    return header.strip(), ""


def parse_resume(md_text: str):
    """Return a structured dict: name, contact_html, sections list."""
    lines = md_text.splitlines()

    # Strip code fences and blockquote NOTE lines anywhere
    cleaned = []
    in_code = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Skip blockquote NOTE callouts at top
        if ln.lstrip().startswith(">"):
            continue
        cleaned.append(ln)
    lines = cleaned

    # Name: first H1
    name = "Kanu Madhok"
    contact_raw = ""
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            raw_name = ln[2:].strip()
            # Title-case fix for shouted KANU MADHOK
            name = raw_name.title() if raw_name.isupper() else raw_name
            # Next non-blank line that isn't italic helper text is contact
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                contact_raw = lines[j].strip()
            body_start = j + 1
            break

    # Convert contact links — keep ' • ' separators
    contact_html = md_inline(contact_raw).replace(" • ", " &nbsp;•&nbsp; ")

    # Parse sections by ## headings
    sections = []
    cur_title = None
    cur_lines: list[str] = []

    def flush():
        if cur_title is not None:
            sections.append((cur_title, cur_lines[:]))

    skip_section = False
    for ln in lines[body_start:]:
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            flush()
            cur_title = m.group(1).strip()
            cur_lines = []
            skip_section = any(cur_title.upper().startswith(p) for p in SKIP_HEADERS_PREFIX)
            if skip_section:
                cur_title = None  # discard
            continue
        # Skip the italic helper note ("Text source for the .docx / .pdf...") near top before first ##
        if cur_title is None:
            continue
        # Drop horizontal rules
        if re.match(r"^\s*---\s*$", ln):
            continue
        cur_lines.append(ln)
    flush()

    return name, contact_html, sections


def parse_experience(section_lines: list[str]):
    """Return list of jobs: [{company, city_date, title, bullets}].

    Handles two structural variants:
      A) ### Company — City, ST · Date – Date
         _Role_
         - bullet ...
      B) ### Company — Role
         *Date · City*
         - bullet ...
    """
    jobs = []
    cur = None

    def push():
        nonlocal cur
        if cur is not None:
            jobs.append(cur)
        cur = None

    for raw in section_lines:
        ln = raw.rstrip()
        if not ln.strip():
            continue
        h = re.match(r"^###\s+(.+?)\s*$", ln)
        if h:
            push()
            header = h.group(1).strip()
            company, city_date = split_company_line(header)
            cur = {"company": company, "city_date": city_date, "title": "", "bullets": []}
            continue
        if cur is None:
            continue
        # Italic line: either title (variant A) or date·city (variant B)
        ital = re.match(r"^\s*[_*](.+?)[_*]\s*$", ln)
        if ital and not cur["bullets"]:
            text = ital.group(1).strip()
            # If we don't have city_date yet AND this line has a date hint, treat as city_date
            if not cur["city_date"] and DATE_HINT_RE.search(text):
                cur["city_date"] = text
            else:
                # Treat as role/title (append if there's already one)
                if cur["title"]:
                    cur["title"] += " — " + text
                else:
                    cur["title"] = text
            continue
        # Bullet
        b = re.match(r"^[-*]\s+(.+?)\s*$", ln)
        if b:
            cur["bullets"].append(b.group(1).strip())
            continue
        # Free-floating paragraph (e.g., H.I.G. summary line before bullets) — append as
        # a leading bullet-less paragraph stored at top of bullets list to keep flow simple.
        if not cur["bullets"]:
            # Stash as a pseudo-bullet without leading dot; we'll detect by sentinel.
            cur.setdefault("preamble", []).append(ln.strip())
    push()
    return jobs


def parse_education(section_lines: list[str]):
    """Each non-empty line treated as one row. Try to split on right side (Chicago, IL)."""
    rows = []
    for raw in section_lines:
        ln = raw.strip()
        if not ln:
            continue
        m_bul = re.match(r"^[-*]\s+(.+)$", ln)
        if m_bul:
            ln = m_bul.group(1).strip()
        # Try to peel off trailing " — Chicago, IL"
        m = re.match(r"^(.*?)\s+—\s+([A-Z][A-Za-z\s.]*,\s*[A-Z]{2})\s*$", ln)
        if m:
            left, right = m.group(1).strip(), m.group(2).strip()
        else:
            left, right = ln, ""
        # Bold the school name (first part before " — ") if not already bold
        if "**" not in left:
            # Split first em-dash and bold the school
            parts = left.split(" — ", 1)
            if len(parts) == 2:
                left = f"**{parts[0]}** — {parts[1]}"
        rows.append((left, right))
    return rows


def parse_lines_generic(section_lines: list[str]):
    """For SKILLS/HONORS/SELECTED PROJECT — return a list of ('bullet'|'para', text)."""
    out = []
    for raw in section_lines:
        ln = raw.rstrip()
        if not ln.strip():
            continue
        b = re.match(r"^[-*]\s+(.+?)\s*$", ln)
        if b:
            out.append(("bullet", b.group(1).strip()))
        else:
            out.append(("para", ln.strip()))
    return out


# ---------- builder ----------

def _detect_title_leak(md_text: str) -> int:
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


def _count_pdf_pages(pdf_path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_path.read_bytes()))


def _build_story(md_text: str, styles: dict[str, ParagraphStyle], frame_width_in: float = 7.2):
    name, contact_html, sections = parse_resume(md_text)
    story = []
    story.append(Paragraph(name, styles["name"]))
    if contact_html:
        story.append(Paragraph(contact_html, styles["contact"]))

    for title, lines in sections:
        up = title.upper()
        if up in EXP_HEADERS:
            story.extend(section_header_flow("PROFESSIONAL EXPERIENCE", styles))
            jobs = parse_experience(lines)
            for idx, job in enumerate(jobs):
                if idx > 0:
                    story.append(Spacer(1, 3))
                story.append(header_row(
                    f"<b>{md_inline(job['company'])}</b>",
                    f"<i>{md_inline(job['city_date'])}</i>" if job["city_date"] else "",
                    styles["company"], styles["city_date"],
                    col_split=4.7, frame_width_in=frame_width_in,
                ))
                if job.get("title"):
                    story.append(Paragraph(f"<i>{md_inline(job['title'])}</i>", styles["title"]))
                for p in job.get("preamble", []):
                    story.append(Paragraph(md_inline(p), styles["body"]))
                for b in job["bullets"]:
                    story.append(bullet_flow(b, styles))
        elif up in PROJECT_HEADERS:
            story.extend(section_header_flow("SELECTED PROJECT", styles))
            for kind, text in parse_lines_generic(lines):
                if kind == "bullet":
                    story.append(bullet_flow(text, styles))
                else:
                    story.append(Paragraph(md_inline(text), styles["body"]))
        elif up in SKILLS_HEADERS:
            story.extend(section_header_flow("SKILLS", styles))
            for kind, text in parse_lines_generic(lines):
                # Bold the lead label "X:" if pattern matches and not already bold
                if kind == "para":
                    m = re.match(r"^([A-Z][^:]{1,40}):\s+(.+)$", text)
                    if m and "**" not in text:
                        text = f"**{m.group(1)}:** {m.group(2)}"
                    story.append(Paragraph(md_inline(text), styles["body"]))
                else:
                    story.append(bullet_flow(text, styles))
        elif up in EDU_HEADERS:
            story.extend(section_header_flow("EDUCATION", styles))
            for left, right in parse_education(lines):
                story.append(header_row(
                    md_inline(left),
                    f"<i>{md_inline(right)}</i>" if right else "",
                    styles["body"], styles["city_date"],
                    col_split=5.5, frame_width_in=frame_width_in,
                ))
        elif up in HONORS_HEADERS:
            story.extend(section_header_flow("HONORS", styles))
            for kind, text in parse_lines_generic(lines):
                if kind == "bullet":
                    story.append(bullet_flow(text, styles))
                else:
                    story.append(Paragraph(md_inline(text), styles["body"]))
        else:
            # Unknown section — render as a generic section
            story.extend(section_header_flow(up, styles))
            for kind, text in parse_lines_generic(lines):
                if kind == "bullet":
                    story.append(bullet_flow(text, styles))
                else:
                    story.append(Paragraph(md_inline(text), styles["body"]))
    return name, story


def _render_pdf_once(md_text: str, pdf_path: Path, tier: dict[str, float]) -> None:
    styles = build_styles(tier["body_pt"])
    frame_width_in = 8.5 - 2 * tier["margin_in"]
    name, story = _build_story(md_text, styles, frame_width_in=frame_width_in)
    margin = tier["margin_in"] * inch

    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=f"{name} Resume",
        author=name,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
        id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates(PageTemplate(id="all", frames=[frame]))

    doc.build(story)


def build_pdf(md_path: Path, pdf_path: Path) -> tuple[int, int, dict[str, float]]:
    md_text = md_path.read_text(encoding="utf-8")
    title_leak = _detect_title_leak(md_text)
    last_error = None
    last_success = None
    floor_tier = TIERS[-1]

    for tier in TIERS:
        try:
            _render_pdf_once(md_text, pdf_path, tier)
            pages = _count_pdf_pages(pdf_path)
        except Exception as e:
            last_error = e
            continue

        last_success = (pages, tier)
        if pages <= 1:
            return pages, title_leak, tier

    if last_success is not None:
        pages, tier = last_success
        if tier is floor_tier:
            return pages, title_leak, tier
    raise RuntimeError(f"reportlab failed before a floor render: {last_error}")


# ---------- discovery ----------

SKIP_FILES = {"Resume Achievements Master.md", "Resume Claims To Verify.md"}


def discover_unpaired() -> list[Path]:
    out = []
    for sub in sorted(ROOT.iterdir()):
        if not sub.is_dir():
            continue
        for f in sorted(sub.iterdir()):
            if not f.is_file():
                continue
            if f.name in SKIP_FILES:
                continue
            if not re.search(r"(?i)resume.*\.md$", f.name):
                continue
            paired = f.with_suffix(".pdf")
            if not paired.exists():
                out.append(f)
    return out


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _title_leak_for_path(md_path: Path):
    try:
        return _detect_title_leak(md_path.read_text(encoding="utf-8"))
    except Exception:
        return "NA"


def _emit_contract(pages, title_leak, prefix: str | None = None) -> None:
    line = f"PAGES={pages} TITLE_LEAK={title_leak}"
    if prefix:
        line = f"{prefix} {line}"
    print(line)


def _run(argv: list[str] | None = None):
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path", nargs="?", help="Specific .md to convert")
    ap.add_argument("--all", action="store_true", help="All unpaired .md resumes")
    ap.add_argument("--out", help="Output .pdf path (single-file mode only)")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2, [(None, "NA", "NA")]

    if args.all:
        targets = discover_unpaired()
        if not targets:
            print("No unpaired resume markdowns found.")
            return 0, [(None, "NA", "NA")]
        print(f"Building {len(targets)} resume PDFs...")
        contracts = []
        rc = 0
        for md in targets:
            pdf = md.with_suffix(".pdf")
            try:
                pages, title_leak, _ = build_pdf(md, pdf)
                print(f"  ✓ {pdf.relative_to(ROOT)}")
                contracts.append((_display_path(pdf), pages, title_leak))
            except Exception as e:
                print(f"  ✗ {md.relative_to(ROOT)} — {e}", file=sys.stderr)
                contracts.append((_display_path(pdf), "NA", _title_leak_for_path(md)))
                rc = 1
        return rc, contracts

    if not args.md_path:
        ap.print_usage(sys.stderr)
        print("build_resume_pdf.py: error: provide md_path or --all", file=sys.stderr)
        return 2, [(None, "NA", "NA")]
    md = Path(args.md_path)
    pdf = Path(args.out) if args.out else md.with_suffix(".pdf")
    try:
        pages, title_leak, _ = build_pdf(md, pdf)
        print(f"Wrote {pdf}")
        return 0, [(None, pages, title_leak)]
    except Exception as e:
        print(f"ERROR: {md} — {e}", file=sys.stderr)
        return 1, [(None, "NA", _title_leak_for_path(md))]


def main():
    rc, contracts = _run()
    for prefix, pages, title_leak in contracts:
        _emit_contract(pages, title_leak, prefix)
    return rc


if __name__ == "__main__":
    sys.exit(main())
