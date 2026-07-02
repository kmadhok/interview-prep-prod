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
    dg.send("test-topic", "hello", opener=opener)
    assert seen["url"] == "https://ntfy.sh/test-topic"
    assert seen["data"] == b"hello"
