# Apply Packet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pass A's finish line becomes a mobile-ready packet (tailored resume PDF + application-answers file) in the Drive `Apply Queue/` folder, freshness-sorted by true ATS posted date, kept in sync by a deterministic reconcile pass, with a daily ntfy digest.

**Architecture:** All mechanical work (upload, reconcile, digest, repost detection) lives in pure-function Python modules in `scripts/drip_runner/` (same shape as `dedupe.py` / `prepped_not_applied.py`: pure functions + thin CLI, no LLM). The LLM side is one new `jd-to-ready` skill step (3.7) that does only judgment work — resolving the canonical ATS posting and drafting `Application Answers.md` — then shells out to the CLI. `run.ps1` invokes reconcile (hourly) and the digest (daily) as deterministic post-Claude steps. The PDF never passes through model context: `rclone` moves it disk→Drive.

**Tech Stack:** Python 3.12+ (invoked as `py -3` from PowerShell, `python3` from skill Bash steps), pytest, rclone (remote `gdrive`, on PATH), ntfy.sh (stdlib `urllib`), PowerShell 5.1 (`run.ps1`).

**Spec:** `Automation Design - Two-Orchestrator/Spec - Apply Packet.md`. Read it before starting.

## Global Constraints

- **Drive is a mirror, never truth** — `Pipeline.md` + role-folder files stay canonical; reconcile makes Drive follow them, never the reverse (spec, invariant 5).
- **The PDF never enters model context** — binary transfer is `rclone` only, shelled from Python/PowerShell, never an MCP call.
- **PC is the sole packet writer** — nothing here runs on the MacBook; run.ps1 is the only scheduler entry.
- **Fail loud, never silent** — any upload/reconcile/digest failure must produce a log line + trace gap (skill side) or log + toast (run.ps1 side), never a silent skip (invariant 4).
- **Pure functions + thin CLI** — new Python modules take injectable `run`/`now` parameters so tests never touch the network, the clock, or rclone.
- **UTF-8 no BOM** for every file written by scripts (repo readers are BOM-sensitive — see run.ps1 comments).
- **Rclone remote:** default `gdrive:Apply Queue`, overridable via `--remote-dir` flag and `APPLY_PACKET_REMOTE_DIR` env var (the e2e test depends on this override).
- **ntfy topic** is read from `~/.claude/ntfy_topic.txt` (outside the repo — the topic name is a secret; never commit it).
- **Never-invent rule** for `Application Answers.md`: copy from `Application Profile.md` or leave a `[?]` placeholder.
- Test command from repo root: `py -3 -m pytest scripts/drip_runner/<test file> -q`. Commit prefix for script work: `drip-runner:`.

---

### Task 1: `apply_packet.py` — core + `upload` CLI

**Files:**
- Create: `scripts/drip_runner/apply_packet.py`
- Test: `scripts/drip_runner/test_apply_packet.py`

**Interfaces:**
- Consumes: `<role folder>/.classification.json` (existing; may lack the new keys), `<role folder>/Kanu Madhok Resume - *.pdf`, `<role folder>/Application Answers.md` (created by Task 6's skill step; upload tolerates its absence with a warning).
- Produces: `upload_packet(folder: Path, remote: str, now_iso: str, run) -> dict` writing `<role folder>/.apply-packet.json`; CLI `py -3 scripts/drip_runner/apply_packet.py upload "<role folder>" [--remote-dir X]`. Record keys later tasks rely on: `state` ("queued"), `pdf_remote`, `answers_remote`, `pdf_sha256`, `uploaded_ts`, `posted_date`, `canonical_url`, `repost`, `easy_apply`, `remote_dir`.

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for apply_packet.py — pure functions, injected runner, no network."""
from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace

import apply_packet as ap


def fake_run_factory(calls):
    def fake_run(args, **kwargs):
        calls.append(list(args))
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    return fake_run


def make_role(tmp_path, company="Scribd", role="Senior AI Data Engineer",
              posted="2026-06-28", with_answers=True):
    folder = tmp_path / f"{company} - {role}"
    folder.mkdir()
    (folder / f"Kanu Madhok Resume - {company} {role.split()[0]}.pdf").write_bytes(b"%PDF-1.4 fake")
    cls = {"themes": [], "archetype": "FDE / client-facing",
           "posted_date": posted, "canonical_url": "https://boards.greenhouse.io/x/1",
           "easy_apply": False, "repost": False}
    (folder / ".classification.json").write_text(json.dumps(cls), encoding="utf-8")
    if with_answers:
        (folder / "Application Answers.md").write_text("Apply: url\n", encoding="utf-8")
    return folder


def test_split_company_role():
    assert ap.split_company_role("Scribd - Senior AI Data Engineer") == ("Scribd", "Senior AI Data Engineer")
    # only the FIRST " - " splits; role may contain hyphens
    assert ap.split_company_role("A - B - C") == ("A", "B - C")


def test_packet_pdf_name_prefixes_posted_date():
    assert ap.packet_pdf_name("Scribd", "Senior AI Data Engineer", "2026-06-28") == \
        "2026-06-28 · Scribd - Senior AI Data Engineer.pdf"
    assert ap.packet_pdf_name("Scribd", "Senior AI Data Engineer", None) == \
        "undated · Scribd - Senior AI Data Engineer.pdf"


def test_upload_packet_writes_record_and_calls_rclone(tmp_path):
    folder = make_role(tmp_path)
    calls = []
    rec = ap.upload_packet(folder, "gdrive:Apply Queue", "2026-07-01T22:00:00-05:00",
                           run=fake_run_factory(calls))
    assert rec["state"] == "queued"
    assert rec["pdf_remote"] == "gdrive:Apply Queue/2026-06-28 · Scribd - Senior AI Data Engineer.pdf"
    assert rec["answers_remote"] == "gdrive:Apply Queue/Scribd - Senior AI Data Engineer - Answers.txt"
    assert rec["posted_date"] == "2026-06-28"
    assert len(rec["pdf_sha256"]) == 64
    # two rclone copyto calls: PDF then answers
    assert [c[:2] for c in calls] == [["rclone", "copyto"], ["rclone", "copyto"]]
    on_disk = json.loads((folder / ".apply-packet.json").read_text(encoding="utf-8"))
    assert on_disk == rec


def test_upload_packet_missing_answers_is_partial_not_fatal(tmp_path):
    folder = make_role(tmp_path, with_answers=False)
    calls = []
    rec = ap.upload_packet(folder, "gdrive:Apply Queue", "2026-07-01T22:00:00-05:00",
                           run=fake_run_factory(calls))
    assert rec["answers_remote"] is None
    assert len(calls) == 1  # only the PDF uploaded


def test_upload_packet_no_pdf_raises(tmp_path):
    folder = tmp_path / "X - Y"
    folder.mkdir()
    (folder / ".classification.json").write_text("{}", encoding="utf-8")
    try:
        ap.upload_packet(folder, "gdrive:Apply Queue", "t", run=fake_run_factory([]))
        assert False, "expected PacketError"
    except ap.PacketError as e:
        assert "resume PDF" in str(e)


def test_upload_packet_rclone_failure_raises(tmp_path):
    folder = make_role(tmp_path)
    def failing_run(args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="boom")
    try:
        ap.upload_packet(folder, "gdrive:Apply Queue", "t", run=failing_run)
        assert False, "expected PacketError"
    except ap.PacketError as e:
        assert "rclone" in str(e)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: FAIL / error with `ModuleNotFoundError: No module named 'apply_packet'`

- [ ] **Step 3: Write the implementation**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/drip_runner/apply_packet.py scripts/drip_runner/test_apply_packet.py
git commit -m "drip-runner: apply_packet upload — build + rclone the per-role packet"
```

---

### Task 2: repost detection (`repost-check` subcommand)

**Files:**
- Modify: `scripts/drip_runner/apply_packet.py` (append functions + subcommand)
- Test: `scripts/drip_runner/test_apply_packet.py` (append tests)

**Interfaces:**
- Consumes: `Job Description.md` files under `Roles/` and `_Archived/`.
- Produces: `find_repost(jd_text: str, corpus: list[tuple[str, str]]) -> dict | None` returning `{"match_folder": str, "similarity": float}` at ≥ 0.85 similarity, else `None`; CLI `py -3 scripts/drip_runner/apply_packet.py repost-check "<role folder>" [--repo-root .]` printing one JSON line `{"repost": bool, "match_folder": ..., "similarity": ...}`. Task 6's skill step consumes that JSON.

- [ ] **Step 1: Write the failing tests** (append to `test_apply_packet.py`)

```python
JD_A = "We are hiring a Forward Deployed Engineer to build AI agents for logistics customers. " * 20
JD_B = JD_A.replace("logistics", "freight")          # near-identical -> repost
JD_C = "Staff accountant needed for tax season support in our Ohio office. " * 20


def test_normalize_jd_strips_noise():
    assert ap.normalize_jd("  Hello,\n\nWORLD!  ") == "hello world"


def test_find_repost_flags_near_duplicate():
    corpus = [("Old Co - FDE", JD_A), ("Other - Accountant", JD_C)]
    hit = ap.find_repost(JD_B, corpus)
    assert hit is not None
    assert hit["match_folder"] == "Old Co - FDE"
    assert hit["similarity"] >= 0.85


def test_find_repost_none_for_unrelated():
    assert ap.find_repost(JD_C, [("Old Co - FDE", JD_A)]) is None


def test_load_jd_corpus_skips_self(tmp_path):
    roles = tmp_path / "Roles"
    for name, text in [("A - X", JD_A), ("B - Y", JD_C)]:
        d = roles / name
        d.mkdir(parents=True)
        (d / "Job Description.md").write_text(text, encoding="utf-8")
    corpus = ap.load_jd_corpus(tmp_path, exclude=roles / "A - X")
    assert [c[0] for c in corpus] == ["B - Y"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: 4 new failures, `AttributeError: ... 'normalize_jd'`

- [ ] **Step 3: Implement** (append to `apply_packet.py`, and register the subcommand in `main`)

```python
import difflib, re

REPOST_THRESHOLD = 0.85
_WORDS = re.compile(r"[a-z0-9]+")


def normalize_jd(text: str) -> str:
    """Lowercased word soup — robust to punctuation/whitespace/casing edits."""
    return " ".join(_WORDS.findall((text or "").lower()))


def jd_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_jd(a), normalize_jd(b)).ratio()


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
```

In `main()`, after the `upload` subparser add:

```python
    rp = sub.add_parser("repost-check", help="fuzzy-match this JD against every filed JD")
    rp.add_argument("role_folder")
    rp.add_argument("--repo-root", default=".")
```
and in the dispatch: `if args.cmd == "repost-check": return _cli_repost_check(args)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/drip_runner/apply_packet.py scripts/drip_runner/test_apply_packet.py
git commit -m "drip-runner: repost-check — difflib JD fuzzy match vs filed corpus"
```

---

### Task 3: reconcile pass (`reconcile` subcommand)

**Files:**
- Modify: `scripts/drip_runner/apply_packet.py`
- Test: `scripts/drip_runner/test_apply_packet.py`

**Interfaces:**
- Consumes: `Pipeline.md` text, every `Roles/*/.apply-packet.json` and `_Archived/*/.apply-packet.json`, `outreach_worklist.active_section` / `row_is_applied` (existing).
- Produces: `reconcile_actions(repo_root: Path, pipeline_text: str) -> list[dict]` (pure; each action `{"action": "move"|"delete"|"reupload", "folder": Path, "record": dict}`), `apply_reconcile(actions, run, now_iso) -> list[str]` (executes rclone + rewrites records, returns human summary lines), CLI `py -3 scripts/drip_runner/apply_packet.py reconcile [--repo-root .] [--commit]`. `--commit` git-commits changed `.apply-packet.json` files with the no-op guard. Task 7 (run.ps1) calls this hourly.

Reconcile table (from the spec):

| Truth changed | Mirror action |
|---|---|
| Row marked Applied (company matched in Active section) | `move` both remotes into `<remote>/Applied/`, state → `applied` |
| Role folder now under `_Archived/` | `delete` both remotes, state → `removed` |
| Local PDF sha256 ≠ recorded (re-tailored resume) | `reupload` PDF, refresh hash + ts |

- [ ] **Step 1: Write the failing tests** (append)

```python
PIPELINE = """## Active
| **Scribd — Senior AI Data Engineer** | Applied 2026-06-30 | notes |
| **DRW — AI Engineer** | Recruiter screen | notes |

## Considering / not yet applied
| **Amazon — AI Builder Ring** | not yet applied | notes |
"""


def make_packet_role(tmp_path, base, company, role, state="queued", pdf_bytes=b"%PDF-1.4 fake"):
    folder = tmp_path / base / f"{company} - {role}"
    folder.mkdir(parents=True)
    pdf = folder / f"Kanu Madhok Resume - {company}.pdf"
    pdf.write_bytes(pdf_bytes)
    rec = {"schema": 1, "state": state,
           "pdf_remote": f"gdrive:Apply Queue/2026-06-28 · {company} - {role}.pdf",
           "answers_remote": f"gdrive:Apply Queue/{company} - {role} - Answers.txt",
           "pdf_sha256": ap.sha256_of(pdf), "uploaded_ts": "2026-06-28T08:00:00-05:00",
           "posted_date": "2026-06-28", "canonical_url": None, "repost": False,
           "easy_apply": False, "remote_dir": "gdrive:Apply Queue"}
    ap.write_packet(folder, rec)
    return folder


def test_reconcile_moves_applied_deletes_archived_reuploads_drift(tmp_path):
    applied = make_packet_role(tmp_path, "Roles", "Scribd", "Senior AI Data Engineer")
    steady = make_packet_role(tmp_path, "Roles", "DRW", "AI Engineer")
    archived = make_packet_role(tmp_path, "_Archived", "Meta", "AI PM")
    drifted = make_packet_role(tmp_path, "Roles", "Amazon", "AI Builder Ring")
    # simulate a re-tailored resume: PDF content changed after upload
    next(drifted.glob("*.pdf")).write_bytes(b"%PDF-1.4 retailored")

    actions = ap.reconcile_actions(tmp_path, PIPELINE)
    by = {a["folder"].name: a["action"] for a in actions}
    assert by == {"Scribd - Senior AI Data Engineer": "move",
                  "Meta - AI PM": "delete",
                  "Amazon - AI Builder Ring": "reupload"}
    assert steady.name not in by  # untouched role produces no action


def test_apply_reconcile_executes_and_updates_state(tmp_path):
    applied = make_packet_role(tmp_path, "Roles", "Scribd", "Senior AI Data Engineer")
    actions = ap.reconcile_actions(tmp_path, PIPELINE)
    calls = []
    lines = ap.apply_reconcile(actions, run=fake_run_factory(calls), now_iso="t2")
    # both remotes moved into Applied/
    assert ["rclone", "moveto"] == calls[0][:2] and "/Applied/" in calls[0][3]
    assert ["rclone", "moveto"] == calls[1][:2]
    rec = ap.read_packet(applied)
    assert rec["state"] == "applied"
    assert any("Scribd" in l for l in lines)


def test_reconcile_skips_non_queued_states(tmp_path):
    make_packet_role(tmp_path, "Roles", "Scribd", "Senior AI Data Engineer", state="applied")
    assert ap.reconcile_actions(tmp_path, PIPELINE) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: 3 new failures, `AttributeError: ... 'reconcile_actions'`

- [ ] **Step 3: Implement** (append; note the `outreach_worklist` import goes at the top of the file with the other imports)

```python
from outreach_worklist import active_section, row_is_applied


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
        except PacketError as e:
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
```

In `main()` add:

```python
    rc = sub.add_parser("reconcile", help="make the Drive mirror follow Pipeline/folder truth")
    rc.add_argument("--repo-root", default=".")
    rc.add_argument("--commit", action="store_true")
```
and dispatch `if args.cmd == "reconcile": return _cli_reconcile(args)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_packet.py -q`
Expected: 13 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/drip_runner/apply_packet.py scripts/drip_runner/test_apply_packet.py
git commit -m "drip-runner: packet reconcile — mirror follows Pipeline/_Archived truth"
```

---

### Task 4: `apply_digest.py` — daily ntfy digest

**Files:**
- Create: `scripts/drip_runner/apply_digest.py`
- Test: `scripts/drip_runner/test_apply_digest.py`
- Create (on the PC, NOT committed): `~/.claude/ntfy_topic.txt` containing `job-auto-abcee`

**Interfaces:**
- Consumes: `.apply-packet.json` records via `apply_packet.read_packet` / `_packet_folders`.
- Produces: `gather(repo_root: Path, now: datetime) -> dict` (keys `queued: list[dict]`, `stale: list[dict]` — queued > 3 days old), `compose(data: dict) -> str`, `send(topic: str, text: str, opener) -> None`, CLI `py -3 scripts/drip_runner/apply_digest.py [--repo-root .] [--send]`. Task 7 calls `--send` daily.

- [ ] **Step 1: Write the failing tests**

```python
"""Tests for apply_digest.py — injected clock + opener, no network."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pathlib import Path

import apply_digest as dg
from test_apply_packet import make_packet_role  # reuses the fixture helper


NOW = datetime.fromisoformat("2026-07-02T08:00:00-05:00")


def test_gather_splits_fresh_and_stale(tmp_path):
    import apply_packet as ap
    fresh = make_packet_role(tmp_path, "Roles", "Scribd", "Senior AI Data Engineer")
    rec = ap.read_packet(fresh)
    rec["uploaded_ts"] = "2026-07-01T08:00:00-05:00"  # 1 day old — inside the 3-day window
    ap.write_packet(fresh, rec)
    stale = make_packet_role(tmp_path, "Roles", "OldCo", "ML Engineer")
    rec = ap.read_packet(stale)
    rec["uploaded_ts"] = "2026-06-25T08:00:00-05:00"  # 7 days old
    ap.write_packet(stale, rec)
    data = dg.gather(tmp_path, NOW)
    names = {q["folder"] for q in data["queued"]}
    assert names == {"Scribd - Senior AI Data Engineer", "OldCo - ML Engineer"}
    assert [s["folder"] for s in data["stale"]] == ["OldCo - ML Engineer"]


def test_compose_reads_like_a_push(tmp_path):
    make_packet_role(tmp_path, "Roles", "Scribd", "Senior AI Data Engineer")
    text = dg.compose(dg.gather(tmp_path, NOW))
    assert "1 ready to apply" in text
    assert "Scribd" in text


def test_compose_empty_queue():
    assert dg.compose({"queued": [], "stale": []}) == "Apply Queue: empty"


def test_send_posts_to_ntfy():
    seen = {}
    def opener(req, timeout):
        seen["url"] = req.full_url
        seen["data"] = req.data
        class R:  # minimal response
            def __enter__(self): return self
            def __exit__(self, *a): return False
            status = 200
        return R()
    dg.send("job-auto-abcee", "hello", opener=opener)
    assert seen["url"] == "https://ntfy.sh/job-auto-abcee"
    assert seen["data"] == b"hello"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_digest.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'apply_digest'`

- [ ] **Step 3: Implement**

```python
"""Daily Apply Queue digest -> ntfy push. Pure compose, injected clock/opener.

Delivers the Applied Detector's fail-loud nudge (Spec - Applied Detector.md)
plus queue freshness. The topic name is a secret: read from
~/.claude/ntfy_topic.txt, never committed (Spec - Apply Packet.md, decision 3).
"""
from __future__ import annotations
import argparse, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

from apply_packet import _packet_folders, read_packet

STALE_DAYS = 3
TOPIC_FILE = Path.home() / ".claude" / "ntfy_topic.txt"


def gather(repo_root: Path, now: datetime) -> dict:
    queued, stale = [], []
    for folder in _packet_folders(repo_root):
        rec = read_packet(folder)
        if not rec or rec.get("state") != "queued":
            continue
        entry = {"folder": folder.name, "posted_date": rec.get("posted_date"),
                 "easy_apply": rec.get("easy_apply"), "uploaded_ts": rec.get("uploaded_ts")}
        queued.append(entry)
        try:
            age = (now - datetime.fromisoformat(rec["uploaded_ts"])).days
        except (TypeError, ValueError):
            age = None
        if age is not None and age > STALE_DAYS:
            stale.append({**entry, "age_days": age})
    queued.sort(key=lambda q: q.get("posted_date") or "", reverse=True)
    return {"queued": queued, "stale": stale}


def compose(data: dict) -> str:
    q, s = data["queued"], data["stale"]
    if not q:
        return "Apply Queue: empty"
    newest = q[0]
    lines = [f"Apply Queue: {len(q)} ready to apply (newest: {newest['folder']}"
             + (f", posted {newest['posted_date']}" if newest.get("posted_date") else "") + ")"]
    for item in s:
        lines.append(f"waiting {item['age_days']}d — did you apply? {item['folder']}")
    easy = [x["folder"] for x in q if x.get("easy_apply")]
    if easy:
        lines.append(f"Easy Apply available: {', '.join(easy)}")
    return "\n".join(lines)


def send(topic: str, text: str, opener=urllib.request.urlopen) -> None:
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=text.encode("utf-8"),
        headers={"Title": "Apply Queue digest"})
    with opener(req, timeout=15) as resp:
        if getattr(resp, "status", 200) >= 300:
            raise RuntimeError(f"ntfy returned {resp.status}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--send", action="store_true")
    args = p.parse_args(argv)
    now = datetime.now(timezone.utc).astimezone()
    text = compose(gather(Path(args.repo_root), now))
    print(text)
    if args.send:
        if not TOPIC_FILE.exists():
            print(f"DIGEST ERROR: {TOPIC_FILE} missing — cannot push", file=sys.stderr)
            return 1
        send(TOPIC_FILE.read_text(encoding="utf-8-sig").strip(), text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_apply_digest.py -q`
Expected: 4 passed

- [ ] **Step 5: Create the topic file on the PC** (one-time; NOT committed — it lives outside the repo)

```powershell
Set-Content -Path "$env:USERPROFILE\.claude\ntfy_topic.txt" -Value "job-auto-abcee" -Encoding utf8
```

- [ ] **Step 6: Live smoke test** (expect a push on Kanu's iPhone ntfy app, subscribed to `job-auto-abcee`)

Run: `py -3 scripts/drip_runner/apply_digest.py --repo-root . --send`
Expected: prints the digest text; exit 0; push arrives on the phone.

- [ ] **Step 7: Commit**

```bash
git add scripts/drip_runner/apply_digest.py scripts/drip_runner/test_apply_digest.py
git commit -m "drip-runner: apply_digest — daily queue digest to ntfy"
```

---

### Task 5: trace layer — register step 3.7

**Files:**
- Modify: `.claude/skills/jd-to-ready/scripts/trace_step.py:23-31`
- Modify: `.claude/skills/jd-to-ready/TRACE_SCHEMA.md:34`

**Interfaces:**
- Produces: step id `"3.7"` (primitive name `apply-packet`) accepted by `trace_step.py begin/end` for run-types `jd-to-ready` and `full`. Task 6's skill step depends on this.

- [ ] **Step 1: Edit `trace_step.py`** — replace lines 23–31 with:

```python
REQUIRED_STEPS = ["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]

# Per-run-type required-steps. REQUIRED_STEPS above stays the legacy "full"
# list so any caller that does not pass a run-type keeps the old contract.
RUN_TYPES = {
    "full": list(REQUIRED_STEPS),
    "jd-to-ready": ["1", "2", "3", "3.5", "3.7", "6", "7"],
    "stage-outreach": ["4", "4b", "4c", "5", "6", "7"],
}
```

- [ ] **Step 2: Edit `TRACE_SCHEMA.md`** — line 34, replace with:

```markdown
`required_steps` defaults to `["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]`.
```

- [ ] **Step 3: Run the full existing test suite** (trace layer has its own tests; nothing may regress)

Run: `py -3 -m pytest scripts/drip_runner .claude/skills/jd-to-ready -q`
Expected: all pass. If a trace test asserts the old step list verbatim, update that assertion to include `"3.7"` — that is the only acceptable test edit.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jd-to-ready/scripts/trace_step.py .claude/skills/jd-to-ready/TRACE_SCHEMA.md
git commit -m "jd-to-ready: register trace step 3.7 (apply-packet)"
```

---

### Task 6: `jd-to-ready` SKILL.md — Step 3.7 (the LLM-side judgment step)

**Files:**
- Modify: `.claude/skills/jd-to-ready/SKILL.md` (insert new `### Step 3.7` section between Step 3.5 and Step 6; update Step 6, Step 7, and the "What this skill produces" list)

**Interfaces:**
- Consumes: Task 1/2's CLI (`upload`, `repost-check`), Task 5's step id `3.7`, root `Application Profile.md`, `AI Build Walkthrough - Master.md`.
- Produces: `<role folder>/Application Answers.md`, updated `.classification.json` (adds `posted_date`, `canonical_url`, `easy_apply`, `repost`), `<role folder>/.apply-packet.json` (via the CLI), trace step 3.7 events.

- [ ] **Step 1: Insert the Step 3.7 section** after the Step 3.5 section (after SKILL.md line 254). Exact text to insert:

````markdown
### Step 3.7 — Build + upload the apply packet

The prep finish line is not "PDF in the repo" — it is "packet on the phone" (`Automation Design - Two-Orchestrator/Spec - Apply Packet.md`). This step resolves the true posting date, drafts the application answers, and uploads both artifacts to the Drive `Apply Queue/` via rclone. The PDF must NEVER be read into context or passed through an MCP call — the upload CLI moves it disk→Drive.

Begin the trace:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py begin --step 3.7 --primitive apply-packet --mode "" --prediction "canonical ATS URL + posted date resolved, Application Answers.md drafted from Application Profile.md with zero invented facts, packet uploaded to the Apply Queue with a date-prefixed filename, .apply-packet.json written"
```

**3.7a — Resolve the canonical posting + true posted date.** LinkedIn's "posted X days ago" is gamed by reposts; the ATS timestamp is the honest one. From the JD source (the LinkedIn posting's outbound apply link, or a search for `<company> greenhouse|ashby|lever <role>`), find the employer's own posting. Greenhouse (`boards-api.greenhouse.io/v1/boards/<org>/jobs`), Ashby (`api.ashbyhq.com/posting-api/job-board/<org>`), and Lever (`api.lever.co/v0/postings/<org>`) expose public JSON with real `updated_at`/`publishedDate`/`createdAt` fields — WebFetch the posting or the board JSON and extract the date. If no canonical source is found after ~3 fetches, set `posted_date: null` and record a gap `{source:"apply-packet", kind:"posted-date-unknown", detail:"no canonical ATS posting found"}` — do NOT trust the LinkedIn relative date. Also note whether the LinkedIn posting offers **Easy Apply** (`easy_apply`: true/false/null if unknown).

**3.7b — Repost check** (deterministic — do not judge similarity yourself):

```bash
python3 "<repo root>/scripts/drip_runner/apply_packet.py" repost-check "<role folder>" --repo-root "<repo root>"
```

Parse the JSON line. If `repost` is true, record a gap `{source:"apply-packet", kind:"repost-detected", detail:"~<similarity> match: <match_folder>"}` — the role still gets a packet (deprioritize, don't drop).

**3.7c — Update `.classification.json`.** Add/overwrite exactly these keys on the existing JSON (preserve everything else): `posted_date` (`"YYYY-MM-DD"` or null), `canonical_url` (string or null), `easy_apply` (true/false/null), `repost` (boolean from 3.7b).

**3.7d — Draft `Application Answers.md`.** The mobile copy-paste sheet for ATS forms. Pull facts ONLY from root `Application Profile.md` (never-invent rule: copy or placeholder). Structure:

```markdown
# Application Answers — <Company> · <Role>

**Apply here:** <canonical_url or the JD source URL>

## Standard fields
- Salary expectation: <from Application Profile.md, verbatim>
- Work authorization: <from Application Profile.md, verbatim>
- Notice period: <from Application Profile.md, verbatim>
- Phone / LinkedIn / GitHub: <from Application Profile.md, verbatim>

## Why <Company>
<3-5 sentences drafted from the step-2 themes + JD evidence, Kanu's voice, no hype words>

## Relevant project
<the 1-2 walkthroughs from AI Build Walkthrough - Master.md matching the archetype, compressed to a form-field paragraph each>

## Custom questions visible on the posting
<question → drafted answer, one pair per question; omit the section if none are visible>
```

**3.7e — Upload:**

```bash
python3 "<repo root>/scripts/drip_runner/apply_packet.py" upload "<role folder>"
```

Honor `APPLY_PACKET_REMOTE_DIR` if the environment sets it (the e2e test does). On non-zero exit, record a gap `{source:"apply-packet", kind:"upload-failed", detail:"<stderr line>"}` and close the step `partial` — the `.md`/`.pdf` in the repo remain the source of truth, and the hourly reconcile will retry the upload via the hash-drift path once the cause is fixed. Never let an upload failure abort the run.

Close the step (gaps from 3.7a/b/e, `--failure-pattern ""` — no taxonomy value covers packet defects yet, same known gap as the PDF-export kinds):

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py end --step 3.7 --primitive apply-packet --mode "" --status "ok|partial|failed" --prediction-met "true|false|partial|unknown" --produced '["Application Answers.md",".apply-packet.json"]' --gaps '<gaps or []>' --failure-pattern "" --tokens "$UNKNOWN_TOKENS"
```
````

- [ ] **Step 2: Update Step 6** (SKILL.md line 256 section) — add one bullet to the report list:

```markdown
- **Apply packet** — confirm the packet uploaded (Drive `Apply Queue/` filename with its posted-date prefix), flag `repost-detected` / `posted-date-unknown` / `upload-failed` gaps, and note Easy Apply availability
```

- [ ] **Step 3: Update Step 7** (line 270) — change the required-steps confirmation sentence to:

```markdown
Before calling `finish-run`, confirm that steps `1`, `2`, `3`, `3.5`, `3.7`, `6`, and `7` all have `step_end` events.
```

Also update the example JSON at lines 308–311: `steps_closed` and `required_steps` become `["1", "2", "3", "3.5", "3.7", "6", "7"]`, and `files_written` gains `"Application Answers.md"` and `".apply-packet.json"` (also add both to the `finish-run --files-written` example at line 288).

- [ ] **Step 4: Update "What this skill produces"** (section at line 24) — add two bullets:

```markdown
- `Application Answers.md` — copy-paste ATS answers drafted from root `Application Profile.md` (never invented)
- `.apply-packet.json` + the uploaded Drive packet (`Apply Queue/<posted-date> · <Company> - <Role>.pdf` + answers `.txt`) — the mobile-ready finish line
```

- [ ] **Step 5: Verify by golden-set dry run** (regression discipline from SKILL.md — the skill's own text is the artifact; no pytest covers it). Run the skill end-to-end on ONE already-prepped golden role in a scratch copy, or minimally verify the CLI half by hand:

```bash
python3 scripts/drip_runner/apply_packet.py repost-check "Roles/Amazon - AI Builder Ring" --repo-root .
APPLY_PACKET_REMOTE_DIR="gdrive:_test/Apply Queue" python3 scripts/drip_runner/apply_packet.py upload "Roles/Amazon - AI Builder Ring"
rclone lsf "gdrive:_test/Apply Queue" && rclone purge "gdrive:_test/Apply Queue"
```
Expected: repost JSON line prints; upload prints `uploaded: gdrive:_test/Apply Queue/...pdf`; lsf shows the files; purge cleans up. Delete the `.apply-packet.json` the dry run wrote into the golden role folder (`git checkout -- "Roles/Amazon - AI Builder Ring"` if tracked, else delete) — the dry run must leave no state.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/jd-to-ready/SKILL.md
git commit -m "jd-to-ready: step 3.7 — apply packet (posted date, answers, rclone upload)"
```

---

### Task 7: run.ps1 wiring — reconcile hourly, digest daily

**Files:**
- Modify: `scripts/drip_runner/run.ps1` (insert after the heartbeat block, i.e. after current line 206 `}` and before `Log "run end..."`)

**Interfaces:**
- Consumes: Task 3's `reconcile --commit` CLI, Task 4's `apply_digest.py --send` CLI, existing `Log` and `Show-Toast` functions.
- Produces: reconcile on every run (all modes — it is cheap and idempotent); digest only on the daily `saved` mode.

- [ ] **Step 1: Insert the block** (exact text; PowerShell 5.1 — no `&&`, no ternary):

```powershell
# ---- Apply Packet post-steps (Spec - Apply Packet.md) ----------------------
# Deterministic, LLM-free: reconcile makes the Drive mirror follow repo truth
# (runs every mode — cheap + idempotent); the digest pushes to ntfy on the
# daily saved pass only. Failures are loud (log + toast) but never kill the run.
try {
  $rec = (& py -3 (Join-Path $repo "scripts\drip_runner\apply_packet.py") reconcile --repo-root $repo --commit) | Out-String
  if ($rec.Trim()) { Log "packet reconcile: $($rec.Trim())" }
  if ($rec -match "FAILED") { Show-Toast "Apply packet reconcile failed" ($rec.Trim()) }
} catch { Log "packet reconcile crashed: $($_.Exception.Message)"; Show-Toast "Apply packet reconcile crashed" $_.Exception.Message }

if ($Mode -eq 'saved') {
  try {
    $dg = (& py -3 (Join-Path $repo "scripts\drip_runner\apply_digest.py") --repo-root $repo --send) | Out-String
    Log "digest: $($dg.Trim())"
    if ($LASTEXITCODE -ne 0) { Show-Toast "Apply digest failed" ($dg.Trim()) }
  } catch { Log "digest crashed: $($_.Exception.Message)"; Show-Toast "Apply digest crashed" $_.Exception.Message }
}
```

- [ ] **Step 2: Verify by manual invocation** (does a real reconcile against the live queue — safe: with no `queued` packets yet it must print `reconcile: no-op`):

```powershell
powershell -File scripts\drip_runner\run.ps1 -Mode outreach
```
Expected in `~/.claude/logs/drip-runner.log`: the usual run lines plus `packet reconcile: reconcile: no-op`.

- [ ] **Step 3: Commit**

```bash
git add scripts/drip_runner/run.ps1
git commit -m "drip-runner: wire packet reconcile (hourly) + ntfy digest (daily) into run.ps1"
```

---

### Task 8: e2e test integration

**Files:**
- Modify: `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` (add `check_packet`)
- Test: `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`
- Modify: `.claude/skills/two-orchestrator-e2e-test/SKILL.md` (add the packet step to the prep-side sequence)

**Interfaces:**
- Consumes: `.apply-packet.json` written by Task 1's CLI; the `APPLY_PACKET_REMOTE_DIR` override.
- Produces: `check_packet(clone: Path) -> dict` in the verifier (same `skill_result`/`check` helpers as the existing `check_*` functions at verify_artifacts.py:47-107).

- [ ] **Step 1: Write the failing test** (append to `test_verify_artifacts.py`, mirroring the file's existing test style — read two neighboring tests first and copy their fixture pattern):

```python
def test_check_packet_passes_on_test_remote(tmp_path):
    import json
    (tmp_path / ".apply-packet.json").write_text(json.dumps({
        "schema": 1, "state": "queued",
        "pdf_remote": "gdrive:_test/Apply Queue/2026-06-28 · X - Y.pdf",
        "answers_remote": "gdrive:_test/Apply Queue/X - Y - Answers.txt",
        "pdf_sha256": "0" * 64, "remote_dir": "gdrive:_test/Apply Queue",
    }), encoding="utf-8")
    (tmp_path / "Application Answers.md").write_text("x", encoding="utf-8")
    result = verify_artifacts.check_packet(tmp_path)
    assert all(c["ok"] for c in result["checks"])


def test_check_packet_fails_on_real_remote(tmp_path):
    import json
    (tmp_path / ".apply-packet.json").write_text(json.dumps({
        "schema": 1, "state": "queued", "pdf_remote": "gdrive:Apply Queue/x.pdf",
        "answers_remote": None, "pdf_sha256": "0" * 64,
        "remote_dir": "gdrive:Apply Queue",
    }), encoding="utf-8")
    result = verify_artifacts.check_packet(tmp_path)
    assert any(c["name"] == "packet-remote-is-test" and not c["ok"] for c in result["checks"])
```

- [ ] **Step 2: Run to verify failure**

Run: `py -3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -q`
Expected: 2 new failures, `AttributeError: ... 'check_packet'`

- [ ] **Step 3: Implement `check_packet`** (add after `check_pdf` at verify_artifacts.py:98; uses the module's existing `check`/`skill_result` helpers):

```python
def check_packet(clone: Path) -> dict:
    """Apply-packet artifacts: record exists, parses, and — non-negotiable —
    points at a _test remote, never the real Apply Queue."""
    f = clone / ".apply-packet.json"
    if not f.exists():
        return skill_result([check("packet-present", False, str(f))])
    try:
        rec = json.loads(f.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return skill_result([check("packet-parses", False, str(exc))])
    return skill_result([
        check("packet-parses", True),
        check("packet-state-queued", rec.get("state") == "queued", str(rec.get("state"))),
        check("packet-remote-is-test", "_test" in str(rec.get("remote_dir", "")),
              rec.get("remote_dir", "")),
        check("answers-md-present", (clone / "Application Answers.md").exists()),
    ])
```

Wire it into the verifier's main/report flow the same way `check_pdf` is wired (find where `check_pdf(...)` is called and add `check_packet(clone)` alongside it under the prep-side skills).

- [ ] **Step 4: Run to verify pass**

Run: `py -3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -q`
Expected: all pass.

- [ ] **Step 5: Update the e2e SKILL.md prep sequence** — after the PDF step in the numbered skill sequence (near line 36), insert:

```markdown
- **apply-packet** (jd-to-ready Step 3.7) → the sub-agent runs it with the test remote so the REAL Apply Queue is never touched: set `APPLY_PACKET_REMOTE_DIR="gdrive:_test/Apply Queue e2e"` in the step's environment (or pass `--remote-dir` to the upload CLI). Writes `<clone>/Application Answers.md` + `<clone>/.apply-packet.json`. Cleanup record in TEST REPORT.md gains one line: `rclone purge "gdrive:_test/Apply Queue e2e"` to empty the test remote.
```

- [ ] **Step 6: Commit**

```bash
git add ".claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" ".claude/skills/two-orchestrator-e2e-test/SKILL.md"
git commit -m "e2e-test: verify apply packet artifacts; force _test remote"
```

---

### Task 9: docs sync

**Files:**
- Modify: `CLAUDE.md` + `AGENTS.md` (the `jd-to-ready` bullet in "Installable skills", identical text in both files)
- Modify: `Skills.md` (jd-to-ready entry) and `Automation Architecture - Drip Runner.md` (Pass A description)

**Interfaces:** none — documentation only.

- [ ] **Step 1: CLAUDE.md + AGENTS.md** — in the `jd-to-ready` bullet, change

```
tailor resume from `Resume Achievements Master.md` → build + verify PDF. **Stops at the apply gate**
```
to
```
tailor resume from `Resume Achievements Master.md` → build + verify PDF → upload the apply packet (PDF + `Application Answers.md` from `Application Profile.md`) to the Drive `Apply Queue/` via rclone. **Stops at the apply gate**
```

- [ ] **Step 2: Skills.md and `Automation Architecture - Drip Runner.md`** — locate the jd-to-ready / Pass A description in each and append this sentence verbatim (do not rewrite anything else):

```
Pass A's finish line is the apply packet: the tailored PDF + an answers file land in the Drive `Apply Queue/` folder (rclone remote `gdrive`), the hourly run reconciles the folder against Pipeline truth, and the daily run pushes an ntfy digest — see `Automation Design - Two-Orchestrator/Spec - Apply Packet.md`.
```

- [ ] **Step 3: Commit + push everything**

```bash
git add CLAUDE.md AGENTS.md Skills.md "Automation Architecture - Drip Runner.md"
git commit -m "docs: apply-packet finish line in skill maps + drip-runner architecture"
git pull --rebase --autostash
git push
```

---

## Self-review notes (spec coverage)

- Spec "What the packet is" → Tasks 1, 6 (filenames, answers doc). ✔
- Spec "Application Profile.md" → already seeded (commit `31a7761`); consumed by Task 6. ✔
- Spec "Freshness" → Task 2 (repost), Task 6 step 3.7a (ATS date), Task 1 (date-prefixed filename), Task 4 (newest-first digest). ✔
- Spec "Lifecycle — mirror" table → Task 3 (all three rows), Task 7 (cadence). Row "verify-postings grades DEAD → packet removed": **deliberately deferred** — verify-postings records grades in its own report, not in a file reconcile can read; the archived-folder delete covers the closure path today. Noted as vNext in the spec if wanted.
- Spec "The digest" → Task 4 + Task 7. Digest v1 carries queue counts + stale nudges + Easy Apply; "unsent outreach drafts" line deferred until the cloud secretary exposes sent-detection in a file.
- Spec "Two-machine rules" → PC-only writer (Task 7 is the only scheduler hook), state in committed `.apply-packet.json` (Task 1/3), repo-relative paths throughout. ✔
- Spec "Resolved decisions" 1–4 → rclone (Tasks 1/3), profile (done), ntfy topic file (Task 4 step 5), Easy Apply flag (Tasks 1/4/6). ✔
- Spec "does NOT do" → e2e test isolation Task 8; no form-filling, no LinkedIn, no state DB anywhere. ✔
- Pipeline-row posted-date (spec "record … in the Pipeline row"): **deliberately narrowed** to `.classification.json`/`.apply-packet.json` only — Pipeline rows are parsed by regex readers (`outreach_worklist`, dashboard) and prose edits there risk breaking the worklist; the digest surfaces freshness instead. Flag to Kanu at review.
