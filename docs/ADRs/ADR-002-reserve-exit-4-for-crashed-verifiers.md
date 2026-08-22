# ADR-002: Reserve exit 4 for crashed verifiers

- **Status:** Accepted
- **Source commit(s):** `9c82d22` (fix: crashed verifier exits 4 with a clean message, never mimics a clause failure)
- **Confidence:** HIGH

## Context

`evals/run_eval.py` previously allowed a verifier exception to resemble an ordinary contract-clause failure.

The full commit changes `evals/run_eval.py`, `evals/test_run_eval.py`.

## Decision

Catch verifier crashes separately, print a clean diagnostic, and return exit 4; reserve clause-failure status for a verifier that completed.

## Alternatives evidenced by history

Let exceptions escape with a traceback or map them to the same status as failed clauses.

## Consequences verified in later/current code

`evals/test_run_eval.py` now distinguishes infrastructure failure from product-behavior failure, so CI and operators can route the two differently.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
