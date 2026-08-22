"""Deterministic CRUD over a Pipeline.md file's 6-column role tables.

Pure functions + a thin CLI, same shape as dedupe.py / outreach_worklist.py.
No LLM, no network.

This owns two invariant-bearing operations the determinism audit
(docs/determinism-audit.md) identified as mechanical-but-critical:

  * the Pipeline row table shape (6 columns, bold role cell, em-dash), and
  * the STAGED marker — it MUST only land on an Applied row in the ## Active
    section. A STAGED marker on a Considering row silently suppresses outreach
    forever; this tool refuses rather than risk that.

Consumers: intake, track-application, stage-outreach.
"""
from __future__ import annotations
import argparse, json, os, re, sys, tempfile
from pathlib import Path

# Section headings (case-insensitive on the H2 prefix, matching the repo's
# other section scanners: outreach_worklist.active_section, prepped_not_applied).
_ACTIVE = "active"
_CONSIDERING = "considering"
_CLOSED = "closed"

def _section_key(line: str) -> str | None:
    """Map a `## <heading>` line to a canonical section key, or None.

    Only the three real Pipeline sections are recognized. Any other H2
    (or a non-heading line) returns None.
    """
    m = re.match(r"^##\s+(.+?)\s*$", line)
    if not m:
        return None
    h = m.group(1).strip().lower()
    if h == "active":
        return _ACTIVE
    if h.startswith("considering"):
        return _CONSIDERING
    if h.startswith("closed"):
        return _CLOSED
    return None


# Bold role cell leader:  | **<Company> <sep> <Role>** |
# Separator is em-dash (—), en-dash (–), or hyphen (-) — same tolerance as
# prepped_not_applied._ROW_LEADER.
_ROW_LEADER = re.compile(
    r"\*\*\s*(?P<company>.+?)\s*[—–-]\s+(?P<role>.+?)\s*\*\*"
)

_STAGED = re.compile(r"STAGED in Gmail", re.IGNORECASE)


def _norm(s: str) -> str:
    """Normalize for case-insensitive matching: lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _row_matches(line: str, company: str, role: str) -> bool:
    """True iff the line's bold role cell matches company+role (case-insensitive).

    Tolerant of em-dash and hyphen separators between company and role.
    """
    m = _ROW_LEADER.search(line)
    if not m:
        return False
    return _norm(m.group("company")) == _norm(company) and _norm(m.group("role")) == _norm(role)


def _find_row(lines: list[str], company: str, role: str) -> tuple[int, str] | None:
    """Return (line_index, line) of the first row matching company+role, or None.

    Scans ALL sections — a company+role must be unique across the whole file
    (add-considering refuses if a row already exists anywhere).
    """
    for i, line in enumerate(lines):
        if _row_matches(line, company, role):
            return (i, line)
    return None


def _find_row_in_section(lines: list[str], section: str, company: str, role: str) -> tuple[int, str] | None:
    """Return (line_index, line) of the row matching company+role in `section` only."""
    current: str | None = None
    for i, line in enumerate(lines):
        key = _section_key(line)
        if key is not None:
            current = key
            continue
        if current == section and _row_matches(line, company, role):
            return (i, line)
    return None


# ---------------------------------------------------------------------------
# Cell parsing — a 6-column Pipeline row splits cleanly on ` | ` after the
# leading `|` and before the trailing `|`. Cells are the inner text, trimmed.
# ---------------------------------------------------------------------------

def _split_row(line: str) -> list[str] | None:
    """Split a 6-column Pipeline row into its cells, or None if not a table row.

    Returns the 6 inner cell strings, stripped of outer whitespace. The role
    cell still carries its `**...**` bold wrapper — callers strip or parse it
    as needed.
    """
    s = line.strip()
    if not s.startswith("|") or not s.endswith("|"):
        return None
    inner = s[1:-1]
    cells = [c.strip() for c in inner.split("|")]
    if len(cells) != 6:
        return None
    return cells


def _row_dict(line: str) -> dict:
    """Parse a row into {section is unknown here, stage, next_action, date, contacts, folder}.

    The `section` key is filled by `get` (which scans sections); this helper
    only parses the single line.
    """
    cells = _split_row(line)
    if cells is None:
        return {}
    return {
        "stage": cells[1],
        "next_action": cells[2],
        "date": cells[3],
        "contacts": cells[4],
        "folder": cells[5],
    }


# ---------------------------------------------------------------------------
# Operations — pure functions that take lines and return new lines (no I/O).
# ---------------------------------------------------------------------------

def _last_row_index(lines: list[str], section: str) -> int | None:
    """Index of the last non-blank line in `section`, or the heading line if empty.

    Returns None if the section heading is absent. For an empty section (heading
    + separator only) the heading index is returned so the caller inserts right
    after it. For a section with rows, the last row's index is returned so the
    caller inserts after it (appends to the end of the table).
    """
    current: str | None = None
    heading_idx = -1
    last_content = -1
    for i, line in enumerate(lines):
        key = _section_key(line)
        if key is not None:
            if current == section:
                break  # we've left the target section
            current = key
            if key == section:
                heading_idx = i
            continue
        if current == section and line.strip():
            last_content = i
    if heading_idx == -1:
        return None
    return last_content if last_content > heading_idx else heading_idx


def add_considering(lines: list[str], company: str, role: str, folder: str,
                    date: str | None = None, next_action: str | None = None,
                    contacts: str | None = None) -> list[str]:
    """Return new lines with a Considering row appended for company+role.

    Raises ValueError if a row for company+role already exists in any section.
    """
    if _find_row(lines, company, role) is not None:
        raise ValueError(
            f"a row for {company!r} — {role!r} already exists in Pipeline.md"
        )
    stage = "Considering — not yet applied"
    na = next_action if next_action else "—"
    d = date if date else "—"
    ct = contacts if contacts else "—"
    row = (f"| **{company} — {role}** | {stage} | {na} | {d} | {ct} "
           f"| [[{folder}]] |")

    insert_at = _last_row_index(lines, _CONSIDERING)
    if insert_at is None:
        raise ValueError("## Considering / not yet applied section not found in Pipeline.md")
    new_lines = list(lines)
    new_lines.insert(insert_at + 1, row)
    return new_lines


def mark_applied(lines: list[str], company: str, role: str, date: str,
                 via: str | None = None) -> list[str]:
    """Return new lines with the row moved from Considering to Active as Applied.

    The stage cell becomes: **Applied** — submitted via <via or "the ATS"> <date>
    Raises ValueError if no Considering row exists (exit 3) or already in Active (exit 4).
    """
    # Check Active FIRST so the "already applied" case returns exit 4, not 3.
    active = _find_row_in_section(lines, _ACTIVE, company, role)
    if active is not None:
        raise ValueError(
            f"a row for {company!r} — {role!r} is already in ## Active"
        )
    considering = _find_row_in_section(lines, _CONSIDERING, company, role)
    if considering is None:
        raise ValueError(
            f"no row for {company!r} — {role!r} in ## Considering / not yet applied"
        )

    idx, old_line = considering
    cells = _split_row(old_line)
    # Preserve the role cell (cell 0) exactly as it was.
    via_text = via if via else "the ATS"
    new_stage = f"**Applied** — submitted via {via_text} {date}"
    cells[1] = new_stage
    cells[3] = date  # date cell follows the apply date
    new_row = "| " + " | ".join(cells) + " |"

    # Remove from Considering, insert into Active.
    new_lines = list(lines)
    del new_lines[idx]  # remove the old Considering row

    active_insert = _last_row_index(new_lines, _ACTIVE)
    if active_insert is None:
        raise ValueError("## Active section not found in Pipeline.md")

    new_lines.insert(active_insert + 1, new_row)
    return new_lines


def append_staged(lines: list[str], company: str, role: str, date: str) -> list[str]:
    """Return new lines with ` · STAGED in Gmail <date>` appended to the row's stage cell.

    HARD INVARIANT: the row MUST be in ## Active AND its stage cell MUST contain
    **Applied**. Raises ValueError (exit 3) otherwise. Raises ValueError (exit 4)
    if STAGED is already present (idempotent no-op).
    """
    active = _find_row_in_section(lines, _ACTIVE, company, role)
    if active is None:
        raise ValueError(
            "STAGED invariant: row is not in ## Active (cannot append STAGED to a non-Applied row)"
        )
    idx, old_line = active
    cells = _split_row(old_line)
    if cells is None:
        raise ValueError("STAGED invariant: row is not a 6-column table row")
    stage = cells[1]
    if "**Applied**" not in stage:
        raise ValueError(
            "STAGED invariant: row's stage cell does not contain **Applied** "
            "(refusing to append STAGED to a non-Applied row)"
        )
    if _STAGED.search(stage):
        raise ValueError(
            f"STAGED in Gmail already present for {company!r} — {role!r} (idempotent no-op)"
        )
    cells[1] = f"{stage} · STAGED in Gmail {date}"
    new_row = "| " + " | ".join(cells) + " |"
    new_lines = list(lines)
    new_lines[idx] = new_row
    return new_lines


def get_row(lines: list[str], company: str, role: str) -> dict | None:
    """Return {section, stage, next_action, date, contacts, folder} or None."""
    current: str | None = None
    for line in lines:
        key = _section_key(line)
        if key is not None:
            current = key
            continue
        if _row_matches(line, company, role):
            d = _row_dict(line)
            d["section"] = current or ""
            return d
    return None


# ---------------------------------------------------------------------------
# I/O — read file → lines, write lines → file atomically (temp + os.replace).
# Preserve every byte of every line we don't touch: we split on \n and rejoin
# with \n, which round-trips any file that uses \n line endings (Markdown does).
# ---------------------------------------------------------------------------

def _read(path: Path) -> tuple[list[str], bool]:
    """Read a Pipeline.md file into (lines, had_trailing_newline).

    splitlines() would lose the trailing-newline distinction; splitting on '\n'
    and dropping the sentinel empty string preserves it so we can reconstruct
    the file byte-for-byte on write.
    """
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    had_trailing_nl = text.endswith("\n")
    lines = text.split("\n")
    if had_trailing_nl and lines and lines[-1] == "":
        lines = lines[:-1]
    return lines, had_trailing_nl


def _join_lines(lines: list[str], had_trailing_nl: bool = True) -> str:
    """Inverse of _read — rejoin with \\n, adding a trailing \\n by default."""
    text = "\n".join(lines)
    if had_trailing_nl:
        text += "\n"
    return text


def _write_atomic(path: Path, lines: list[str], had_trailing_nl: bool) -> None:
    """Write lines to path via temp file + os.replace. Preserves other bytes."""
    text = _join_lines(lines, had_trailing_nl)
    d = path.parent
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(d))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    """Run the command-line workflow; parse/user/provider failures terminate with the documented nonzero status."""
    p = argparse.ArgumentParser(description="Pipeline.md row CRUD (deterministic)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # --pipeline is required on every subcommand (added to each so it works
    # before OR after the subcommand name — argparse doesn't share parent-level
    # args with subparsers cleanly).
    def _add_pipeline(sp):
        sp.add_argument("--pipeline", required=True)

    a = sub.add_parser("add-considering")
    _add_pipeline(a)
    a.add_argument("--company", required=True)
    a.add_argument("--role", required=True)
    a.add_argument("--folder", required=True)
    a.add_argument("--date", default=None)
    a.add_argument("--next-action", default=None)
    a.add_argument("--contacts", default=None)

    m = sub.add_parser("mark-applied")
    _add_pipeline(m)
    m.add_argument("--company", required=True)
    m.add_argument("--role", required=True)
    m.add_argument("--date", required=True)
    m.add_argument("--via", default=None)

    s = sub.add_parser("append-staged")
    _add_pipeline(s)
    s.add_argument("--company", required=True)
    s.add_argument("--role", required=True)
    s.add_argument("--date", required=True)

    g = sub.add_parser("get")
    _add_pipeline(g)
    g.add_argument("--company", required=True)
    g.add_argument("--role", required=True)

    args = p.parse_args(argv)
    path = Path(args.pipeline)
    lines, had_nl = _read(path)

    if args.cmd == "get":
        row = get_row(lines, args.company, args.role)
        if row is None:
            print(f"no row for {args.company!r} — {args.role!r}", file=sys.stderr)
            return 1
        print(json.dumps(row, ensure_ascii=False))
        return 0

    # All write subcommands: operate, then write atomically.
    try:
        if args.cmd == "add-considering":
            new_lines = add_considering(lines, args.company, args.role, args.folder,
                                        args.date, args.next_action, args.contacts)
        elif args.cmd == "mark-applied":
            new_lines = mark_applied(lines, args.company, args.role, args.date, args.via)
        elif args.cmd == "append-staged":
            new_lines = append_staged(lines, args.company, args.role, args.date)
        else:
            print(f"unknown command: {args.cmd}", file=sys.stderr)
            return 2
    except ValueError as e:
        msg = str(e)
        print(msg, file=sys.stderr)
        # Exit codes: 3 = refused (precondition not met / invariant), 4 = idempotent no-op
        if "already" in msg and "STAGED" in msg:
            return 4
        if "already in ## Active" in msg:
            return 4
        if "already exists" in msg:
            return 3
        if "STAGED invariant" in msg or "no row" in msg or "not found" in msg:
            return 3
        return 3

    _write_atomic(path, new_lines, had_nl)
    print(f"ok: {args.cmd} {args.company} — {args.role}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
