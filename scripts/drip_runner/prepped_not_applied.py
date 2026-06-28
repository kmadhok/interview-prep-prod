"""Fail-loud nudge: roles prepped (resume in folder) but never resolved.

Pure functions + thin CLI, same shape as dedupe.py. No LLM, no network.

A role is "resolved" if it reached an Applied row in `## Active` OR appears in
`## Closed / On hold` (rejected/archived). A prepped role that is NOT resolved
and whose resume is older than the staleness threshold is the silent-failure
path: prepped, never applied, outreach never staged. The secretary/report turns
this into a visible "did you apply?" nudge — the machine reminds, Kanu decides.

Age-in-days is supplied by the caller (CLI boundary) so the pure functions stay
clock-free and unit-testable.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

from outreach_worklist import row_is_applied, active_section

_CLOSED_HEADING = re.compile(r"^##\s+Closed", re.IGNORECASE)
_ROW_LEADER = re.compile(r"\*\*\s*(?P<company>.+?)\s+[—–-]\s+.+?\s*\*\*")


# TODO: extract a shared _section(text, heading) helper if a third section scanner is needed
def _closed_section(pipeline_text: str) -> list[str]:
    """Lines under the `## Closed / On hold` heading, to the next `## ` H2."""
    out: list[str] = []
    in_closed = False
    for line in (pipeline_text or "").splitlines():
        if re.match(r"^##\s", line):
            in_closed = bool(_CLOSED_HEADING.match(line))
            continue
        if in_closed:
            out.append(line)
    return out


def _company_in(company: str, line: str) -> bool:
    company = (company or "").strip()
    if not company:
        return False
    return re.search(r"\b" + re.escape(company) + r"\b", line, re.IGNORECASE) is not None


def role_is_resolved_in_pipeline(company: str, pipeline_text: str) -> bool:
    """True iff the company is applied (Active section) OR closed/archived.

    "Resolved" means: no further action needed (applied and in-flight, or
    terminal). A closed/rejected role should NOT be nudged ("did you apply?")
    because it is terminal — nudging it is noise and erodes signal trust.
    Only roles in `## Considering` (or entirely absent) are unresolved.
    """
    if any(row_is_applied(l) and _company_in(company, l) for l in active_section(pipeline_text)):
        return True
    # Closed = resolved, but match ONLY the company in the row's leading bold
    # cell — never notes/dates/prose, which would falsely resolve (and silently
    # suppress the nudge for) an unrelated prepped role that happens to be
    # mentioned in another closed row's notes.
    for line in _closed_section(pipeline_text):
        m = _ROW_LEADER.match(line.lstrip("| "))
        if m and _company_in(company, m.group("company")):
            return True
    return False


def stale_prepped_not_applied(prepped, pipeline_text, threshold_days=3):
    """Return entries from `prepped` that are stale AND unresolved.

    `prepped` is an iterable of (company, role, age_days). Age threshold is
    inclusive: age_days == threshold_days qualifies. The caller (CLI) computes
    age from the filesystem so this function stays clock-free and testable.
    """
    out = []
    for company, role, age_days in prepped:
        if age_days < threshold_days:
            continue
        if role_is_resolved_in_pipeline(company, pipeline_text):
            continue
        out.append((company, role, age_days))
    return out


def _scan_prepped(roles_dir: str):
    """Yield (company, role, age_days) for Roles/ folders holding a tailored resume.

    Age is computed here (CLI boundary) so the pure functions stay clock-free.
    Folder names follow the convention `Company - Role` (split on first ` - `).
    """
    from datetime import datetime, timezone
    base = Path(roles_dir)
    if not base.is_dir():
        return
    now = datetime.now(timezone.utc).timestamp()
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        resumes = list(folder.glob("Kanu Madhok Resume - *.md"))
        if not resumes:
            continue
        newest = max(r.stat().st_mtime for r in resumes)
        age_days = int((now - newest) / 86400)  # floor division: nudge fires at exactly threshold days, never earlier
        company, sep, role = folder.name.partition(" - ")
        if not sep:
            continue  # non-standard folder name (no " - "); skip silently
        yield (company.strip(), role.strip(), age_days)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="prepped-but-not-applied nudge")
    p.add_argument("--roles-dir", required=True)
    p.add_argument("--pipeline", required=True)
    p.add_argument("--threshold-days", type=int, default=3)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    prepped = list(_scan_prepped(args.roles_dir))
    for company, role, age in stale_prepped_not_applied(prepped, text, args.threshold_days):
        print(f"{company}\t{role}\t{age}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
