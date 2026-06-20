# Application Drip-Runner — Ops

## One-time setup (Kanu, in the Gmail UI / a terminal)
1. **Labels** already exist: drip-queue, drip-processing, drip-done, drip-error.
2. **Gmail filter:** Settings -> Filters -> Create. Criteria: Subject `JOB`. Action: Apply label `drip-queue`, Skip Inbox (optional). This auto-queues a self-sent "JOB <title>" email with a URL in the body.
3. **`.env`** at repo root contains `Email_Finder_Dev=<key>` (no BOM — create via an editor or `Set-Content ... -Encoding utf8NoBOM`).
4. **Deps:** `py -3 -m pip install reportlab`. Optional: install poppler (`pdftoppm`) for the resume vision-verify.
5. **Daemon auto-start:** run `install-tasks.ps1` once (elevated).

## How to send a job
Email yourself: Subject `JOB <anything>`, body = one job URL (LinkedIn or ATS).

## Run manually (smoke test)
`powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1`

## What it does
Drains label:drip-queue oldest-first -> claim -> URL->JD -> dedupe -> jd-to-ready (drafts only) -> Pipeline row -> drip-done. Failures park to drip-error and append to a "[DRIP-RUNNER] failures" Gmail draft. Never sends.

## Re-queue a parked job
In Gmail, relabel it drip-error -> drip-queue.
