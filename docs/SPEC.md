# interview-prep-prod — spec

_Drafted by push-project on 2026-09-03. Merging this PR approves the spec;
editing the checklist re-prioritizes the work._

## Goal

The productionalized, template/instance-split version of the interview-prep
job-search workspace: a deterministic tool layer, behavior-contract evals, traced
skill runs, and conversational onboarding, with all personal data isolated under
`workspace/`. A friend can clone the template, self-onboard through the interview
skill, run `jd-to-ready` on a real JD, and debug any output by following the trace
from output to skill to prompt to source file.

## Done looks like

- The machine half of `docs/release-gate.md` runs as one command from a clean
  export and exits 0: export, onboard from fixture answers, `verify_setup.py
  --skip-live`, every fixture behavior contract, the trace audit, and
  `python3 -m pytest scripts/`.
- Every user-facing skill (all skills except the three developer/guidance skills
  `linkedin-mcp-operations`, `skill-loop-trainer`, `two-orchestrator-e2e-test`)
  carries the trace block (`start-run` … `finish-run` plus the rendered run
  report), and a test fails when one is missing.
- No template-side file references a home-directory or machine-specific path,
  `AGENTS.md` and `CLAUDE.md` say the same thing, and every `scripts/*.py` path a
  skill mentions resolves in a clean clone; a test enforces all three.
- `scripts/onboard_workspace.py`, `scripts/verify_setup.py`, and
  `scripts/build_fixture_workspace.py` have requirement-driven tests.
- `python3 -m pytest` from the repository root collects and passes.

## Current state

Facts below were measured against commit `b733b0a` (last commit 2026-08-29) in
this run. The brief's constraint that the repo "has been frozen since
2026-08-02" is out of date: six commits landed between 2026-08-18 and
2026-08-29, including the onboard skill, clean export, release gate, infra
manifest, and the two-tier LinkedIn setup.

**Evals (workstream 2) are complete for the pipeline tier.** `evals/` holds 9
`contract.md` / `verify.py` pairs (`apply-packet`, `classify`,
`enrich-contacts`, `find-contacts`, `interview-prep-intake`, `resume-export`,
`tailor-resume`, `verify-emails`, `write-outreach`). `python3
evals/run_eval.py --all` against a fresh fixture evaluates 41 clauses: 37 `PASS`,
4 `BLOCKED` (the live-only LinkedIn, EmailFinder, and Gmail clauses), exit 0.

**Tests.** `python3 -m pytest scripts/` passes (158 tests across 7 test files in
`scripts/` and 9 in `scripts/drip_runner/`). The 2 eval self-test files pass
when run from inside `evals/` (31 passed, 1 skipped) but `python3 -m pytest`
from the repository root aborts at collection: `evals/test_verify_behavior_traces.py`
cannot import `common`. `scripts/test_no_personal_refs.py` passes.

**Trace (workstream 1) covers the pipeline only.** 8 of 19 skill `SKILL.md`
files carry the `trace_step.py` block: `jd-to-ready`, `stage-outreach`, and the
six pipeline primitives (`interview-prep-intake`, `tailor-resume`,
`find-contacts`, `enrich-contacts`, `verify-emails`, `write-outreach`). The 11
others do not; 8 of those are user-facing (`onboard`, `follow-up`,
`track-application`, `linkedin-saved-jobs-intake`, `find-fresh-jobs`,
`recruiter-contact-tracker`, `verify-postings`, `interview-prep-reusables`).
`scripts/trace_step.py` already supports `--run-type primitive --skill <name>`
and `scripts/render_run_report.py` renders the report; the Claude Code hooks in
`.claude/settings.json` append tool telemetry and block silent completion.
`evals/verify_behavior_traces.py` (the cross-behavior trace audit documented in
`docs/trace/TRACE_SCHEMA.md` and `docs/RUNBOOK.md`) cannot run in the machine
gate: the fixture workspace has no `runs/` directory, so the documented command
exits with "runs directory does not exist".

**Deterministic tools (workstream 3).** `scripts/pipeline_row.py` and
`scripts/role_folder.py` (the two "extract now" items in
`docs/determinism-audit.md`) exist, are tested, and are called by the skills.
The audit's deferred items (ledger re-sort helper, runtime classification
validator, Verified Emails writer, outreach linter) remain deferred.

**Infra (workstream 4) is declared.** `infra/` holds 6 files: the launchd plist
template and README, the cloud-routine README and prompt, and the PC-runner
README pointing at `scripts/drip_runner/install-tasks.ps1`; each declares a
manual-invocation equivalent.

**Onboarding and template split (workstream 5) work end to end.** In this run,
`scripts/export_template.py` produced a 153-file clean export with a passing
personal-reference scan; inside that export, `scripts/onboard_workspace.py
--answers evals/fixtures/onboarding-answers.json` wrote `profile.yaml` and the
nine masters, `scripts/verify_setup.py --skip-live` reported 13/13 checks
non-failing (one reportlab warning), the fixture evals passed, and `pytest
scripts/` passed. None of these three scripts has a test of its own.

**Drift a friend would hit.** `AGENTS.md` and `CLAUDE.md` differ in two
places: `AGENTS.md` still says LinkedIn stdio "is forbidden" and that the live
LinkedIn check "must pass", while `CLAUDE.md`, the README, and
`docs/onboarding/linkedin-mcp.md` describe stdio as the default tier and the
check as warn-only. `.claude/skills/stage-outreach/SKILL.md` line 122 and
`.claude/skills/two-orchestrator-e2e-test/SKILL.md` line 96 invoke scripts by a
`~/.claude/skills/...` home-directory path; both scripts actually live in the
repo under `.claude/skills/<skill>/scripts/`, so the documented command fails on
any machine that lacks the author's global skills.

**Not built.** `docs/superpowers/plans/2026-08-20-user-behavior-evaluation-harness.md`
specifies a conversational journey harness that drives a real Claude Code
session against the real LinkedIn and Gmail connectors; the plan states no
harness code exists yet, and none does (`evals/journeys/` is absent). The
repository has no `.project-meta.yaml` builder contract; the two attempts by the
registry's autonomous builder on 2026-08-27 were rejected in review because the
`personal_data` globs were incomplete (the embedded-PII skill bundle those
reviews cited was removed in `b733b0a`). This private repository tracks 959
files under `workspace/` plus root `profile.yaml`; the export, not `.gitignore`,
is what keeps them out of the template.

## Remaining work

- [ ] **Clean-clone consistency guard.** Replace the two `~/.claude/skills/...`
      invocations with `<repo root>/.claude/skills/<skill>/scripts/...`; bring
      `AGENTS.md` back in line with `CLAUDE.md` (LinkedIn tiers, `verify_setup`
      wording); make `python3 -m pytest` collect from the root (an
      `evals/conftest.py` that puts `evals/` on `sys.path`, or the equivalent).
      Add `scripts/test_clean_clone.py`: no template-side file contains
      `~/.claude/skills` or `$HOME/.claude/skills`; `AGENTS.md` equals
      `CLAUDE.md`; every `scripts/<name>.py` path mentioned in any `SKILL.md`
      resolves at the repo root or under that skill's own directory.
- [ ] **Tests for the setup tools.** Requirement-driven tests for
      `scripts/onboard_workspace.py` (writes `profile.yaml` and all nine masters
      from `evals/fixtures/onboarding-answers.json` into a temp root; refuses to
      overwrite an existing file without `--refresh`; rejects non-object
      answers; prints only paths written), `scripts/verify_setup.py --repo-root
      <tmp> --skip-live` (exit 0 on an onboarded temp export; a `FAIL` row when
      a master is still the untouched template or `profile.yaml` lacks a
      required key; `--json` if supported), and
      `scripts/build_fixture_workspace.py` (refuses an existing target without
      `--force`; the rebuilt fixture passes `run_eval.py --all`). Stdlib only, no
      network, never touches the live `workspace/`.
- [ ] **Trace coverage for the eight untraced user-facing skills.** Add the
      primitive trace block (`start-run --run-type primitive --skill <name>`,
      `begin`/`end --step main`, `finish-run`, `render_run_report.py`) to
      `onboard`, `follow-up`, `track-application`, `linkedin-saved-jobs-intake`,
      `find-fresh-jobs`, `recruiter-contact-tracker`, `verify-postings`, and
      `interview-prep-reusables`, with each skill's real canonical inputs as
      `--sources`. `onboard` runs before `workspace/` exists, so confirm
      `trace_step.py` accepts a run with no role folder for it (or extend it).
      Add `scripts/test_skill_trace_coverage.py`: every user-facing `SKILL.md`
      contains `start-run`, `finish-run`, and `render_run_report.py`; plus a
      `trace_step.py` happy path for a non-pipeline skill name.
- [ ] **Trace audit in the machine gate.** `scripts/build_fixture_workspace.py`
      emits one closed synthetic primitive trace per audited behavior into
      `<fixture>/runs/` through `trace_step.py`, so `python3
      evals/verify_behavior_traces.py --runs-dir <fixture>/runs` exits 0 on a
      fresh fixture; `verify_setup.py`'s fixture check and step 4 of
      `docs/release-gate.md` run the audit. Tests: the audit passes on the
      fixture; a fixture missing one behavior's trace fails it; `TRACE_SCHEMA.md`
      and `RUNBOOK.md` commands match the real invocation.
- [ ] **Release gate as one command.** `scripts/release_gate.py` runs machine
      steps 1–4 of `docs/release-gate.md` end to end (export to a temp dir, git
      init/commit/clone, onboard from fixture answers, `verify_setup.py
      --skip-live`, `run_eval.py --all` plain and `--json`, the trace audit,
      `pytest scripts/`), prints one PASS/FAIL table, exits non-zero on the
      first failure, and never touches the live `workspace/`. Step 5 (LinkedIn
      registration) stays a documented human step. `docs/release-gate.md` and
      the README point at the script. Tests: a passing run against this repo;
      a seeded failure (a template file with a forbidden reference) is reported
      with the failing step named.

## Non-goals

- No token or internal-reasoning capture; traces record actions and reasons.
- No non-Claude harness support beyond keeping logic in portable markdown and
  scripts.
- No public GitHub release or history rewrite; publishing is a later
  clean-history export of the template.
- No changes to the live interview-prep instance on its main branch.
- No automated sending; every outward action keeps a human gate.
- No state database; state is read from files that already exist.
- No new runtime dependencies without owner approval (reportlab stays the one
  exception).
- The conversational journey harness in
  `docs/superpowers/plans/2026-08-20-user-behavior-evaluation-harness.md` is
  out of scope for this checklist: it needs a live Claude Code session, the real
  LinkedIn daemon, and the real Gmail connector, which no unattended run can
  verify. It stays owner-run.
- The `.project-meta.yaml` builder contract is the registry builder's
  `bootstrap_contract` chunk, not this roadmap.
- The determinism audit's deferred extractions stay deferred until eval history
  shows drift, per `docs/determinism-audit.md`.
