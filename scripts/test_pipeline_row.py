"""Regression tests for pipeline_row.py — Pipeline.md row CRUD CLI.

Drives the real CLI via subprocess so the exit-code contract (0 ok,
3 refused/invariant, 4 duplicate/idempotent no-op) and byte-preservation
are exercised end-to-end. Synthetic data only — no real names/emails/paths.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("pipeline_row.py")

# 6-column Pipeline.md headers (mirrors scripts/drip_runner/test_lifecycle_integration.py)
_HEADER = "| Role | Stage | Next action | Date | Contacts | Folder |"
_HEADER_SEP = "| --- | --- | --- | --- | --- | --- |"


def _pipeline(active_rows=None, considering_rows=None) -> str:
    """Assemble a minimal two-section Pipeline.md (## Active + ## Considering)."""
    parts = ["## Active", _HEADER, _HEADER_SEP]
    parts.extend(active_rows or [])
    parts.append("")
    parts.append("## Considering / not yet applied")
    parts.append(_HEADER)
    parts.append(_HEADER_SEP)
    parts.extend(considering_rows or [])
    return "\n".join(parts) + "\n"


@pytest.fixture
def pipeline_file(tmp_path):
    """A fresh Pipeline.md with empty Active + empty Considering sections."""
    p = tmp_path / "Pipeline.md"
    p.write_text(_pipeline(), encoding="utf-8")
    return p


def _run(pipeline: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--pipeline", str(pipeline)],
        capture_output=True, text=True,
    )


def _get(pipeline: Path, company: str, role: str) -> dict | None:
    r = _run(pipeline, "get", "--company", company, "--role", role)
    assert r.returncode == 0, f"get failed: {r.stderr}"
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# 1. add-considering then get → section "considering", folder wikilink
# ---------------------------------------------------------------------------

def test_add_considering_then_get(pipeline_file):
    r = _run(pipeline_file, "add-considering",
             "--company", "Acme", "--role", "Agent Builder",
             "--folder", "Acme - Agent Builder")
    assert r.returncode == 0, f"add-considering failed: {r.stderr}"

    row = _get(pipeline_file, "Acme", "Agent Builder")
    assert row["section"] == "considering"
    assert row["folder"] == "[[Acme - Agent Builder]]"


# ---------------------------------------------------------------------------
# 2. duplicate add-considering → exit 3
# ---------------------------------------------------------------------------

def test_duplicate_add_considering_exit3(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    r = _run(pipeline_file, "add-considering",
             "--company", "Acme", "--role", "Agent Builder",
             "--folder", "Acme - Agent Builder")
    assert r.returncode == 3, f"expected exit 3 for duplicate, got {r.returncode}: {r.stderr}"


# ---------------------------------------------------------------------------
# 3. mark-applied moves row → get shows section "active", stage has Applied+date
# ---------------------------------------------------------------------------

def test_mark_applied_moves_to_active(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    r = _run(pipeline_file, "mark-applied",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-10")
    assert r.returncode == 0, f"mark-applied failed: {r.stderr}"

    row = _get(pipeline_file, "Acme", "Agent Builder")
    assert row["section"] == "active"
    assert "**Applied**" in row["stage"]
    assert "2026-07-10" in row["stage"]


# ---------------------------------------------------------------------------
# 4. mark-applied with no considering row → exit 3
# ---------------------------------------------------------------------------

def test_mark_applied_no_considering_row_exit3(pipeline_file):
    r = _run(pipeline_file, "mark-applied",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-10")
    assert r.returncode == 3, f"expected exit 3, got {r.returncode}: {r.stderr}"


# ---------------------------------------------------------------------------
# 5. mark-applied twice → exit 4 (already in Active)
# ---------------------------------------------------------------------------

def test_mark_applied_twice_exit4(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    _run(pipeline_file, "mark-applied",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-10")
    r = _run(pipeline_file, "mark-applied",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-10")
    assert r.returncode == 4, f"expected exit 4 for double apply, got {r.returncode}: {r.stderr}"


# ---------------------------------------------------------------------------
# 6. append-staged on Applied row → exit 0, stage gains "STAGED in Gmail <date>"
# ---------------------------------------------------------------------------

def test_append_staged_on_applied(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    _run(pipeline_file, "mark-applied",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-10")
    r = _run(pipeline_file, "append-staged",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-11")
    assert r.returncode == 0, f"append-staged failed: {r.stderr}"

    row = _get(pipeline_file, "Acme", "Agent Builder")
    assert "STAGED in Gmail 2026-07-11" in row["stage"], row["stage"]


# ---------------------------------------------------------------------------
# 7. append-staged on Considering row → exit 3, message mentions invariant
# ---------------------------------------------------------------------------

def test_append_staged_on_considering_exit3_invariant(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    r = _run(pipeline_file, "append-staged",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-11")
    assert r.returncode == 3, f"expected exit 3, got {r.returncode}: {r.stderr}"
    combined = (r.stdout + r.stderr).lower()
    assert "staged invariant" in combined, f"invariant message missing: {r.stderr!r}"


# ---------------------------------------------------------------------------
# 8. append-staged twice → exit 4 (idempotent no-op)
# ---------------------------------------------------------------------------

def test_append_staged_twice_exit4(pipeline_file):
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    _run(pipeline_file, "mark-applied",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-10")
    _run(pipeline_file, "append-staged",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-11")
    r = _run(pipeline_file, "append-staged",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-11")
    assert r.returncode == 4, f"expected exit 4 for double stage, got {r.returncode}: {r.stderr}"


# ---------------------------------------------------------------------------
# 9. byte-preservation: every line except the target row unchanged
# ---------------------------------------------------------------------------

def _row_for(pipeline: Path, company: str, role: str) -> str:
    """Return the exact line of the row matching company+role."""
    for line in pipeline.read_text(encoding="utf-8").splitlines():
        if f"{company}" in line and f"{role}" in line and line.startswith("| **"):
            return line
    raise AssertionError(f"row not found for {company} — {role}")


def test_byte_preservation_add_considering(pipeline_file):
    """add-considering inserts exactly one line; all pre-existing lines intact."""
    before = pipeline_file.read_text(encoding="utf-8").splitlines()
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    after = pipeline_file.read_text(encoding="utf-8").splitlines()

    # Every before-line must still be present (insertion only, no mutation)
    for line in before:
        assert line in after, f"pre-existing line lost: {line!r}"


def test_byte_preservation_mark_applied(tmp_path):
    """mark-applied removes the Considering row and adds a new Active row;
    every OTHER line is byte-identical (the old row line is gone, one new
    line appears — both are the target row)."""
    p = tmp_path / "Pipeline.md"
    p.write_text(_pipeline(), encoding="utf-8")
    _run(p, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    before = p.read_text(encoding="utf-8").splitlines()
    _run(p, "mark-applied",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-10")
    after = p.read_text(encoding="utf-8").splitlines()

    before_rows = {l for l in before if l.startswith("| **")}
    after_rows = {l for l in after if l.startswith("| **")}
    target_removed = before_rows - after_rows   # the old Considering row
    target_added = after_rows - before_rows       # the new Active row

    # Exactly one row changed out (the target); everything else identical
    assert len(target_removed) == 1, f"expected 1 removed row, got {target_removed}"
    assert len(target_added) == 1, f"expected 1 added row, got {target_added}"
    # All non-row lines preserved byte-for-byte
    before_nonrow = [l for l in before if not l.startswith("| **")]
    after_nonrow = [l for l in after if not l.startswith("| **")]
    assert before_nonrow == after_nonrow, "non-target lines changed"


def test_byte_preservation_append_staged(pipeline_file):
    """append-staged mutates only the target row's stage cell."""
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")
    _run(pipeline_file, "mark-applied",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-10")
    before = pipeline_file.read_text(encoding="utf-8").splitlines()
    _run(pipeline_file, "append-staged",
         "--company", "Acme", "--role", "Agent Builder",
         "--date", "2026-07-11")
    after = pipeline_file.read_text(encoding="utf-8").splitlines()

    # Exactly one line differs (the target row); all others identical
    diffs = [(b, a) for b, a in zip(before, after) if b != a]
    assert len(diffs) == 1, f"expected 1 changed line, got {len(diffs)}: {diffs}"
    assert "STAGED in Gmail" in diffs[0][1]


# ---------------------------------------------------------------------------
# 10. matching tolerates em-dash and hyphen in --role/--company lookups
# ---------------------------------------------------------------------------

def test_em_dash_hyphen_tolerance(pipeline_file):
    """add-considering writes an em-dash row; get with plain hyphen-free
    company+role strings still matches (the separator tolerance)."""
    # add-considering writes the row with em-dash separator: **Acme — Agent Builder**
    _run(pipeline_file, "add-considering",
         "--company", "Acme", "--role", "Agent Builder",
         "--folder", "Acme - Agent Builder")

    # get with plain company/role (no separator chars in the args) must match
    row = _get(pipeline_file, "Acme", "Agent Builder")
    assert row is not None
    assert row["folder"] == "[[Acme - Agent Builder]]"

    # mark-applied via plain-string lookup also works across the em-dash row
    r = _run(pipeline_file, "mark-applied",
             "--company", "Acme", "--role", "Agent Builder",
             "--date", "2026-07-10")
    assert r.returncode == 0, f"mark-applied failed on em-dash row: {r.stderr}"
    row = _get(pipeline_file, "Acme", "Agent Builder")
    assert row["section"] == "active"
