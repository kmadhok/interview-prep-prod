# ADR-019: Drive social handles from profile configuration

- **Status:** Accepted
- **Source commit(s):** `3b70bf7` (fix: profile-driven social handles in outreach; guard covers handle patterns)
- **Confidence:** HIGH

## Context

Outreach instructions contained literal social handles, defeating de-personalization even after profile-based path work.

The full commit changes `.claude/skills/write-outreach/SKILL.md`, `profile.yaml`, `scripts/test_no_personal_refs.py`.

## Decision

Read handles from flat `profile.yaml` and extend `scripts/test_no_personal_refs.py` to detect handle-shaped leaks.

## Alternatives evidenced by history

Keep handles embedded in skill prose or infer them from the user name.

## Consequences verified in later/current code

Different instances can reuse outreach skills, and the guard fails when template-side files regain personal handles.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
