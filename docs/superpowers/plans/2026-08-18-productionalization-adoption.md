# Implementation Plan: Productionalization — Adoption Surface

Upstream: [docs/spec/productionalization-v1.md](../../spec/productionalization-v1.md) (workstreams 4–5; workstreams 1–3 are done on `main`)
Assessment: `.lavish/productionalization-assessment.html` (2026-08-17 readout)
Date: 2026-08-18
Implementer: Opus (Claude Code). Each task is a single focused session.

## Overview

The engine (skills, trace, behavior evals, deterministic tools) is built. This plan
covers everything between "engine" and "a friend can clone, onboard, and run it
without Kanu": onboarding, setup verification, templates, portability, infra
manifest, packaging, and the release checklist. Tasks are ordered so the system is
in a working state after every task, and so onboarding — the critical path — lands
first and defines what everything downstream must support.

## Ground rules for the implementer

- **Testing philosophy: evals are behavior tests.** The verification command for
  product behavior is `python3 evals/run_eval.py …` (stdlib-only). Never gate any
  task, install step, or release criterion on pytest. The `scripts/test_*.py` files
  are optional dev-side self-tests of deterministic helpers; you may run them if
  pytest happens to be available, but nothing depends on it.
- **Stdlib-first.** No new runtime dependencies without asking. reportlab (PDF
  export) remains the sole existing exception and must stay optional/graceful.
- **Guard-scanned dirs** (`scripts/`, `.claude/skills/`, `templates/`, `evals/`,
  `infra/`, `docs/onboarding/`) must contain zero personal references. Run
  `python3 scripts/test_no_personal_refs.py` after every task that touches them
  (Task 6 gives it a `__main__`; until then run the check logic via
  `python3 -c` or wait for Task 6 — but never introduce new violations).
- **Don't touch `workspace/`** (Kanu's live instance) or `workspace/Pipeline.md`
  except where a task explicitly says so (none do). Never write `STAGED` markers.
- Skills are specified by **end-state behavior**, not implementation. When you add
  or change a skill, the deliverable includes its behavior being checkable.
- Match existing patterns: `scripts/config.py` for profile access,
  `evals/common.py` for clause results, existing SKILL.md structure for skills.

## Architecture decisions (made in planning; don't relitigate)

- `verify_setup.py` is a thin orchestration of checks that already exist
  conceptually: profile parse, workspace completeness, connector reachability,
  then the fixture eval run. It does not invent a second verification system.
- A canonical fixture workspace becomes buildable by one deterministic script, so
  "run the evals" is a two-command story for a stranger (build fixture → run_eval).
- Infra is **manual-mode-first**: the only *required* infrastructure for the
  friend test is the LinkedIn MCP daemon (spec decision 2). Cloud routine and PC
  runner are documented-optional (spec decision 3).
- Bare first-name references ("Kanu") in guard-scanned dirs are instance
  assumptions and get swept; the guard is extended to keep them out.

---

## Phase 1 — One-command behavior verification

### Task 1: Fixture workspace builder

**Description:** A deterministic script assembles a synthetic workspace from
`evals/fixtures/` so `run_eval.py --all` has a canonical, documented target.
Today only the dev-side tests know how to build one (see
`_build_good_intake_workspace` in `evals/test_run_eval.py` and the fixture files
`jd-acme-agent-builder.md`, `classification.json`, `contacts-ledger.md`,
`application-profile.md`, `pipeline-fixture.md`). Reuse those fixtures; the
builder lays them out as a real workspace (Roles/ folder, Pipeline.md, role
artifacts) satisfying every skill's contract inputs. Read each
`evals/<skill>/contract.md` first to learn what end-state each verifier expects.

**Acceptance criteria:**
- [ ] `python3 scripts/build_fixture_workspace.py <dir>` creates a fresh fixture
      workspace (refuses to overwrite a non-empty dir without `--force`).
- [ ] `python3 evals/run_eval.py --all --workspace <dir>` exits 0 — every local
      clause PASS, live clauses BLOCKED as designed.
- [ ] Content is fully synthetic (Acme people/data), guard-clean.

**Verification:**
- [ ] The two commands above, run back-to-back from a clean checkout.
- [ ] `python3 evals/run_eval.py --all --workspace <dir> --json` parses as JSON.

**Dependencies:** None.
**Files likely touched:** `scripts/build_fixture_workspace.py` (new),
possibly additions under `evals/fixtures/`.
**Estimated scope:** M (1 new script, careful contract reading).

### Task 2: Complete the template set

**Description:** `templates/` has six starters + `profile.yaml`; the live system
uses nine canonical masters. Add blank starters for the three missing:
`AI Build Walkthrough - Master.md`, `Demo Portfolio.md`,
`Resume Claims To Verify.md`. Mirror the section structure of the live
`workspace/` counterparts (read them for headings/scaffold only — copy zero
content). Include the same kind of inline guidance comments the existing
starters use.

**Acceptance criteria:**
- [ ] All nine masters + `profile.yaml` exist in `templates/`.
- [ ] Each new starter's heading skeleton matches its workspace counterpart.
- [ ] Guard stays green (no personal content copied).

**Verification:**
- [ ] `ls templates/` shows all ten files.
- [ ] Personal-refs guard passes over `templates/`.

**Dependencies:** None.
**Files likely touched:** 3 new files under `templates/`.
**Estimated scope:** S.

### Task 3: `scripts/verify_setup.py`

**Description:** The deterministic post-onboarding check named in the spec's
Commands section. Stdlib-only. Checks, in order, printing a PASS/WARN/FAIL/SKIP
table in the style of `run_eval.py`'s output:
1. `profile.yaml` parses via `scripts/config.py` and contains every key the
   template `templates/profile.yaml` declares.
2. `workspace/` exists and contains each canonical master; each differs from its
   `templates/` starter (i.e., has actually been filled in). Missing/blank → FAIL
   naming the file.
3. reportlab importable → PASS; not importable → WARN with the message that PDF
   export will degrade gracefully (never FAIL).
4. LinkedIn MCP daemon reachable on its configured endpoint (default
   `http://127.0.0.1:8765/mcp`; endpoint overridable via a profile key with that
   default) → PASS; unreachable → FAIL with a pointer to
   `docs/onboarding/linkedin-mcp.md` (it is required per spec decision 2). Offer
   `--skip-live` to downgrade to SKIP for machine-only validation.
5. Fixture eval: build a fixture workspace in a temp dir (Task 1 script) and run
   `run_eval.py --all` against it; report its exit status as one summary row.

Exit 0 iff no FAIL rows.

**Acceptance criteria:**
- [ ] `python3 scripts/verify_setup.py` on Kanu's live repo exits 0 (his instance
      is the reference proof).
- [ ] Each failure mode above produces a FAIL row naming the file/fix, verified
      against synthetic broken setups in a temp dir (use `--repo-root` or
      equivalent injection so checks are testable without touching the live repo).
- [ ] `--skip-live` runs with the LinkedIn check as SKIP.

**Verification:**
- [ ] Run on the live repo (expect 0) and on a temp dir missing a master
      (expect 1 naming that master).

**Dependencies:** Tasks 1, 2.
**Files likely touched:** `scripts/verify_setup.py` (new).
**Estimated scope:** M.

### Checkpoint: Phase 1
- [ ] From a clean checkout: build fixture → `run_eval.py --all` → exit 0.
- [ ] `verify_setup.py` exits 0 on the live repo, correct FAILs on broken setups.
- [ ] Guard green. Nothing under `workspace/` modified (`git status`).

---

## Phase 2 — Onboarding

### Task 4: Connector setup docs (`docs/onboarding/`)

**Description:** The reproducible connector guides onboarding will link to.
Source the knowledge from `Automation Architecture - *.md`, the
`linkedin-mcp-operations` skill, and CLAUDE.md — rewritten second-person,
zero personal references (this dir is guard-scanned). Three docs:
- `docs/onboarding/linkedin-mcp.md` — REQUIRED connector. Install, launchd
  supervision (plist template lives in `infra/launchd/`, Task 7 — reference the
  path now), the http-transport invariant and why stdio is forbidden, health
  check, the kickstart recovery command, and how `verify_setup.py` checks it.
- `docs/onboarding/gmail.md` — claude.ai Gmail connector authorization, the
  draft-never-send safety model, what staging drafts looks like.
- `docs/onboarding/manual-mode.md` — how to run the whole system by hand with no
  schedulers: the save→`jd-to-ready`→apply→`stage-outreach` loop as explicit
  commands/skill invocations, per spec decision 3.

**Acceptance criteria:**
- [ ] Three docs exist; each is followable without access to Kanu's machine
      (no absolute personal paths, no personal handles).
- [ ] The LinkedIn doc preserves the http-transport invariant and never instructs
      starting the daemon by hand when launchd owns it.
- [ ] Guard green over `docs/onboarding/`.

**Verification:**
- [ ] Personal-refs guard passes.
- [ ] Cross-references (file paths, commands) all resolve in-repo.

**Dependencies:** None (parallel-safe with Phase 1).
**Files likely touched:** 3 new docs.
**Estimated scope:** M (mostly consolidation).

### Task 5: `/onboard` skill

**Description:** `.claude/skills/onboard/SKILL.md` — the conversational
interview that creates a new user's instance. CLAUDE.md already promises this
skill exists; this task makes that true. Behavior contract (end-state):
1. `profile.yaml` written at repo root from `templates/profile.yaml`, every key
   filled from interview answers.
2. `workspace/` created; all nine masters copied from `templates/` and the core
   evidence set filled through interview: Resume Achievements Master (from the
   user's resume/history — real achievements only, `[NUMBER?]` placeholders when
   a number is unknown, never invented), Master Story Bank (seeded from those
   achievements), Tell Me About Yourself - Master (spine + closest archetype),
   Job Search Target Profile, Application Profile. The remaining masters may
   start as copied starters with a follow-up note.
3. Connector setup walked via the Task 4 docs (LinkedIn required, Gmail for
   outreach staging).
4. Finishes by running `python3 scripts/verify_setup.py` and reporting the table.

Re-running on an existing instance must detect it and offer refresh per-file,
never silent overwrite. The skill must be written for *any* user (no Kanu
references — guard-scanned dir).

**Acceptance criteria:**
- [ ] SKILL.md defines the interview flow, the end-state contract above, the
      no-invention rule, and idempotent re-run behavior.
- [ ] Dry-run proof: executing the skill's mechanical steps against a temp clone
      (scripted answers) yields a workspace where `verify_setup.py --skip-live`
      exits 0.
- [ ] Guard green.

**Verification:**
- [ ] Temp-clone dry run as above; live repo untouched (`git status`).

**Dependencies:** Tasks 2, 3, 4.
**Files likely touched:** `.claude/skills/onboard/SKILL.md` (new), possibly a
small `scripts/` helper for the copy/refresh mechanics if a step is mechanical
(determinism-first rule).
**Estimated scope:** M.

### Checkpoint: Phase 2
- [ ] Fresh temp clone → `/onboard` mechanical path → `verify_setup.py --skip-live`
      exit 0 → fixture eval green. This is the machine half of the friend test.
- [ ] Human review of the interview script's tone/questions before Phase 3.

---

## Phase 3 — Portability and infra manifest

### Task 6: Extend the personal-refs guard + first-name sweep

**Description:** The guard (`scripts/test_no_personal_refs.py`) is green today,
but ~20 files in `.claude/skills/` and `scripts/drip_runner/` still say "Kanu"
bare — instance assumptions the patterns don't catch. Three changes:
1. Add `re.compile(r"\bKanu\b")` and `re.compile(r"\bMadhok\b")` to `FORBIDDEN`.
2. Add a `__main__` block so `python3 scripts/test_no_personal_refs.py` runs
   standalone, prints violations, exits 1 on any — no pytest needed (keep the
   `test_` function so it still collects as a dev-side self-test).
3. Sweep every violation the extended guard finds: rephrase to "the user" or
   route through `profile.yaml` (`load_profile()["user_name"]`) where a real
   name is needed at run time. In SKILL.md trigger descriptions, "Kanu shares a
   JD" → "the user shares a JD", etc. Do not change skill behavior — wording and
   config-routing only.

**Acceptance criteria:**
- [ ] `python3 scripts/test_no_personal_refs.py` exits 0 with the new patterns.
- [ ] No behavior change: fixture eval still green.
- [ ] Skill trigger descriptions still read naturally (spot-check 3).

**Verification:**
- [ ] Guard standalone run; `run_eval.py --all` against a fixture workspace.

**Dependencies:** Task 1 (for the regression check).
**Files likely touched:** the guard + ~20 files under `.claude/skills/` and
`scripts/drip_runner/`. Mechanical but wide — keep to wording/config edits only.
**Estimated scope:** M.

### Task 7: `infra/` manifest

**Description:** Declare the three undeclared systems in-repo (spec workstream 4),
manual-mode-first:
- `infra/launchd/` — `com.<user>.linkedin-mcp` plist **template** (placeholders,
  not Kanu's live plist) + setup/health/rollback/teardown doc. This is the one
  *required* piece (backs Task 4's LinkedIn doc).
- `infra/cloud-routines/` — the Gmail-secretary routine: what it does, its
  prompt/cron shape, how to set up your own, and the manual equivalent.
  Documented-optional.
- `infra/pc-runner/` — Pass A/B scheduler definitions + setup doc, and the
  manual equivalent of each pass. Documented-optional. Resolve or explicitly
  mark-historical any "pending wiring" claims copied from the architecture docs.
- `infra/README.md` — one page: what's required (LinkedIn daemon) vs optional
  (everything else), and the manual-mode pointer.

Source from `Automation Architecture - *.md` and `scripts/drip_runner/` docs;
consolidate, don't duplicate — the root architecture docs can then point here.
Guard-scanned: zero personal references.

**Acceptance criteria:**
- [ ] The four items above exist; required-vs-optional is unambiguous.
- [ ] Every scheduled behavior has a documented manual invocation.
- [ ] Guard green over `infra/`.

**Verification:**
- [ ] Guard standalone run; in-repo cross-references resolve.

**Dependencies:** Task 4 (shared LinkedIn content — keep one canonical, one pointer).
**Files likely touched:** ~6 new files under `infra/`.
**Estimated scope:** M (consolidation-heavy, little code).

### Checkpoint: Phase 3
- [ ] Extended guard green repo-wide over scanned dirs.
- [ ] Fixture eval green. `workspace/` untouched.

---

## Phase 4 — Packaging and release readiness

### Task 8: Root `README.md` + `LICENSE`

**Description:** The stranger-facing front door. Contents: what the product is
(one paragraph, human-gated job-search system — draft-never-send up front);
requirements (Claude Code, Python ≥3.11 stdlib, optional reportlab for PDF,
Gmail connector, LinkedIn MCP required); quick start (clone → `/onboard` →
`python3 scripts/verify_setup.py`); the test story
(`python3 scripts/build_fixture_workspace.py <dir> && python3 evals/run_eval.py
--all --workspace <dir>` — evals are behavior tests; pytest is not part of the
product); repo map (template vs `workspace/` instance); safety model (apply
gate, draft-never-send, no state database); troubleshooting pointers
(`docs/onboarding/`, `infra/`); trace-as-repair-manual pointer
(`docs/trace/TRACE_SCHEMA.md`). License: MIT unless Kanu says otherwise
(**open question 3**).

**Acceptance criteria:**
- [ ] Every command in the README executes as written from a clean checkout.
- [ ] No personal references in README (it ships in the export).

**Verification:**
- [ ] Execute each quick-start/test command verbatim.

**Dependencies:** Tasks 3, 5 (commands must exist before being documented).
**Files likely touched:** `README.md`, `LICENSE` (new).
**Estimated scope:** S.

### Task 9: Clean-export tooling

**Description:** Per spec decision 1: public release is a clean-history export
to a fresh repo — no rewrite of this repo. Build
`scripts/export_template.py`: copies the template surface (guard's
`TEMPLATE_DIRS` + root `README.md`, `LICENSE`, `AGENTS.md`/`CLAUDE.md`,
`Skills.md`, `templates/`, `.gitignore`) into a target dir, **excluding**
`workspace/`, root `profile.yaml` (ships the blank template only), `.lavish/`,
`runs/`, `.obsidian/`, `docs/intent|spec|superpowers`, and the root
`Automation Architecture`/personal `.md` files; writes a `.gitignore` that
ignores `workspace/` and `profile.yaml` by default; then runs the guard's
FORBIDDEN patterns over the **entire** export tree (not just scanned dirs) and
exits 1 listing any hit. It does not create the GitHub repo or push — that
stays human.

**Acceptance criteria:**
- [ ] `python3 scripts/export_template.py <dir>` produces a tree with zero
      personal references (full-tree scan green) and no `workspace/` content.
- [ ] In the export: `git init` + fixture build + `run_eval.py --all` green;
      `verify_setup.py` fails cleanly with the "run /onboard" message (no
      profile yet — that's correct behavior).
- [ ] AGENTS.md/CLAUDE.md as exported make sense for a new user (if they don't,
      flag for a follow-up rather than rewriting them silently).

**Verification:**
- [ ] Run the export to a temp dir and execute the checks above.

**Dependencies:** Tasks 6, 7, 8.
**Files likely touched:** `scripts/export_template.py` (new).
**Estimated scope:** M.

### Task 10: Release-gate checklist (doc only — humans execute)

**Description:** Write `docs/release-gate.md` capturing the two five-step
checklists from the assessment (machine validation: clean clone → install →
onboard + `verify_setup` → fixture evals → live LinkedIn handshake; human
validation: real JD through `jd-to-ready` → manual apply → `stage-outreach` →
drafts-exist-nothing-sent → trace a disliked output to its source and fix it),
each step with the exact command and expected result. This is the friend-test
script; Opus writes it, Kanu and the friend run it.

**Acceptance criteria:**
- [ ] Every step names its command and observable pass condition.
- [ ] No step requires undocumented knowledge (each references a doc in-repo).

**Verification:** Human review.
**Dependencies:** Tasks 8, 9.
**Files likely touched:** `docs/release-gate.md` (new).
**Estimated scope:** S.

### Checkpoint: Complete
- [ ] Export dry-run clean; README commands all execute; release-gate doc ready.
- [ ] Hand to Kanu for the clean-machine run and the friend test.

---

## Parallelization

- Safe in parallel: Task 2 ∥ Task 1; Task 4 ∥ Phase 1; Task 8 drafting ∥ Task 7.
- Sequential: 1→3→5 (fixture → verify_setup → onboard), 6→9 (guard before export).
- If running one Opus session per task, keep Phase order anyway — checkpoints
  are the review gates.

## Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LinkedIn MCP setup is Mac/launchd-specific; a non-Mac friend can't complete required setup | High | v1 declares macOS-only in README (open question 1); `verify_setup --skip-live` keeps machine validation possible anywhere |
| Onboarding interview scope creep (filling all nine masters conversationally is a long session) | Med | Core-five masters filled, rest copied with follow-up notes; refresh path handles the rest later |
| First-name sweep (Task 6) breaks skill trigger phrasing or drip-runner prompts | Med | Wording/config-only edits; fixture eval + spot-check triggers after |
| Export list drifts from reality (new root files appear) | Med | Export script scans the whole tree with guard patterns and fails loud, rather than trusting the include list |
| `verify_setup` false-FAILs on legitimate setups (e.g., custom MCP port) | Low | Endpoint configurable via profile key; every FAIL row names its fix |

## Open questions (need Kanu, not blockers to start)

1. Is v1 officially macOS-only (LinkedIn daemon via launchd)? Affects README and
   release-gate wording only.
2. Onboarding minimum: is the core-five master set (Achievements, Story Bank,
   TMAY, Target Profile, Application Profile) the right "done" bar for a first
   onboard?
3. License: MIT?
