"""Apply Packet: build + upload the Drive Apply Queue mirror for one role.

Pure functions + thin CLI, same shape as dedupe.py. No LLM. The only side
effects are rclone subprocesses (injectable `run`) and the .apply-packet.json
write. Spec: Automation Design - Two-Orchestrator/Spec - Apply Packet.md.

The mirror is a PROJECTION of repo state (invariant 5): .classification.json
supplies posted_date/canonical_url/easy_apply/repost; this module never
decides them. The PDF goes disk -> Drive via rclone, never through a model.
"""
from __future__ import annotations
import argparse, difflib, hashlib, json, os, re, subprocess, sys
from pathlib import Path

from outreach_worklist import active_section, row_is_applied

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


REPOST_THRESHOLD = 0.85
_WORDS = re.compile(r"[a-z0-9]+")


def normalize_jd(text: str) -> str:
    """Lowercased word soup — robust to punctuation/whitespace/casing edits."""
    return " ".join(_WORDS.findall((text or "").lower()))


def jd_similarity(a: str, b: str) -> float:
    # autojunk=False: real JDs exceed 200 chars, where difflib's autojunk
    # heuristic treats common words as junk and collapses the ratio to noise.
    return difflib.SequenceMatcher(None, normalize_jd(a), normalize_jd(b),
                                   autojunk=False).ratio()


def load_jd_corpus(repo_root: Path, exclude: Path | None = None) -> list[tuple[str, str]]:
    """(folder name, JD text) for every filed role except `exclude`."""
    out: list[tuple[str, str]] = []
    for base in (repo_root / "Roles", repo_root / "_Archived"):
        if not base.is_dir():
            continue
        for jd in sorted(base.glob("*/Job Description.md")):
            if exclude is not None and jd.parent.resolve() == Path(exclude).resolve():
                continue
            out.append((jd.parent.name, jd.read_text(encoding="utf-8-sig", errors="replace")))
    return out


def find_repost(jd_text: str, corpus: list[tuple[str, str]]) -> dict | None:
    """Best corpus match at >= REPOST_THRESHOLD, else None.

    A re-appearing JD keeps its ORIGINAL posting's age (repost correlates with
    ghost/evergreen postings) — the caller records the flag; this only detects.
    """
    best_name, best_ratio = None, 0.0
    for name, text in corpus:
        r = jd_similarity(jd_text, text)
        if r > best_ratio:
            best_name, best_ratio = name, r
    if best_name is not None and best_ratio >= REPOST_THRESHOLD:
        return {"match_folder": best_name, "similarity": round(best_ratio, 3)}
    return None


def _cli_repost_check(args) -> int:
    folder = Path(args.role_folder)
    jd = folder / "Job Description.md"
    if not jd.exists():
        print(json.dumps({"repost": False, "error": "no Job Description.md"}))
        return 0
    corpus = load_jd_corpus(Path(args.repo_root), exclude=folder)
    hit = find_repost(jd.read_text(encoding="utf-8-sig", errors="replace"), corpus)
    print(json.dumps({"repost": hit is not None, **(hit or {})}))
    return 0


def _company_applied(company: str, pipeline_text: str) -> bool:
    pat = re.compile(r"\b" + re.escape(company) + r"\b", re.IGNORECASE)
    return any(row_is_applied(l) and pat.search(l) for l in active_section(pipeline_text))


def _packet_folders(repo_root: Path) -> list[Path]:
    out = []
    for base in (repo_root / "Roles", repo_root / "_Archived"):
        if base.is_dir():
            out.extend(sorted(p.parent for p in base.glob(f"*/{PACKET_FILE}")))
    return out


def reconcile_actions(repo_root: Path, pipeline_text: str) -> list[dict]:
    """Pure diff of repo truth vs recorded mirror state. No side effects."""
    actions: list[dict] = []
    for folder in _packet_folders(repo_root):
        rec = read_packet(folder)
        if not rec or rec.get("state") != "queued":
            continue
        company, _ = split_company_role(folder.name)
        if folder.parent.name == "_Archived":
            actions.append({"action": "delete", "folder": folder, "record": rec})
        elif _company_applied(company, pipeline_text):
            actions.append({"action": "move", "folder": folder, "record": rec})
        else:
            pdf = find_resume_pdf(folder)
            if pdf is not None and sha256_of(pdf) != rec.get("pdf_sha256"):
                actions.append({"action": "reupload", "folder": folder, "record": rec})
    return actions


def _applied_dest(remote_path: str, remote_dir: str) -> str:
    name = remote_path[len(remote_dir) + 1:]  # strip "<remote_dir>/"
    return f"{remote_dir}/Applied/{name}"


def apply_reconcile(actions: list[dict], run=subprocess.run, now_iso: str = "") -> list[str]:
    """Execute actions via rclone; rewrite each record; return summary lines.

    One failing role must not block the rest (fail loud per role, keep going):
    errors become summary lines the digest/log surfaces.
    """
    lines: list[str] = []
    for a in actions:
        folder, rec = a["folder"], a["record"]
        try:
            if a["action"] == "move":
                for key in ("pdf_remote", "answers_remote"):
                    if rec.get(key):
                        dest = _applied_dest(rec[key], rec["remote_dir"])
                        _rclone(["moveto", rec[key], dest], run)
                        rec[key] = dest
                rec["state"] = "applied"
                rec["moved_ts"] = now_iso
                lines.append(f"moved to Applied/: {folder.name}")
            elif a["action"] == "delete":
                for key in ("pdf_remote", "answers_remote"):
                    if rec.get(key):
                        _rclone(["deletefile", rec[key]], run)
                rec["state"] = "removed"
                rec["removed_ts"] = now_iso
                lines.append(f"removed (archived): {folder.name}")
            elif a["action"] == "reupload":
                pdf = find_resume_pdf(folder)
                _rclone(["copyto", str(pdf), rec["pdf_remote"]], run)
                rec["pdf_sha256"] = sha256_of(pdf)
                rec["uploaded_ts"] = now_iso
                lines.append(f"re-uploaded stale PDF: {folder.name}")
            write_packet(folder, rec)
        except Exception as e:
            # Broad on purpose: a malformed .apply-packet.json (missing
            # remote_dir/pdf_remote etc.) must become a FAILED summary line and
            # let the pass continue to the next role, not abort the whole sweep.
            lines.append(f"FAILED {a['action']} {folder.name}: {e}")
    return lines


def _cli_reconcile(args) -> int:
    from datetime import datetime, timezone
    repo_root = Path(args.repo_root)
    pipeline = (repo_root / "Pipeline.md").read_text(encoding="utf-8-sig", errors="replace")
    now_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    actions = reconcile_actions(repo_root, pipeline)
    lines = apply_reconcile(actions, now_iso=now_iso)
    for l in lines:
        print(l)
    if args.commit and lines and not any(l.startswith("FAILED") for l in lines):
        # Stage ONLY the packet records this pass rewrote — never a blanket
        # `git add Roles` (a crashed Claude run can leave unrelated dirty files
        # there, and sweeping them into this commit would hide the crash).
        changed = [str((a["folder"] / PACKET_FILE).relative_to(repo_root)) for a in actions]
        subprocess.run(["git", "add"] + changed, cwd=repo_root)
        r = subprocess.run(["git", "commit", "-m", "drip-runner: packet reconcile"],
                           cwd=repo_root, capture_output=True, text=True)
        if r.returncode == 0:
            subprocess.run(["git", "push"], cwd=repo_root)
    if not lines:
        print("reconcile: no-op")
    return 1 if any(l.startswith("FAILED") for l in lines) else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    up = sub.add_parser("upload", help="upload one role's packet to the Apply Queue")
    up.add_argument("role_folder")
    up.add_argument("--remote-dir", default=None)
    rp = sub.add_parser("repost-check", help="fuzzy-match this JD against every filed JD")
    rp.add_argument("role_folder")
    rp.add_argument("--repo-root", default=".")
    rc = sub.add_parser("reconcile", help="make the Drive mirror follow Pipeline/folder truth")
    rc.add_argument("--repo-root", default=".")
    rc.add_argument("--commit", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "upload":
        return _cli_upload(args)
    if args.cmd == "repost-check":
        return _cli_repost_check(args)
    if args.cmd == "reconcile":
        return _cli_reconcile(args)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PacketError as e:
        print(f"PACKET ERROR: {e}", file=sys.stderr)
        sys.exit(1)
