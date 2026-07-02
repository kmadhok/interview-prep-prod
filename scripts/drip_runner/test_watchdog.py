"""Tests for watchdog.py — the five staleness/threshold checks + anti-flap.

`now` is injected everywhere so the suite is clock-free and deterministic. A
healthy heartbeat is the shared baseline; each test perturbs exactly one field.
"""
from datetime import datetime, timedelta, timezone

import watchdog as w

# Fixed reference "now": Wed 2026-07-01 21:00 CDT. All fixtures are relative to it.
NOW = datetime(2026, 7, 1, 21, 0, tzinfo=timezone(timedelta(hours=-5)))


def hb(**overrides):
    """A HEALTHY heartbeat relative to NOW; overrides patch pc.*/cloud.* fields.

    Keys with a dot (e.g. 'pc.last_ok_outreach') patch nested fields.
    """
    base = {
        "pc": {
            "last_ok_saved": (NOW - timedelta(hours=5)).isoformat(),
            "last_ok_outreach": (NOW - timedelta(hours=2)).isoformat(),
            "consecutive_aborts": 0,
            "daemon_ok": True,
        },
        "cloud": {
            "last_ok_sweep": (NOW - timedelta(hours=6)).isoformat(),
        },
    }
    for k, v in overrides.items():
        section, _, field = k.partition(".")
        base[section][field] = v
    return base


# --- healthy baseline ------------------------------------------------------
def test_healthy_all_checks_pass():
    assert w.evaluate(hb(), NOW, "all") == []


# --- pc_pass_b (>26h) ------------------------------------------------------
def test_pass_b_trips_past_26h():
    a = w.check_pc_pass_b(hb(**{"pc.last_ok_outreach": (NOW - timedelta(hours=27)).isoformat()}), NOW)
    assert a.tripped and a.key == "pc_pass_b"
    assert a.line.startswith("⚠ WATCHDOG 2026-07-01:")
    assert "Pass B" in a.line


def test_pass_b_ok_just_under_26h():
    assert not w.check_pc_pass_b(hb(**{"pc.last_ok_outreach": (NOW - timedelta(hours=25, minutes=59)).isoformat()}), NOW).tripped


def test_pass_b_missing_timestamp_trips():
    assert w.check_pc_pass_b({"pc": {}}, NOW).tripped


# --- pc_pass_a (>50h) ------------------------------------------------------
def test_pass_a_trips_past_50h():
    a = w.check_pc_pass_a(hb(**{"pc.last_ok_saved": (NOW - timedelta(hours=51)).isoformat()}), NOW)
    assert a.tripped and "Pass A" in a.line


def test_pass_a_ok_at_49h():
    assert not w.check_pc_pass_a(hb(**{"pc.last_ok_saved": (NOW - timedelta(hours=49)).isoformat()}), NOW).tripped


# --- daemon ----------------------------------------------------------------
def test_daemon_trips_when_false():
    a = w.check_daemon(hb(**{"pc.daemon_ok": False}), NOW)
    assert a.tripped and "daemon" in a.line.lower()


def test_daemon_ok_when_true():
    assert not w.check_daemon(hb(), NOW).tripped


def test_daemon_missing_flag_does_not_trip():
    # Unknown != down; the pass checks cover a dead PC, this is daemon-specific.
    assert not w.check_daemon({"pc": {}}, NOW).tripped


# --- cloud_sweep (>3 weekdays) + weekday arithmetic ------------------------
def test_cloud_sweep_healthy_recent():
    assert not w.check_cloud_sweep(hb(), NOW).tripped


def test_cloud_sweep_survives_a_weekend():
    # Sweep last ran Fri 2026-06-26 16:00; "now" is Mon 06-29 09:00. Only Monday
    # counts (1 weekday) — the weekend must NOT trip the >3-weekday rule.
    fri = datetime(2026, 6, 26, 16, 0, tzinfo=timezone(timedelta(hours=-5)))
    mon = datetime(2026, 6, 29, 9, 0, tzinfo=timezone(timedelta(hours=-5)))
    assert w.weekdays_between(fri, mon) == 1
    assert not w.check_cloud_sweep({"cloud": {"last_ok_sweep": fri.isoformat()}}, mon).tripped


def test_cloud_sweep_trips_after_4_weekdays():
    # Sweep last ran Mon 06-22 10:00; now Fri 06-26 12:00 → Tue,Wed,Thu,Fri = 4 weekdays > 3.
    mon = datetime(2026, 6, 22, 10, 0, tzinfo=timezone(timedelta(hours=-5)))
    fri = datetime(2026, 6, 26, 12, 0, tzinfo=timezone(timedelta(hours=-5)))
    assert w.weekdays_between(mon, fri) == 4
    a = w.check_cloud_sweep({"cloud": {"last_ok_sweep": mon.isoformat()}}, fri)
    assert a.tripped and "weekdays" in a.line


def test_weekdays_between_boundary_is_3_not_tripped():
    # Exactly 3 weekdays elapsed must NOT trip (rule is strictly > 3).
    mon = datetime(2026, 6, 22, 10, 0, tzinfo=timezone(timedelta(hours=-5)))
    thu = datetime(2026, 6, 25, 12, 0, tzinfo=timezone(timedelta(hours=-5)))
    assert w.weekdays_between(mon, thu) == 3
    assert not w.check_cloud_sweep({"cloud": {"last_ok_sweep": mon.isoformat()}}, thu).tripped


def test_weekdays_between_same_day_is_zero():
    assert w.weekdays_between(NOW, NOW) == 0
    assert w.weekdays_between(NOW, NOW - timedelta(hours=1)) == 0  # end before start


def test_cloud_sweep_missing_timestamp_trips():
    assert w.check_cloud_sweep({"cloud": {}}, NOW).tripped


# --- aborts (>=3) ----------------------------------------------------------
def test_aborts_trips_at_3():
    a = w.check_aborts(hb(**{"pc.consecutive_aborts": 3}), NOW)
    assert a.tripped and "self-deadlocked" in a.line


def test_aborts_ok_at_2():
    assert not w.check_aborts(hb(**{"pc.consecutive_aborts": 2}), NOW).tripped


def test_aborts_trips_at_38():
    assert w.check_aborts(hb(**{"pc.consecutive_aborts": 38}), NOW).tripped


# --- evaluate groups -------------------------------------------------------
def test_evaluate_pc_group_runs_three_checks():
    sick = hb(**{"pc.daemon_ok": False, "pc.last_ok_outreach": (NOW - timedelta(hours=40)).isoformat()})
    keys = {a.key for a in w.evaluate(sick, NOW, "pc")}
    assert keys == {"pc_pass_b", "daemon"}


def test_evaluate_cloud_group_only_sweep():
    # A dead PC is invisible to the PC-side group; it only watches the cloud sweep.
    sick = hb(**{"pc.consecutive_aborts": 9})
    assert w.evaluate(sick, NOW, "cloud") == []


def test_evaluate_aborts_group_local_only():
    keys = {a.key for a in w.evaluate(hb(**{"pc.consecutive_aborts": 5}), NOW, "aborts")}
    assert keys == {"aborts"}


# --- anti-flap: once per incident / re-alert after 24h ---------------------
def test_should_alert_first_time_when_no_prior():
    assert w.should_alert(None, NOW) is True


def test_should_alert_suppressed_within_24h():
    last = NOW - timedelta(hours=5)
    assert w.should_alert(last, NOW) is False


def test_should_alert_refires_after_24h():
    last = NOW - timedelta(hours=25)
    assert w.should_alert(last, NOW) is True


def test_should_alert_boundary_exactly_24h_refires():
    last = NOW - timedelta(hours=24)
    assert w.should_alert(last, NOW) is True


# --- CLI -------------------------------------------------------------------
def test_cli_healthy_prints_nothing(tmp_path, capsys):
    import json
    f = tmp_path / "hb.json"
    f.write_text(json.dumps(hb()), encoding="utf-8")
    rc = w.main(["--heartbeat", str(f), "--check", "all", "--now", NOW.isoformat()])
    assert rc == 0 and capsys.readouterr().out.strip() == ""


def test_cli_tripped_prints_line(tmp_path, capsys):
    import json
    f = tmp_path / "hb.json"
    f.write_text(json.dumps(hb(**{"pc.consecutive_aborts": 4})), encoding="utf-8")
    rc = w.main(["--heartbeat", str(f), "--check", "aborts", "--now", NOW.isoformat()])
    out = capsys.readouterr().out
    assert rc == 0 and "⚠ WATCHDOG" in out and "aborted 4 runs" in out


def test_cli_anti_flap_suppresses_recent(tmp_path, capsys):
    import json
    f = tmp_path / "hb.json"
    f.write_text(json.dumps(hb(**{"pc.consecutive_aborts": 4})), encoding="utf-8")
    recent = (NOW - timedelta(hours=3)).isoformat()
    rc = w.main(["--heartbeat", str(f), "--check", "aborts", "--now", NOW.isoformat(), "--last-alert", recent])
    assert rc == 0 and capsys.readouterr().out.strip() == ""


def test_cli_missing_heartbeat_file_trips(tmp_path, capsys):
    # Missing file -> empty dict -> pass checks trip (fail loud).
    missing = tmp_path / "nope.json"
    rc = w.main(["--heartbeat", str(missing), "--check", "pc", "--now", NOW.isoformat()])
    assert rc == 0 and "⚠ WATCHDOG" in capsys.readouterr().out
