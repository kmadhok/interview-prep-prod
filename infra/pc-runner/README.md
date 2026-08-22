# Optional PC runner

The PC runner turns the manual two-orchestrator loop into two Windows Task Scheduler
passes. The implementation already lives under `scripts/drip_runner/`; this manifest
declares its schedule and manual equivalents without duplicating executable code.

## Pass definitions

| Pass | Default schedule | Canonical entrypoint | State gate |
| --- | --- | --- | --- |
| Pass A — prep saved jobs | Daily at 05:07 local | `scripts/drip_runner/run.ps1` (default `saved` mode) | Saved job has not already been filed or attempted. |
| Pass B — stage outreach | Hourly | `scripts/drip_runner/run.ps1 -Mode outreach` | Active Pipeline row contains `Applied` and no `STAGED` or outreach-error marker. |

The seven-minute offset keeps the daily startup pull from racing an hourly Pass B
pull. Both definitions use `MultipleInstances IgnoreNew`, run in the logged-in user's
interactive session, and keep LinkedIn calls sequential.

The old “Pass A/Pass B wiring is pending” note in
`scripts/drip_runner/README.md` is historical. The canonical scheduler installer,
`scripts/drip_runner/install-tasks.ps1`, registers `LinkedInDaemon`, `DripRunner`, and
`DripRunnerOutreach`; inspect that script before installation.

## Setup

1. Complete LinkedIn and Gmail onboarding.
2. Clone the repository on the always-on Windows machine and sign Claude Code in.
3. Ensure `python3` or the `py -3` launcher, Git, PowerShell, and `uv` are on the
   interactive user's PATH.
4. From PowerShell, run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\drip_runner\install-tasks.ps1
   ```

5. Inspect the three tasks in Task Scheduler and execute each pass once manually.
6. Confirm each successful run updates `scripts/drip_runner/heartbeat.json`, produces
   no unexpected sent mail, and does not overlap another runner instance.

## Manual equivalents

```powershell
# Pass A: prepare newly saved LinkedIn roles
powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1 -Mode saved

# Pass B: stage outreach for every eligible Applied row
powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1 -Mode outreach

# Optional ATS/email ingestion variant
powershell -ExecutionPolicy Bypass -File scripts\drip_runner\run.ps1 -Mode email
```

Manual mode without the wrapper is documented at
[`docs/onboarding/manual-mode.md`](../../docs/onboarding/manual-mode.md).

## Disable, roll back, or remove

```powershell
Disable-ScheduledTask -TaskName DripRunner
Disable-ScheduledTask -TaskName DripRunnerOutreach

# Remove only after confirming manual mode works.
Unregister-ScheduledTask -TaskName DripRunner -Confirm:$false
Unregister-ScheduledTask -TaskName DripRunnerOutreach -Confirm:$false
```

Do not unregister `LinkedInDaemon` unless another supervisor owns the one permitted
daemon. Disabling schedulers does not alter Pipeline state or delete role artifacts.
