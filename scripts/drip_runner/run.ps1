# Application Drip-Runner entrypoint. Run by Task Scheduler.
#   -Mode saved (default): ingest from the LinkedIn saved-jobs list.
#   -Mode email          : ingest from the Gmail drip-queue (ATS / any-URL escape hatch).
param([ValidateSet('saved','email')][string]$Mode = 'saved')
$ErrorActionPreference = "Stop"
$repo = "G:\projects\interview-prep"
$log  = Join-Path $env:USERPROFILE ".claude\logs\drip-runner.log"
$logDir = Split-Path $log
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force $logDir | Out-Null }
Set-Location $repo

# Echo to console AND append UTF-8 (no BOM) — Tee-Object writes UTF-16 on PS 5.1,
# which garbles the log and trips this repo's BOM-sensitive readers.
function Log($m) {
  $line = "$(Get-Date -Format o) $m"
  Write-Host $line
  [System.IO.File]::AppendAllText($log, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
}

Log "run start (mode=$Mode)"
git pull --rebase
if (-not $?) { Log "git pull failed; aborting run (no claude invocation)"; exit 1 }

$promptFile = if ($Mode -eq 'email') { 'runner-prompt.md' } else { 'runner-prompt-saved.md' }
$prompt = Get-Content -Raw (Join-Path $repo "scripts\drip_runner\$promptFile")
Log "invoking claude -p (prompt=$promptFile)"
claude -p $prompt
Log "run end (exit $LASTEXITCODE)"
exit $LASTEXITCODE
