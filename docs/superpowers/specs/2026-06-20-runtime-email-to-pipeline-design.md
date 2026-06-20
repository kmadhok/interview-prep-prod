# Runtime (Email → Pipeline) — Design Spec

_Created 2026-06-20. Brainstorming output for the Application Drip-Runner's runtime loop. Next step: `writing-plans` → implementation plan. Companion concern (skill sync + safety gate) is a separate spec; see `Automation Architecture - Skill Sync (Mac to PC).md`. Parent/history: `Automation Architecture - Drip Runner.md`._

## Goal

A scheduled job on the always-on Windows PC that turns job URLs Kanu emails himself into apply-ready prep packages — unattended, crash-safe, and never sending anything outward.

## Scope

**In:** email intake → scheduler → per-job queue state machine → URL→JD → `jd-to-ready` → Pipeline.md reflection → failure alerting.
**Out:** how skills are refined and synced to the PC, and the regression gate that guards this loop (separate spec). This loop *assumes* a green, synced skill set. It also does **not** re-implement `jd-to-ready` — it orchestrates it.

## Validation status (de-risked by live test 2026-06-20)

Every risky link was exercised by hand before this spec was written:

- **Rung 1 — URL→JD:** WebFetch on a live LinkedIn job URL returned a **login wall (NO JD)** on this machine; `get_job_details` returned the full JD. → URL→JD path corrected.
- **Rung 2 — label state machine:** create / apply / query / transition / cleanup all work via the Gmail MCP. Surfaced the apply-by-ID / query-by-name invariant.
- **Rung 3 — full loop:** a real `JOB ...` email → claim → `get_job_details` → dedupe → `jd-to-ready` (resume + PDF + LinkedIn contacts + outreach + Gmail draft) → `drip-done`, end-to-end clean. Output promoted to a real role (Pinterest AI Solutions Engineer).

## Architecture

A single PowerShell-scheduled entrypoint (`git pull` → health check → drain queue → push). State lives in **Gmail labels** (the queue) and **Pipeline.md** (the durable record). The PC is the sole automated writer once the cloud routine is retired at cutover.

```
You ──"JOB <title>" email w/ URL in body──▶ Gmail filter auto-labels `drip-queue`
                                                   │
                        Task Scheduler (PC, weekday cadence — set in Phase 1)
                                                   │
  ┌─ run ───────────────────────────────────────────────────────────────────┐
  │ 0. git pull --rebase                         (abort run if it fails)      │
  │ 1. health check: daemon :8765 + Gmail reachable?                         │
  │       └─ if down → exit cleanly, claim NOTHING (jobs stay drip-queue)    │
  │ 2. list label:drip-queue, oldest first                                  │
  │ 3. FOR EACH, sequentially, until queue empty OR staging pause trips:     │
  │      a. claim: +drip-processing, −drip-queue                            │
  │      b. extract URL from body → fetch JD                                │
  │      c. dedupe vs Pipeline.md                                           │
  │      d. run jd-to-ready end-to-end (drafts only)                        │
  │      e. append role row + STAGED marker to Pipeline.md                  │
  │      f. success: +drip-done, −drip-processing                           │
  │      g. ANY failure: +drip-error, −drip-processing, append to alert draft│
  │      h. if ≥4 drafts unsent → stop draining this run                    │
  │ 4. git commit `drip-runner:` + push                                     │
  └──────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Input channel — email
- **Trigger:** a Gmail filter auto-applies the `drip-queue` label to mail whose subject starts with the token `JOB` (loose match — `JOB`, `JOB:`, `JOB <title>` all qualify; **do not require a colon** — live test sent `JOB Pinterest…`). The filter is a one-time Gmail-UI setup (the MCP cannot create filters).
- **Payload:** one job URL in the body. One-per-email (multi-URL is out of scope for v1).

### 2. Scheduler — local Task Scheduler
- Cloud routine cannot reach the LinkedIn daemon (`127.0.0.1:8765`), so the runner is local.
- PowerShell chaining only (`; if ($?)`, never `&&`).
- **Cadence: deferred to Phase 1** (set from observed run duration; never schedule runs closer than the longest observed run).
- The daemon **and** the scheduler must be registered as auto-start at logon ("always on" ≠ "auto-recovers"; the daemon currently runs by hand).

### 3. Queue — Gmail label state machine
Per-job 3-state machine: `drip-queue` → **`drip-processing`** (claimed the instant a job is picked) → `drip-done` (success) / `drip-error` (failure).
- **Crash-safety falls out for free:** completed jobs are already `drip-done`; the in-flight one sits in `drip-processing` (parked + visible); the rest stay `drip-queue` for the next run.
- **No auto-retry.** A parked job is re-queued manually (relabel `drip-error` → `drip-queue`).
- **MCP invariant (live-tested):** apply/remove labels by **ID** (`Label_3`); query the queue by **name** (`label:drip-queue`). Querying by ID returns empty.
- **Label IDs (this account):** `drip-queue`=Label_3, `drip-processing`=Label_4, `drip-done`=Label_5, `drip-error`=Label_6.

### 4. URL → JD
- **LinkedIn job URL** (`/jobs/view/<id>/`) → extract `<id>` → `mcp__linkedin__get_job_details`. **WebFetch does NOT work on LinkedIn here (login wall).**
- **Non-LinkedIn URL** (Greenhouse/Lever/Workday/company careers) → WebFetch (not login-walled).
- A closed/expired req → `get_job_details` error → `drip-error` park.

### 5. Runner — jd-to-ready
- Invoked end-to-end per job. JD already fetched in step 4, handed in as text.
- **Drafts only, never sent.** LinkedIn messages staged as paste-ready text.

### 6. Pipeline writer
- **Append-as-it-goes:** add a role row to the Considering/Apply-ready table + a `STAGED <date>` marker; never rewrite existing rows or status prose.
- **Rebase-retry** safety net for the rare Mac-vs-PC concurrent edit.
- **Pipeline.md is the durable cross-machine record.** The `active_interview_pipeline.md` auto-memory is **Mac-local and not synced** — the memory-update step is a **no-op on the PC runner** (live-confirmed: file absent on this machine). Do not fabricate it.

### 7. Alerter
- On any per-job failure: append the job + one-line reason to a `[DRIP-RUNNER] failures` Gmail **draft-to-self** (created/updated, never sent), and leave the email in `drip-error`.

## Error handling

| Failure | Behavior |
|---|---|
| `git pull` fails | Abort run, change nothing. |
| Daemon/Gmail down (pre-run health check) | Exit cleanly before claiming; jobs stay `drip-queue` (no park on a transient blip). |
| JD fetch fails (login wall / stale req / unparseable) | `drip-error` + alert; move on. |
| `jd-to-ready` crashes mid-job | `drip-error` + alert; the one in-flight job is parked, others unaffected. |
| Pipeline rebase conflict | Re-pull, re-apply just this run's additions, retry push. |
| ≥4 drafts unsent | Stop draining this run (staging pause). |

**Policy:** park-everything-on-failure + alert, **no auto-retry**; Kanu re-queues by relabeling. (Chosen for simplicity / human-in-loop over smart-retry.)

## Testing

- **Unit (no daemon):** URL extraction + LinkedIn-vs-other detection + job_id parse; claim/relabel transitions (mock Gmail); Pipeline append + rebase-retry; dedupe key; loose `JOB`-prefix subject match.
- **Integration smoke test:** email a `JOB` URL → run → assert draft staged + Pipeline row appended + email `drip-done` + queue empty. (Executed manually as Rung 3; automate as the acceptance test.)

## Decisions (resolved in brainstorming)

1. Queue state → 3-state Gmail labels.
2. Recovery → park everything + alert, no auto-retry, manual re-queue; pre-run health check exits before claiming.
3. URL→JD → `get_job_details` for LinkedIn, WebFetch for non-LinkedIn (corrected from live test).
4. Pipeline writes → append-as-it-goes + rebase-retry; retire cloud routine at cutover (PC = sole automated writer).
5. Per-run scope → drain queue sequentially until empty or staging pause.
6. Queue trigger → Gmail filter on loose `JOB` subject prefix → `drip-queue`.
7. Failure alert → `[DRIP-RUNNER] failures` Gmail draft-to-self.

## Deferred (not blockers)

- Exact cron cadence (Phase 1, from observed run duration).
- Whether to verify inferred emails (Apollo unavailable in this env → emails inferred `first@company.com`; flagged per job).

## Dependency

Do **not** enable the cron until the Skill Sync canary + rollback (separate spec) is live — until then every skill push is an unguarded change to an autonomous writer of outreach.
