# ADR-012: Make skills share one trace contract

- **Status:** Accepted
- **Source commit(s):** `f596f59` (docs: skills adopt shared trace contract (reason+sources, runs/ layout))
- **Confidence:** HIGH

## Context

The original jd-to-ready trace was skill-local, used a single trace location, and lacked enough provenance for repair reports.

The full commit changes `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/RUNBOOK.md`, `.claude/skills/jd-to-ready/SKILL.md`, `.claude/skills/jd-to-ready/TRACEABILITY.md`, `.claude/skills/jd-to-ready/TRACEABILITY_IMPLEMENTATION_SUMMARY.md`, `.claude/skills/stage-outreach/SKILL.md`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/verify-emails/SKILL.md`.

## Decision

Use repo-level `scripts/trace_step.py`, one `runs/<run-id>/` directory per run, schema-v2 `reason` and `sources` fields, explicit primitive run types, and `scripts/render_run_report.py` for human repair output.

## Alternatives evidenced by history

Keep the skill-local script, overwrite one trace file, or record step names without source/reason provenance.

## Consequences verified in later/current code

Parallel and aborted runs remain separable; abort gaps appear in reports; every participating skill must satisfy the shared schema documented under `docs/trace/`.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
