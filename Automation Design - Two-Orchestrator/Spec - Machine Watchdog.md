# Spec — Machine Watchdog (runner-level fail-loud)

_Drafted 2026-07-01, the evening the belt came back after a 34-hour silent stall. Parent: `Automation Architecture - Purpose.md` (invariant 4). Companions: `Spec - Applied Detector.md` (role-level fail-loud), `Spec - Orchestrator 1 (jd-to-ready prep).md`, `Spec - Orchestrator 2 (stage-outreach).md`._

## Why this spec exists — the purpose it serves

The system's purpose says **"no babysitting"** (invariant 3) and **"fail loud, never fail silent"** (invariant 4). Those two invariants are in tension at exactly one layer: the machines themselves. "No babysitting" is only true while the belt is moving; the moment a runner stops, every hour of continued silence is unbounded, invisible loss of the system's highest-value output — and nothing in the current design notices.

Invariant 4 is today implemented only at the **role level**: the prepped-but-not-applied nudge (`Spec - Applied Detector.md`) catches a forgotten *human* step. Nothing catches a forgotten *machine*. The watchdog closes that gap.

**The incident that proves the class (2026-06-30 → 07-01).** A Pass B `stage-outreach` run crashed mid-flight, leaving its trace `.jsonl` unstaged. `run.ps1`'s plain `git pull --rebase` refuses to run on a dirty tree, so **38 consecutive scheduled runs aborted before invoking Claude** — a self-deadlock a run can cause but no run can cure. Every health surface lied by omission: Task Scheduler said `Ready` and kept firing on time, the log dutifully recorded "git pull failed" 38 times that nobody reads, and the repo simply went quiet. Separately, the **LinkedIn daemon had been dead since 06-28** (logon-triggered only; the trigger never re-fires until a reboot). Total cost: ~34 hours of stalled outreach staging, discovered only because Kanu happened to ask "is the cron running?"

**One-sentence purpose of the watchdog:** *bound the time between "the belt stops" and "Kanu knows" — to hours, not days — without adding any human attention cost while the belt is healthy.*

Scored against the purpose doc's judging order: it keeps every outward action human-gated (§1 — it only writes notes and, at most, mails Kanu himself), spends zero LinkedIn budget (§2), **reduces** required attention (§3 — it replaces "periodically wonder if the machine is alive" with "be told when it isn't"), and is the direct implementation of §4 at the layer where it's missing.

## The design in one line

**The two machines watch each other.** A machine cannot reliably report its own death — that is the failure mode. But the PC and the cloud routine run on independent infrastructure and already share a truth channel (git). Each side emits a cheap heartbeat as a **byproduct of successful work**; each side checks the *other's* heartbeat every run and raises a loud, human-visible alert when it goes stale.

No new service, no monitoring stack, no state database (invariant 5) — one small committed file and two checks inside runs that already happen.

## The heartbeat — `scripts/drip_runner/heartbeat.json`

One JSON file in the repo, readable by both sides via git. Written only at the **end of a successful run** (Claude invoked and exited 0), so it asserts "the whole chain worked," not "the scheduler fired":

```json
{
  "pc": {
    "last_ok_saved":    "2026-07-01T05:12:00-05:00",
    "last_ok_outreach": "2026-07-01T21:04:00-05:00",
    "consecutive_aborts": 0,
    "daemon_ok": true
  },
  "cloud": {
    "last_ok_sweep": "2026-07-01T16:03:00-05:00"
  }
}
```

**Commit discipline (the no-op guard survives).** The heartbeat must not churn `main` hourly. Rule: a successful run updates the file locally, but **commits it only when the committed copy is >20h old** — piggybacking on a real work commit when one exists, or as a lone `drip-runner: heartbeat` commit otherwise. Net cost: ≤1 tiny commit per machine per day. A healthy-but-idle machine (empty worklist for days) therefore still proves liveness daily — which is exactly what distinguishes "idle" from "dead," the distinction the incident showed we cannot currently make. (Commit timestamps alone can't do this job: the no-op guard means a healthy quiet machine and a dead machine look identical in `git log`.)

`consecutive_aborts` is the one field written on *failure*: `run.ps1` increments it locally on every abort-before-Claude (pull failure, daemon down, trace blocked) and zeroes it on success. It exists so the PC can distinguish "one flaky hour" from "systemic" for its own local escalation — it is best-effort (a PC that can't push can't share it; that's what the cloud-side staleness check is for).

## The checks

| Watcher | Watched | Check (every run of the watcher) | Threshold (default) |
|---|---|---|---|
| **Cloud secretary** | PC Pass B | `now − pc.last_ok_outreach` | > **26h** (daily heartbeat + margin) |
| **Cloud secretary** | PC Pass A | `now − pc.last_ok_saved` | > **50h** (daily pass + margin) |
| **Cloud secretary** | LinkedIn daemon | `pc.daemon_ok == false` in the latest heartbeat | immediately |
| **PC (either pass)** | Cloud secretary | `now − cloud.last_ok_sweep` | > **3 weekdays** |
| **PC (locally)** | itself | `consecutive_aborts` | ≥ **3** |

Thresholds are tuned to the *heartbeat cadence*, not the run cadence — detection latency is bounded by `staleness threshold + one watcher interval`. With today's 2×/weekday secretary that means a dead PC is flagged by the next weekday-morning sweep after ~26h; when build-list item 7 makes the secretary hourly, the same spec tightens to same-day automatically. Good enough: the target is **"next morning," not "next minute"** — the loss rate of a stalled belt is hours-scale, and a tighter budget would buy nothing but noise.

## The alert — loud, human-visible, once per incident

When a check trips, the watcher must put the failure **where Kanu already looks**, in the same shape the rest of the system fails loud:

1. **Dated audit line at the top of `Pipeline.md`** (the existing chained `_Last updated:_` format):
   > _⚠ WATCHDOG 2026-07-01: PC outreach pass has not completed since 06-30 08:00 (38 aborts logged). Belt is stalled — roles marked Applied are not being staged. Check `~/.claude/logs/drip-runner.log` on the PC._
2. **The watcher's own run report** (the cloud routine's summary / Pass B's chat output) opens with the same line.
3. **PC-local only:** on `consecutive_aborts ≥ 3`, also raise a Windows toast notification — zero-risk, catches Kanu at the machine he uses daily.

**Anti-flap:** alert **once per incident**, re-alert at most every 24h while still unhealthy, and write one closing line when the heartbeat recovers ("watchdog: PC outreach pass healthy again as of …"). A watchdog that nags every run trains the human to ignore it, which re-creates silence by other means.

**Open decision — the self-email escalation.** The strongest channel would be the cloud secretary *sending* a plain alert email to madhok.kanu@gmail.com. Invariant 1 says "never sends" — but its stated rationale is human-gating of *outward* actions toward recruiters/companies. A machine-to-operator alert is inward: no third party, no reputational surface, and it serves invariant 3 directly. Recommendation: allow **exactly this one send**, hard-scoped to `to: madhok.kanu@gmail.com` with a fixed subject prefix (`[drip-watchdog]`), and record the carve-out in `Automation Architecture - Purpose.md` so invariant 1's wording stays honest. Until Kanu ratifies that carve-out, the audit note + report are the channels.

## What the watchdog does NOT do

- Does **not** fix anything (no restarts, no git surgery, no trace-run reaping — self-healing is a separate concern; this spec only guarantees the failure is *seen*). The one exception worth pairing with it: `run.ps1` may retry-once transient checks (e.g., start the daemon task and re-probe) *before* counting an abort — retries reduce false alarms, which is a watchdog concern.
- Does **not** run on its own schedule — it lives inside runs that already happen. No new cron entry, no new process to watch.
- Does **not** page in real time or track per-role state (that's the Applied Detector's job).
- Does **not** monitor Gmail, LinkedIn, or any external service — only the two machines' own liveness (plus the daemon flag the PC already knows).

**Named residual risk — both machines dead.** Mutual watching cannot cover simultaneous death (e.g., GitHub outage, or the cloud routine disabled while the PC is broken). Accepted: the tell is *total* silence — no morning secretary report at 8 AM CT — which is a human-observable absence, and cheap to notice once the watchdog has made every partial failure loud. If this ever bites, the escape hatch is a third-party dead-man's-switch (healthchecks.io-style ping), deliberately out of scope today (KISS, judged per the purpose doc's order — it would add a service to babysit).

## State table (invariant 5 — files that already exist, plus one)

| Signal | Where it lives | Written by |
|---|---|---|
| PC pass health | `scripts/drip_runner/heartbeat.json` → `pc.*` | `run.ps1` on successful run end |
| Cloud sweep health | same file → `cloud.last_ok_sweep` | cloud secretary on successful sweep |
| Abort streak | same file → `pc.consecutive_aborts` (+ detail in `~/.claude/logs/drip-runner.log`, local) | `run.ps1` on abort |
| Active incident | dated `⚠ WATCHDOG` audit line in `Pipeline.md` | whichever watcher tripped |

## Build delta

1. **`run.ps1`** — write/zero the `pc.*` heartbeat fields at run end; increment `consecutive_aborts` on abort; daemon probe result → `daemon_ok`; toast at ≥3; commit heartbeat when committed copy >20h old.
2. **Cloud secretary prompt** — read `heartbeat.json` after pull; run the three cloud-side checks; emit the audit line + report line on trip (with anti-flap rule); stamp `cloud.last_ok_sweep` under the same >20h commit discipline.
3. **PC prompts (`runner-prompt-saved.md` / `runner-prompt-outreach.md`)** — one added step: check `cloud.last_ok_sweep` and emit the same alert shape if stale.
4. **`Automation Architecture - Purpose.md`** — if the self-email carve-out is ratified, amend invariant 1's wording to name the single permitted send.
5. **Tests** — pure functions for staleness/threshold logic (same pattern as `outreach_worklist.py`: deterministic, pytest-covered); a fixture heartbeat file; no live dependencies.
