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
