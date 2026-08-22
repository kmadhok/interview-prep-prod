# Application Drip-Runner — Ops

Two ingestion modes, one pipeline. Each run drains ALL un-acted saved jobs newest-first,
up to a safety cap of 6 roles per run (commits per-role so a timeout never loses work);
the 3h task limit bounds the session.

## Two-skill model (apply-gated)

`jd-to-ready` now does **PREP only**: intake → classify → resume → PDF, writes
`.classification.json` into the role folder, and stops at the apply gate (steps
1/2/3/3.5/6/7). No Gmail drafts, no LinkedIn contact research.

The apply-side work (find recruiter → enrich → verify email → Gmail draft) moved to a
new `stage-outreach` skill that fires on roles marked **Applied** with no `STAGED` marker.

Two deterministic readers drive the apply-side poll (no LLM):

- **`outreach_worklist.py`** — lists `Pipeline.md` `## Active` rows that are Applied &
  not STAGED (the Pass B worklist).
  Run: `py -3 scripts/drip_runner/outreach_worklist.py --pipeline Pipeline.md`

- **`prepped_not_applied.py`** — fail-loud nudge: prepped roles not yet applied or
  closed, past a staleness threshold. Surfaces as a visible report line so silent gaps
  don't go unnoticed.
  Run: `py -3 scripts/drip_runner/prepped_not_applied.py --roles-dir Roles --pipeline Pipeline.md`

> **Status:** Pass A and Pass B scheduler wiring is implemented in
> `install-tasks.ps1`. Older architecture notes that call it pending are historical.
> The portable required/optional manifest lives under `infra/`.

## Mode: saved (default, primary)
Ingests your **LinkedIn saved-jobs list** — save a job on LinkedIn = consent to
process it. No email step.

- **How to queue a job:** click **Save** on any LinkedIn job posting.
- **Run manually:** `powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1`
- **What it does:** `get_saved_jobs` (pages 1-5, newest first) -> for each id skip if
  already filed (Pipeline.md), already attempted (`saved_seen.json` ledger), or a role
  folder exists -> build a newest-first worklist of survivors (cap 6) -> for each:
  `get_job_details` -> `jd-to-ready` (**PREP-only**: intake → classify → resume → PDF,
  no outreach drafted) -> Pipeline row + ledger `done` -> commit `drip-runner:` + push
  (per role). Failures -> ledger `error` + a `[DRIP-RUNNER] failures` Gmail draft, then
  continue to the next id. Survivors past 6 defer to the next daily run. Outreach drafts
  are staged later via `stage-outreach` after the user applies.
- **Re-attempt a parked job:** remove its id from `scripts/drip_runner/saved_seen.json`.
- **Requires:** the daemon running the `feature/522-get-saved-jobs` branch (stride-10
  fix) so `get_saved_jobs` is served. `install-tasks.ps1` starts it from the repo dir.

## Mode: email (secondary — ATS / any non-LinkedIn URL)
Ingests the Gmail `drip-queue` label. Use for postings that aren't LinkedIn-native.

- **One-time:** labels `drip-queue/processing/done/error` exist; Gmail filter
  (Subject `JOB` -> apply `drip-queue`). **Known issue:** the filter is not currently
  matching self-sent mail — apply the label by hand or fix the filter before relying on it.
- **How to queue:** email yourself Subject `JOB <anything>`, body = one job URL.
- **Run manually:** `powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1 -Mode email`
- **Re-queue a parked job:** in Gmail, relabel `drip-error` -> `drip-queue`.

## One-time setup
1. **Daemon auto-start + schedulers:** `install-tasks.ps1` once (registers
   `LinkedInDaemon` at logon, daily `DripRunner`, and hourly
   `DripRunnerOutreach`; all are enabled by the installer).
2. **Deps (optional):** `py -3 -m pip install reportlab` for resume PDF export; without
   it the resume renders to `.md` and the PDF step graceful-skips. Optional poppler
   (`pdftoppm`) for the resume vision-verify.
3. **.env** at repo root carries `Email_Finder_Dev=<key>` (no BOM).

## Pause or resume a scheduler

Use `Disable-ScheduledTask` / `Enable-ScheduledTask` with `DripRunner` or
`DripRunnerOutreach`. See `infra/pc-runner/README.md` for the portable setup and
manual equivalents.

## Tests
`py -3 -m pytest scripts/drip_runner -q`

Covers: `test_dedupe.py`, `test_job_parser.py`, `test_saved_jobs_ledger.py`,
`test_outreach_worklist.py` (Pass B worklist reader), `test_prepped_not_applied.py`
(fail-loud nudge reader).
