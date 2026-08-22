# ADR-007: Classify deterministic versus LLM responsibilities

- **Status:** Accepted
- **Source commit(s):** `bbce9ee` (docs: determinism audit — tool/LLM classification + extraction list (plan 3 task 3))
- **Confidence:** HIGH

## Context

Relative to `bbce9ee^`, commit `bbce9ee` changes `docs/determinism-audit.md`; the changed paths and prior state below delimit the decision evidence.

The full commit changes `docs/determinism-audit.md`.

## Decision

Adopt **Classify deterministic versus LLM responsibilities** in `docs/determinism-audit.md`.

## Alternatives evidenced by history

continue without `docs/determinism-audit.md`.

## Consequences verified in later/current code

The current tree still carries this contract in `docs/determinism-audit.md`; changing it requires updating the adjacent tests and operator guidance.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
