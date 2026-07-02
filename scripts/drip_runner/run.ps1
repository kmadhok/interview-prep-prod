# Application Drip-Runner entrypoint. Run by Task Scheduler.
#   -Mode saved (default): Pass A — prep resumes from the LinkedIn saved-jobs list.
#   -Mode email          : ingest from the Gmail drip-queue (ATS / any-URL escape hatch).
#   -Mode outreach       : Pass B — stage recruiter outreach for roles marked Applied.
param([ValidateSet('saved','email','outreach')][string]$Mode = 'saved')
$ErrorActionPreference = "Stop"
$repo = "G:\projects\interview-prep"
$log  = Join-Path $env:USERPROFILE ".claude\logs\drip-runner.log"
$logDir = Split-Path $log
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force $logDir | Out-Null }
Set-Location $repo

$heartbeatFile = Join-Path $repo "scripts\drip_runner\heartbeat.json"
$watchdogPy    = Join-Path $repo "scripts\drip_runner\watchdog.py"

# Decode the claude subprocess's stdout as UTF-8. PS 5.1 otherwise reads native-exe
# output through the OEM codepage, turning UTF-8 em-dashes etc. into mojibake (Γûö)
# in the captured log. Cosmetic only, but the log exists to be read.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# Echo to console AND append UTF-8 (no BOM) — Tee-Object writes UTF-16 on PS 5.1,
# which garbles the log and trips this repo's BOM-sensitive readers.
function Log($m) {
  $line = "$(Get-Date -Format o) $m"
  Write-Host $line
  [System.IO.File]::AppendAllText($log, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
}

# ---- Heartbeat mechanics (Spec - Machine Watchdog.md) ---------------------
# The heartbeat is one committed JSON file the two machines share via git. This
# PC writes its own `pc.*` fields; the cloud secretary writes `cloud.*`. Threshold
# logic lives ONLY in watchdog.py — run.ps1 shells out to it and never re-encodes
# a number. All JSON writes are UTF-8 no-BOM (this repo's readers are BOM-sensitive).

function Read-Heartbeat {
  # Returns a PSCustomObject, or $null if the file is missing/corrupt. A bad
  # heartbeat must never crash the belt — it is a health byproduct, not the work.
  try {
    if (-not (Test-Path $heartbeatFile)) { Log "heartbeat.json missing; skipping heartbeat update"; return $null }
    return (Get-Content -Raw $heartbeatFile | ConvertFrom-Json)
  } catch { Log "heartbeat read failed: $($_.Exception.Message)"; return $null }
}

function Write-Heartbeat($hb) {
  try {
    $json = $hb | ConvertTo-Json -Depth 6
    # UTF-8 no BOM, trailing newline — same discipline as the log writer above.
    [System.IO.File]::WriteAllText($heartbeatFile, $json + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
  } catch { Log "heartbeat write failed: $($_.Exception.Message)" }
}

function Probe-Daemon {
  # Quick TCP connect to the LinkedIn MCP daemon (127.0.0.1:8765). True iff it
  # accepts a connection within 2s. Best-effort — any error is treated as down.
  try {
    $c = New-Object System.Net.Sockets.TcpClient
    $iar = $c.BeginConnect("127.0.0.1", 8765, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(2000, $false)
    $connected = $ok -and $c.Connected
    if ($connected) { $c.EndConnect($iar) }
    $c.Close()
    return [bool]$connected
  } catch { return $false }
}

function Increment-Aborts {
  # Called on an abort-BEFORE-Claude (e.g. git pull failed). Best-effort local:
  # a PC that can't pull can't push either, so this stays uncommitted — the cloud
  # side's pass-staleness check is the backstop when we can't share the counter.
  $hb = Read-Heartbeat
  if (-not $hb) { return }
  $n = 0
  if ($hb.pc.consecutive_aborts) { $n = [int]$hb.pc.consecutive_aborts }
  $hb.pc.consecutive_aborts = $n + 1
  Write-Heartbeat $hb
  Log "heartbeat: consecutive_aborts -> $($n + 1)"
}

function Stamp-Success($mode, $daemonOk) {
  # Called only when Claude exited 0 — asserts "the whole chain worked". Stamps
  # the pass-specific last_ok field, zeroes the abort streak, records the daemon
  # probe. 'email' is a prep-side ingest variant, so it stamps the Pass A field.
  $hb = Read-Heartbeat
  if (-not $hb) { return }
  $stamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")  # e.g. 2026-07-01T21:04:00-05:00
  if ($mode -eq 'outreach') { $hb.pc.last_ok_outreach = $stamp }
  else { $hb.pc.last_ok_saved = $stamp }   # saved + email both prove Pass A liveness
  $hb.pc.consecutive_aborts = 0
  $hb.pc.daemon_ok = [bool]$daemonOk
  Write-Heartbeat $hb
  Log "heartbeat: stamped $mode ok, aborts=0, daemon_ok=$([bool]$daemonOk)"
}

function HeartbeatCommitAgeHours {
  # Age of the COMMITTED heartbeat.json (its last commit time), in hours. Never
  # committed -> huge (forces a first commit). The no-op guard lives here: we only
  # commit when this exceeds 20h, so a healthy machine churns main at most 1x/day.
  try {
    $iso = (& git log -1 --format=%cI -- "scripts/drip_runner/heartbeat.json") | Select-Object -First 1
    if (-not $iso) { return 1000000.0 }
    return ([DateTimeOffset]::Now - [DateTimeOffset]::Parse($iso)).TotalHours
  } catch { return 1000000.0 }
}

function Commit-HeartbeatIfStale {
  # Commit+push the heartbeat ONLY when the committed copy is >20h old. This keeps
  # the daily liveness proof (distinguishes "idle" from "dead") without churning
  # main hourly. Claude already made its own per-role work commits this run; the
  # heartbeat file is not among their staged paths, so here it is a lone tiny
  # "drip-runner: heartbeat" commit. (Piggyback-into-a-work-commit isn't possible
  # given Claude commits internally per role — see spec note; net cost is identical:
  # <=1 tiny commit/day either way.)
  $age = HeartbeatCommitAgeHours
  if ($age -le 20) { Log "heartbeat commit skipped (committed copy ~$([int]$age)h old, <=20h)"; return }
  git add "scripts/drip_runner/heartbeat.json"
  git commit -m "drip-runner: heartbeat" | Out-Null
  if (-not $?) { Log "heartbeat commit produced nothing / failed; not pushing"; return }
  git push
  if (-not $?) {
    Log "heartbeat push rejected; git pull --rebase --autostash then push once more"
    git pull --rebase --autostash
    git push
    if (-not $?) { Log "heartbeat push failed again; leaving for next run" }
  } else { Log "heartbeat committed + pushed (committed copy was ~$([int]$age)h old)" }
}

function Show-Toast($title, $message) {
  # PC-local loud alert: a Windows tray balloon (rendered as a toast on Win10).
  # Uses NotifyIcon so there is NO external module dependency (BurntToast etc.).
  # Wrapped so a headless/service session that can't show UI never breaks the run.
  try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $ni = New-Object System.Windows.Forms.NotifyIcon
    $ni.Icon = [System.Drawing.SystemIcons]::Warning
    $ni.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
    $ni.BalloonTipTitle = $title
    $ni.BalloonTipText = $message
    $ni.Visible = $true
    $ni.ShowBalloonTip(15000)
    Start-Sleep -Seconds 8   # keep the process alive long enough for the balloon to render
    $ni.Dispose()
    Log "toast raised: $title"
  } catch { Log "toast failed: $($_.Exception.Message)" }
}

function Maybe-ToastOnAborts {
  # Shell out to watchdog.py for the >=3 threshold — never re-encode the number here.
  # Empty stdout = under threshold (or anti-flap suppressed). Non-empty = toast.
  try {
    $alert = (& py -3 $watchdogPy --check aborts --heartbeat $heartbeatFile) | Out-String
    if ($alert.Trim()) { Show-Toast "Drip-runner stalled" $alert.Trim() }
  } catch { Log "abort-watchdog check failed: $($_.Exception.Message)" }
}

Log "run start (mode=$Mode)"
# --autostash: a crashed run can leave an unclosed trace .jsonl dirty in the tree,
# and plain --rebase then refuses to pull — deadlocking every future run until a
# human commits the file (happened 2026-06-30 → 07-01, ~34h of silent no-ops).
git pull --rebase --autostash
if (-not $?) {
  Log "git pull failed; aborting run (no claude invocation)"
  Increment-Aborts        # abort-before-Claude: bump the streak (best-effort, local)
  Maybe-ToastOnAborts     # loud PC-local alert once the streak hits >=3
  exit 1
}

$promptFile = switch ($Mode) {
  'email'    { 'runner-prompt.md' }
  'outreach' { 'runner-prompt-outreach.md' }
  default    { 'runner-prompt-saved.md' }
}
$prompt = Get-Content -Raw (Join-Path $repo "scripts\drip_runner\$promptFile")
Log "invoking claude -p (prompt=$promptFile)"
# Pipe the prompt via stdin, NOT as a -p argument: PowerShell 5.1's native-arg
# quoting breaks on embedded quotes (e.g. --company "") and leaks prompt text like
# --job-id to claude as bogus CLI options. Stdin sidesteps arg parsing entirely.
#
# Capture stdout so the run summary lands in the persistent log (this is an
# unattended cron run; without this the only durable record is the 4 wrapper
# lines). stdout only: do NOT 2>&1 a native exe under -ErrorActionPreference Stop
# (PS 5.1 wraps stderr as a terminating NativeCommandError). $LASTEXITCODE survives.
#
# --permission-mode bypassPermissions: this is an UNATTENDED Task Scheduler run with
# no human to approve tool prompts. We relied on .claude/settings.json's allow-list
# until a `claude` CLI auto-update (autoUpdatesChannel=latest, 2.1.195) stopped
# honoring the coarse entries ("Bash","mcp__linkedin") for headless -p calls, so every
# run STOPped at the pre-run LinkedIn health check (2026-06-28 onward). Bypass is safe
# here: the runner is drafts-only and never sends — the human gate is downstream
# (review + Send in Gmail), so invariant 1 (human-gated output) is preserved.
$out = $prompt | claude -p --permission-mode bypassPermissions | Out-String
$code = $LASTEXITCODE
Write-Host $out
[System.IO.File]::AppendAllText($log, "---- claude output ----" + [Environment]::NewLine + $out + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))

# Heartbeat: stamp liveness only when the whole chain worked (Claude exited 0).
# A non-zero exit is NOT an abort-before-Claude (the streak is for pre-Claude
# deadlocks); we simply do not stamp, and the cloud's pass-staleness check catches
# a persistently failing PC via the >26h/>50h thresholds.
if ($code -eq 0) {
  $daemonOk = Probe-Daemon
  Stamp-Success $Mode $daemonOk
  Commit-HeartbeatIfStale
} else {
  Log "claude exited $code (not a pre-Claude abort; heartbeat not stamped, streak unchanged)"
}

# ---- Apply Packet post-steps (Spec - Apply Packet.md) ----------------------
# Deterministic, LLM-free: reconcile makes the Drive mirror follow repo truth
# (runs every mode — cheap + idempotent); the digest pushes to ntfy on the
# daily saved pass only. Failures are loud (log + toast) but never kill the run.
try {
  $rec = (& py -3 (Join-Path $repo "scripts\drip_runner\apply_packet.py") reconcile --repo-root $repo --commit) | Out-String
  if ($rec.Trim()) { Log "packet reconcile: $($rec.Trim())" }
  if ($LASTEXITCODE -ne 0 -or $rec -match "FAILED") { Show-Toast "Apply packet reconcile failed" ($rec.Trim()) }
} catch { Log "packet reconcile crashed: $($_.Exception.Message)"; Show-Toast "Apply packet reconcile crashed" $_.Exception.Message }

if ($Mode -eq 'saved') {
  try {
    $dg = (& py -3 (Join-Path $repo "scripts\drip_runner\apply_digest.py") --repo-root $repo --send) | Out-String
    Log "digest: $($dg.Trim())"
    if ($LASTEXITCODE -ne 0) { Show-Toast "Apply digest failed" ($dg.Trim()) }
  } catch { Log "digest crashed: $($_.Exception.Message)"; Show-Toast "Apply digest crashed" $_.Exception.Message }
}

Log "run end (exit $code)"
exit $code
