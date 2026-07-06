"""Guard: template-side code must contain zero personal references.

This is the regression stopper for the template/instance split
(spec: docs/spec/productionalization-v1.md, success criterion 6).
It goes green when the workspace/ migration (Tasks 3-6) completes,
and must stay green forever after.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()

# Dirs that ship in the template. workspace/ and docs/intent|spec|superpowers
# are instance/history material and exempt.
TEMPLATE_DIRS = ["scripts", ".claude/skills", "templates", "evals", "infra",
                 "docs/onboarding"]

SCAN_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".ps1", ".sh", ".txt"}

FORBIDDEN = [
    re.compile(r"kanumadhok", re.IGNORECASE),
    re.compile(r"madhok\.kanu"),
    re.compile(r"Kanu Madhok"),
    re.compile(r"/Users/[A-Za-z]"),          # absolute Mac home paths
    re.compile(r"G:[/\\]projects"),           # Kanu's PC drive layout
    re.compile(r"Documents/Claude/Projects"), # any form of the live workspace path
]


def iter_template_files():
    for d in TEMPLATE_DIRS:
        base = REPO_ROOT / d
        if not base.exists():
            continue
        for f in base.rglob("*"):
            # the guard's own pattern definitions are not violations
            if f.resolve() == THIS_FILE:
                continue
            if f.is_file() and f.suffix in SCAN_SUFFIXES:
                yield f


def test_no_personal_refs_in_template_dirs():
    violations = []
    for f in iter_template_files():
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN:
            for m in pattern.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(f"{f.relative_to(REPO_ROOT)}:{line_no}: {m.group(0)!r}")
    assert not violations, (
        "Personal references found in template-side files:\n" + "\n".join(violations)
    )
