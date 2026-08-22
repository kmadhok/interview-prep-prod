# ADR-005: Cover all nine pipeline behaviors with verifiers

- **Status:** Accepted
- **Source commit(s):** `dea9a58` (feat: behavior verifiers for all nine pipeline behaviors)
- **Confidence:** HIGH

## Context

The evaluation work progressed from two synthetic behavior verifiers to nine contracts and finally trace verification integrated with the runner.

The full commit changes `evals/_ledger.py`, `evals/apply-packet/contract.md`, `evals/apply-packet/verify.py`, `evals/classify/contract.md`, `evals/classify/verify.py`, `evals/enrich-contacts/contract.md`, `evals/enrich-contacts/verify.py`, `evals/find-contacts/contract.md`, `evals/find-contacts/verify.py`, `evals/fixtures/application-profile.md`.

## Decision

Treat contract clauses, synthetic Acme fixtures, verifier exit codes, and behavior-trace checks as the release evidence for the nine pipeline behaviors.

## Alternatives evidenced by history

Rely on pytest implementation tests or manually inspect generated application artifacts without clause-level behavior contracts.

## Consequences verified in later/current code

Current `evals/run_eval.py`, the per-behavior `contract.md`/`verify.py` pairs, and `evals/verify_behavior_traces.py` provide machine-readable failures without touching the live workspace.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
