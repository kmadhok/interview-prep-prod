# Application Drip-Runner (Email-Cron) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the manually-validated email→jd-to-ready loop into an unattended runner on the always-on Windows PC: a Task Scheduler job that `git pull`s, then runs a frozen `claude -p` prompt which drains the Gmail `drip-queue`, runs `jd-to-ready` per job, and stages drafts — never sending.

**Architecture:** A thin shell around an agent. Deterministic, unit-tested Python helpers (`job_parser`, `dedupe`) handle parsing and dedupe; a frozen agent prompt (`runner-prompt.md`) drives the loop using the Gmail + LinkedIn MCP tools and the `jd-to-ready` skill (only the agent can call those); PowerShell (`run.ps1`) wraps `git pull → claude -p`; Task Scheduler runs it. The loop was already proven end-to-end by two live manual runs (Pinterest, Blackstone) — this plan codifies that loop.

**Tech Stack:** Python 3.12 (`py -3`), pytest, PowerShell 5.1 (Windows Task Scheduler), Claude Code CLI (`claude -p`), Gmail MCP, LinkedIn MCP, the `jd-to-ready` skill.

## Global Constraints

- **Platform: Windows 10 / PowerShell 5.1.** Chain with `; if ($?) { ... }` — `&&` is a parse error. Python launcher is `py -3`.
- **Drafts only, never send.** All outward output is staged (Gmail drafts + paste-ready InMail text). No task may send mail or LinkedIn messages.
- **Gmail label invariant (live-tested):** mutate labels by **ID** (`Label_3`…`Label_6`); query the queue by **name** (`label:drip-queue`). Querying by ID returns empty. Resolve IDs at runtime via `list_labels` by name — do not hardcode.
- **Label state machine:** `drip-queue` → `drip-processing` (claim on pick) → `drip-done` (success) / `drip-error` (failure). No auto-retry; parked jobs are re-queued by hand.
- **URL→JD:** LinkedIn job URL (`/jobs/view/<id>/`) → `get_job_details`; non-LinkedIn (ATS) URL → WebFetch. WebFetch login-walls LinkedIn — never use it for LinkedIn.
- **Recovery policy:** park-everything-on-failure + alert (a `[DRIP-RUNNER] failures` Gmail draft-to-self). Pre-run health check exits before claiming if the daemon/Gmail is down.
- **Pipeline.md is the durable record; append-only.** The `active_interview_pipeline.md` memory is Mac-local and unsynced — the memory step is a no-op on the PC; never fabricate it.
- **Per-run scope:** drain the queue sequentially, oldest first, until empty or the staging pause trips (≥4 unsent job drafts).
- **Runner deps on this PC:** `reportlab` (resume PDF) installed; EmailFinder.dev key in repo-root `.env` as `Email_Finder_Dev` (read utf-8-sig). poppler/`pdftoppm` is optional (only the resume vision-verify uses it; absence degrades to a gap).
- **HARD DEPENDENCY:** do **not** enable the Task Scheduler cron (Task 7) until the Skill Sync canary + rollback (separate plan) is live. Every other task may ship independently.

---

### Task 1: Email parser (`job_parser`)

Pure functions that turn a queued email into a structured job reference, so the agent never eyeballs URLs/IDs.

**Files:**
- Create: `scripts/drip_runner/__init__.py` (empty)
- Create: `scripts/drip_runner/job_parser.py`
- Test: `scripts/drip_runner/test_job_parser.py`

**Interfaces:**
- Produces: `parse_job_email(subject: str, body: str) -> JobRef` where `JobRef` is a dataclass `{is_job: bool, url: str, source: str, job_id: str, reason: str}` (`source` ∈ `"linkedin"|"ats"|""`). Also `is_job_subject(subject)->bool`, `first_url(body)->str`. CLI: `py -3 scripts/drip_runner/job_parser.py --subject S --body B` prints the JobRef as JSON.

- [ ] **Step 1: Write the failing test**

```python
# scripts/drip_runner/test_job_parser.py
from job_parser import parse_job_email, is_job_subject, first_url

def test_subject_loose_job_prefix():
    assert is_job_subject("JOB Blackstone")
    assert is_job_subject("JOB: Pinterest AI")
    assert is_job_subject("  job something")
    assert not is_job_subject("Jobs report Q3")   # 'Jobs' != leading 'JOB' token
    assert not is_job_subject("Re: JOB forwarded")  # not leading
    assert not is_job_subject("")

def test_first_url_strips_trailing_punct():
    assert first_url("see https://x.com/a). end") == "https://x.com/a"
    assert first_url("no link here") == ""

def test_linkedin_job_parsed():
    r = parse_job_email("JOB Blackstone", "https://www.linkedin.com/jobs/view/4428726955/")
    assert r.is_job and r.source == "linkedin" and r.job_id == "4428726955"
    assert r.url == "https://www.linkedin.com/jobs/view/4428726955/"

def test_ats_url_is_ats_no_jobid():
    r = parse_job_email("JOB Acme", "apply here https://boards.greenhouse.io/acme/jobs/123")
    assert r.is_job and r.source == "ats" and r.job_id == ""

def test_non_job_subject_rejected():
    r = parse_job_email("lunch?", "https://www.linkedin.com/jobs/view/1/")
    assert not r.is_job and "subject" in r.reason

def test_job_subject_no_url_rejected():
    r = parse_job_email("JOB Cohere", "forgot the link")
    assert not r.is_job and "URL" in r.reason
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3 -m pytest scripts/drip_runner/test_job_parser.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'job_parser'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/drip_runner/job_parser.py
"""Parse a 'JOB' drip-queue email into a structured job reference. Pure, no I/O."""
from __future__ import annotations
import argparse, json, re, sys
from dataclasses import dataclass, asdict

LINKEDIN_JOB_RE = re.compile(r"linkedin\.com/jobs/view/(\d+)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)


@dataclass
class JobRef:
    is_job: bool
    url: str = ""
    source: str = ""
    job_id: str = ""
    reason: str = ""


def is_job_subject(subject: str) -> bool:
    return bool(re.match(r"\s*job\b", subject or "", re.IGNORECASE))


def first_url(body: str) -> str:
    m = URL_RE.search(body or "")
    return m.group(0).rstrip(".,);]") if m else ""


def parse_job_email(subject: str, body: str) -> JobRef:
    if not is_job_subject(subject):
        return JobRef(False, reason="subject does not start with JOB token")
    url = first_url(body)
    if not url:
        return JobRef(False, reason="no URL found in body")
    m = LINKEDIN_JOB_RE.search(url)
    if m:
        return JobRef(True, url=url, source="linkedin", job_id=m.group(1))
    return JobRef(True, url=url, source="ats")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    args = p.parse_args(argv)
    print(json.dumps(asdict(parse_job_email(args.subject, args.body))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_job_parser.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/drip_runner/__init__.py scripts/drip_runner/job_parser.py scripts/drip_runner/test_job_parser.py
git commit -m "drip-runner: add job_parser (email -> JobRef) with tests"
```

---

### Task 2: Pipeline dedupe (`dedupe`)

Pure check so the runner skips roles already in the pipeline.

**Files:**
- Create: `scripts/drip_runner/dedupe.py`
- Test: `scripts/drip_runner/test_dedupe.py`

**Interfaces:**
- Produces: `is_duplicate(company: str, job_id: str, pipeline_text: str) -> bool` (True if the LinkedIn `job_id` substring appears, OR the company name appears case-insensitively). Helpers `company_in_pipeline`, `job_id_in_pipeline`. CLI: `py -3 scripts/drip_runner/dedupe.py --company C --job-id ID --pipeline Pipeline.md` exits 0 if duplicate, 1 if new, and prints `DUPLICATE`/`NEW`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/drip_runner/test_dedupe.py
from dedupe import is_duplicate, company_in_pipeline, job_id_in_pipeline

PIPE = "| **Pinterest — AI Solutions Engineer** | ... | Pinterest careers (job 4387218136) | ... |"

def test_company_match_case_insensitive():
    assert company_in_pipeline("pinterest", PIPE)
    assert not company_in_pipeline("Acme Corp", PIPE)
    assert not company_in_pipeline("", PIPE)

def test_job_id_match():
    assert job_id_in_pipeline("4387218136", PIPE)
    assert not job_id_in_pipeline("9999999999", PIPE)
    assert not job_id_in_pipeline("", PIPE)

def test_is_duplicate_combines():
    assert is_duplicate("Pinterest", "0", PIPE)        # company hit
    assert is_duplicate("Other", "4387218136", PIPE)   # job-id hit
    assert not is_duplicate("Brand New Co", "123", PIPE)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -3 -m pytest scripts/drip_runner/test_dedupe.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dedupe'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/drip_runner/dedupe.py
"""Decide whether a role is already in Pipeline.md. Pure + a thin CLI."""
from __future__ import annotations
import argparse, sys
from pathlib import Path


def company_in_pipeline(company: str, pipeline_text: str) -> bool:
    company = (company or "").strip().lower()
    return bool(company) and company in (pipeline_text or "").lower()


def job_id_in_pipeline(job_id: str, pipeline_text: str) -> bool:
    return bool(job_id) and job_id in (pipeline_text or "")


def is_duplicate(company: str, job_id: str, pipeline_text: str) -> bool:
    return job_id_in_pipeline(job_id, pipeline_text) or company_in_pipeline(company, pipeline_text)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--company", default="")
    p.add_argument("--job-id", default="")
    p.add_argument("--pipeline", required=True)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    dup = is_duplicate(args.company, args.job_id, text)
    print("DUPLICATE" if dup else "NEW")
    return 0 if dup else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `py -3 -m pytest scripts/drip_runner/test_dedupe.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/drip_runner/dedupe.py scripts/drip_runner/test_dedupe.py
git commit -m "drip-runner: add Pipeline.md dedupe with tests"
```

---

### Task 3: Frozen runner prompt (`runner-prompt.md`)

The agent loop, encoded once. This is the `claude -p` payload. Not pytest-tested (it's agent instructions); validated by the smoke test in Task 6. Mirrors the manual Pinterest/Blackstone loops exactly.

**Files:**
- Create: `scripts/drip_runner/runner-prompt.md`

**Interfaces:**
- Consumes: `job_parser.py`, `dedupe.py` (Task 1/2), the Gmail + LinkedIn MCP tools, the `jd-to-ready` skill.

- [ ] **Step 1: Write the prompt file (full content)**

```markdown
You are the Application Drip-Runner on Kanu's always-on Windows PC. Repo root: G:\projects\interview-prep. Work top to bottom; do not ask questions; never send anything outward.

PRE-RUN HEALTH CHECK
1. Confirm the LinkedIn daemon is up: a `mcp__linkedin__get_my_profile` call returns without transport error. If it errors, STOP — write nothing, claim nothing, exit. (Jobs stay in drip-queue for the next run.)
2. Resolve the four label IDs with `list_labels`, matching names: drip-queue, drip-processing, drip-done, drip-error. Remember: mutate by ID, query by NAME.

DRAIN THE QUEUE (oldest first, one job at a time)
Repeat until `search_threads "label:drip-queue"` is empty OR you have staged 2 roles this run OR ≥4 job drafts already sit unsent (check list_drafts):
  a. Take the oldest drip-queue thread. CLAIM it: add drip-processing (ID), remove drip-queue (ID).
  b. Read the thread (get_thread). Run: py -3 scripts/drip_runner/job_parser.py --subject "<subject>" --body "<body>" → JSON.
     - If is_job is false → drip-error (ID), remove drip-processing, append the reason to the failures alert (see ALERT), continue.
  c. Get the JD text:
     - source "linkedin" → mcp__linkedin__get_job_details(job_id). If it errors/empty → drip-error + alert, continue.
     - source "ats" → WebFetch the url for the JD. If it returns no JD → drip-error + alert, continue.
  d. DEDUPE: py -3 scripts/drip_runner/dedupe.py --company "<employer>" --job-id "<job_id>" --pipeline Pipeline.md.
     - If DUPLICATE → drip-done (already handled), remove drip-processing, continue (do not re-file).
  e. Run the jd-to-ready skill end-to-end on the JD text (real run into Roles/). Drafts only; never send. The memory step is a no-op on this PC (note as a gap; do not create active_interview_pipeline.md).
  f. On success → drip-done (ID), remove drip-processing.
  g. On any failure in (e) → drip-error (ID), remove drip-processing, append role + failing step + reason to the failures alert, continue.

ALERT (failures only)
Maintain a single Gmail draft-to-self titled "[DRIP-RUNNER] failures <YYYY-MM-DD>": create it (To: madhok.kanu@gmail.com) the first time a job parks this run, and append one line per parked job (role, failing step, reason). Never send it.

FINISH
- git add the role folders + Pipeline.md you changed; commit with a "drip-runner:" prefix summarizing roles staged/parked; push (git push). If push fails on rebase, git pull --rebase then push once more.
- End with a one-line summary: roles staged, roles parked, gaps.
```

- [ ] **Step 2: Verify the prompt references only things that exist**

Run: `py -3 scripts/drip_runner/job_parser.py --subject "JOB test" --body "https://www.linkedin.com/jobs/view/123/"`
Expected: `{"is_job": true, "url": "https://www.linkedin.com/jobs/view/123/", "source": "linkedin", "job_id": "123", "reason": ""}`
Run: `py -3 scripts/drip_runner/dedupe.py --company "ZzzNope" --job-id "000" --pipeline Pipeline.md`
Expected: prints `NEW`, exit code 1.

- [ ] **Step 3: Commit**

```bash
git add scripts/drip_runner/runner-prompt.md
git commit -m "drip-runner: add frozen agent runner prompt"
```

---

### Task 4: PowerShell entrypoint (`run.ps1`)

Wraps `git pull → claude -p (frozen prompt)` with logging. The agent (per prompt) does the commit+push.

**Files:**
- Create: `scripts/drip_runner/run.ps1`

**Interfaces:**
- Consumes: `runner-prompt.md` (Task 3), the `claude` CLI on PATH, `.claude/settings.json` tool allowlist (already committed).

- [ ] **Step 1: Write the entrypoint (full content)**

```powershell
# Application Drip-Runner entrypoint. Run by Task Scheduler.
$ErrorActionPreference = "Stop"
$repo = "G:\projects\interview-prep"
$log  = Join-Path $env:USERPROFILE ".claude\logs\drip-runner.log"
Set-Location $repo

function Log($m) { "$(Get-Date -Format o) $m" | Tee-Object -FilePath $log -Append }

Log "run start"
git pull --rebase
if (-not $?) { Log "git pull failed; aborting run (no claude invocation)"; exit 1 }

$prompt = Get-Content -Raw (Join-Path $repo "scripts\drip_runner\runner-prompt.md")
Log "invoking claude -p"
claude -p $prompt
Log "run end (exit $LASTEXITCODE)"
exit $LASTEXITCODE
```

- [ ] **Step 2: Dry-run the entrypoint's safe half (pull + prompt load, no claude)**

Run (manually, in PowerShell):
```powershell
cd G:\projects\interview-prep
git pull --rebase; if ($?) { (Get-Content -Raw scripts\drip_runner\runner-prompt.md).Length }
```
Expected: pull succeeds (or "Already up to date"), then prints the prompt length (a number > 0). This confirms the chaining + path resolution without launching the agent.

- [ ] **Step 3: Commit**

```bash
git add scripts/drip_runner/run.ps1
git commit -m "drip-runner: add PowerShell entrypoint (pull -> claude -p)"
```

---

### Task 5: Daemon auto-start (Task Scheduler) + install script

Make the LinkedIn daemon survive reboots ("always on" ≠ "auto-recovers"). Registers ONLY the daemon now; the cron job is Task 7 (gated).

**Files:**
- Create: `scripts/drip_runner/install-tasks.ps1`

**Interfaces:**
- Produces: a Task Scheduler job `LinkedInDaemon` (at logon) running the daemon from `G:\projects\linkedin-mcp-server`.

- [ ] **Step 1: Write the install script (full content)**

```powershell
# Registers the LinkedIn MCP daemon as an at-logon Task Scheduler job.
# Run once, in an elevated PowerShell. The drip-runner cron is registered
# separately (see plan Task 7) and stays disabled until the safety gate lands.
$ErrorActionPreference = "Stop"
$daemonDir = "G:\projects\linkedin-mcp-server"
$uv = (Get-Command uv).Source

$action  = New-ScheduledTaskAction -Execute $uv -Argument "run linkedin-mcp-server" -WorkingDirectory $daemonDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable
Register-ScheduledTask -TaskName "LinkedInDaemon" -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "Registered LinkedInDaemon (at logon)."
```

- [ ] **Step 2: Verify (registration is a one-time manual elevated run)**

Run (elevated PowerShell): `powershell -ExecutionPolicy Bypass -File scripts\drip_runner\install-tasks.ps1`
Then: `schtasks /query /tn LinkedInDaemon /fo LIST | Select-String "TaskName","Status"`
Expected: shows `TaskName: \LinkedInDaemon` and `Status: Ready`.
Then confirm the daemon serves: `(netstat -ano | Select-String 8765)` shows a LISTENING line.

- [ ] **Step 3: Commit**

```bash
git add scripts/drip_runner/install-tasks.ps1
git commit -m "drip-runner: Task Scheduler install script for LinkedIn daemon auto-start"
```

---

### Task 6: Ops doc + Gmail filter + smoke test (`README.md`)

The human-setup steps the runner depends on, and the acceptance test that proves the whole loop.

**Files:**
- Create: `scripts/drip_runner/README.md`

- [ ] **Step 1: Write the ops doc (full content)**

```markdown
# Application Drip-Runner — Ops

## One-time setup (Kanu, in the Gmail UI / a terminal)
1. **Labels** already exist: drip-queue, drip-processing, drip-done, drip-error.
2. **Gmail filter:** Settings → Filters → Create. Criteria: Subject `JOB`. Action: Apply label `drip-queue`, Skip Inbox (optional). This auto-queues a self-sent "JOB <title>" email with a URL in the body.
3. **`.env`** at repo root contains `Email_Finder_Dev=<key>` (no BOM — create via an editor or `Set-Content ... -Encoding utf8NoBOM`).
4. **Deps:** `py -3 -m pip install reportlab`. Optional: install poppler (`pdftoppm`) for the resume vision-verify.
5. **Daemon auto-start:** run `install-tasks.ps1` once (elevated).

## How to send a job
Email yourself: Subject `JOB <anything>`, body = one job URL (LinkedIn or ATS).

## Run manually (smoke test)
`powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1`

## What it does
Drains label:drip-queue oldest-first → claim → URL→JD → dedupe → jd-to-ready (drafts only) → Pipeline row → drip-done. Failures park to drip-error and append to a "[DRIP-RUNNER] failures" Gmail draft. Never sends.

## Re-queue a parked job
In Gmail, relabel it drip-error → drip-queue.
```

- [ ] **Step 2: Smoke test (the acceptance test for Tasks 1–4)**

Run:
1. Send yourself an email: Subject `JOB SmokeTest`, body a real LinkedIn job URL not already in Pipeline.md.
2. Confirm it gets `drip-queue` (the filter), or label it by hand.
3. `powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1`

Expected (verify after):
- `search_threads "label:drip-done"` includes the test email; `label:drip-processing` and `label:drip-queue` are empty.
- A new `Roles/<Company - Role>/` folder exists with `Job Description.md`, the resume `.md`+`.pdf`, `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`.
- A new Pipeline.md row; a `drip-runner:` commit was pushed.
- A Gmail draft exists for the lead contact and was NOT sent.

(This is exactly the Pinterest + Blackstone manual runs, now driven by `run.ps1`.)

- [ ] **Step 3: Commit**

```bash
git add scripts/drip_runner/README.md
git commit -m "drip-runner: ops doc + Gmail filter setup + smoke-test procedure"
```

---

### Task 7: Register + enable the cron job — GATED

**Do not start this task until the Skill Sync canary + rollback plan is live.** Until then a bad skill push reaches an autonomous writer of outreach. This task is the on-switch; everything above is safe to ship without it.

**Files:**
- Modify: `scripts/drip_runner/install-tasks.ps1` (append the cron registration, created disabled)

**Interfaces:**
- Consumes: `run.ps1` (Task 4), the Skill Sync safety gate (separate plan) wired into `run.ps1` before the `claude -p` call.

- [ ] **Step 1: Append the cron registration (disabled by default)**

```powershell
# --- Append to install-tasks.ps1 ---
# Drip-runner cron. Registered DISABLED; enable only after the Skill Sync
# canary is wired into run.ps1. Cadence is a placeholder — tune to observed
# run duration (LinkedIn sequences run 35-60 min/role; do not overlap runs).
$ps = (Get-Command powershell).Source
$runAction = New-ScheduledTaskAction -Execute $ps -Argument "-ExecutionPolicy Bypass -File `"$repoRun`""
$runTrigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "DripRunner" -Action $runAction -Trigger $runTrigger -Settings $settings -Force
Disable-ScheduledTask -TaskName "DripRunner"
Write-Host "Registered DripRunner (DISABLED). Enable with: Enable-ScheduledTask -TaskName DripRunner"
```

- [ ] **Step 2: Verify it is registered and DISABLED**

Run: `schtasks /query /tn DripRunner /fo LIST | Select-String "TaskName","Status"`
Expected: `Status: Disabled`.

- [ ] **Step 3: Enable only after the safety gate + one supervised live run**

Run: `Enable-ScheduledTask -TaskName DripRunner`
Then watch the first scheduled run's `~/.claude/logs/drip-runner.log` and the `drip-runner:` commit before trusting it unattended.

- [ ] **Step 4: Commit**

```bash
git add scripts/drip_runner/install-tasks.ps1
git commit -m "drip-runner: register cron Task Scheduler job (disabled, gated on safety canary)"
```

---

## Self-Review

**Spec coverage:**
- Input channel / Gmail filter → Task 6. ✅
- Scheduler (Task Scheduler, local) → Tasks 4, 5, 7. ✅
- 3-state queue state machine + claim/relabel → Task 3 (prompt), invariants in Global Constraints. ✅
- URL→JD (get_job_details / WebFetch) → Task 1 (classify) + Task 3 (fetch). ✅
- jd-to-ready run (drafts only) → Task 3. ✅
- Pipeline append + memory no-op → Task 3 + Global Constraints. ✅
- Alerting (failures draft) → Task 3. ✅
- Per-run drain + staging pause → Task 3. ✅
- Pre-run health check → Task 3. ✅
- Daemon/scheduler auto-start → Task 5. ✅
- Cron gated on safety canary → Task 7 + Global Constraints. ✅

**Placeholder scan:** No TBD/TODO. Cron cadence in Task 7 is explicitly a tunable placeholder with the tuning rule stated (not a gap). The agent-prompt and PowerShell tasks use verification commands + the smoke test instead of pytest, by necessity (MCP/agent/OS surfaces aren't unit-testable); the two pure-Python tasks (1, 2) are full TDD.

**Type/name consistency:** `JobRef` fields (`is_job, url, source, job_id, reason`) are referenced consistently in Tasks 1 and 3. `is_duplicate(company, job_id, pipeline_text)` consistent in Tasks 2 and 3. Label names/IDs and the state machine match Global Constraints throughout. `$repoRun` in Task 7 refers to `run.ps1`'s path — define `$repoRun = Join-Path $repo "scripts\drip_runner\run.ps1"` alongside `$repo` when implementing Task 7.

**Scope:** one subsystem (the runtime loop), one plan. The safety gate is a separate plan by design.
