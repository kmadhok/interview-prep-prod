"""Tests for saved_jobs_ledger — the saved-jobs processed-ledger."""
from __future__ import annotations
import json
from pathlib import Path

import saved_jobs_ledger as L


def test_missing_file_is_empty_ledger(tmp_path):
    led = L.load(str(tmp_path / "nope.json"))
    assert led == {"version": 1, "entries": {}}
    assert L.is_processed("123", led) is False


def test_mark_then_is_processed_roundtrip(tmp_path):
    path = str(tmp_path / "ledger.json")
    led = L.load(path)
    L.mark(led, "4420569994", "done", note="filed NBA", ts="2026-06-21")
    L.save(path, led)

    reloaded = L.load(path)
    assert L.is_processed("4420569994", reloaded) is True
    assert reloaded["entries"]["4420569994"]["status"] == "done"
    assert reloaded["entries"]["4420569994"]["note"] == "filed NBA"


def test_error_and_skipped_count_as_processed(tmp_path):
    led = L.load(str(tmp_path / "l.json"))
    L.mark(led, "111", "error", note="get_job_details empty")
    L.mark(led, "222", "skipped")
    assert L.is_processed("111", led) is True
    assert L.is_processed("222", led) is True


def test_unknown_id_is_new(tmp_path):
    led = L.load(str(tmp_path / "l.json"))
    L.mark(led, "111", "done")
    assert L.is_processed("999", led) is False


def test_empty_job_id_never_processed(tmp_path):
    led = L.load(str(tmp_path / "l.json"))
    assert L.is_processed("", led) is False


def test_bad_status_rejected(tmp_path):
    led = L.load(str(tmp_path / "l.json"))
    try:
        L.mark(led, "1", "queued")
    except ValueError:
        return
    raise AssertionError("expected ValueError for bad status")


def test_corrupt_ledger_fails_loud(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    try:
        L.load(str(path))
    except SystemExit:
        return
    raise AssertionError("expected SystemExit on corrupt ledger")


def test_save_is_utf8_no_bom_sorted(tmp_path):
    path = str(tmp_path / "l.json")
    led = L.load(path)
    L.mark(led, "b", "done")
    L.mark(led, "a", "done")
    L.save(path, led)
    raw = Path(path).read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")  # no BOM
    # sorted keys -> 'a' entry appears before 'b'
    text = raw.decode("utf-8")
    assert text.index('"a"') < text.index('"b"')
