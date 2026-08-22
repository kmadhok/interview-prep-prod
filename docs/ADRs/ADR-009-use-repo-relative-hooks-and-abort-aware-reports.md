# ADR-009: Use repo-relative hooks and abort-aware reports

- **Status:** Accepted
- **Source commit(s):** `bd6ce3d` (fix: address Codex review — repo-relative hooks, honest standalone finish, abort-aware reports)
- **Confidence:** HIGH

## Context

Relative to `bd6ce3d^`, commit `bd6ce3d` changes `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/verify-emails/SKILL.md`; the changed paths and prior state below delimit the decision evidence.

The full commit changes `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/verify-emails/SKILL.md`, `.claude/skills/write-outreach/SKILL.md`, `scripts/render_run_report.py`.

## Decision

Adopt **Use repo-relative hooks and abort-aware reports** in `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/verify-emails/SKILL.md`.

## Alternatives evidenced by history

retain the parent version of `.claude/skills/enrich-contacts/SKILL.md`; retain the parent version of `.claude/skills/find-contacts/SKILL.md`; retain the parent version of `.claude/skills/interview-prep-intake/SKILL.md`; retain the parent version of `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py`; retain the parent version of `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py`; retain the parent version of `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py`; retain the parent version of `.claude/skills/tailor-resume/SKILL.md`; retain the parent version of `.claude/skills/verify-emails/SKILL.md`; retain the parent version of `.claude/skills/write-outreach/SKILL.md`; retain the parent version of `scripts/render_run_report.py`; retain the parent version of `scripts/test_render_run_report.py`.

## Consequences verified in later/current code

The current tree still carries this contract in `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py`, `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/verify-emails/SKILL.md`; changing it requires updating the adjacent tests and operator guidance.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
