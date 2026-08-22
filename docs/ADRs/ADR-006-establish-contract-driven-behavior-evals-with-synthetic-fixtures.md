# ADR-006: Establish contract-driven behavior evals with synthetic fixtures

- **Status:** Accepted
- **Source commit(s):** `7b4310e` (feat: eval harness scaffold — runner, fixtures, first two behavior verifiers)
- **Confidence:** HIGH

## Context

The evaluation work progressed from two synthetic behavior verifiers to nine contracts and finally trace verification integrated with the runner.

The full commit changes `evals/__init__.py`, `evals/common.py`, `evals/fixtures/classification.json`, `evals/fixtures/contacts-ledger.md`, `evals/fixtures/jd-acme-agent-builder.md`, `evals/fixtures/pipeline-fixture.md`, `evals/interview-prep-intake/contract.md`, `evals/interview-prep-intake/verify.py`, `evals/run_eval.py`, `evals/tailor-resume/contract.md`.

## Decision

Treat contract clauses, synthetic Acme fixtures, verifier exit codes, and behavior-trace checks as the release evidence for the nine pipeline behaviors.

## Alternatives evidenced by history

Rely on pytest implementation tests or manually inspect generated application artifacts without clause-level behavior contracts.

## Consequences verified in later/current code

Current `evals/run_eval.py`, the per-behavior `contract.md`/`verify.py` pairs, and `evals/verify_behavior_traces.py` provide machine-readable failures without touching the live workspace.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
