# ADR-013: Require reason and sources on trace steps

- **Status:** Accepted
- **Source commit(s):** `00cbe8d` (feat: trace schema v2 — reason+sources on steps, primitive run-type)
- **Confidence:** HIGH

## Context

The original jd-to-ready trace was skill-local, used a single trace location, and lacked enough provenance for repair reports.

The full commit changes `scripts/drip_runner/test_lifecycle_integration.py`, `scripts/test_trace_step.py`, `scripts/trace_step.py`.

## Decision

Use repo-level `scripts/trace_step.py`, one `runs/<run-id>/` directory per run, schema-v2 `reason` and `sources` fields, explicit primitive run types, and `scripts/render_run_report.py` for human repair output.

## Alternatives evidenced by history

Keep the skill-local script, overwrite one trace file, or record step names without source/reason provenance.

## Consequences verified in later/current code

Parallel and aborted runs remain separable; abort gaps appear in reports; every participating skill must satisfy the shared schema documented under `docs/trace/`.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
