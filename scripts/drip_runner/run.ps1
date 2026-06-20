# Application Drip-Runner entrypoint. Run by Task Scheduler.
$ErrorActionPreference = "Stop"
$repo = "G:\projects\interview-prep"
$log  = Join-Path $env:USERPROFILE ".claude\logs\drip-runner.log"
$logDir = Split-Path $log
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force $logDir | Out-Null }
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
