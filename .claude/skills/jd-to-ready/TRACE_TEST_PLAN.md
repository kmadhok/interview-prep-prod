# jd-to-ready Trace Test Plan

This is the regression plan for hardening `trace_step.py`. The executable tests
live in `scripts/test_trace_step.py`.

## Unit-Level Scenarios

Test the trace helper in a temporary log directory. Do not write to real
`~/.claude/logs` during tests.

Required scenarios:

- Happy path (`--run-type full`): all 11 steps (`1`, `2`, `3`, `3.5`, `3.7`,
  `4`, `4b`, `4c`, `5`, `6`, `7`) open and close in order; `finish-run` writes
  status `ok`.
- Run-type contracts: `required_steps_for("jd-to-ready")` is
  `1, 2, 3, 3.5, 3.7, 6, 7`; `required_steps_for("stage-outreach")` is
  `4, 4b, 4c, 5, 6, 7`; a `stage-outreach` run finishes with only its own
  steps closed.
- Run-type typo guard: `start-run --run-type <unknown>` is rejected at the
  CLI; the function-level fallback to the legacy full list applies only to
  legacy state files.
- Early finish: `finish-run` after step `3` fails because later steps are
  missing.
- Stateless finish/abort: `finish-run` and `abort-run` fail loudly when no
  active run exists.
- Overlapping step: `begin --step 4b` fails while step `4` is open.
- Invalid end: `end --step 4` fails if step `4` was never opened.
- Failed step: a step ending with `status: failed` causes final computed status
  to be `failed`.
- Abort path: `abort-run --reason "<reason>"` records `run_abort`, missing
  steps, open step, and clears active state.
- Token validation: missing `tokens`, malformed token JSON, negative counts,
  and inconsistent totals fail validation.
- Gap validation: `gaps` must parse as a JSON array.
- Produced validation: `produced` must parse as a JSON array.
- Failure pattern validation: values outside the allowed taxonomy fail;
  `pdf-export-defect` and `apply-packet-defect` are accepted.
- Role folder validation: production role folders outside `Roles/` fail.
- Test harness folder validation: non-`Roles/` folders pass only when explicitly
  marked as test runs.
- Session scoping: `check --strict` flags an incomplete run only for the
  session that started it; unstamped legacy runs are flagged by any session.

## Fixture Scenarios

McKinsey fixture:

- Based on run `jdtr-20260607140047-54dd1654`.
- Should fail validation because the per-role trace closed only steps `1`, `2`,
  and `3`.
- Validator should report missing steps `4`, `4b`, `5`, `6`, and `7`.
- A corrected summary line must not make the trace healthy.

Morningstar fixture:

- Based on `_jd-to-ready-test/Morningstar - Product AI Engineer/traces/`.
- Should validate as a healthy harness trace if represented with explicit test
  run metadata and required harness steps.
- Should preserve activity-enrichment provenance and post-enrichment outreach
  target selection.

## Acceptance Criteria

The hardening pass is complete when:

- A missing step cannot be hidden by `finish-run`.
- A run cannot have two open steps.
- A production run cannot finish with a root-level role path when the role lives
  under `Roles/`.
- Every `step_end` has a valid `tokens` object.
- The McKinsey fixture fails for the expected reason.
- The Morningstar fixture passes.
- The runbook commands still work against real traces.
