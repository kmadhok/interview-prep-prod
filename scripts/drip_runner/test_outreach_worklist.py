"""Tests for outreach_worklist.py — Pass B worklist reader.

Fixtures are real-shaped rows from Pipeline.md. Tests encode the key gotchas:
  - "not yet applied" rows must NOT be classified as applied
  - A role whose TITLE contains the word "Applied" must parse correctly
  - Already-STAGED rows must be excluded from the worklist
  - Closed/On hold rows must NEVER appear (section-scope bug regression)
"""
from outreach_worklist import row_is_applied, row_is_staged, row_has_error, applied_not_staged

# Real-shaped rows from Pipeline.md
APPLIED_ACTIVE = "| **Harrison Street — AVP, AI Engineer, Innovation** | **Applied** — submitted via Harrison Street careers | next | date | contacts | [[folder]] |"
APPLIED_PLUS   = "| **Capgemini — AI Product Engineer** | **Applied + outreach sent** — submitted via Capgemini careers 2026-05-24 | next | date | contacts | [[folder]] |"
APPLIED_VIA    = "| **Greylock Partners — Applied AI Engineer, Investment Team** | **Applied via LinkedIn** — ack received 2026-06-20 | next | date | contacts | [[folder]] |"
# ^ NOTE this role's TITLE contains the word "Applied" — exercises that company/role parsing still works and applied-detection isn't fooled either way (it IS applied, correctly).
CONSIDERING    = "| **Tailscale — Software Engineer, Strategic Projects** | Considering — JD reviewed, not yet applied · **STAGED in Gmail 2026-06-26** | next | date | contacts | [[folder]] |"
APPLIED_STAGED = "| **Acme — Agent Builder** | **Applied** — submitted · STAGED in Gmail 2026-06-27 | next | date | contacts | [[folder]] |"
# Applied row that Pass B already failed on and parked with an error note — must NOT be re-attempted.
APPLIED_ERROR  = "| **Initech — ML Engineer** | **Applied** — submitted · Outreach error 2026-06-27: LinkedIn daemon down | next | date | contacts | [[folder]] |"
HEADER         = "| Role | Stage | Next action | Date | Contacts | Folder |"
# A Closed/On hold row whose Date cell carries "Applied <date>" — this is the defect trigger.
CLOSED_REJECTED = "| **Deloitte — FDE, Agentic AI (req 350685)** | **Rejected** (form email) | Applied 2026-05-21 → rejected 2026-05-25 | notes |"

PIPELINE = "\n".join(["## Active", APPLIED_ACTIVE, APPLIED_PLUS, APPLIED_VIA, APPLIED_STAGED,
                      "## Considering / not yet applied", CONSIDERING])

FULL = "\n".join([
    "## This week",
    "## Active",
    APPLIED_ACTIVE, APPLIED_PLUS, APPLIED_VIA, APPLIED_STAGED,
    "## Considering / not yet applied",
    CONSIDERING,
    "## Closed / On hold",
    CLOSED_REJECTED,
])


def test_row_is_applied_true_for_active_applied_rows():
    assert row_is_applied(APPLIED_ACTIVE)
    assert row_is_applied(APPLIED_PLUS)
    assert row_is_applied(APPLIED_VIA)


def test_row_is_applied_false_for_not_yet_applied_rows():
    assert not row_is_applied(CONSIDERING)   # contains "applied" only inside "not yet applied"


def test_row_is_applied_false_for_header_and_blank():
    assert not row_is_applied(HEADER)
    assert not row_is_applied("")


def test_row_is_staged():
    assert row_is_staged(APPLIED_STAGED)
    assert row_is_staged(CONSIDERING)
    assert not row_is_staged(APPLIED_ACTIVE)


def test_applied_not_staged_excludes_staged_and_considering():
    rows = applied_not_staged(PIPELINE)
    companies = [c for c, r in rows]
    # Harrison Street, Capgemini, Greylock = applied & not staged. Acme is staged. Tailscale is considering.
    assert companies == ["Harrison Street", "Capgemini", "Greylock Partners"]


def test_applied_not_staged_parses_company_and_role():
    rows = applied_not_staged(PIPELINE)
    assert ("Harrison Street", "AVP, AI Engineer, Innovation") in rows
    assert ("Greylock Partners", "Applied AI Engineer, Investment Team") in rows  # role contains "Applied" — parsing still correct


def test_row_has_error():
    assert row_has_error(APPLIED_ERROR)
    assert not row_has_error(APPLIED_ACTIVE)
    assert not row_has_error("")


def test_applied_not_staged_excludes_errored_rows():
    """Park-on-error: a row carrying 'Outreach error' is excluded so a failed
    role is not re-scraped on LinkedIn every run (no auto-retry; design D)."""
    pipeline = "\n".join(["## Active", APPLIED_ACTIVE, APPLIED_ERROR])
    companies = [c for c, r in applied_not_staged(pipeline)]
    assert companies == ["Harrison Street"]   # Initech parked by its error note


def test_empty_pipeline():
    assert applied_not_staged("") == []


def test_closed_section_rows_never_appear():
    """Regression: Closed/On hold rows with 'Applied <date>' in Date cell must not leak."""
    rows = applied_not_staged(FULL)
    companies = [c for c, r in rows]
    assert "Deloitte" not in companies           # closed row excluded by section scope
    assert companies == ["Harrison Street", "Capgemini", "Greylock Partners"]


def test_only_active_section_scanned():
    """Regression: rows outside ## Active must never appear, even if they look applied."""
    # Same applied-looking row placed in Considering only — must not appear.
    assert applied_not_staged("## Considering / not yet applied\n" + APPLIED_ACTIVE) == []
    # The SAME row inside Active does appear.
    assert applied_not_staged("## Active\n" + APPLIED_ACTIVE) == [("Harrison Street", "AVP, AI Engineer, Innovation")]


def test_staged_marker_is_case_insensitive():
    row = "| **Acme — Agent Builder** | **Applied** — submitted · Staged in Gmail 2026-06-27 | n | d | c | f |"
    assert row_is_staged(row)
    # and such a row is excluded from the worklist
    assert applied_not_staged("## Active\n" + row) == []
