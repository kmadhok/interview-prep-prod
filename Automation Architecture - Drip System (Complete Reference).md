# Automation Architecture — Drip System (Complete Reference)

_Last updated 2026-06-23. This is the **canonical "how it actually runs today" reference** for the drip system. The five `Automation Architecture - *.md` design docs and `scripts/drip_runner/README.md` remain as design history / ops quickstart and are cross-linked at the bottom; where they disagree with this file, **this file is correct** (see §13 for the specific stale spots)._

---

## 1. TL;DR

The drip system turns "I saved a job on LinkedIn" into a fully-prepared application package, unattended, every morning. A Windows Task Scheduler job wakes at **05:00 Central daily**, runs a headless Claude Code session that pulls the newest saved jobs off LinkedIn, and for each un-acted one runs the `jd-to-ready` skill end-to-end — tailored resume + PDF, scored contacts, verified emails, and two cold-outreach emails — then files it under `Roles/`, adds a `Pipeline.md` row, and commits + pushes to GitHub.

**Status:** Saved-jobs mode is the default and is **live and validated** (first full end-to-end run 2026-06-21; running unattended since — the ledger shows roles staged across 06-21 → 06-23). Email mode is a secondary fallback for non-LinkedIn postings.

**The one invariant that never changes: all outward output is STAGED, never sent.** Every email is a Gmail **draft**. Nothing is sent, no LinkedIn message is dispatched, no connection request is fired. A human (Kanu) reviews and sends.

---

## 2. End-to-end data flow

```
Windows Task Scheduler  (DripRunner, daily 05:00 Central)
   │
   ▼
run.ps1  ── git pull --rebase ──▶ (abort if it fails)
   │   selects prompt by -Mode (default: saved)
   │   pipes prompt via stdin ▼
claude -p   (headless Claude Code session, runner-prompt-saved.md)
   │
   ├─▶ LinkedIn MCP daemon @ 127.0.0.1:8765/mcp
   │       get_saved_jobs(max_pages=5)  ─▶ ~50 newest job_ids (newest-saved first)
   │
   ▼  for each job_id, in order, SKIP if ANY:
   │     a. saved_jobs_ledger.py check  → PROCESSED
   │     b. dedupe.py (vs Pipeline.md)  → DUPLICATE
   │     c. Roles/<Company - Role>/ folder already exists
   │  collect survivors → WORKLIST, capped at 6 (rest deferred + logged)
   │
   ▼  for each pick in the worklist (sequential — never parallel LinkedIn ops):
   │     get_job_details(job_id) ─▶ JD text + company + title
   │     jd-to-ready  ─▶ resume.md + resume.pdf, .contacts-ledger.md,
   │                     Verified Emails.md, Cold Outreach.md (2 Gmail DRAFTS)
   │     Pipeline.md row ("Considering …") + "STAGED in Gmail <date>"
   │     saved_jobs_ledger.py mark --status done
   │     git add (role folder + Pipeline.md + saved_seen.json) → commit → push   ← PER ROLE
   │
   ▼
~/.claude/logs/drip-runner.log  (wrapper lines + full run summary)
```

The downstream (everything after a `job_id` is resolved) is **source-agnostic**. The email mode (§7) is just a different front-end that fills the same pipeline.

---

## 3. Scheduling layer — Windows Task Scheduler

Registered once by `scripts/drip_runner/install-tasks.ps1`. Two tasks, both running **inside the logged-on user session** (an explicit `New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited`). Interactive is required because the browser profile, the `claude` login, and the MCP servers do not exist under the SYSTEM account; Limited lets a non-elevated user register the tasks.

### `LinkedInDaemon`
| Property | Value |
|---|---|
| Trigger | At logon, scoped to this user (`-AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"`) |
| Action | `uv run linkedin-mcp-server` |
| Working dir | `G:\projects\linkedin-mcp-server` |
| Recovery | `-RestartCount 3 -RestartInterval 1 min`, `-StartWhenAvailable` |
| Purpose | Keeps the LinkedIn MCP daemon alive across reboots so `get_saved_jobs`/`get_job_details` are always served |

### `DripRunner`
| Property | Value (verified live 2026-06-23) |
|---|---|
| Trigger | `-Daily -At 5am` — local time; the box's Central zone makes this 05:00 CST/CDT |
| Action | `powershell -NoProfile -ExecutionPolicy Bypass -File "…\run.ps1"` |
| Working dir | `G:\projects\interview-prep` |
| Execution time limit | **3 hours** (`PT3H`) — covers the 6-role cap |
| Multiple instances | `IgnoreNew` — runs never overlap; a new trigger while one is running is dropped |
| Misc | `-StartWhenAvailable` (runs if the scheduled time was missed) |
| State | **Enabled / Ready** |

> The "disabled until a safety gate lands" rule from the early Skill-Sync plan was **dropped 2026-06-21**. The decision was to learn from real runs + logging rather than build CI/canary/rollback first. See §13.

---

## 4. Entrypoint — `scripts/drip_runner/run.ps1`

PowerShell 5.1 wrapper. Flow:

1. `param([ValidateSet('saved','email')][string]$Mode = 'saved')` — default is **saved**.
2. `Set-Location G:\projects\interview-prep`.
3. `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` — so Claude's UTF-8 stdout (em-dashes etc.) isn't mojibake'd through the OEM codepage in the log.
4. `git pull --rebase`; **if it fails, log and `exit 1`** — never invoke Claude against an inconsistent tree.
5. Pick the prompt: `runner-prompt.md` for `-Mode email`, else `runner-prompt-saved.md`.
6. `$out = $prompt | claude -p | Out-String` — **the prompt is piped via stdin, not passed as a `-p` argument.** PS 5.1's native-arg quoting mangles embedded quotes (e.g. `--company ""`) and leaks prompt text like `--job-id` to `claude` as bogus CLI flags. Stdin sidesteps arg parsing entirely. stdout only — **never `2>&1`** a native exe under `-ErrorActionPreference Stop` (PS 5.1 wraps stderr as a terminating `NativeCommandError`).
7. `$LASTEXITCODE` is captured before anything else can clobber it, the captured stdout is appended to the log, and the script exits with that code.

**Manual invocation:**
```
powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1            # saved (default)
powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1 -Mode email
```
Or trigger the registered task exactly as the cron would: `Start-ScheduledTask -TaskName DripRunner`.

---

## 5. Logging & tracking — six durable layers

| Layer | What it records | Where |
|---|---|---|
| **Operational log** | Per run: start (+mode), git pull result, `claude -p` invocation, **full run summary**, exit code | `~/.claude/logs/drip-runner.log` (UTF-8, no BOM, append-only across all runs) |
| **Processed-ledger** | Per-job terminal state (`done`/`error`/`skipped`) — drives dedupe | `scripts/drip_runner/saved_seen.json` (committed in-repo) |
| **Pipeline rows** | `STAGED in Gmail <date>` per filed role | `Pipeline.md` |
| **Git history** | One commit per staged/errored role | `git log --grep "drip-runner:"` |
| **Per-role trace** | `jd-to-ready` step/token JSONL | `Roles/<Company - Role>/.jd-to-ready-trace.jsonl` |
| **Failure alert** | One Gmail draft-to-self per run with a line per failure | Gmail draft titled `[DRIP-RUNNER] failures <date>` (never sent) |

The log line `Log()` writes with `[System.IO.File]::AppendAllText(..., UTF8Encoding($false))` — `Tee-Object` was avoided because it writes UTF-16 on PS 5.1, which garbles the log and trips this repo's BOM-sensitive readers.

---

## 6. Saved-jobs mode (primary) — `runner-prompt-saved.md`

**Ingestion model:** your LinkedIn **saved jobs** list. Saving a job = consent to process it. The list is a flat set with **no per-job save timestamp**, so "process everything I saved this week" is implemented as **"process every un-acted job in the newest-first window."** Run daily, that is functionally the same thing.

**Pre-run health check.** Call `get_saved_jobs(max_pages=5)`. This both fetches the worklist and proves the daemon is up; on a transport/login error the run **stops cleanly** (jobs stay saved for next time). `max_pages=5` ≈ the **50 newest** saved jobs (page size 10 — see §10). Anything older is explicitly **not considered** this run, and the summary says so (no silent caps).

**Build the worklist.** Walk the `job_ids` newest-first; keep an id only if it survives **all three** skip-checks:
- `py -3 scripts/drip_runner/saved_jobs_ledger.py check --job-id <id> --ledger scripts/drip_runner/saved_seen.json` → not `PROCESSED`
- `py -3 scripts/drip_runner/dedupe.py --company "" --job-id <id> --pipeline Pipeline.md` → not `DUPLICATE`
- no `Roles/<Company - Role>/` folder already exists

**Cap = 6 per run.** A LinkedIn sequence runs ~6–30 min per role; 6 keeps the session bounded and inside the 3h task limit. If more than 6 survive, take the **first 6 (newest)** and report how many were **deferred** to the next daily run. At daily cadence, 6/run = 42/week of capacity — more than a real week of saves, so the cap protects against a runaway first-run backlog without truncating a normal week.

**Process each pick, one at a time (never parallel LinkedIn ops):**
1. `get_job_details(<job_id>)` → JD text + company + title. On error/empty → ledger `error` + alert, **continue to the next id** (don't abort the whole run).
2. Run `jd-to-ready` end-to-end on the JD text (real run into `Roles/`). Drafts only.
3. On success: add the `Pipeline.md` row (`Considering - JD reviewed, not yet applied`), write `STAGED in Gmail <today>` in the role folder + Pipeline row, mark the ledger `done`.
4. On failure in step 2: ledger `error` (failing step + reason) + alert, **continue**.
5. **Commit + push this role now**, before moving on: `git add` the role folder + `Pipeline.md` + `saved_seen.json`; commit `drip-runner: <role>`; push (on a rejected push, `git pull --rebase` then push once). **Per-role commit means a 3h timeout or interruption never loses completed work.**

---

## 7. Email mode (secondary / fallback) — `runner-prompt.md`

For postings that aren't LinkedIn-native (Greenhouse / Lever / Workday / any URL). Ingests the Gmail `drip-queue` label; state lives in Gmail labels rather than the JSON ledger.

- **Queue a job:** email yourself Subject `JOB <anything>`, body = one job URL.
- **Health check:** `get_my_profile` (daemon up?) + resolve label IDs via `list_labels` for `drip-queue` / `drip-processing` / `drip-done` / `drip-error` (mutate by ID, query by name).
- **Drain loop (oldest first, cap 2 roles/run):** claim the thread (`drip-queue` → `drip-processing`) → `job_parser.py --subject --body` → if `source=linkedin` fetch via `get_job_details`, if `source=ats` fetch via `WebFetch` → `dedupe.py` (+ folder check) → `jd-to-ready` → on success `drip-done`, on failure `drip-error` + alert.
- **Known issue:** the Gmail filter (Subject `JOB` → apply `drip-queue`) does **not** reliably match self-sent mail; apply the label by hand or fix the filter before relying on email mode.
- **Re-queue a parked job:** relabel `drip-error` → `drip-queue`.

---

## 8. Helper scripts (the deterministic, testable core)

All pure functions + a thin CLI, so the fragile/non-deterministic work stays in the LLM and the bookkeeping stays in code with tests.

**`dedupe.py`** — is this job already in `Pipeline.md`?
- Auto-skip triggers on a **precise `job_id` substring match only**. Company-name match is a *soft* signal and never auto-skips — `Pipeline.md` is append-only and a company that appears in any closed/archived row would falsely kill a genuinely new role. Bias is **toward NEW** (at worst we re-file; the folder-exists check is the backstop), never toward silent loss.
- CLI: `--company <name> --job-id <id> --pipeline Pipeline.md` → prints `DUPLICATE` (exit 0) or `NEW` (exit 1).

**`job_parser.py`** (email mode) — email subject/body → structured `JobRef`.
- Subject must start with a `JOB` token (`\s*job\b`, case-insensitive; `Jobs` is rejected by the word boundary). First URL is extracted and trailing punctuation stripped.
- LinkedIn URLs (`linkedin\.com/jobs/view/(?:[\w-]*-)?(\d+)`, slug-aware) → `source=linkedin` + `job_id`; any other URL → `source=ats`, no `job_id`.
- CLI prints JSON `{is_job, url, source, job_id, reason}`; always exit 0 (the `is_job` flag carries success/failure).

**`saved_jobs_ledger.py`** — the processed-ledger for saved mode.
- Schema: `{"version":1,"entries":{"<job_id>":{"status","ts","note"}}}`. Terminal statuses `{done, error, skipped}` all count as "processed."
- `load()` tolerates a missing file; `save()` writes UTF-8 no-BOM, sorted keys, trailing newline (clean git diffs); `mark()` rejects an empty job_id or a non-terminal status.
- CLI: `check --job-id <id> --ledger <path>` → `PROCESSED` (exit 0) / `NEW` (exit 1); `mark --job-id <id> --status <s> --note <n> --ts <YYYY-MM-DD> --ledger <path>`.

**`saved_seen.json`** — the live ledger. As of 2026-06-23 it holds **20 entries** (19 `done`, 1 `error` — job `4429727366`, whose JD body came back empty because responses are managed off LinkedIn), spanning **2026-06-21 → 06-23**. This is the concrete evidence the cron has been running unattended.

**Tests:** 16 cases across `test_saved_jobs_ledger.py` (7), `test_dedupe.py` (3), `test_job_parser.py` (6). Run: `py -3 -m pytest scripts/drip_runner -q`.

---

## 9. The `jd-to-ready` pipeline (what each role run actually does)

`jd-to-ready` is near-pure orchestration — it wires together primitive skills end-to-end. The runner calls it once per picked role. Required steps and what each produces into `Roles/<Company - Role>/`:

1. **intake** — files the JD → `Job Description.md`.
2. **classify** (inline subagent) — themes + archetype. The one piece of logic this skill owns. Fixed vocab: **18 themes** (`agents`, `RAG`, `NL→SQL`, `MCP`, `LLM-orchestration`, `ML-pipeline`, `platform`, `business-translation`, `end-to-end`, `RPA`, `experimentation`, `dashboards`, `consulting`, `simplification`, `leverage`, `cross-functional`, `engineering-rigor`, `evaluation`) and **5 archetypes** (`agent-builder`, `FDE / client-facing`, `consulting / product-builder`, `platform / ML engineering`, `data-engineering / analytics`).
3. **tailor-resume** (mode `pipeline`) — `Kanu Madhok Resume - <Company> <Short Role>.md` + a one-page `.pdf`. Canonical-only discipline (pulls bullets from `Resume Achievements Master.md`; no invented numbers — `[NUMBER?]` placeholders instead).
4. **find-contacts** (mode `full`) — ~5 recruiters + ~5 HM/peer-ICs → `.contacts-ledger.md`.
4b. **enrich-contacts** — recruiter activity scrape; appends + re-sorts the ledger. (Auto-skipped under the drip budget to keep multi-role runs bounded.)
4c. **verify-emails** — SMTP-verifies the top recruiters via EmailFinder.dev → `Verified Emails.md`.
5. **write-outreach** (mode `drip`) — two intro emails (recruiter #1 + HM #1) created as **Gmail drafts, never sent** → `Cold Outreach.md`.
6/7. **pipeline row + report-back**.

**Trace contract.** Every run writes an append-only `.jd-to-ready-trace.jsonl` (per role) and a compact line to `~/.claude/logs/jd-to-ready.jsonl`. The contract (documented in the skill's `TRACEABILITY.md`, `TRACE_SCHEMA.md`, `TOKEN_ACCOUNTING.md`, `RUNBOOK.md`) requires every step to open and close, per-step token accounting, and fail-closed `finish-run` so a run can't be marked `ok` with missing steps. **Read those four files before editing the skill's logging/tracing.**

---

## 10. LinkedIn MCP dependency

- **Daemon:** `stickerdaniel/linkedin-mcp-server`, served over **streamable-http at `127.0.0.1:8765/mcp`** (never stdio). Browser profile at `G:\linkedin-mcp\profile`.
- **Tools the runner calls:** `get_my_profile` (email-mode health check), `get_saved_jobs(max_pages)` → `{url, sections, job_ids}`, `get_job_details(job_id)` → company/title/JD.
- **Branch dependency:** `get_saved_jobs` lives on branch **`feature/522-get-saved-jobs`** (PR #523, **not merged upstream**). The daemon must run this branch or the tool disappears on restart. This is an ongoing maintenance pin — re-verify after any daemon update; revert to upstream once #523 merges.
- **Stride fix:** the saved-jobs page size is **10**, not 25. The extractor has a dedicated `_SAVED_JOBS_PAGE_SIZE = 10` (the generic `_PAGE_SIZE = 25` used by job-search was left untouched). Before the fix, stride-25 pagination silently skipped saved jobs at offsets 10–24, 35–49, … Verified empirically via the harness's `?start=` diff method.
- **Hard rules:** **sequential only** (one browser op at a time — single authenticated account, single daemon) and **headless + gentle**. A long unbroken session of many scrapes is the main account-flag vector — this is why the per-run cap is 6, not higher.

---

## 11. Idempotency & safety model

- **Saving = consent to process.** Once a role is filed it lands in `Pipeline.md` + the ledger + a `Roles/` folder, and all three dedupe it out of future runs.
- **Three-way dedupe** (ledger / Pipeline / folder) makes re-scanning the flat saved list harmless.
- **Failed jobs are remembered** as ledger `error` (the saved-list equivalent of `drip-error`), so a permanently-bad posting isn't retried forever. To deliberately retry, remove its id from `saved_seen.json`.
- **Per-role commit + push** → a timeout or crash mid-batch never loses completed roles.
- **Drafts only, never sent** — the non-negotiable invariant (§1).
- **No draft-backlog cap.** An earlier "pause if ≥4 unsent drafts" guard was **removed 2026-06-21 per Kanu**; a backlog of unsent drafts must never block processing. The only per-run bound is the role cap.
- **Never print the cookie/profile file** — credential-leak risk.
- Commit messages end with the `Co-Authored-By: Claude Opus 4.8 (1M context)` trailer; messages must avoid embedded double-quotes/backticks (PS 5.1 native-arg bug).

---

## 12. Operations runbook

- **Run it now (true cron rehearsal):** `Start-ScheduledTask -TaskName DripRunner`. Watch with `Get-ScheduledTask DripRunner | Get-ScheduledTaskInfo` and `git log --oneline --grep "drip-runner:"`.
- **Read this morning's run:** the tail of `~/.claude/logs/drip-runner.log` now contains Claude's full summary (roles staged, deferred count, gaps).
- **Re-attempt a parked/errored saved job:** delete its id from `scripts/drip_runner/saved_seen.json` (saved mode) or relabel `drip-error` → `drip-queue` (email mode).
- **Change the cap or cadence:** the cap `6` lives in `runner-prompt-saved.md`; the schedule + 3h limit live in `install-tasks.ps1` (re-run it, or `Set-ScheduledTask`/`Enable-ScheduledTask`/`Disable-ScheduledTask -TaskName DripRunner`).
- **Confirm everything pushed:** `git rev-list --left-right --count origin/main...HEAD` should print `0  0`.
- **Tests before changing helper logic:** `py -3 -m pytest scripts/drip_runner -q`.

---

## 13. Known gaps & discrepancies (read before trusting older docs)

1. **`scripts/drip_runner/README.md` is stale** on the schedule: it says `DripRunner` is "weekday 08:00, DISABLED until smoke-tested." Reality (this file, verified live): **daily 05:00 Central, ENABLED, 3h limit.**
2. **`jd-to-ready/SKILL.md` uses Mac paths** (`/Users/kanumadhok/…`) and lists a step-6 memory update to `active_interview_pipeline.md`. On the Windows runner the workspace root is `G:\projects\interview-prep` and **the memory step is a no-op** (that file is Mac-local and unsynced) — the runner notes it as a gap and creates no stray file.
3. **`Automation Architecture - Saved Jobs Ingestion.md`** still reads "smoke test pending." That smoke test is **done** — saved mode has run unattended since 2026-06-21 (see the ledger).
4. **Email-mode Gmail filter** doesn't match self-sent mail; apply the label by hand until fixed.
5. **Staged emails are often inferred/unverified** (pattern guesses like `first.last@company.com`, Medium confidence) when no in-house recruiter anchors the pattern — verify before sending; LinkedIn InMail is the safer channel where emails are unverified.
6. **Daemon branch pin** — if the daemon is ever restarted off `feature/522-get-saved-jobs`, `get_saved_jobs` vanishes and saved mode degrades to a clean health-check stop.

---

## 14. Companion docs

- `Automation Architecture - Drip Runner.md` — the original master plan / phase history.
- `Automation Architecture - Runtime (Email to Pipeline).md` — the email-intake loop design.
- `Automation Architecture - Saved Jobs Ingestion.md` — the saved-jobs design + stride-bug write-up.
- `Automation Architecture - Skill Sync (Mac to PC).md` — the (not-yet-built) CI/canary/rollback safety net.
- `LinkedIn MCP - Local Verification Harness.md` — how to verify MCP tool behavior without disturbing the daemon (isolated-profile mode, `?start=` stride diff).
- `scripts/drip_runner/README.md` — the short ops quickstart (note the stale schedule line, §13).
