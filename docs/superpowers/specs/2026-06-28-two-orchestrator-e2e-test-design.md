# Two-Orchestrator E2E Test Skill — Design

**Date:** 2026-06-28
**Status:** Design approved; pending spec review → implementation plan.
**Branch:** `worktree-two-orchestrator-split`
**Origin:** Codifies the manual end-to-end test harness run on 2026-06-28 (see `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`).

---

## 1. Goal

A purpose-built skill that runs the full two-orchestrator lifecycle for **one real role** through **7 sequential sub-agents (one per skill)**, in an isolated `_jd-to-ready-test/` clone, deterministically verifies each skill, and emits a `TEST REPORT.md`. It turns the bugs the manual test found by hand into automatic, repeatable regressions.

The pipeline under test (unchanged):
```
PREP (jd-to-ready):  1 intake → 2 classify → 3 tailor-resume → 3.5 PDF
  ── simulated apply gate ──
APPLY (stage-outreach):  4 find-contacts → 5 enrich-contacts → 6 verify-emails → 7 write-outreach → Gmail draft
```

## 2. Approved design decisions

| Decision | Choice |
|---|---|
| **Scope** | This pipeline only, end-to-end (hard-codes the 7-skill chain). Not a general harness. |
| **Run mode** | Always full live — real LinkedIn scraping, real EmailFinder, real Gmail draft (never sent). No dry-run mode. |
| **Target + isolation** | Test-clone in `_jd-to-ready-test/`. Real `Roles/` and `Pipeline.md` are never touched; the apply gate is simulated against a local pipeline fixture. |
| **Architecture** | `SKILL.md` orchestration + a deterministic `verify_artifacts.py` (structured pass/fail) + its pytest. |
| **Distribution** | Committed under `.claude/skills/two-orchestrator-e2e-test/`; syncs to Mac via the canonical-repo + junction model (no install step). |

## 3. Invariants preserved

From `Automation Architecture - Purpose.md`: human-gated (Gmail draft only, never sends) · protect the LinkedIn channel (sequential calls only, preflight before scraping, STOP if daemon down) · fail loud never silent (the verifier FAILs loudly, e.g. on empty verified-emails) · truth from existing files (real `Roles/`/`Pipeline.md` untouched; the clone is the record).

## 4. File structure

```
.claude/skills/two-orchestrator-e2e-test/
├── SKILL.md                          # orchestration procedure (the harness)
└── scripts/
    ├── verify_artifacts.py           # deterministic per-skill checks → JSON; stdlib-only
    └── test_verify_artifacts.py      # pytest over fixture clone folders
```

Test records are written under `_jd-to-ready-test/<Company - Role> (e2e <date>)/` (existing convention).

## 5. Run flow (SKILL.md procedure)

**Step 0 — Setup (main loop).**
- Resolve the target role + JD source: an existing `Roles/<role>/Job Description.md`, a saved job, or a pasted JD. The role must be a *real* company (full-live apply side needs a real LinkedIn presence).
- Create `_jd-to-ready-test/<Company - Role> (e2e <date>)/`.
- Seed the JD as the sub-agent input (a `*-saved-job.md` in the clone or scratchpad).
- Write a local `_pipeline-fixture.md` in the clone — a minimal `## Active` / `## Considering` Pipeline used only for the gate + `outreach_worklist.py` check. **Never** the real `Pipeline.md`.
- Every sub-agent prompt is scoped to the clone and states: do NOT touch real `Roles/` or `Pipeline.md`; do NOT run `trace_step.py`; do NOT send anything.

**Steps 1–3 — Prep sub-agents (sequential).** intake → classify → tailor-resume, each a fresh `general-purpose` sub-agent. The orchestrator waits for each, runs the verifier's relevant checks, and only then launches the next.

**Step 3.5 — PDF (main loop, deterministic).** Run `python3 "<repo root>/scripts/build_resume_pdf.py" "<clone>/<resume>.md"`, parse the `PAGES=<n> TITLE_LEAK=<0|1>` contract line.

**Step 3.6 — Simulated apply gate (main loop).** In `_pipeline-fixture.md`, mark the role row `Applied <date>` under `## Active`; run `outreach_worklist.py --pipeline <clone>/_pipeline-fixture.md` and assert the role surfaces (exercises the Pass B reader without touching real state).

**Step 3.7 — LinkedIn preflight (main loop).** Invoke `linkedin-mcp-operations`; handshake `POST http://127.0.0.1:8765/mcp` (expect HTTP 200). If down → STOP the apply side, mark #4–#7 `BLOCKED` in the report (faithful to the degradation rule), jump to Step 8.

**Steps 4–7 — Apply sub-agents (sequential, one LinkedIn stream at a time).** find-contacts → enrich-contacts → verify-emails → write-outreach. The write-outreach sub-agent creates the Gmail draft via `create_draft` only (never send), to the resolved real recruiter.

**Step 8 — Verify + report (main loop).**
- Call the skill's own `list_drafts` check (Gmail MCP) to confirm the draft exists + is unsent; pass that result into the verifier.
- Run `verify_artifacts.py --clone <folder> --pipeline-fixture <...> --pages <n> --title-leak <0|1> --draft-json <...>` → structured JSON.
- Assemble `TEST REPORT.md` in the clone, same format as the 2026-06-28 report: summary table, per-skill detail, findings (agent narrative on top of the verifier's deterministic pass/fail), environment notes, cleanup record (Gmail draft id + delete instruction).

## 6. The verifier — `verify_artifacts.py`

Stdlib-only (argparse, json, re, pathlib), pure-function + thin-CLI in the `dedupe.py` style. It cannot reach MCP servers, so Gmail-draft state is passed in as `--draft-json`. Emits `{ "skills": { "<name>": {"status": "pass|fail|warn|blocked", "checks": [{"name","ok","detail"}], "notes"} }, "summary": {...} }`.

Per-skill checks:

| Skill | Checks |
|---|---|
| intake | clone folder exists; `Job Description.md` present + non-empty |
| classify | `.classification.json` parses; 4–6 themes; **all themes in the 18-string vocab**; archetype in the 5-string vocab; every theme has non-empty evidence; `classified_ts` present |
| tailor-resume | resume `.md` exists + non-trivial; **no `[VERIFY]` / `[NUMBER?]` in body**; contact header present |
| PDF (3.5) | `.pdf` exists; `PAGES==1` else `warn` (overflow gap); `TITLE_LEAK==0` else `fail` |
| gate (3.6) | `outreach_worklist.py` output (passed in) contains the role |
| find-contacts | `.contacts-ledger.md` exists; ≥1 contact row |
| enrich-contacts | ledger has a `hooks` section / row count grew vs find-contacts baseline |
| verify-emails | `Verified Emails.md` exists with ≥1 verified row; **if 0 rows while the ledger has contacts → `fail` (loud)** ← auto-catches Issue 1 |
| write-outreach | `Cold Outreach.md` exists; draft (from `--draft-json`) exists, has the resolved recipient, and is **unsent** |

`status` rollup: any `fail` → skill fails; `warn` (e.g., PDF overflow) is a pass-with-gap.

`test_verify_artifacts.py` covers it with fixture clone folders: clean pass; **broken-format ledger that yields empty `Verified Emails.md` → verify-emails fail** (the Issue 1 regression); off-vocab classification → classify fail; `[VERIFY]` leak → tailor fail; 2-page PDF → PDF warn.

## 7. Two deliberate behaviors (lessons from the manual run)

- **No trace run.** The skill does NOT open a `jd-to-ready` trace — an open trace step trips `jd-to-ready-stop.py` on every async-sub-agent yield (manual-run Issue 4). The report states the trace contract is independently covered by `test_trace_step.py` (15 tests).
- **Light cleanup.** Real data is untouched (clone model), so the only real side effect is the Gmail draft. The report prints its id + a one-line delete instruction. The clone folder *is* the durable, committable test record. No destructive restore.

## 8. Portability & distribution

- **Scripts** are referenced as `~/.claude/skills/two-orchestrator-e2e-test/scripts/...` (resolves on both Mac and PC via the `~/.claude/skills` junction into the repo).
- **Workspace data paths** (`Pipeline.md`, `Roles/`, `scripts/build_resume_pdf.py`, `_jd-to-ready-test/`) are written relative to the current workspace root — never a hardcoded `G:\…` or `/Users/…`. The SKILL.md uses a `<repo root>` placeholder like the existing skills.
- **`verify_artifacts.py` takes all paths as arguments** — no embedded absolutes, so it is portable and unit-testable.
- **Python invocation:** `python3` as primary; note the Windows `py -3` alternative (consistent with the drip-runner prompts).
- **Sync:** commit under `.claude/skills/two-orchestrator-e2e-test/` on this branch. Per Skill Sync branch discipline, skill changes reach the PC runner via `main`; to use on Mac, pull this branch (or merge to `main`). No install/copy step — the junction means `git pull` is the deploy.

## 9. Relationship to the Skill Sync canary (§4 of `Automation Architecture - Skill Sync (Mac to PC).md`)

This skill is the **interactive, full-lifecycle sibling** of the planned (unbuilt) Layer-2 canary. The canary is an automated, offline-core, golden-JD self-check wired into the runtime cron; this skill is a human-invoked, full-live, real-role end-to-end test. Their validation overlaps (deliverables exist, themes in-vocab, no `[VERIFY]` leak, 1-page PDF), so `verify_artifacts.py` is designed as a reusable validator the future `scripts/canary.py` can import rather than re-implement.

## 10. Out of scope (YAGNI)

- No general/configurable multi-pipeline harness (scope decision).
- No dry-run / stub mode (run-mode decision).
- No automatic destructive reset of real role folders (the clone model removes the need).
- No CI wiring or cron canary in this skill (separate Skill Sync build items; this skill only makes its validator reusable by them).
- No auto-deletion of the Gmail draft (human-gated; report surfaces the id).

## 11. Open detail resolved

Gmail draft goes to the **real recruiter** (full fidelity, matching the full-live decision); repeated runs leave real unsent drafts. The report surfaces each draft id with a delete instruction. (Alternative considered and rejected for now: redirect to `madhok.kanu@gmail.com`.)
