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

Log "run start (mode=$Mode)"
git pull --rebase
if (-not $?) { Log "git pull failed; aborting run (no claude invocation)"; exit 1 }

$promptFile = if ($Mode -eq 'email') { 'runner-prompt.md' } else { 'runner-prompt-saved.md' }
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
$out = $prompt | claude -p | Out-String
$code = $LASTEXITCODE
Write-Host $out
[System.IO.File]::AppendAllText($log, "---- claude output ----" + [Environment]::NewLine + $out + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
Log "run end (exit $code)"
exit $code
