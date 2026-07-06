#!/usr/bin/env python3
"""Prepare resume PDF render artifacts and deterministic verification gates.

Usage:
    python3 scripts/verify_resume.py "/abs/or/rel/path/Resume.pdf"

This script does not call an LLM. It rasterizes the target resume and the BCG X
gold-standard reference, then emits a JSON packet for a vision agent or human.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from config import WORKSPACE as ROOT, resume_glob_prefix

# Gold-standard reference lives in the workspace, relative to the repo root. The
# filename prefix follows the profile's resume pattern; the reference itself is
# opt-in via --reference, so a missing default just SKIPs (see _run).
DEFAULT_REFERENCE = (
    "Roles/BCG X - Senior AI Factory Product Builder/"
    f"{resume_glob_prefix()}BCG X Senior AI Factory.pdf"
)
DEFAULT_OUT_ROOT = Path("/tmp/resume_verify")

VISUAL_CRITERIA = [
    "Name is centered, large, bold at the very top — and there is NO 'Resume' title line above the name",
    "Contact line is centered directly under the name",
    "Each section header (PROFESSIONAL EXPERIENCE, SELECTED PROJECT, SKILLS, EDUCATION) is uppercase with a full-width horizontal rule under it",
    "Each job entry has the company in bold on the LEFT and the location · dates in italic on the RIGHT, on the SAME line (two-column, right-aligned dates — NOT wrapping onto the next line)",
    "Role/title appears in italic on its own line below the company",
    "Bullets use a real bullet glyph, are tight, and no header text wraps oddly",
    "SKILLS section uses a bold inline label (e.g. 'Agent stack:') followed by the list",
    "EDUCATION is two-column: school + degree on the left, location on the right, one row per school (NOT a run-on paragraph)",
    "The whole resume fits on exactly one page",
]

VERDICT_INSTRUCTIONS = (
    "A vision agent should open each page PNG and the reference PNG, then return "
    "PASS only if ALL deterministic gates pass AND all visual_criteria hold. "
    "On FAIL, list each failing criterion with a concrete reason."
)


def _resolve_cli_path(path: str, base: Path | None = None) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p.resolve()
    return ((base or Path.cwd()) / p).resolve()


def _default_out_dir(target_pdf: Path) -> Path:
    return DEFAULT_OUT_ROOT / target_pdf.stem


def _count_pages(pdf_path: Path) -> int:
    try:
        return len(re.findall(rb"/Type\s*/Page[^s]", pdf_path.read_bytes()))
    except OSError:
        return 0


def _title_leak_gate(pdf_path: Path) -> dict[str, object]:
    if not shutil.which("pdftotext"):
        return {
            "pass": None,
            "detail": "pdftotext missing; could not check first text line.",
        }

    try:
        proc = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return {
            "pass": None,
            "detail": f"pdftotext failed; could not check first text line: {exc}",
        }

    first = ""
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if stripped:
            first = stripped
            break

    if first.lower() == "resume":
        return {
            "pass": False,
            "detail": "First non-empty PDF text line is standalone 'Resume'.",
        }
    if first:
        return {
            "pass": True,
            "detail": f"First non-empty PDF text line is {first!r}.",
        }
    return {
        "pass": True,
        "detail": "No non-empty PDF text line was extracted; no standalone title leak detected.",
    }


def _deterministic_gates(pdf_path: Path, page_count: int) -> dict[str, dict[str, object]]:
    return {
        "one_page": {
            "pass": page_count == 1,
            "detail": f"Detected {page_count} page(s).",
        },
        "title_leak": _title_leak_gate(pdf_path),
    }


def _clean_generated_files(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("page-*.png", "reference-*.png", "verify.json"):
        for path in out_dir.glob(pattern):
            try:
                path.unlink()
            except OSError:
                pass


def _run_pdftoppm(args: list[str]) -> bool:
    try:
        subprocess.run(args, capture_output=True, text=True, check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"SKIP: pdftoppm failed: {exc}", file=sys.stderr)
        return False


def _png_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"-(\d+)\.png$", path.name)
    if match:
        return int(match.group(1)), path.name
    return 10**9, path.name


def _rasterize(target_pdf: Path, reference_pdf: Path, out_dir: Path) -> tuple[list[str], str]:
    _clean_generated_files(out_dir)
    reference_png = out_dir / "reference-1.png"

    if not _run_pdftoppm(["pdftoppm", "-png", "-r", "150", str(target_pdf), str(out_dir / "page")]):
        return [], str(reference_png)
    _run_pdftoppm(
        [
            "pdftoppm",
            "-png",
            "-r",
            "150",
            "-f",
            "1",
            "-l",
            "1",
            str(reference_pdf),
            str(out_dir / "reference"),
        ]
    )

    page_pngs = [str(p) for p in sorted(out_dir.glob("page-*.png"), key=_png_sort_key)]
    return page_pngs, str(reference_png)


def _build_packet(
    target_pdf: Path,
    page_count: int,
    page_pngs: list[str],
    reference_png: str,
    deterministic: dict[str, dict[str, object]],
) -> dict[str, object]:
    return {
        "target_pdf": str(target_pdf),
        "page_count": page_count,
        "page_pngs": page_pngs,
        "reference_png": reference_png,
        "deterministic": deterministic,
        "visual_criteria": VISUAL_CRITERIA,
        "verdict_instructions": VERDICT_INSTRUCTIONS,
    }


def _write_packet(packet: dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(packet, indent=2)
    (out_dir / "verify.json").write_text(text + "\n", encoding="utf-8")
    print(text)


def _ready_value(value: object) -> str:
    if value is True:
        return "1"
    if value is False:
        return "0"
    return "NA"


def _emit_ready(packet: dict[str, object]) -> None:
    deterministic = packet["deterministic"]
    one_page = deterministic["one_page"]["pass"]
    title_leak_pass = deterministic["title_leak"]["pass"]
    title_leak = None if title_leak_pass is None else not title_leak_pass
    page_pngs = packet["page_pngs"]
    png = page_pngs[0] if page_pngs else "NA"
    print(
        "VERIFY_READY "
        f"pages={packet['page_count']} "
        f"one_page={_ready_value(one_page)} "
        f"title_leak={_ready_value(title_leak)} "
        f"png={png}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and verify a resume PDF.")
    parser.add_argument("target_pdf", help="Resume PDF to verify.")
    parser.add_argument(
        "--out-dir",
        help="Output directory for PNGs and verify.json. Defaults under /tmp/resume_verify/<basename>.",
    )
    parser.add_argument(
        "--reference",
        default=DEFAULT_REFERENCE,
        help="Gold-standard reference PDF. Relative paths resolve from the repo root.",
    )
    return parser.parse_args()


def _run() -> int:
    args = parse_args()
    target_pdf = _resolve_cli_path(args.target_pdf)
    reference_pdf = _resolve_cli_path(args.reference, ROOT)
    out_dir = _resolve_cli_path(args.out_dir) if args.out_dir else _default_out_dir(target_pdf)

    if not target_pdf.exists():
        print(f"SKIP: target PDF not found: {target_pdf}")
        return 0
    if not reference_pdf.exists():
        print(f"SKIP: reference PDF not found: {reference_pdf}")
        return 0
    if not shutil.which("pdftoppm"):
        print("SKIP: pdftoppm missing; cannot rasterize resume PDF.")
        return 0

    page_count = _count_pages(target_pdf)
    deterministic = _deterministic_gates(target_pdf, page_count)
    page_pngs, reference_png = _rasterize(target_pdf, reference_pdf, out_dir)
    packet = _build_packet(target_pdf, page_count, page_pngs, reference_png, deterministic)
    _write_packet(packet, out_dir)
    _emit_ready(packet)
    return 0


def main() -> int:
    return _run()


if __name__ == "__main__":
    sys.exit(main())
