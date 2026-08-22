"""Pass B worklist: Pipeline rows marked Applied with no STAGED or error marker.

Pure functions + a thin CLI, same shape as dedupe.py. No LLM, no network.
The apply-side poll (stage-outreach) runs on exactly the rows this returns.

"Applied" in Pipeline.md is prose in the stage cell, not a clean token, and the
"## Considering / not yet applied" rows contain the word inside "not yet applied".
So applied = has a word-boundaried "Applied" AND not "not yet applied".
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# Leading bold cell of a role row: **<Company> — <Role>**  (em-dash, non-greedy)
_ROW = re.compile(r"\*\*\s*(?P<company>.+?)\s+—\s+(?P<role>.+?)\s*\*\*")
_APPLIED = re.compile(r"\bApplied\b", re.IGNORECASE)
_NOT_YET = re.compile(r"not yet applied", re.IGNORECASE)
_STAGED = re.compile(r"STAGED in Gmail", re.IGNORECASE)
_ERROR = re.compile(r"Outreach error", re.IGNORECASE)


def row_is_applied(row: str) -> bool:
    """Recognize an Applied marker without misclassifying 'not yet applied' prose."""
    row = row or ""
    return bool(_APPLIED.search(row)) and not bool(_NOT_YET.search(row))


def row_is_staged(row: str) -> bool:
    """Return whether a row already carries the case-insensitive Gmail staging marker."""
    return bool(_STAGED.search(row or ""))


def row_has_error(row: str) -> bool:
    """A row Pass B already failed on and parked with an 'Outreach error' note.

    No auto-retry (design D): a parked row is excluded from the worklist until
    the user removes the note. Without this, an hourly Pass B would re-scrape a
    failing role on LinkedIn every run — the exact account-flag surface to avoid.
    """
    return bool(_ERROR.search(row or ""))


def active_section(pipeline_text: str) -> list[str]:
    """Lines under the `## Active` heading, up to the next `## ` heading.

    Worklist state is only meaningful in Active. Considering rows are
    excluded by the 'not yet applied' predicate; Closed/On hold rows have a
    different table schema whose Date cell carries 'Applied <date>' and would
    otherwise leak — section-scoping is the clean structural exclusion.
    """
    lines = (pipeline_text or "").splitlines()
    out: list[str] = []
    in_active = False
    for line in lines:
        if re.match(r"^##\s", line):
            # Enter on exactly "## Active"; any other H2 ends the section.
            in_active = line.strip().lower() == "## active"
            continue  # skip the heading line itself; only collect rows under it
        if in_active:
            out.append(line)
    return out


def applied_not_staged(pipeline_text: str) -> list[tuple[str, str]]:
    """Extract Active company/role pairs that are applied, unstaged, and not parked."""
    out: list[tuple[str, str]] = []
    for line in active_section(pipeline_text):
        if not row_is_applied(line) or row_is_staged(line) or row_has_error(line):
            continue
        m = _ROW.search(line)
        if m:
            out.append((m.group("company").strip(), m.group("role").strip()))
    return out


def main(argv=None) -> int:
    """Print the Pass B worklist as tab-separated company and role pairs."""
    p = argparse.ArgumentParser(description="Pass B worklist: Applied & not STAGED")
    p.add_argument("--pipeline", required=True)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    for company, role in applied_not_staged(text):
        print(f"{company}\t{role}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
