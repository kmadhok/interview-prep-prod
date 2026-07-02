"""Apply Packet: build + upload the Drive Apply Queue mirror for one role.

Pure functions + thin CLI, same shape as dedupe.py. No LLM. The only side
effects are rclone subprocesses (injectable `run`) and the .apply-packet.json
write. Spec: Automation Design - Two-Orchestrator/Spec - Apply Packet.md.

The mirror is a PROJECTION of repo state (invariant 5): .classification.json
supplies posted_date/canonical_url/easy_apply/repost; this module never
decides them. The PDF goes disk -> Drive via rclone, never through a model.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

PACKET_FILE = ".apply-packet.json"
CLASSIFICATION_FILE = ".classification.json"
ANSWERS_MD = "Application Answers.md"
DEFAULT_REMOTE = "gdrive:Apply Queue"


class PacketError(RuntimeError):
    """Fail-loud: callers convert this to a trace gap / log line, never swallow."""


def default_remote() -> str:
    return os.environ.get("APPLY_PACKET_REMOTE_DIR", DEFAULT_REMOTE)


def split_company_role(folder_name: str) -> tuple[str, str]:
    """'Company - Role Title' -> (company, role). First ' - ' only."""
    company, _, role = folder_name.partition(" - ")
    return company.strip(), role.strip()


def packet_pdf_name(company: str, role: str, posted_date: str | None) -> str:
    """Date-prefixed so the Drive folder name-sorts by true posting freshness."""
    prefix = posted_date if posted_date else "undated"
    return f"{prefix} · {company} - {role}.pdf"


def packet_answers_name(company: str, role: str) -> str:
    return f"{company} - {role} - Answers.txt"


def find_resume_pdf(folder: Path) -> Path | None:
    pdfs = sorted(folder.glob("Kanu Madhok Resume - *.pdf"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_classification(folder: Path) -> dict:
    f = folder / CLASSIFICATION_FILE
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def write_packet(folder: Path, record: dict) -> None:
    # UTF-8 no BOM, trailing newline — repo readers are BOM-sensitive.
    (folder / PACKET_FILE).write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_packet(folder: Path) -> dict | None:
    f = folder / PACKET_FILE
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


def _rclone(args: list[str], run) -> None:
    proc = run(["rclone"] + args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise PacketError(f"rclone {args[0]} failed ({proc.returncode}): {getattr(proc, 'stderr', '')}".strip())


def upload_packet(folder: Path, remote: str, now_iso: str, run=subprocess.run) -> dict:
    """Upload PDF (+ answers if present) for one role folder; write .apply-packet.json."""
    company, role = split_company_role(folder.name)
    pdf = find_resume_pdf(folder)
    if pdf is None:
        raise PacketError(f"no resume PDF in {folder} — run jd-to-ready step 3.5 first")
    cls = read_classification(folder)
    posted = cls.get("posted_date")
    pdf_name = packet_pdf_name(company, role, posted)
    _rclone(["copyto", str(pdf), f"{remote}/{pdf_name}"], run)

    answers_remote = None
    answers = folder / ANSWERS_MD
    if answers.exists():
        answers_name = packet_answers_name(company, role)
        _rclone(["copyto", str(answers), f"{remote}/{answers_name}"], run)
        answers_remote = f"{remote}/{answers_name}"

    record = {
        "schema": 1,
        "state": "queued",
        "pdf_remote": f"{remote}/{pdf_name}",
        "answers_remote": answers_remote,
        "pdf_sha256": sha256_of(pdf),
        "uploaded_ts": now_iso,
        "posted_date": posted,
        "canonical_url": cls.get("canonical_url"),
        "repost": bool(cls.get("repost", False)),
        "easy_apply": cls.get("easy_apply"),
        "remote_dir": remote,
    }
    write_packet(folder, record)
    return record


def _cli_upload(args) -> int:
    from datetime import datetime, timezone
    folder = Path(args.role_folder)
    remote = args.remote_dir or default_remote()
    now_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    rec = upload_packet(folder, remote, now_iso)
    print(f"uploaded: {rec['pdf_remote']}"
          + ("" if rec["answers_remote"] else "  WARNING: no Application Answers.md"))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    up = sub.add_parser("upload", help="upload one role's packet to the Apply Queue")
    up.add_argument("role_folder")
    up.add_argument("--remote-dir", default=None)
    args = p.parse_args(argv)
    if args.cmd == "upload":
        return _cli_upload(args)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PacketError as e:
        print(f"PACKET ERROR: {e}", file=sys.stderr)
        sys.exit(1)
