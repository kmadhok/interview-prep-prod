# ADR-011: Render machine traces into human repair reports

- **Status:** Accepted
- **Source commit(s):** `d971cd9` (feat: run report renderer — trace to human repair manual)
- **Confidence:** HIGH

## Context

The original jd-to-ready trace was skill-local, used a single trace location, and lacked enough provenance for repair reports.

The full commit changes `.gitignore`, `scripts/render_run_report.py`, `scripts/test_render_run_report.py`.

## Decision

Use repo-level `scripts/trace_step.py`, one `runs/<run-id>/` directory per run, schema-v2 `reason` and `sources` fields, explicit primitive run types, and `scripts/render_run_report.py` for human repair output.

## Alternatives evidenced by history

Keep the skill-local script, overwrite one trace file, or record step names without source/reason provenance.

## Consequences verified in later/current code

Parallel and aborted runs remain separable; abort gaps appear in reports; every participating skill must satisfy the shared schema documented under `docs/trace/`.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
