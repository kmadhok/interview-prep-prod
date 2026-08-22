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
    re.compile(r"\bKanu\b"),
    re.compile(r"\bMadhok\b"),
    re.compile(r"kanumadhok", re.IGNORECASE),
    re.compile(r"madhok\.kanu"),
    re.compile(r"the user the user"),
    re.compile(r"/Users/[A-Za-z]"),          # absolute Mac home paths
    re.compile(r"G:[/\\]projects"),           # the user's PC drive layout
    re.compile(r"Documents/Claude/Projects"), # any form of the live workspace path
    re.compile(r"kanu-madhok"),               # personal LinkedIn handle
    re.compile(r"\bkmadhok\b"),               # personal GitHub handle
]

# The distribution repo's own clone URL is the one sanctioned handle occurrence.
ALLOWED_LITERALS = ("github.com/kmadhok/interview-prep-template",)


def redact_allowed(text: str) -> str:
    """Blank sanctioned literals so the forbidden patterns do not match them."""
    for literal in ALLOWED_LITERALS:
        text = text.replace(literal, "#" * len(literal))
    return text


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


def find_violations() -> list[str]:
    violations = []
    for f in iter_template_files():
        text = redact_allowed(f.read_text(encoding="utf-8", errors="surrogateescape"))  # surrogateescape: lossless — never silently drop bytes that could hide a violation
        for pattern in FORBIDDEN:
            for m in pattern.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(f"{f.relative_to(REPO_ROOT)}:{line_no}: {m.group(0)!r}")
    return violations


def test_no_personal_refs_in_template_dirs():
    violations = find_violations()
    assert not violations, (
        "Personal references found in template-side files:\n" + "\n".join(violations)
    )


def main() -> int:
    violations = find_violations()
    if violations:
        print("Personal references found in template-side files:")
        print("\n".join(violations))
        return 1
    print("PASS: no personal references found in template-side files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
