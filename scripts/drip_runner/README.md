# Application Drip-Runner — Ops

Two ingestion modes, one pipeline. Both run `jd-to-ready` end-to-end, stage Gmail
drafts only (never send), and honor the `>=4 unsent job drafts` backpressure pause.

## Mode: saved (default, primary)
Ingests your **LinkedIn saved-jobs list** — save a job on LinkedIn = consent to
process it. No email step.

- **How to queue a job:** click **Save** on any LinkedIn job posting.
- **Run manually:** `powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1`
- **What it does:** `get_saved_jobs` (pages 1-5, newest first) -> for each id skip if
  already filed (Pipeline.md), already attempted (`saved_seen.json` ledger), or a role
  folder exists -> pick the first survivor -> `get_job_details` -> `jd-to-ready` ->
  Pipeline row + ledger `done` -> commit `drip-runner:` + push. Failures -> ledger
  `error` + a `[DRIP-RUNNER] failures` Gmail draft. One role per run.
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
1. **Daemon auto-start + cron:** `install-tasks.ps1` once (registers `LinkedInDaemon`
   at-logon and `DripRunner` weekday 08:00, the latter DISABLED until smoke-tested).
2. **Deps (optional):** `py -3 -m pip install reportlab` for resume PDF export; without
   it the resume renders to `.md` and the PDF step graceful-skips. Optional poppler
   (`pdftoppm`) for the resume vision-verify.
3. **.env** at repo root carries `Email_Finder_Dev=<key>` (no BOM).

## Enable the cron once smoke-tested
`Enable-ScheduledTask -TaskName DripRunner`  (runs `run.ps1` with default `-Mode saved`).

## Tests
`py -3 -m pytest scripts/drip_runner -q`
