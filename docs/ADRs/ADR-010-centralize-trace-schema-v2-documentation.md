# ADR-010: Centralize trace schema v2 documentation

- **Status:** Accepted
- **Source commit(s):** `4a73caf` (docs: trace schema v2 docs at docs/trace/, smoke-verified end to end)
- **Confidence:** HIGH

## Context

The original jd-to-ready trace was skill-local, used a single trace location, and lacked enough provenance for repair reports.

The full commit changes `.claude/skills/jd-to-ready/TRACEABILITY.md`, `.claude/skills/jd-to-ready/TRACEABILITY_IMPLEMENTATION_SUMMARY.md`, `AGENTS.md`, `CLAUDE.md`, `docs/trace/TOKEN_ACCOUNTING.md`, `docs/trace/TRACE_SCHEMA.md`.

## Decision

Use repo-level `scripts/trace_step.py`, one `runs/<run-id>/` directory per run, schema-v2 `reason` and `sources` fields, explicit primitive run types, and `scripts/render_run_report.py` for human repair output.

## Alternatives evidenced by history

Keep the skill-local script, overwrite one trace file, or record step names without source/reason provenance.

## Consequences verified in later/current code

Parallel and aborted runs remain separable; abort gaps appear in reports; every participating skill must satisfy the shared schema documented under `docs/trace/`.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
