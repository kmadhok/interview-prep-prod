# ADR-003: Document the actual eval CLI syntax

- **Status:** Accepted
- **Source commit(s):** `41f229d` (docs: spec commands reflect real run_eval syntax)
- **Confidence:** HIGH

## Context

Relative to `41f229d^`, commit `41f229d` changes `docs/spec/productionalization-v1.md`; the changed paths and prior state below delimit the decision evidence.

The full commit changes `docs/spec/productionalization-v1.md`.

## Decision

Adopt **Document the actual eval CLI syntax** in `docs/spec/productionalization-v1.md`.

## Alternatives evidenced by history

retain the parent version of `docs/spec/productionalization-v1.md`.

## Consequences verified in later/current code

The current tree still carries this contract in `docs/spec/productionalization-v1.md`; changing it requires updating the adjacent tests and operator guidance.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
