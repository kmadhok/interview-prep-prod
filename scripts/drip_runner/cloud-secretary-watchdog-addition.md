# Cloud Secretary — Machine Watchdog addition (paste into the web-UI routine)

The cloud secretary routine's prompt is managed in the claude.ai web UI
(routine `trig_01Dhy19jRLQM6sggLQ4249rm`), not in this repo. There is **no
committed copy** to edit, so paste the two blocks below into that routine's
prompt: BLOCK A near the top (right after the `git pull` step, before the Gmail
sweep) and BLOCK B at the very end (after the sweep succeeds, as part of the
commit step). Source of truth: `Automation Design - Two-Orchestrator/Spec - Machine Watchdog.md`.

This is the cloud half of "the two machines watch each other": the PC watches the
cloud's sweep freshness; the cloud watches the PC's pass freshness + daemon flag.
All threshold numbers live in `scripts/drip_runner/watchdog.py` — never re-encode
them in the prompt.

---

## BLOCK A — watch the PC (run once, every run, right after `git pull`)

WATCHDOG — PC-SIDE LIVENESS CHECK
After the repo is pulled and before the Gmail sweep, run:

```
python3 scripts/drip_runner/watchdog.py --check pc --heartbeat scripts/drip_runner/heartbeat.json
```

(Use `py -3` instead of `python3` if this routine runs on Windows.) This runs the
three PC-side checks from the spec: Pass B stale (`pc.last_ok_outreach` >26h),
Pass A stale (`pc.last_ok_saved` >50h), and LinkedIn daemon down (`pc.daemon_ok == false`).

- If it prints **nothing**, the PC is healthy — continue with the sweep.
- If it prints one or more `⚠ WATCHDOG …` lines, the PC belt has stalled. **ANTI-FLAP:**
  scan the top of `Pipeline.md` for an existing `⚠ WATCHDOG` line for the SAME check
  (PC Pass A / PC Pass B / LinkedIn daemon) dated within the last 24h. Skip any check
  already alerted in that window (alert once per incident; re-alert at most every 24h).
  For each remaining tripped line:
  1. Prepend it verbatim as a new `_⚠ WATCHDOG …_` audit line at the top of `Pipeline.md`
     (same chained style as the existing `_Last updated:_` line).
  2. Open this run's summary/report with the same line(s).
  Then continue the sweep — the watchdog only makes the failure **seen**; it does not
  block or fix anything.
- **Recovery line:** if a prior `⚠ WATCHDOG` PC line exists in `Pipeline.md` but this
  run's check for that same signal now prints nothing (the PC recovered), append one
  closing line: `_watchdog: PC <pass> healthy again as of <YYYY-MM-DD HH:MM>_`.

---

## BLOCK B — stamp the cloud heartbeat (at the end, only on a successful sweep)

WATCHDOG — STAMP CLOUD LIVENESS
On a **successful** sweep (Gmail read + Pipeline reconcile completed without error),
before/with the routine's normal commit:

1. Update `scripts/drip_runner/heartbeat.json`: set `cloud.last_ok_sweep` to the
   current time in ISO-8601 with offset (e.g. `2026-07-01T16:03:00-05:00`). Leave all
   `pc.*` fields untouched — those belong to the PC. Write the file as UTF-8 **without a BOM**.

2. **>20h commit discipline (do NOT churn `main` hourly):** check the age of the
   committed heartbeat with
   `git log -1 --format=%cI -- scripts/drip_runner/heartbeat.json`.
   - If the committed copy is **≤20h old**, DO NOT commit the heartbeat this run
     (the local timestamp bump stays uncommitted; a later run past the 20h mark
     commits it). This preserves the no-op guard so a healthy-but-idle cloud still
     proves liveness ~once/day without hourly churn.
   - If it is **>20h old** (or never committed), commit the heartbeat: piggyback it
     onto this run's existing sweep/reconcile commit if one is being made, otherwise
     make a lone `git commit -m "drip-runner: heartbeat (cloud)"`. Then `git push`
     (if the push is rejected, `git pull --rebase` and push once more).

3. If the sweep **failed**, do NOT stamp `cloud.last_ok_sweep` — a stale timestamp is
   exactly what lets the PC's `--check cloud` catch a dead cloud routine.
