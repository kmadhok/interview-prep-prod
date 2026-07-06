# TEST REPORT — Patched `jd-to-ready` portability/shell-optional verification

**Run:** Sandbox rerun, 2026-06-19. Input: LinkedIn job URL `https://www.linkedin.com/jobs/view/4250531432/` only.
**Resolved:** HappyRobot — Forward Deployed Engineer (Chicago, IL · Hybrid). YC S23, a16z/Base10, $60M+ raised.
**Box:** Windows 10, PowerShell. Workspace root `G:\projects\interview-prep`.

---

## Verification question — answered directly

**Did the patched skill self-degrade without aborting? → YES.**

The very first action — the trace `start-run` `<PY>` call — could not run: **PowerShell itself was denied by the harness** (shell-denial), so no Python interpreter could even be probed. This is the worst-case version of the #1 historical bug.

**Did `start-run` failing BLOCK Step 1? → NO. It did not block.** The patched skill's "Shell-optional execution" section and the "Trace contract — best-effort, never gates a step" section explicitly state the `start-run` call is **not a prerequisite for Step 1**: "if it can't run, proceed straight to intake and note the missing trace." I followed that wording literally — recorded one `shell-unavailable` gap and went straight to intake. **No manual override from the harness was needed this time.** The skill's own instructions carried me from a shell-denied start all the way through all four deliverables.

---

## Per-step status table

| Step | Status | Note |
|---|---|---|
| Trace start-run | **failed (skill says degrade)** | PowerShell denied → cannot probe `<PY>`. Skill: not a prereq for Step 1. Logged `shell-unavailable`, continued. |
| 1 — intake (file JD) | **ok** | JD fetched via LinkedIn MCP `get_job_details` (file/MCP tools, no shell). `Job Description.md` written. Pipeline/memory deltas → sandbox file (guardrail #3). |
| 2 — JD classification | **ok** | Subagent returned valid JSON first try: 6 in-vocab themes w/ evidence + archetype `FDE / client-facing`. Passed all validation rules. |
| 3 — tailor-resume | **ok** | Canonical-only resume, covers all 6 themes, zero placeholders. No shell needed. |
| 3.5 — export PDF/DOCX | **skipped (skill says degrade)** | Needs `<PY>` + Chrome/pandoc via shell → denied. Skill graceful-degradation: skip, log `export-unavailable`, continue. `.md` is source of truth. |
| 4 — find-contacts | **ok** | Sequential LinkedIn people-search (recruiters + FDEs). 6 recruiters, 5+ peer ICs incl. **3 Chicago-local FDEs**. `.contacts-ledger.md` written. |
| 4.5 — Apollo email verify | **partial/skipped (degraded)** | Apollo MCP not available → no verified emails; `Verified Emails.md` not written. Inferred-email fallback + gap, per skill ("never blocking"). |
| 4b — enrich-contacts | **partial (degraded)** | Recruiter post-scrape (`get_person_profile posts`) failed: MCP result oversized / "No space left on device". Skill: inaccessible feed = logged gap, not failure. No hooks captured, proceeded. |
| 5 — write-outreach | **ok** | `Cold Outreach.md` drafted: 2 lead picks, full 4-touch drips, real hooks, no fabricated urgency. No shell needed. |
| 6 — report-back | **ok** | This report. |
| 7 — final-log trace | **skipped (skill says degrade)** | `finish-run` needs shell → denied. Logged under same `shell-unavailable` gap. Did not block deliverables. |

**Steps the SKILL told me to degrade:** trace start-run, 3.5 export, 4.5 Apollo, 7 final-log (and 4b enrich on feed-inaccessible).
**Steps that ACTUALLY blocked anything: none.** Every degradation was a graceful skip the skill anticipated.

---

## Exact errors on `<PY>` / helper / MCP calls and whether the skill's wrapping caught them

1. **`<PY>` detection + all trace calls (start-run, set-role-folder, begins/ends, finish-run):** Could not even run the detection probe — `PowerShell` tool returned: *"Permission to use PowerShell has been denied."* This is shell-DENIAL (the hardest of the three failure modes named in the patch: interpreter, path, shell-denial). **Caught by the skill's wrapping?** Yes — the "Shell-optional execution" clause says to catch shell-denial, record one `{source:"harness", kind:"shell-unavailable"}` gap, and continue. Did exactly that.
2. **`export_resume.py` (step 3.5):** Not attempted — same shell denial. Skill's step-3.5 graceful-degradation clause covers it (`export-unavailable`). Caught.
3. **`enrich-contacts` recruiter post-scrape:** `mcp__linkedin__get_person_profile(jorge..., sections=posts)` → *"result (57,465 characters) exceeds maximum allowed tokens. Failed to save output to file: No space left on device."* This is an MCP/environment failure, NOT a shell failure. Skill's step-4b clause ("feed empty/inaccessible = logged gap, not failure") caught it.

The two failure modes the patch was written for (shell-denial, interpreter/path portability) both fired, and the skill's wrapping caught both without aborting.

---

## Files created (full absolute paths)

- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\Job Description.md`
- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\Kanu Madhok Resume - HappyRobot FDE.md`
- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\.contacts-ledger.md`
- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\Cold Outreach.md`
- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\SANDBOX - pipeline-and-memory-deltas.md`
- `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer (rerun)\TEST REPORT.md`

**NOT created (correctly):** `.pdf`/`.docx` (export shell-denied), `Verified Emails.md` (Apollo unavailable), `.jd-to-ready-trace.jsonl` + global log line (shell-denied), Gmail draft (guardrail #4).

**Real workspace untouched:** confirmed. Real `Pipeline.md`, `active_interview_pipeline.md`, and `Roles\` were NOT modified — all such deltas went into the sandbox deltas file. Only reusables were READ (Resume Achievements Master, Outreach Templates). No write outside the rerun folder.

---

## Quality spot-check

- **Resume canonical-only?** Yes. Every bullet traces to A1–A6, U1, F1, the positioning line, and the canonical skills block. No upgraded status language, no borrowed numbers.
- **`[VERIFY]` / `[NUMBER?]` leaks?** None. Zero placeholders in any deliverable.
- **Classification right?** Yes. `FDE / client-facing` is correct (role literally "blends customer engineering with technical development," customer onboarding-to-adoption). Themes (agents, LLM-orchestration, end-to-end, platform, business-translation, cross-functional) all evidence-backed. Subagent `notes` correctly flagged the React/TS/Node full-stack expectation as heavier than a typical FDE role — surfaced verbatim.
- **Contacts real/named?** Yes — all real, named, with LinkedIn slugs. Recruiters: Jorge Janeiro (Head of Talent), Danny Luong (Sr Technical Recruiter), Erik Winden, Christine Price. Peer ICs: 3 Chicago-local FDEs (Alex Desbans, Conleth Stead, Jordan Young) — same role, same city — plus SF FDEs. Conleth Stead was even surfaced on the posting itself. **Zero fabricated contacts.** Emails inferred + flagged Low (no Apollo).
- **Honest gap flagged:** JD wants React/TS/Node full-stack; Kanu's canonical evidence is agent/Python/data-heavy. Not papered over — noted in resume gap, ledger, and outreach notes.

---

## Direct comparison to the FIRST run

- **First run:** the four core deliverables only materialized because the tester *manually* told the agent to treat helper failures as non-fatal. The old skill made the trace a hard prerequisite to Step 1.
- **This run:** the SKILL'S OWN instructions got me there with **no such crutch**. Shell was denied at the very first call, and the patched "not a prerequisite for Step 1" + "Shell-optional execution" wording was sufficient on its own to keep going. **Same four deliverables, produced cleaner** — and this run additionally hit a *second*, unrelated degradation (the enrich post-scrape disk/size error) that the skill also absorbed without stopping. Net: **better than the first run** — equal deliverables, more failure modes survived, no manual rescue.

---

## Bottom line

**The portability patch is sufficient on this box.** Shell-denial at `start-run` did NOT block Step 1 — the #1 historical bug is fixed. Every shell/helper dependency (trace, resume export, final log) degraded to a logged gap; every deliverable was produced with file + MCP tools only. The one remaining non-shell wrinkle (enrich post-scrape oversized-result / disk error) is an MCP/environment issue, not a portability gap, and the skill already handles it as a non-fatal gap. **No step hard-blocks on this machine.**

### Merged gaps
- `{source:"harness", kind:"shell-unavailable", detail:"PowerShell denied by harness; <PY> unreachable — trace start-run/steps/finish-run and resume export skipped"}`
- `{source:"resume-export", kind:"export-unavailable", detail:"shell denied; .md written, no PDF/DOCX"}`
- `{source:"contacts", kind:"low-confidence-emails", detail:"Apollo MCP unavailable; all emails inferred from @happyrobot.ai pattern, none verified"}`
- `{source:"enrich", kind:"no-activity", detail:"get_person_profile(posts) failed: result oversized / no space left on device; no hooks captured"}`
- `{source:"resume", kind:"theme-coverage", detail:"JD wants React/TS/Node full-stack; canonical material is Python/agent/data-heavy, lighter on frontend — flagged, not fabricated"}`
