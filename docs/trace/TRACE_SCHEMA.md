# Trace Schema (v3 — behavior contracts)

This document defines the trace schema for every orchestrator and primitive
skill run. The helper is `scripts/trace_step.py` at the repo root; traces live
at `runs/<run-id>/trace.jsonl`, the active state at `runs/.active-run.json`,
and the per-run summary at `runs/summary.jsonl`. `TRACE_RUNS_DIR` overrides
the runs location for tests and harnesses. After `finish-run`, render the
human report with `scripts/render_run_report.py <run-dir>`.

The helper writes JSONL events and enforces the state transitions below for
production runs.

## Common Fields

Every event should include:

| Field | Type | Notes |
|---|---|---|
| `event` | string | Event type |
| `run_id` | string | Stable run identifier |
| `timestamp` | string | ISO 8601 timestamp |
| `seq` | integer | Monotonic sequence number within the run |
| `role_folder` | string or null | Absolute role folder once known |

`seq` starts at `1` for `run_start` and increments by one for each event written
to that run's trace.

## Event Types

### `run_start`

Required fields:

- `company`
- `role`
- `required_steps`
- `source`
- `skill` — the skill this run belongs to (for `--run-type primitive` it is the
  required `--skill` value; for orchestrator run-types it defaults to the
  run-type string)
- `schema_version` — `3` for new runs. v1/v2 traces lack contract fields and
  remain readable.

`required_steps` is set per `--run-type` at `start-run` (see the `RUN_TYPES`
map in `trace_step.py`). The CLI default is `jd-to-ready` →
`["1", "2", "3", "3.5", "3.7", "6", "7"]`; `stage-outreach` →
`["4", "4b", "4c", "5", "6", "7"]`; `primitive` → `["main"]` (a standalone
run of a single primitive skill — requires `--skill`). The full 11-step list
(`["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]`) is the
legacy `full` contract, kept for old state files and the combined test
harness. Unknown run-type strings are rejected at the CLI.

### `role_folder_set`

Required fields:

- `company`
- `role`
- `role_folder`

For active roles, `role_folder` must resolve under the workspace `Roles/`
directory. The role folder is metadata on events — the trace itself always
lives in the run directory, never in the role folder. Test harnesses must mark themselves explicitly as test runs before
using a non-`Roles/` folder.

### `step_begin`

Required fields:

- `step`
- `primitive`
- `mode`
- `prediction`
- `inputs_summary`
- `status`
- `reason` — one line: why this step is running now (v2, mandatory)
- `sources` — JSON array of the files whose content shapes this step's output
  (the skill prompt plus static inputs). This is the debuggability chain: a
  user walks from a bad output to the file to edit via this field. Never omit
  or pad it (v2, mandatory)
- `contract_clauses` — JSON array of clause IDs from the authoritative
  `evals/<behavior>/contract.md`; `[]` preserves old callers.

Rules:

- `status` is always `running`.
- `prediction` is a short, checkable claim.
- Only one step can be open at a time.
- `reason` must be non-empty; `sources` must be a JSON array of strings
  (may be `[]` only when the step genuinely reads no files).

### `step_end`

Required fields:

- `step`
- `primitive`
- `mode`
- `status`
- `prediction_met`
- `produced`
- `gaps`
- `failure_pattern`
- `tokens`
- `clause_results` — verifier-produced objects with `id`, `status`, and
  optional `detail`. Status is `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Allowed `status` values:

- `ok`
- `partial`
- `failed`
- `skipped`

Allowed `prediction_met` values:

- `true`
- `false`
- `partial`
- `unknown`

Allowed `failure_pattern` values:

- `generic-resume-language`
- `verify-placeholder-leak`
- `non-decision-maker-contact`
- `low-confidence-emails`
- `fabricated-hook`
- `thin-jd-stub`
- `theme-unmatched`
- `thin-results`
- `pdf-export-defect`
- `apply-packet-defect`
- `null`
- empty string

Rules:

- `produced` is a JSON array.
- `gaps` is a JSON array.
- `tokens` follows `TOKEN_ACCOUNTING.md`.
- A step can end only if it is the currently open step.
- Clause result IDs must have been declared by `step_begin`, be unique, and
  use the registered statuses.
- When clause results are provided, `prediction_met` is validated: all PASS →
  `true`; any FAIL → `false`; PASS mixed with BLOCKED/NOT_RUN → `partial`;
  only BLOCKED/NOT_RUN → `unknown`.
- Live-only clauses are BLOCKED/NOT_RUN when their service is unavailable;
  they must never be emitted as PASS without verifier evidence.

### `tool_event`

Required fields:

- `tool_name`
- `status`
- `summary`

`summary` must be compact. It can include a command name, path, search pattern,
or high-level action. It must not include full private content.

### `subagent_event`

Required fields:

- `agent_name`
- `status`
- `summary`

Use this for subagent completion telemetry. The parent step still owns the
decision and token accounting.

### `run_finish`

Required fields:

- `status`
- `steps_closed`
- `required_steps`
- `gaps`
- `files_written`
- `steps`

Rules:

- `finish-run` computes `status`.
- `ok` requires all required steps closed and no failed steps.
- `partial` is not caller-selected for normal production runs.
- Missing steps make `finish-run` fail unless the run is explicitly aborted.

### `run_abort`

Required fields:

- `reason`
- `open_step`
- `missing_steps`
- `steps_closed`
- `gaps`

Use `run_abort` only when a run cannot continue. It is the deterministic
replacement for manually appending a corrected summary after the fact.

## State Machine

State fields:

- `run_id`
- `company`
- `role`
- `role_folder`
- `started_at`
- `required_steps`
- `current_step`
- `closed_steps`
- `next_seq`
- `is_test_run`

State transition rules:

- `start-run` creates state and writes `run_start`.
- `set-role-folder` updates state and writes `role_folder_set`.
- `begin` requires no `current_step`.
- `end` requires `current_step == step`.
- Successful `end` clears `current_step` and appends to `closed_steps`.
- `finish-run` requires `current_step == null`.
- `finish-run` requires every required step in `closed_steps`.
- `abort-run` records incomplete state and clears active state.

## Gap Kind Registry

`gaps[]` entries are `{source, kind, detail}` objects. `kind` is documented
here but NOT enforced by the validator (unlike `failure_pattern`) — new kinds
may appear, but prefer reusing one of these before inventing another:

| Kind | Meaning |
|---|---|
| `pdf-overflow` | PDF exceeded one page; a bullet needs trimming |
| `pdf-formatting-defect` | Visual defect in the rendered PDF (title leak, wrapping dates, layout) |
| `export-unavailable` | PDF export could not run (reportlab missing, render failed) |
| `export-quality-unknown` | Export contract or vision verify could not be evaluated |
| `posted-date-unknown` | No canonical ATS posting date found; LinkedIn relative date not trusted |
| `repost-detected` | Deterministic repost check matched an existing role folder |
| `upload-failed` | Apply-packet upload to Drive failed; hourly reconcile will retry |
| `memory-noop` | Session memory file update skipped (expected on PC drip-runner runs) |
| `no-canonical-match` | JD requirement has no matching canonical achievement; not claimed |
| `needs-stronger-claim` | JD bar exceeds what canonical material supports; flagged, not invented |
| `hard-gate` | JD blocker surfaced (citizenship, clearance, RTO, travel, location) |

## Healthy Trace Checklist

- One `run_start`.
- One `role_folder_set`.
- Required steps all have exactly one `step_begin` and one `step_end`.
- No `step_end` appears before its matching `step_begin`.
- No overlapping open steps.
- `seq` values are continuous.
- Every `step_end` includes `tokens`.
- `run_finish.status` is `ok`.
- Global summary and per-role trace agree on `role_folder`, `steps_closed`, and
  `files_written`.

## Cross-behavior audit

After local artifact evaluation, verify that all nine authoritative behaviors
have one closed primitive trace:

```
python3 evals/run_eval.py --all --workspace "<fixture-workspace>"
python3 evals/verify_behavior_traces.py --runs-dir "<fixture-workspace>/runs"
```

The trace audit validates exact contract IDs/results, lifecycle closure, and
derived `prediction_met`. `BLOCKED` and `NOT_RUN` are legal tracked outcomes;
missing traces or malformed local evidence fail the audit.
