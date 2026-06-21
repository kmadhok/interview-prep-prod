# Registers the always-on automation as Task Scheduler jobs:
#   1. LinkedInDaemon - the LinkedIn MCP daemon, at logon (auto-recovers across reboots).
#   2. DripRunner     - the application drip-runner (run.ps1), weekday cadence.
#
# Run once. Per-user at-logon / time-of-day triggers do NOT require elevation; if
# Register-ScheduledTask reports access denied, re-run from an elevated PowerShell.
#
# DripRunner is registered DISABLED on purpose: smoke-test run.ps1 by hand first,
# then enable it with `Enable-ScheduledTask -TaskName DripRunner`. (The old
# "disabled until the safety gate lands" rule was dropped 2026-06-21 - we learn
# from real runs + logging instead of a canary; see Drip Runner plan.)
$ErrorActionPreference = "Stop"
$repo      = "G:\projects\interview-prep"
$daemonDir = "G:\projects\linkedin-mcp-server"
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
# CADENCE (tunable): weekday mornings 08:00 local. One role per run; LinkedIn
# sequences run 35-60 min, so never schedule runs closer together than the longest
# observed run. Re-tune after the first real runs reveal actual duration.
$runner     = Join-Path $repo "scripts\drip_runner\run.ps1"
$rAction    = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`"" -WorkingDirectory $repo
$rTrigger   = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 8am
$rSettings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "DripRunner" -Action $rAction -Trigger $rTrigger -Settings $rSettings -Principal $principal -Force | Out-Null
Disable-ScheduledTask -TaskName "DripRunner" | Out-Null
Write-Host "Registered DripRunner (weekday 08:00) - DISABLED until smoke-tested. Enable with: Enable-ScheduledTask -TaskName DripRunner"
