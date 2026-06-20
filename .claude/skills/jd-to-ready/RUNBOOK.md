# jd-to-ready Trace Runbook

Use this runbook when inspecting or repairing `jd-to-ready` trace behavior.

## Find The Logs

Global summary:

```bash
tail -n 20 ~/.claude/logs/jd-to-ready.jsonl
```

Per-role trace:

```bash
ls "Roles/<Company - Role>/.jd-to-ready-trace.jsonl"
```

Fallback trace before a role folder was bound:

```bash
ls ~/.claude/logs/jd-to-ready-runs
```

Active run state:

```bash
ls ~/.claude/logs/jd-to-ready-active.json
```

## Inspect A Run

Show step endings:

```bash
jq -r 'select(.event=="step_end") | [.timestamp,.step,.primitive,.status,.prediction_met,((.gaps//[])|length),(.tokens.total//"tokens?")] | @tsv' \
  "Roles/<Company - Role>/.jd-to-ready-trace.jsonl"
```

Show finish or abort events:

```bash
jq -r 'select(.event=="run_finish" or .event=="run_abort")' \
  "Roles/<Company - Role>/.jd-to-ready-trace.jsonl"
```

Check global summaries:

```bash
jq -r '[.timestamp,.company,.role,.status,((.steps_closed//[])|join(",")),((.gaps//[])|length)] | @tsv' \
  ~/.claude/logs/jd-to-ready.jsonl
```

## Healthy Run Criteria

A production run is healthy when:

- Required steps `1,2,3,4,4b,5,6,7` all have `step_end` events.
- No step is left open.
- The per-role trace and global summary agree on the role folder.
- Every `step_end` has a `tokens` object, even if counts are unknown.
- The final event is `run_finish` with status `ok`.
- Gaps explain real limitations; they are not used to hide missing trace events.

## Diagnosing The McKinsey Failure Mode

Symptoms:

- Global log says `partial`.
- Later line says `run_summary_corrected`.
- Per-role trace has only steps `1`, `2`, and `3`.
- Output files exist for later steps, but no matching `step_end` events exist.

Interpretation:

The artifacts may be useful, but the run is not auditable. Treat corrected
summary lines as historical notes, not as a valid replacement for missing trace
events.

Correct fix:

- Harden `trace_step.py` so `finish-run` cannot close with missing production
  steps.
- Add an explicit abort path for interrupted runs.
- Re-run or manually audit artifacts only after the trace contract is fixed.

## Interrupted Runs

If active state exists and the run is genuinely still in progress, continue from
the open step and close it normally.

If the run cannot continue, use:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py abort-run --reason "<why the run cannot continue>"
```

Do not append fake `step_end` events. The abort event is the audit trail for an
incomplete run.

## What Not To Do

- Do not mark `finish-run --status ok` when required steps are missing.
- Do not append a corrected global summary as the only record of later work.
- Do not omit token fields because the runtime did not expose counts.
- Do not log full JD text, email bodies, or outreach bodies.
- Do not use a root-level role folder path when the real role folder is under
  `Roles/`.

## Regression Fixtures

Use these as validation examples when hardening `trace_step.py`:

- McKinsey fixture: should fail validation because steps `4`, `4b`, `5`, `6`,
  and `7` are missing from the per-role trace.
- Morningstar fixture: should pass as a healthy harness run if marked as a test
  run and if all required harness steps are represented.
