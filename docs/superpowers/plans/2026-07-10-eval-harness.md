# Eval Harness + Determinism Audit Implementation Plan (Plan 3 of 5)

> **For agentic workers:** Execute task-by-task with verification between tasks. Worker split: GLM (synclaude) does mechanical scaffolding from exact specs; Fable writes contracts/audit judgment and verifies everything.

**Goal:** Every pipeline skill has a behavior contract (`evals/<skill>/contract.md`) and a deterministic verifier; `python3 evals/run_eval.py <skill> --workspace <dir>` gives a clause-by-clause verdict; the determinism audit classifies each pipeline skill's steps tool-vs-LLM and extracts the mechanical stragglers.

**Architecture:** The eval harness generalizes what already exists — `two-orchestrator-e2e-test/scripts/verify_artifacts.py` has per-skill check functions and the e2e skill proves the isolated-clone pattern. `evals/` adds: one contract per skill (the WHAT), one thin verifier per skill (the CHECK, importing shared checks where verify_artifacts already has them), fixtures for the per-skill tier (Decision 6: no live side effects), and a runner that reports per-clause pass/fail as JSON + human text. Verifiers are the only pass/fail authority (spec, Evaluation Strategy).

**Tech Stack:** Python 3.11+ stdlib, pytest for the harness's own tests. No new deps.

**Spec:** docs/spec/productionalization-v1.md — workstreams 2+3, Decisions 6+7, success criteria 2+3.

**Scope note (Decision 7):** the 8 pipeline behaviors = intake, classify, tailor-resume, resume-export, apply-packet, find-contacts, enrich-contacts, verify-emails, write-outreach — "8" counts resume-export+apply-packet as one prep finish stage; contracts are per-behavior, so 9 contract dirs.

---

## Target structure

```
evals/
  run_eval.py                 runner: --workspace <dir> [--json]; discovers evals/<skill>/verify.py
  common.py                   shared helpers: clause dataclass, workspace resolution, reporting
  fixtures/
    jd-acme-agent-builder.md  fixture JD (synthetic company, no personal data)
    pipeline-fixture.md       minimal Pipeline.md (same shape as e2e T0)
    classification.json       valid .classification.json fixture
    contacts-ledger.md        fixture ledger (synthetic people)
  <skill>/contract.md         numbered clauses: observable end-state a run MUST produce
  <skill>/verify.py           def verify(workspace: Path) -> list[ClauseResult]
  test_run_eval.py            harness self-tests against synthetic workspaces
docs/determinism-audit.md     per-skill step classification (tool vs LLM) + extraction list
```

Contract clause numbering is stable (`<skill>-C1`, `-C2`, …) so eval history is comparable across runs (the loop-engineering metric "verifier pass rate per contract clause").

## Behavior contracts (clause lists — the source of truth GLM formats into contract.md)

- **interview-prep-intake**: C1 role folder exists `workspace/Roles/<Company - Role>/`; C2 `Job Description.md` non-empty inside it; C3 Pipeline row added under Considering (fixture pipeline contains the row); C4 no other role folder created/modified.
- **classify**: C1 `.classification.json` exists in role folder; C2 parses as JSON with `themes` (non-empty array) + `archetype` (string) + `evidence`; C3 every theme is from the vocab in jd-to-ready SKILL.md step 2; C4 file matches the schema verify_artifacts.check_classification enforces.
- **tailor-resume**: C1 resume md exists matching `resume_glob_prefix()` + company; C2 zero content from `Resume Claims To Verify.md` (provenance grep on marker phrases); C3 no `[NUMBER?]`/placeholder leaks; C4 gaps returned when JD demands non-canonical claims (fixture JD includes one deliberate unmatched requirement).
- **resume-export**: C1 PDF exists next to md; C2 one page (PAGES=1 contract line or pypdf-free check via verify_artifacts.check_pdf); C3 no title leak.
- **apply-packet**: C1 `Application Answers.md` exists, every answer traceable to `Application Profile.md` fixture; C2 `.apply-packet.json` valid per verify_artifacts.check_apply_packet; C3 remote dir recorded is a `_test` remote in fixture mode.
- **find-contacts**: C1 `.contacts-ledger.md` exists with scored rows; C2 ledger table parses (columns per find-contacts SKILL.md); C3 no fabricated emails (every email flagged inferred/verified per ledger legend).
- **enrich-contacts**: C1 ledger still parses after enrichment; C2 appended rows marked with activity source; C3 hooks reference real ledger people only.
- **verify-emails**: C1 `Verified Emails.md` exists; C2 each entry has status verified|inferred|flagged; C3 no email invented (every address appears in ledger or is domain-pattern-derived with the inferred tag).
- **write-outreach**: C1 `Cold Outreach.md` exists with two intros; C2 recipients resolve from `Verified Emails.md`; C3 zero placeholder leaks (`[NUMBER?]`, `<user_`, template slot names); C4 never-sent invariant is out of per-skill scope (Gmail is live-tier only — Decision 6).

Per-skill tier runs against a FIXTURE workspace (pre-baked artifacts simulating a completed run) — the verifier judges end-state, not execution. Live execution belongs to the e2e tier (existing skill).

---

### Task 1 (GLM): scaffold + runner + first two verifiers

`evals/common.py` (ClauseResult dataclass: id, description, passed, detail), `evals/run_eval.py` (discovers `evals/<skill>/verify.py`, runs `verify(workspace)`, prints table + `--json`; exit 1 on any clause fail; `--list` lists skills), fixtures (all four files, synthetic data only — the guard test scans evals/), `evals/interview-prep-intake/` + `evals/tailor-resume/` (contract.md from clause lists above + verify.py), `evals/test_run_eval.py` (runner discovers skills; passing workspace → exit 0; broken workspace → exit 1 naming the failed clause; --json parses). Verifiers import shared checks from verify_artifacts where they exist (sys.path bootstrap parents[1] → repo scripts/ + e2e scripts dir).

Acceptance: `python3 evals/run_eval.py --list` shows 2 skills; self-tests green; full suite green; guard green.

### Task 2 (GLM): remaining seven verifier dirs

classify, resume-export, apply-packet, find-contacts, enrich-contacts, verify-emails, write-outreach — same pattern, contracts from the clause lists, fixtures extended as needed (fixture PDF generated via build_resume_pdf on the fixture resume md at eval-fixture-build time, NOT committed as binary).

Acceptance: `--list` shows 9; every verifier runs against its fixture workspace and passes; suite + guard green.

### Task 3 (Fable): determinism audit

`docs/determinism-audit.md`: for each of the 9 behaviors, table of steps → classification (tool-call | LLM-judgment | LLM-that-should-be-tool) with the extraction list. Fable judgment work.

### Task 4 (GLM): extract the audited mechanical helpers

From the audit's extraction list (expected: pipeline row insert/update helper, STAGED marker writer, role-folder namer — final list comes from Task 3). Each: `scripts/<name>.py` + tests, then the owning SKILL.md swaps prose instructions for the tool call.

Acceptance: new helpers' tests green; SKILL.md meaning preserved (Fable reviews); suite + guard green.

### Task 5 (Fable): wire-up + close

Spec's Commands section updated (`run_eval.py` real syntax); Skills.md gains eval mention if touched by Task 4 SKILL edits; independent review (Codex) of the whole range; fixes; done.

## Boundaries

Branch-only; live system untouched; guard green before every commit; no live LinkedIn/Gmail in per-skill tier (Decision 6); verifiers are the only pass/fail authority; GLM output always verified by Fable before commit (git stays with Fable).
