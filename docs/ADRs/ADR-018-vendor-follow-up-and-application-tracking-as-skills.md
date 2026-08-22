# ADR-018: Vendor follow-up and application tracking as skills

- **Status:** Accepted
- **Source commit(s):** `ac0d929` (feat: vendor follow-up and track-application skills into repo)
- **Confidence:** HIGH

## Context

Relative to `ac0d929^`, commit `ac0d929` changes `.claude/skills/follow-up/SKILL.md`, `.claude/skills/track-application/SKILL.md`; the changed paths and prior state below delimit the decision evidence.

The full commit changes `.claude/skills/follow-up/SKILL.md`, `.claude/skills/track-application/SKILL.md`.

## Decision

Adopt **Vendor follow-up and application tracking as skills** in `.claude/skills/follow-up/SKILL.md`, `.claude/skills/track-application/SKILL.md`.

## Alternatives evidenced by history

continue without `.claude/skills/follow-up/SKILL.md`; continue without `.claude/skills/track-application/SKILL.md`.

## Consequences verified in later/current code

The current tree still carries this contract in `.claude/skills/follow-up/SKILL.md`, `.claude/skills/track-application/SKILL.md`; changing it requires updating the adjacent tests and operator guidance.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
