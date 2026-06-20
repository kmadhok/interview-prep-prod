# Spec: Telegram JD Trigger → PC jd-to-ready Runner

_Status: DRAFT for review (Phase 1 — Specify). Companion to `Automation Architecture - Drip Runner.md`; this spec covers the **drop-triggered** runner that doc's Phase 3 left undefined. Confirmed intent is in that doc's spirit but this is a NEW path: trigger-driven, not the cron queue-walker._

## Objective

**What:** A Telegram bot on Kanu's always-on **Windows PC**. Kanu sends a job-posting **URL** in a private Telegram chat → the PC fetches/extracts the JD, runs the full `jd-to-ready` pipeline unattended, commits + pushes results to the repo, and replies in the same chat with a compact status summary.

**Who:** Kanu, from his phone, away from the Mac — kick off an apply-ready package from anywhere.

**Why now:** `jd-to-ready` works on the Mac but is tethered to it. The PC can host the logged-in LinkedIn daemon (`127.0.0.1:8765`) a cloud VM cannot, so the **full** package (resume + 5+5 contacts + verified emails + 2 Gmail drafts) can run unattended only on a machine Kanu controls.

**Success looks like:** Kanu sends a URL → within one run-cycle (LinkedIn sequences run 35–60 min per the architecture doc) he gets a `✅ done` reply listing: role+company, repo paths pushed, # contacts, # Gmail drafts staged, and any `gaps[]`. He reviews/sends the 2 Gmail drafts himself in Gmail; he `git pull`s on the Mac to see resume/contacts/Pipeline.

### Acceptance criteria (testable)

1. Sending a LinkedIn or ATS (Greenhouse/Lever/Ashby) **job URL** from Kanu's Telegram account triggers exactly one `jd-to-ready` run on the PC.
2. A message from **any other Telegram user** is ignored (no run, no reply, or a polite "not authorized").
3. The JD is extracted from the URL with **no pasted text required**: LinkedIn URLs via the LinkedIn MCP daemon; ATS URLs via WebFetch.
4. The run produces the full `jd-to-ready` output set (resume `.md`/`.pdf`/`.docx`, `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, Pipeline row) and **pushes** it to `origin` with a `drip-runner:` commit prefix.
5. Outward output stays **STAGED, never sent** — 2 Gmail drafts created, nothing auto-sent; no Telegram approve/send surface.
6. The bot replies with the **status summary** (format in §Code Style) on success, and a distinct **failure** reply (with the failing step + reason) when a run aborts.
7. **One run at a time.** A second URL arriving mid-run is **rejected** — the bot replies `busy, try again in ~40 min` and does not run it. (Simpler than a persisted queue; no queue state to recover after a crash. Revisit if rejection proves annoying.)
8. The bot and LinkedIn daemon **auto-start on PC boot** and survive reboots without manual intervention.

## Tech Stack

- **OS:** Windows (10/11). Services via **Task Scheduler** (preferred — native, no extra install) or **NSSM** if a true Windows-service wrapper is wanted. Spec defaults to Task Scheduler "At log on / at startup" triggers with "restart on failure."
- **Runner:** Claude Code CLI (`claude -p`, headless), same account as Mac (brings the claude.ai Gmail connector).
- **Bot:** Python 3.11+, [`python-telegram-bot`](https://docs.python-telegram-bot.org/) v21+, **long-polling** (no webhook, no public IP, works behind home NAT).
- **LinkedIn:** `linkedin-scraper-mcp` daemon, HTTP transport on `127.0.0.1:8765` (the invariant — never stdio), logged into LinkedIn once in its browser profile.
- **Repo:** `https://github.com/kmadhok/interview-prep.git`, cloned on the PC; push via PAT or SSH deploy key.
- **Email verification:** EmailFinder.dev key, supplied via PC-local `.env` (never committed).

## Commands

```
# One-time PC setup (documented in setup runbook, not run by the bot)
git clone https://github.com/kmadhok/interview-prep.git
claude login                      # same account as Mac → Gmail connector
# install linkedin-scraper-mcp, log in once, register linkedin server (type:http :8765)
# create skill symlinks/junctions (see §Project Structure), register jd-to-ready hooks,
# place .env, place Telegram token, register Task Scheduler entries

# What the bot runs per accepted URL (conceptually):
cd <repo> && git pull --rebase
claude -p "<FROZEN_PROMPT with the URL substituted>"   # headless, allowlisted, full pipeline
# jd-to-ready itself commits + pushes its outputs (drip-runner: prefix)

# Bot process (long-running service):
python pc-runner/telegram_jd_bot.py

# Manual smoke test over Remote Desktop / SSH before trusting the bot:
claude -p "run jd-to-ready on https://www.linkedin.com/jobs/view/<id>"
```

## Project Structure

New code lives in a `pc-runner/` directory at the repo root (committed — it's infra, not secrets):

```
pc-runner/
  telegram_jd_bot.py        → the long-polling bot: auth gate, URL validation, FIFO queue, run orchestration, reply formatting
  run_jd_to_ready.py        → wraps `claude -p`: builds the frozen prompt, runs git pull, invokes CLI, captures the run summary
  prompt.txt                → the FROZEN Phase-1 prompt (the cron payload), URL injected at {{JOB_URL}}
  config.example.toml       → template: allowed Telegram user id, repo path, claude bin path, daemon health URL
  README-windows-setup.md   → the Phase-3 Windows setup runbook (Task Scheduler, junctions, daemon, hooks, secrets)
  .gitignore-additions      → ensures config.toml, .env, *.token never commit

# NOT committed, PC-local only:
pc-runner/config.toml       → real config (allowed user id, paths)
.env                        → EmailFinder key (repo root, already gitignored on Mac)
pc-runner/telegram.token    → bot token from @BotFather
```

**Skill symlinks on Windows:** the Mac uses `ln -s`. Windows equivalent is a **directory junction** (`mklink /J`) or symlink (`mklink /D`, needs admin/dev-mode). The `jd-to-ready` hooks resolve paths via `Path.home()`, so the PC needs `%USERPROFILE%\.claude\skills\<name>` → repo `.claude\skills\<name>` for all 7 pipeline skills, identical structure to the Mac.

## Code Style

Python, std-lib-first, small single-purpose functions, fail-loud logging to a rotating file. The bot is a thin trigger — no business logic about resumes/contacts lives here; that's all in the skill.

```python
# telegram_jd_bot.py — the accept gate and the only place a run is launched
ALLOWED_USER_ID = config.allowed_telegram_user_id  # int, from config.toml — single-tenant

async def on_message(update: Update, ctx) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # silent ignore — never run for anyone else
    url = extract_job_url(update.message.text)       # None if not a recognized job URL
    if url is None:
        await reply(update, "Send a LinkedIn or ATS job URL.")
        return
    if run_in_progress:                              # single global flag — one run at a time
        await reply(update, "🛑 Busy with a run — try again in ~40 min.")
        return
    await reply(update, f"▶️ Starting: {url}")
    launch_run(url, update.message.chat_id)          # sets run_in_progress; clears on completion
```

### Building the reply from the run log (the structured-output contract)

The bot does **not** parse `claude -p` stdout. After the CLI exits, it reads the **last line** of
`~/.claude/logs/jd-to-ready.jsonl` — the global summary log the skill writes at step 7 — and
matches that line's `run_id`/`timestamp` to the run it just launched (the file is **append-only and
multi-run**; never blindly tail without matching). Real fields available per line (confirmed from
live runs):

| Field | Type | Used for |
|---|---|---|
| `company`, `role` | str | reply headline |
| `status` | `"ok"` / other | ✅ vs ⚠️ — **but see the partial-run rule below** |
| `steps_closed` | str[] e.g. `["1","2","3","4","4b","5","6","7"]` | did the pipeline finish? |
| `role_folder` | str | the path to report |
| `files_written` | str[] | the "filed" line (resume .pdf/.docx, Verified Emails.md, Cold Outreach.md, …) |
| `gaps` | `[{source, kind, detail}]` | the "needs your eyes" bullets |
| `run_id`, `timestamp` | str | match the line to this run; recency guard |

**Success/failure decision (do NOT trust `status` alone):** a line can be `status:"ok"` yet
represent a half-run (observed: a hook fired `run_finish(partial)` mid-step-4, finished by hand,
logged `ok`). So:

```python
REQUIRED = {"1", "2", "3", "4", "4b", "5"}           # 6,7 are report/log, not pipeline work
def is_success(line: dict) -> bool:
    return line.get("status") == "ok" and REQUIRED.issubset(set(line.get("steps_closed", [])))
```

**Robustness:** lines are NOT all the same shape (hand-appended `run_summary_corrected` lines omit
`steps`/`files_written`). The reader must `.get(key, default)` every field and tolerate missing
keys — never index assuming a fixed schema. If no line matches this run's `run_id` within a
timeout, treat as failure and reply with the failure format (the run likely died before step 7).

**Status summary reply format (fixed):**

```
✅ <Company> — <Role>
   resume + 5 recruiters / 5 HMs filed · 2 Gmail drafts staged
   pushed: Roles/<Company - Role>/  (commit <short-sha>)
   gaps: HM #1 email unverified; 1 LinkedIn msg paste-ready (not sent)
```

Failure reply:

```
⚠️ <Company> — <Role>  (run aborted at step <N>: <step name>)
   reason: <one line>
   partial: <what did land, if anything> · nothing pushed
```

## Testing Strategy

No formal unit-test framework exists in this repo (it's a prep workspace, not an app). Testing is **scenario-based validation**, run manually over Remote Desktop before the bot is trusted. Each acceptance criterion maps to ≥1 scenario:

| Scenario | Verifies AC | How |
|---|---|---|
| LinkedIn URL from Kanu's account | 1,3,4,5 | Send a real LinkedIn job URL; confirm full output set pushed, 2 drafts staged, nothing sent |
| ATS (Greenhouse) URL | 3 | Send a Greenhouse URL; confirm WebFetch path extracts the JD |
| URL from a different Telegram account | 2 | Second account sends a URL; confirm no run, no leak |
| Non-URL / junk message | — | Confirm polite "send a job URL" reply, no run |
| Second URL during a run | 7 | Send two URLs ~1 min apart; confirm `queued, 1 ahead` then serial execution |
| Daemon down at run start | 6 | Stop the LinkedIn daemon, send a URL; confirm failure reply names the daemon, nothing half-pushed |
| PC reboot | 8 | Reboot; confirm bot + daemon auto-start and a URL still works |
| Stale-claim guard (from doc) | — | Confirm the run re-verifies draft claims against current Pipeline.md before staging |

**Pre-flight the bot must run before each `claude -p`:** daemon health check on `127.0.0.1:8765`; if unhealthy, fail fast with the daemon failure reply rather than letting jd-to-ready burn half a run.

## Boundaries

- **Always:** run `git pull --rebase` before a run; commit runner outputs with `drip-runner:` prefix; gate every message on `ALLOWED_USER_ID`; health-check the daemon before invoking the CLI; keep outward output STAGED (Gmail drafts only); honor the architecture doc's **≥4-unsent draft pause**; one run at a time.
- **Ask first:** changing `jd-to-ready`'s internal logic (out of scope here — flag as a gap instead); widening the headless tool allowlist beyond what's in repo `.claude/settings.json`; adding any send/approve capability to the bot; running a second LinkedIn daemon while the Mac daemon is still active (single-daemon rule — account-flag risk).
- **Never:** commit secrets (`.env`, `telegram.token`, `config.toml`); auto-**send** any email or LinkedIn message; run for any Telegram user other than Kanu; expose the bot via a public webhook/inbound port; run two `jd-to-ready` invocations concurrently.

## Success Criteria

Done when all 8 acceptance criteria pass their scenario in the table above, AND:

- The bot + LinkedIn daemon auto-start on boot and recover from a reboot unattended.
- An end-to-end run launched purely from a phone Telegram message produces a pushed apply-ready package + 2 staged Gmail drafts + a correct status reply, with **zero** Mac interaction.
- The single-daemon rule is honored: when the PC daemon is live, the Mac daemon is retired/paused for automation (per the architecture doc's Phase 3 ⚠).

## Open Questions

1. **Service wrapper:** Task Scheduler (native, simplest) vs NSSM (true service, cleaner restart semantics). Default: Task Scheduler unless setup reveals restart flakiness.
2. **Frozen prompt:** this spec assumes the Phase-1 prompt is "run `jd-to-ready` on this URL." The architecture doc's Phase 1 (queue rule) is a *different* effort and explicitly out of scope; the trigger supplies the role, so no queue rule is needed here. Confirm we are NOT blending in the queue-walker.
3. ~~**`claude -p` summary capture:**~~ **RESOLVED** — the bot reads the last matching line of `~/.claude/logs/jd-to-ready.jsonl` (confirmed structured: `company`, `role`, `status`, `steps_closed`, `files_written`, `gaps[]`, `run_id`, `timestamp`). See §"Building the reply from the run log." Success = `status==ok AND {1,2,3,4,4b,5} ⊆ steps_closed`. Reader tolerates heterogeneous/missing keys.
4. **Mac daemon coexistence during testing:** run PC + Mac daemons in parallel briefly for the smoke test, or cut over hard? Default: keep Mac daemon for interactive use, stop using it for automation the moment the PC bot goes live.
5. **GitHub push auth on Windows:** PAT in Git Credential Manager vs SSH deploy key. Default: SSH deploy key scoped to this one repo.

## Out of Scope (explicit non-goals)

- The cron **queue-walker** (architecture doc Phase 1) — this is drop-triggered, not scheduled.
- Any change to `jd-to-ready`'s internal pipeline logic — if headless runs expose a bug, it's flagged as a gap and fixed separately.
- In-Telegram draft approval or sending — Kanu approves in Gmail.
- Cloud-VM deployment — fails the logged-in-LinkedIn-daemon constraint.
- Auto-clicking **Apply** on the ATS.
- Retiring the cloud "secretary" routine (architecture doc Phase 4 cutover) — orthogonal.
