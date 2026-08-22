"""Machine Watchdog: staleness/threshold logic for the two machines' heartbeats.

Pure functions + a thin CLI, same shape as outreach_worklist.py / prepped_not_applied.py.
No LLM, no network, no clock reads in the pure layer — `now` is injected at the CLI
boundary so every check is deterministic and pytest-covered.

Source of truth: `Automation Design - Two-Orchestrator/Spec - Machine Watchdog.md`.
The two machines (PC + cloud secretary) watch EACH OTHER via a single committed
heartbeat file. Each side checks the OTHER's freshness every run and raises a loud,
human-visible alert when it goes stale. This module is the single home of the five
threshold checks so run.ps1 and the runner prompts never duplicate the numbers.

The five checks (from the spec's checks table):
  key            watcher  watched          tripped when
  pc_pass_b      cloud    PC Pass B        now - pc.last_ok_outreach > 26h
  pc_pass_a      cloud    PC Pass A        now - pc.last_ok_saved    > 50h
  daemon         cloud    LinkedIn daemon  pc.daemon_ok == false
  cloud_sweep    PC       cloud secretary  now - cloud.last_ok_sweep > 3 weekdays
  aborts         PC-local itself           pc.consecutive_aborts     >= 3

Anti-flap: alert once per incident, re-alert at most every 24h while unhealthy
(see should_alert). The caller passes the timestamp of the last alert it already
emitted (read from Pipeline.md's existing WATCHDOG line, or a local marker); the
module decides whether a fresh alert is due.
"""
from __future__ import annotations
import argparse, json, sys
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Default thresholds (hours unless noted). Named so tests and the two runners
# reference one number, never a literal scattered across shell + prompts.
PASS_B_HOURS = 26
PASS_A_HOURS = 50
SWEEP_WEEKDAYS = 3
ABORT_STREAK = 3
REALERT_HOURS = 24

# A single evaluated check. `line` is the ready-to-paste ⚠ WATCHDOG audit/alert
# text (empty when not tripped). `key` lets callers select/suppress by check.
Alert = namedtuple("Alert", ["key", "tripped", "line"])


# ---------------------------------------------------------------------------
# Parsing / small time helpers (pure)
# ---------------------------------------------------------------------------
def load_heartbeat(path) -> dict:
    """Load the heartbeat JSON. Missing file -> empty dict (treated as 'unknown',
    which the checks surface as tripped — fail loud, never fail silent)."""
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def parse_ts(s):
    """Parse an ISO-8601 timestamp (with offset) to an aware datetime, or None.

    None/'' -> None so the checks can treat 'never stamped' as stale explicitly.
    A naive timestamp is assumed UTC so arithmetic never raises.
    """
    if not s:
        return None
    dt = datetime.fromisoformat(str(s))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def hours_since(now, ts) -> float:
    """Whole-and-fractional hours from `ts` to `now`. Both aware datetimes."""
    return (now - ts).total_seconds() / 3600.0


def weekdays_between(start, end) -> int:
    """Count Mon–Fri calendar dates crossed going from `start` to `end`.

    Counts each weekday DATE strictly after start's date, up to and including
    end's date. Weekends don't count, so a Friday-evening heartbeat is still
    '0 weekdays stale' on Saturday and Sunday and only reaches 1 on Monday.
    That is what makes the >3-weekday rule survive a normal weekend without
    false-alarming. Returns 0 when end <= start.
    """
    if end <= start:
        return 0
    days = 0
    cur = start.date()
    end_date = end.date()
    while cur < end_date:
        cur += timedelta(days=1)
        if cur.weekday() < 5:  # Mon=0 .. Fri=4
            days += 1
    return days


def _stamp(dt) -> str:
    """Format an aware datetime as 'MM-DD HH:MM' for the human-readable alert."""
    return dt.strftime("%m-%d %H:%M")


def _today(now) -> str:
    return now.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# The five checks (pure). Each returns an Alert; .tripped drives the decision,
# .line is the rendered audit text ready for Pipeline.md / a run report.
# ---------------------------------------------------------------------------
def check_pc_pass_b(hb, now, threshold_hours=PASS_B_HOURS) -> Alert:
    """Trip when outreach has never succeeded or is older than the strict hour limit."""
    ts = parse_ts((hb.get("pc") or {}).get("last_ok_outreach"))
    if ts is None:
        return Alert("pc_pass_b", True, (
            f"⚠ WATCHDOG {_today(now)}: PC outreach pass (Pass B) has no recorded "
            f"successful run (pc.last_ok_outreach missing). Belt may be stalled — roles "
            f"marked Applied are not being staged. Check ~/.claude/logs/drip-runner.log on the PC."))
    hrs = hours_since(now, ts)
    if hrs > threshold_hours:
        return Alert("pc_pass_b", True, (
            f"⚠ WATCHDOG {_today(now)}: PC outreach pass (Pass B) has not completed since "
            f"{_stamp(ts)} ({int(hrs)}h ago, >{threshold_hours}h). Belt is stalled — roles "
            f"marked Applied are not being staged. Check ~/.claude/logs/drip-runner.log on the PC."))
    return Alert("pc_pass_b", False, "")


def check_pc_pass_a(hb, now, threshold_hours=PASS_A_HOURS) -> Alert:
    """Trip when saved-job preparation has no timestamp or exceeds its hour limit."""
    ts = parse_ts((hb.get("pc") or {}).get("last_ok_saved"))
    if ts is None:
        return Alert("pc_pass_a", True, (
            f"⚠ WATCHDOG {_today(now)}: PC saved-jobs pass (Pass A) has no recorded "
            f"successful run (pc.last_ok_saved missing). Saved jobs are not being prepped. "
            f"Check ~/.claude/logs/drip-runner.log on the PC."))
    hrs = hours_since(now, ts)
    if hrs > threshold_hours:
        return Alert("pc_pass_a", True, (
            f"⚠ WATCHDOG {_today(now)}: PC saved-jobs pass (Pass A) has not completed since "
            f"{_stamp(ts)} ({int(hrs)}h ago, >{threshold_hours}h). Saved jobs are not being "
            f"prepped. Check ~/.claude/logs/drip-runner.log on the PC."))
    return Alert("pc_pass_a", False, "")


def check_daemon(hb, now) -> Alert:
    """LinkedIn daemon down flag. Only the explicit boolean False trips it; a
    missing flag is 'unknown' and does NOT trip (the pass checks already cover a
    dead PC — this check exists only for the specific daemon-down-but-PC-alive case)."""
    val = (hb.get("pc") or {}).get("daemon_ok")
    if val is False:
        return Alert("daemon", True, (
            f"⚠ WATCHDOG {_today(now)}: LinkedIn daemon reported down (daemon_ok=false) in "
            f"the latest PC heartbeat. LinkedIn scraping is blocked until it is restarted "
            f"(reboot, or re-run the daemon Task Scheduler task)."))
    return Alert("daemon", False, "")


def check_cloud_sweep(hb, now, threshold_weekdays=SWEEP_WEEKDAYS) -> Alert:
    """Trip after more than the allowed crossed weekdays, treating no stamp as stale."""
    ts = parse_ts((hb.get("cloud") or {}).get("last_ok_sweep"))
    if ts is None:
        return Alert("cloud_sweep", True, (
            f"⚠ WATCHDOG {_today(now)}: Cloud secretary sweep has no recorded successful run "
            f"(cloud.last_ok_sweep missing). Applied detection from Gmail is stalled — check "
            f"routine trig_01Dhy19jRLQM6sggLQ4249rm in the claude.ai UI."))
    n = weekdays_between(ts, now)
    if n > threshold_weekdays:
        return Alert("cloud_sweep", True, (
            f"⚠ WATCHDOG {_today(now)}: Cloud secretary sweep has not completed since "
            f"{_stamp(ts)} ({n} weekdays ago, >{threshold_weekdays}). Applied detection from Gmail "
            f"is stalled — check routine trig_01Dhy19jRLQM6sggLQ4249rm in the claude.ai UI."))
    return Alert("cloud_sweep", False, "")


def check_aborts(hb, now, threshold=ABORT_STREAK) -> Alert:
    """Trip at or above the consecutive-abort threshold, defaulting a missing count to zero."""
    n = int((hb.get("pc") or {}).get("consecutive_aborts") or 0)
    if n >= threshold:
        return Alert("aborts", True, (
            f"⚠ WATCHDOG {_today(now)}: PC drip-runner has aborted {n} runs in a row "
            f"(>={threshold}) before invoking Claude. The belt is self-deadlocked — check "
            f"~/.claude/logs/drip-runner.log on the PC."))
    return Alert("aborts", False, "")


# Which checks each watcher runs. 'pc' = the cloud secretary watching the PC;
# 'cloud' = the PC watching the cloud secretary; 'aborts' = the PC watching itself.
_GROUPS = {
    "pc": (check_pc_pass_b, check_pc_pass_a, check_daemon),
    "cloud": (check_cloud_sweep,),
    "aborts": (check_aborts,),
}
_GROUPS["all"] = _GROUPS["pc"] + _GROUPS["cloud"] + _GROUPS["aborts"]


def evaluate(hb, now, group="all") -> list:
    """Run a group of checks and return the Alerts that tripped (in table order)."""
    checks = _GROUPS[group]
    return [a for a in (fn(hb, now) for fn in checks) if a.tripped]


def should_alert(last_alert, now, min_hours=REALERT_HOURS) -> bool:
    """Anti-flap gate: emit an alert only if none was emitted in the last `min_hours`.

    `last_alert` is the aware datetime of the most recent WATCHDOG alert for this
    incident (None if never alerted). Alert once per incident; while still
    unhealthy, re-alert at most every 24h so the watchdog never trains the user to
    ignore it. Returns True when a fresh alert is due.
    """
    if last_alert is None:
        return True
    return hours_since(now, last_alert) >= min_hours


# ---------------------------------------------------------------------------
# CLI — run.ps1 and the runner prompts shell out here rather than duplicating
# thresholds. Prints one ⚠ WATCHDOG line per tripped-and-due check; prints
# nothing (and exits 0) when healthy or when anti-flap suppresses the alert.
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    """Emit due watchdog lines in UTF-8, suppressing healthy and anti-flapped incidents."""
    p = argparse.ArgumentParser(description="Machine Watchdog staleness checks")
    p.add_argument("--heartbeat", required=True, help="path to heartbeat.json")
    p.add_argument("--check", choices=sorted(_GROUPS), default="all",
                   help="which watcher's checks to run (pc=cloud watches PC, "
                        "cloud=PC watches cloud, aborts=PC-local, all)")
    p.add_argument("--now", default=None, help="ISO timestamp to evaluate against (default: real now)")
    p.add_argument("--last-alert", default=None,
                   help="ISO timestamp of the last alert already emitted; suppresses "
                        "output if <24h ago (anti-flap)")
    args = p.parse_args(argv)

    # The alert lines carry a ⚠ (U+26A0). Windows' default cp1252 stdout can't
    # encode it and would crash on print — force UTF-8 (run.ps1 already reads the
    # child's stdout as UTF-8). Guarded: older/replaced stdout may lack reconfigure.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    now = parse_ts(args.now) if args.now else datetime.now(timezone.utc).astimezone()
    hb = load_heartbeat(args.heartbeat)
    alerts = evaluate(hb, now, args.check)
    if not alerts:
        return 0
    if not should_alert(parse_ts(args.last_alert), now):
        return 0  # tripped but within the 24h anti-flap window
    for a in alerts:
        print(a.line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
