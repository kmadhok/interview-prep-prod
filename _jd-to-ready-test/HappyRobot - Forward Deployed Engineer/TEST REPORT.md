# TEST REPORT — `jd-to-ready` sandboxed run

**Date:** 2026-06-19 · **Platform:** Windows 10 / Windows PowerShell 5.1
**Input:** single LinkedIn URL — https://www.linkedin.com/jobs/view/4250531432/
**Resolved role:** **HappyRobot — Forward Deployed Engineer** (Chicago, IL · Hybrid · Full-time). Real employer confirmed: HappyRobot, Inc. (YC S23; domain happyrobot.ai; LinkedIn company URN 82462935).
**Sandbox root:** `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\`

---

## Per-step results

| Step | Primitive | Status | What happened |
|------|-----------|--------|---------------|
| Trace start | trace_step.py start-run | **failed (non-fatal)** | Could not run — see harness problems. No trace files written all run. |
| 1 — intake | interview-prep-intake | **ok** | `get_job_details` fetched full JD; parsed company/role/location/gates; wrote `Job Description.md`. Pipeline + memory writes redirected to sandbox delta file. |
| 2 — classification | jd-classification (subagent) | **ok** | Spawned general-purpose subagent; returned valid JSON first try — 6 in-vocab themes w/ evidence quotes, archetype `FDE / client-facing`, useful notes. No re-spawn needed. |
| 3 — resume | tailor-resume | **ok (with flagged gap)** | Wrote `Kanu Madhok Resume - HappyRobot FDE.md`, canonical-only, FDE-led ordering. One real JD/skills gap flagged via `[VERIFY]` (React/TS/Node + voice). |
| 3.5 — export | export_resume.py | **failed (non-fatal)** | Helper could not run (PowerShell denied + macOS/python3 helper). `.md` is source of truth; no `.pdf`/`.docx`. |
| 4 — find-contacts | find-contacts (full) | **ok** | LinkedIn MCP, strictly sequential. 4 calls: company profile (URN), recruiter search, HM/founder search, 1 peer-IC deep profile. 5 recruiters + 2 founders + 5+ FDE peers, all named/real. Wrote `.contacts-ledger.md`. |
| 4.5 — Apollo verify | apollo_people_match | **skipped** | Apollo MCP not available/authed in sandbox. All emails inferred (Low confidence), logged as gap. No `Verified Emails.md`. |
| 4b — enrich | enrich-contacts | **partial/ok** | Scraped Jordan Young's posts → real, specific outreach hook captured. Recruiter feed not scraped (recruiter activity typically thin); logged. No NEW people added (search coverage already strong). |
| 5 — outreach | write-outreach (drip) | **ok** | Wrote `Cold Outreach.md`: peer-IC lead (Jordan Young) + recruiter (Christine Price), each with intro + FU1 + FU2 (+ conditional Hail Mary). Real hooks, no fabricated urgency, LinkedIn channel. No Gmail draft (sandbox rule). |
| 6 — report | report-back | **ok** | This file. |
| 7 — final log | trace_step.py finish-run | **failed (non-fatal)** | Same helper blocker. Summary captured here instead. |

**Overall:** core deliverables all produced and real. Only the two python helper steps (trace, export) and the two external-MCP steps (Apollo, Gmail draft) did not run.

---

## Files created (full paths)

1. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\Job Description.md`
2. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\Kanu Madhok Resume - HappyRobot FDE.md`
3. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\.contacts-ledger.md`
4. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\Cold Outreach.md`
5. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\SANDBOX - pipeline-and-memory-deltas.md`
6. `G:\projects\interview-prep\_jd-to-ready-test\HappyRobot - Forward Deployed Engineer\TEST REPORT.md` (this file)

No real-workspace files were modified. `Roles/`, `Pipeline.md`, `Pipeline.html`, and the auto-memory were not touched.

---

## Portability / harness problems (specific)

1. **PowerShell is fully denied in this sandbox.** Every `PowerShell` tool call returned: *"Permission to use PowerShell has been denied."* This is the hard blocker for ALL of the skill's shell steps. On this box I literally cannot execute any command-line step, regardless of OS-path correctness.

2. **Trace contract is dead on this box.** The skill mandates `python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py {start-run, set-role-folder, begin, end, finish-run}` around every step. Two failure layers: (a) it's a `python3` + `~/.claude/...` POSIX path; on Windows the home is `%USERPROFILE%\.claude\...` and the interpreter may be `python`/`py`, not `python3`; (b) even the path-corrected command can't run because PowerShell is denied. Net: zero trace/observability output. Treated non-fatal per instructions; core work continued.

3. **Resume export helper (`export_resume.py`) cannot run** — same two layers (POSIX path + `python3`, plus PowerShell denial), and additionally depends on pandoc + headless Chrome which aren't confirmed present. No `.pdf`/`.docx`. `.md` remains source of truth. Non-fatal.

4. **macOS-only workspace paths throughout SKILL.md.** It hardcodes `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/` as workspace root and `~/.claude/logs/...`. The real workspace here is `G:\projects\interview-prep`. A literal run that trusted those paths would read/write the wrong place. I used the real Windows workspace for reads and the sandbox for writes.

5. **Apollo MCP unavailable** — `mcp__claude_ai_Apollo_MCP__apollo_people_match` not present in this environment, so step 4.5 email verification could not run. Emails are inferred-only. Logged as a gap, not a failure (skill degrades gracefully here by design).

6. **Gmail draft step skipped by sandbox rule** (and Gmail tools were not exercised). The skill's step-6 "auto-create the lead intro as a Gmail draft" did not run; outreach is file-only.

7. **LinkedIn MCP worked well** under the sequential discipline — 4 sequential calls, never two in flight, well under the ~25 cap. No transport errors. This was the most reliable external dependency in the run.

---

## Quality spot-check

- **Canonical-only resume?** Yes. Every bullet traces to a Resume Achievements Master entry (A3, A1, A2, A5, A4, A6, F1, U1, I1) + the A7 demo. No invented metrics, no status upgrades ("production"/"shipped"/"adopted" all match canonical language).
- **`[VERIFY]`/`[NUMBER?]` leaks?** None in the resume *body*. One deliberate `[VERIFY]` lives inside an HTML tailoring-notes comment (clearly marked "strip before export") flagging the React/TS/Node + voice gap. No `[NUMBER?]` anywhere. Nothing leaks into outward-facing text.
- **Classification correct?** Yes — `FDE / client-facing` is right: title is literally Forward Deployed Engineer and the JD centers on working with customers from onboarding through ongoing use, blending customer engineering with building. Themes (end-to-end, agents, LLM-orchestration, platform, business-translation, cross-functional) all evidence-backed and on-vocab.
- **Contacts real (named) or empty?** Real and named, not placeholders. Recruiters: Christine Price, Erik Winden, Judy A., Jackson Armstrong, Jorge Janeiro. Founders: Luis Paarup (CTO), Pablo Palafox (CEO). Peer FDEs: Jordan Young (Chicago — lead), Chinmay Avsarkar (Chicago), Conleth Stead, Jaime Maqueda, John Hartle, Erin DeLong. Hook on the lead is sourced from his actual reposts, not fabricated.

---

## Gaps / human review needed

1. **Resume skills gap is real, not cosmetic.** JD asks for React/TypeScript/Node.js full-stack and LLM voice/transcriber tuning. Kanu's canonical material is Python/agents/RAG/eval-heavy with React only on the *viz* side (Recharts) and no voice/speech work. He should decide: (a) does he have claimable React/TS/Node depth (→ promote into Resume Achievements Master first), and (b) how to address the voice/transcriber ask in a cover note/interview rather than the resume.
2. **Sponsorship unknown.** JD is silent; ~161-person YC startup — confirm with recruiter before investing further.
3. **Emails unverified.** All inferred from the happyrobot.ai pattern. Reach out via LinkedIn, not cold email, until verified. Run Apollo + Gmail warm-tie check when those tools are available.
4. **No format intel yet** (no recruiter contact). Founder-mindset framing suggests a speed/ownership-weighted loop; revisit once a recruiter responds.
5. **Comp not published** — "competitive + equity." No floor to check.

---

## Bottom line

**Would this skill have produced an apply-ready package if run for real on this box? Mostly yes — the *content* is apply-ready, the *automation* is not.** All four core human-facing deliverables (clean JD, canonical-only tailored resume, real scored contact ledger, drip outreach with genuine hooks) came out correct and high-quality, and the classification + LinkedIn-contact engine — the load-bearing logic — worked cleanly. What did NOT run is every helper that shells out: trace/observability (entire trace contract), resume PDF/DOCX export, Apollo verification, and the Gmail draft. So Kanu would still have to export the resume himself, verify emails, and send via LinkedIn — i.e., a few manual steps short of the skill's promised "just click Apply and Send" end state.

**Single biggest thing to fix: make the skill OS-portable and shell-optional.** Concretely: (a) resolve workspace root and `~/.claude` from the environment instead of hardcoding macOS paths; (b) call `python3` via a detected interpreter (`python`/`py -3`) and tolerate its absence; and most importantly (c) make the **trace contract degrade gracefully** — right now a denied/missing shell would, on a strict reading, block the very first step (`start-run`) before any deliverable is produced. The trace should be best-effort telemetry that never gates the core pipeline. Fix that and this exact run would produce the full content package on Windows with zero shell access — which is what it did here once I treated the helpers as non-fatal.
