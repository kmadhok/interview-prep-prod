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
