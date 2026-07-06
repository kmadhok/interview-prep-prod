# Registers the always-on automation as Task Scheduler jobs:
#   1. LinkedInDaemon - the LinkedIn MCP daemon, at logon (auto-recovers across reboots).
#   2. DripRunner     - the application drip-runner (run.ps1), weekday cadence.
#
# Run once. Per-user at-logon / time-of-day triggers do NOT require elevation; if
# Register-ScheduledTask reports access denied, re-run from an elevated PowerShell.
#
# DripRunner is registered ENABLED (validated by a full end-to-end run 2026-06-21).
# The old "disabled until the safety gate lands" rule was dropped 2026-06-21 - we
# learn from real runs + logging instead of a canary; see Drip Runner plan.
# $Repo defaults to two levels up from this script (scripts\drip_runner\install-tasks.ps1).
# $DaemonDir defaults to the linkedin-mcp-server checkout beside the repo; override
# both if your layout differs.
param(
  [string]$Repo,
  [string]$DaemonDir
)
$ErrorActionPreference = "Stop"
if (-not $Repo)      { $Repo      = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path }
if (-not $DaemonDir) { $DaemonDir = (Join-Path (Split-Path $Repo -Parent) "linkedin-mcp-server") }
$repo      = $Repo
$daemonDir = $DaemonDir
$uv        = (Get-Command uv).Source
$ps        = (Get-Command powershell).Source

# Both tasks run inside the logged-on user session (Limited/Interactive). An explicit
# principal is what lets a non-elevated user register these; the default principal
# requires admin. The daemon AND the runner need the interactive session anyway -
# the browser profile, the claude login, and the MCP servers don't exist under SYSTEM.
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

# --- 1. LinkedIn MCP daemon: always-on at logon ---
$dAction   = New-ScheduledTaskAction -Execute $uv -Argument "run linkedin-mcp-server" -WorkingDirectory $daemonDir
# Scope the at-logon trigger to THIS user; an all-users at-logon trigger needs admin.
$dTrigger  = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$dSettings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable
Register-ScheduledTask -TaskName "LinkedInDaemon" -Action $dAction -Trigger $dTrigger -Settings $dSettings -Principal $principal -Force | Out-Null
Write-Host "Registered LinkedInDaemon (at logon)."

# --- 2. Drip-runner: weekday cadence ---
# CADENCE: every day at 05:07 local (Central). Each run drains ALL un-acted saved jobs
# (newest-first) up to a cap of 6 roles; runs are ~20-30 min per role and never overlap
# (MultipleInstances IgnoreNew). 3h limit covers the 6-role cap. The trigger time is
# local, so the box's Central time zone makes this ~5 AM CST/CDT.
# OFFSET OFF THE HOUR (:07, not :00): DripRunnerOutreach repeats hourly ON the hour, so a
# 05:00 daily start raced it — both run.ps1 instances hit `git pull --rebase` in the same
# second, one lost the index.lock with no retry, and the saved-jobs run aborted 0x1
# (observed 2026-06-30). Starting at :07 keeps the two startup pulls from ever colliding.
$runner     = Join-Path $repo "scripts\drip_runner\run.ps1"
$rAction    = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`"" -WorkingDirectory $repo
$rTrigger   = New-ScheduledTaskTrigger -Daily -At 5:07am
$rSettings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "DripRunner" -Action $rAction -Trigger $rTrigger -Settings $rSettings -Principal $principal -Force | Out-Null
Write-Host "Registered DripRunner (daily 05:00, ENABLED)."

# --- 3. Drip-runner Pass B (outreach): hourly ---
# Pass B polls Pipeline.md for roles marked Applied with no STAGED/error marker
# (via outreach_worklist.py) and stages recruiter outreach for each via the
# stage-outreach skill. Hourly per Kanu's decision; there is NO per-role cap, so
# the worklist drains fully — the 3h ExecutionTimeLimit is the only bound and
# per-role commits make a killed run resume next hour. IgnoreNew prevents an
# hourly trigger from overlapping a long-running outreach session (sequential
# LinkedIn only). Same interactive principal as DripRunner (needs the daemon,
# the claude login, and the MCP servers in the logged-on session).
$oAction   = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -Mode outreach" -WorkingDirectory $repo
# Omit -RepetitionDuration → repeats indefinitely. Do NOT pass [TimeSpan]::MaxValue:
# it serializes to P99999999DT23H59M59S, which Task Scheduler rejects as out-of-range,
# so the whole Register-ScheduledTask throws and the hourly task is never created.
$oTrigger  = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1)
$oSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "DripRunnerOutreach" -Action $oAction -Trigger $oTrigger -Settings $oSettings -Principal $principal -Force | Out-Null
Write-Host "Registered DripRunnerOutreach (hourly, ENABLED)."
