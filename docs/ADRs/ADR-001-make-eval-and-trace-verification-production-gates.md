# ADR-001: Make eval and trace verification production gates

- **Status:** Accepted
- **Source commit(s):** `b76d952` (feat: productionalize eval and trace verification)
- **Confidence:** HIGH

## Context

The evaluation work progressed from two synthetic behavior verifiers to nine contracts and finally trace verification integrated with the runner.

The full commit changes `.claude/skills/enrich-contacts/SKILL.md`, `.claude/skills/find-contacts/SKILL.md`, `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/jd-to-ready/SKILL.md`, `.claude/skills/stage-outreach/SKILL.md`, `.claude/skills/tailor-resume/SKILL.md`, `.claude/skills/two-orchestrator-e2e-test/SKILL.md`, `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`, `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`, `.claude/skills/verify-emails/SKILL.md`.

## Decision

Treat contract clauses, synthetic Acme fixtures, verifier exit codes, and behavior-trace checks as the release evidence for the nine pipeline behaviors.

## Alternatives evidenced by history

Rely on pytest implementation tests or manually inspect generated application artifacts without clause-level behavior contracts.

## Consequences verified in later/current code

Current `evals/run_eval.py`, the per-behavior `contract.md`/`verify.py` pairs, and `evals/verify_behavior_traces.py` provide machine-readable failures without touching the live workspace.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
