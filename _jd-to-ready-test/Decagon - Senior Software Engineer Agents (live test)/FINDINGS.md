# Two-Orchestrator Live Test — FINDINGS

**Date:** 2026-06-27
**Branch:** worktree-two-orchestrator-split
**Goal:** Run one fresh saved job end-to-end through both redesigned orchestrators (sandboxed, via subagents) and capture every finding before enabling the hourly Pass B runner.

## Test input
- **Company / Role:** Decagon — Senior Software Engineer, Agents
- **job_id:** 4395231105
- **Source:** LinkedIn saved jobs (newest-saved eligible). Sourced via `get_saved_jobs` (note: this session's MCP registry initially lacked `get_saved_jobs`; it surfaced mid-session and was used).
- **Eligibility:** NEW on all three checks — not in `saved_seen.json`, not in `Pipeline.md` (dedupe), no `Roles/` folder.
- **Pick caveat:** JD requires "5+ years industry software engineering" → may trigger jd-to-ready hard-gate flag (seniority/SWE bar vs. analyst background). Kanu approved testing the hard-gate path.

## Harness / isolation
- **Sandboxed.** All outputs → this folder (`_jd-to-ready-test/Decagon - Senior Software Engineer Agents (live test)/`).
- `trace_step.py --test-run` used so the role folder validates outside `Roles/`.
- Real `Pipeline.md`, `Roles/`, `saved_seen.json` NOT touched. Would-be Pipeline writes captured in `SANDBOX - pipeline-and-memory-deltas.md`.
- Gmail draft (O2): created for real (never sent); id/recipient/subject captured below; left in Drafts.
- Pre-flight confirmed: LinkedIn daemon up (127.0.0.1:8765, PID 28960); installed `~/.claude/skills/` == repo.

---

## Orchestrator 1 — jd-to-ready (prep) — ✅ PASS

**Verdict:** PASS. All required steps {1,2,3,3.5,6,7} closed; `finish-run` ok; zero outward calls; no real Pipeline/Roles/ledger writes. Wall-clock ~2–3 min.

| Step | Status | Note |
|---|---|---|
| 1 intake | ok | wrote Job Description.md (+ hard-gate "Notes for Kanu"); Pipeline/memory → SANDBOX file |
| 2 classify | ok | subagent classifier ran (nested spawn works), valid JSON first try, 6 in-vocab themes |
| 3 tailor-resume | ok | canonical-only, 0 unverified claims; 3 gaps (TS/async, voice/multimodal, 5yr-SWE) |
| 3.5 resume-export | partial | PDF clean (1 page, no title leak); vision verify SKIPPED — pdftoppm/Poppler missing on Windows → graceful degrade per spec |
| 6 report-back | ok | paths, hard gates, gaps assembled |
| 7 final-log | ok | global summary appended; run closed |

**Files produced (bytes):** Job Description.md 3986 · resume .md 4298 · resume .pdf 5983 · .classification.json 1585 · SANDBOX deltas 1458 · trace .jsonl 19130.

**Classification:** archetype `agent-builder`; themes = agents, evaluation, experimentation, end-to-end, platform, engineering-rigor. Secondary FDE flavor noted; flagged heavier production-eng role + on-site NYC.

**Hard gate (5+yr SWE):** raised in 3 places — Job Description.md "Notes for Kanu", `.classification.json` notes, and step-3/finish-run gaps.

**Isolation confirmed:** `git status` clean for Pipeline.md / Roles/ / saved_seen.json; 0 outward calls; all outputs in the test folder.

### Findings / bugs surfaced by O1
1. **Vision verify unavailable on the PC** — `verify_resume.py`: `SKIP: pdftoppm missing`. Poppler isn't installed on this Windows box → resume PDFs are never vision-checked in production either. Degrades gracefully, but the quality gate is effectively off on the PC. *Worth installing Poppler if vision verify is wanted in prod.*
2. **`finish-run` status-assertion gotcha** — passing `--status partial` (because gaps existed) fails closed: computed status is derived only from step end-statuses, not gaps. Caller must pass the computed value. Correct behavior, but a real foot-gun for the runner prompts (they should pass `ok` when all steps are ok, regardless of gaps).
3. **Test runs not stamped in the global log** — `--test-run` validates the folder but `test_run` is null/absent in the `~/.claude/logs/jd-to-ready.jsonl` summary line → test and prod runs are indistinguishable in the global log. Minor observability improvement.

---

## Orchestrator 2 — stage-outreach (outreach)

_Pending subagent run (after O1 finishes clean)._

---

## Overall verdict

_Pending._
