"""Canonical role-folder naming + create-or-detect.

Pure functions + a thin CLI, same shape as dedupe.py / pipeline_row.py.
No LLM, no network.

The determinism audit (docs/determinism-audit.md) lists role-folder naming +
collision detection as an *extract* target: the naming rule is fixed
(`Company - Role Title`, forbidden chars stripped) and the collision check is a
pure filesystem question. Prose-instructing an LLM to do this is a
non-determinism tax on every intake.

  * `name` — pure: compute the canonical folder name from company+role, no
    filesystem access.
  * `ensure` — resolve the name against `<workspace>/Roles/` and
    `<workspace>/_Archived/`: create the folder if neither exists, report
    EXISTS if it's already in Roles/, or ARCHIVED (exit 3) if it's in
    _Archived/ (the caller decides whether to revive or rename).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# Forbidden filesystem chars across macOS/Windows/Linux + whitespace cleanup.
_FORBIDDEN = re.compile(r'[/:*?"<>|]')


def folder_name(company: str, role: str) -> str:
    """Canonical role-folder name: '<Company> - <Role>' sanitized for the filesystem.

    Forbidden chars (/:*?"<>|) are removed. Whitespace runs collapse to a single
    space. Em-dashes in the NAME are kept as given — they're valid filesystem
    chars and the repo convention (see workspace/Roles/) uses them. The company
    and role are joined with ' - ' (space-hyphen-space), the partition point the
    repo's folder-name parser splits on (`folder.name.partition(" - ")`).
    """
    company = _FORBIDDEN.sub("", company or "")
    role = _FORBIDDEN.sub("", role or "")
    company = re.sub(r"\s+", " ", company).strip()
    role = re.sub(r"\s+", " ", role).strip()
    return f"{company} - {role}"


def ensure_folder(workspace: Path, company: str, role: str) -> tuple[Path, str]:
    """Resolve the canonical folder against workspace; create if absent.

    Returns (path, status) where status is one of:
      - "EXISTS"   — folder already in <workspace>/Roles/
      - "ARCHIVED" — folder found in <workspace>/_Archived/ (caller decides)
      - "CREATED" — folder created in <workspace>/Roles/

    Raises FileNotFoundError if <workspace>/Roles/ does not exist (a workspace
    with no Roles/ dir is a caller bug, not something this tool silently fixes).
    """
    name = folder_name(company, role)
    roles = Path(workspace) / "Roles"
    archived = Path(workspace) / "_Archived"

    active_path = roles / name
    if active_path.is_dir():
        return (active_path, "EXISTS")

    if archived.is_dir():
        archived_path = archived / name
        if archived_path.is_dir():
            return (archived_path, "ARCHIVED")

    if not roles.is_dir():
        raise FileNotFoundError(f"{roles} does not exist — workspace is not initialized")

    active_path.mkdir(parents=True, exist_ok=True)
    return (active_path, "CREATED")


def main(argv=None) -> int:
    """Run the command-line workflow; parse/user/provider failures terminate with the documented nonzero status."""
    p = argparse.ArgumentParser(description="Canonical role-folder naming + ensure")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("name")
    n.add_argument("--company", required=True)
    n.add_argument("--role", required=True)

    e = sub.add_parser("ensure")
    e.add_argument("--workspace", required=True)
    e.add_argument("--company", required=True)
    e.add_argument("--role", required=True)

    args = p.parse_args(argv)

    if args.cmd == "name":
        print(folder_name(args.company, args.role))
        return 0

    if args.cmd == "ensure":
        try:
            path, status = ensure_folder(Path(args.workspace), args.company, args.role)
        except FileNotFoundError as ex:
            print(str(ex), file=sys.stderr)
            return 1
        print(f"{path} {status}")
        if status == "ARCHIVED":
            return 3
        return 0

    print(f"unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
