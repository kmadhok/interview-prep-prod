# jd-to-ready Trace Schema

This document defines the trace schema for `jd-to-ready`.

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

`required_steps` defaults to `["1", "2", "3", "3.5", "4", "4b", "4c", "5", "6", "7"]`.

### `role_folder_set`

Required fields:

- `company`
- `role`
- `role_folder`

For active roles, `role_folder` must resolve under the workspace `Roles/`
directory. Test harnesses must mark themselves explicitly as test runs before
using a non-`Roles/` folder.

### `step_begin`

Required fields:

- `step`
- `primitive`
- `mode`
- `prediction`
- `inputs_summary`
- `status`

Rules:

- `status` is always `running`.
- `prediction` is a short, checkable claim.
- Only one step can be open at a time.

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
- `null`
- empty string

Rules:

- `produced` is a JSON array.
- `gaps` is a JSON array.
- `tokens` follows `TOKEN_ACCOUNTING.md`.
- A step can end only if it is the currently open step.

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
