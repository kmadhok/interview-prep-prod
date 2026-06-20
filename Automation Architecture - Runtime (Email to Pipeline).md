# Automation Architecture — Runtime (Email → Pipeline)

_Created 2026-06-20. One of two split plans. Companion: `Automation Architecture - Skill Sync (Mac to PC).md`. Parent context / history: `Automation Architecture - Drip Runner.md`._

**Scope — the runtime loop.** How a job *enters* the system and gets processed, unattended, on the always-on Windows PC: email intake → scheduler → queue → `jd-to-ready` run → Pipeline.md reflection + staged drafts.

**Out of scope (other plan).** How skills are refined on the Mac and synced to the PC, and the regression safety net that guards this loop. See `Automation Architecture - Skill Sync (Mac to PC).md`. This plan *assumes* a green, synced skill set; the other plan guarantees it.

---

## The loop

```
You ──email a job URL──▶ Gmail (auto-labeled `drip-queue`)
                               │
        Task Scheduler (PC, weekday cadence)
                               │
   1. git pull            ──▶ [safety gate lives in the Skill Sync plan]
   2. read labeled emails ──▶ extract URL ──▶ build queue
   3. dedupe vs Pipeline.md ──▶ pick ONE role
   4. URL ──▶ fetch JD text
   5. run jd-to-ready end-to-end
   6. reflect in Pipeline.md + stage Gmail draft (never send)
   7. relabel email `drip-done` · commit `drip-runner:` · push
```

One role per run — LinkedIn sequences take 35–60 min, so a run is bounded to a single role.

---

## Components

### 1. Input channel — email
- **Convention: a Gmail label `drip-queue`, not a bare subject match.** A label avoids false positives from ordinary mail. You apply it automatically via a Gmail filter on a subject prefix (e.g. `JOB:`), so day-to-day you still just type a prefix.
- **Payload:** one job URL per email body. (One-per-email keeps dedup + mark-done clean; multiple URLs per email is a v2.)
- **Sender:** you, forwarding/emailing a posting to yourself.
- **DECISION NEEDED:** exact label name + the subject prefix the filter keys on.

### 2. Scheduler — local Task Scheduler (resolved)
- **"cron job OR a routine" → RESOLVED: local Task Scheduler.** The cloud routine cannot reach the LinkedIn daemon (`127.0.0.1:8765`), so the full-pipeline runner must be local. The cloud routine stays as a secretary-only fallback (see master doc).
- **Job shape:** weekday cadence; `git pull` → [safety gate] → run. PowerShell chaining only (`; if ($?)` — no `&&`).
- **DECISION NEEDED — cadence:** set after Phase-1 reveals real run duration. Never schedule runs closer together than the longest observed run.
- ⚠️ **"Always on" ≠ "auto-recovers."** The box still reboots (Windows updates) and the daemon can crash. The LinkedIn daemon **and** this scheduler must be registered as auto-start at logon — the daemon is currently running by hand (no Task Scheduler entry).

### 3. The queue
- **Physical queue = the labeled, unread emails themselves.** No separate queue file; state lives in Gmail labels.
- **Idempotency:** mark each processed email `drip-done` (relabel). Do **not** rely on a "past X days" window — a fixed window re-processes the same email on every run.
- **Throughput:** one role per run.
- **Dedup:** before running, confirm the URL/company isn't already an active Pipeline.md row.

### 4. URL → JD fetch (NEW capability)
- ⚠️ Today `interview-prep-intake` expects pasted JD **text**. An emailed **URL** means the runner must fetch + parse the posting first (WebFetch for general URLs; LinkedIn MCP `get_job_details` for LinkedIn job links).
- **DECISION NEEDED:** add this as a pre-intake step in the runner prompt, **or** extend `interview-prep-intake` to accept a URL. The latter is cleaner and reusable — but it's a skill change, so it must go through the Skill Sync safety gate.

### 5. The skill run
- `jd-to-ready` end-to-end on the single picked role.
- Staging rules carry over: **Gmail drafts only, never sent**; LinkedIn messages staged as paste-ready text in the role folder.
- Honor the staging pause: ≤2 staged per run; stop if ≥4 job drafts sit unsent.
- Re-verify every claim in any pre-written draft against current Pipeline.md before staging (this caught real stale-urgency errors on 6/10).

### 6. Pipeline.md reflection
- New role → add a Pipeline row (`Considering — JD reviewed, not yet applied`), per intake.
- After staging → write `STAGED in Gmail <date>` in **both** the role folder and the Pipeline row, so reruns never duplicate.
- Commit with the `drip-runner:` prefix; push.

---

## Open decisions
1. Label name + subject prefix (§1).
2. Run cadence (§2) — set after Phase-1 timing.
3. URL→JD: runner-step vs. `interview-prep-intake` extension (§4).
4. One-URL-per-email now, multi-URL later? (§1).

## Build checklist
- [ ] Pick label + subject convention; create the Gmail filter.
- [ ] Register the LinkedIn daemon **and** the runner as Task Scheduler auto-start jobs (closes the "always on ≠ auto-recover" gap).
- [ ] URL→JD fetch step (decide where per §4).
- [ ] Queue reader: labeled email → URL → dedupe vs Pipeline.md → pick one → relabel `drip-done`.
- [ ] Wire the above into the frozen Phase-1 runner prompt (see master doc Phase 1).
- [ ] Smoke test: email yourself one URL → run → verify draft staged + Pipeline row updated + email relabeled.

## Dependencies
- A green, synced skill set — guaranteed by `Automation Architecture - Skill Sync (Mac to PC).md`. Do not turn on this cron until that plan's Layer-2 canary + rollback is in place; otherwise a bad skill push reaches live outreach.
