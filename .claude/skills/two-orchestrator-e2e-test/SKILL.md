---
name: two-orchestrator-e2e-test
description: Use this skill to run the full two-orchestrator end-to-end pipeline test — take ONE real role through all 7 skills (interview-prep-intake → classify → tailor-resume → PDF → [apply gate] → find-contacts → enrich-contacts → verify-emails → write-outreach) via sequential sub-agents in an isolated _jd-to-ready-test/ clone, verify each artifact deterministically with verify_artifacts.py, and write a TEST REPORT.md. Trigger on "run the e2e pipeline test", "end-to-end test the two-orchestrator pipeline", "test the whole jd-to-ready + stage-outreach flow on <role>". FULL LIVE RUN (real LinkedIn scraping + real Gmail draft, never sent). Does NOT touch real Roles/ or Pipeline.md. Do NOT trigger to file a JD (interview-prep-intake), prep a resume (jd-to-ready), or stage real outreach (stage-outreach).
---

# Two-Orchestrator E2E Test (full live, per-skill, isolated clone)

Runs one real role through all 7 pipeline skills, one sub-agent per skill, **sequentially**, in a throwaway clone. Real `Roles/` and `Pipeline.md` are never touched; the apply gate is simulated on a local fixture. The only real external side effect is one unsent Gmail draft. Read root `AGENTS.md`/`CLAUDE.md` first; it overrides anything here.

`<repo root>` = the Interview Prep workspace root (cwd). Use `python3` (Windows: `py -3`).

## What this skill does NOT do
No real Pipeline/Roles writes. No `jd-to-ready` trace run (an open trace step trips the Stop hook on every async sub-agent yield; the trace contract is covered by `test_trace_step.py`). Never sends — Gmail `create_draft` only.

## Step 0 — Setup
1. Pick the target: a real `Company - Role` whose JD is available (an existing `Roles/<role>/Job Description.md`, a saved job, or pasted JD). Must be a real company (full-live apply side needs a LinkedIn presence).
2. Create `<repo root>/_jd-to-ready-test/<Company - Role> (e2e <YYYY-MM-DD>)/` (the clone).
3. Write the JD to `<clone>/Job Description.md` is the intake sub-agent's job — for now save the source JD to a scratch file the intake sub-agent will read.
4. Write `<clone>/_pipeline-fixture.md` — a minimal pipeline with the role under `## Considering / not yet applied`:
   ```
   ## Active

   | Role | Stage | Next action | Date | Contacts | Folder |
   |------|-------|-------------|------|----------|--------|

   ## Considering / not yet applied

   | Role | Stage | Next action | Date | Contacts | Folder |
   | **<Company> — <Role>** | Considering — not yet applied | — | — | — | — |
   ```
5. Every sub-agent prompt below MUST include: "Operate ONLY in `<clone>`. Do NOT touch real Roles/ or Pipeline.md. Do NOT run trace_step.py. Do NOT send anything."

## Steps 1–3 — Prep sub-agents (sequential)
Launch a fresh `general-purpose` sub-agent per skill; wait for each, then run its verifier check before the next.
1. **interview-prep-intake** → writes `<clone>/Job Description.md`. (Tell it to skip the Pipeline row — the fixture already has it.)
2. **classify** (jd-to-ready Step 2) → writes `<clone>/.classification.json`. Give it the theme/archetype vocab from `.claude/skills/jd-to-ready/SKILL.md` Step 2.
3. **tailor-resume** → writes `<clone>/Kanu Madhok Resume - <Company> <Short Role>.md` (canonical-only).

## Step 3.5 — PDF (main loop)
```
python3 "<repo root>/scripts/build_resume_pdf.py" "<clone>/Kanu Madhok Resume - <Company> <Short Role>.md"
```
Capture the `PAGES=<n> TITLE_LEAK=<0|1>` line.

## Step 3.6 — Simulated apply gate (main loop)
In `<clone>/_pipeline-fixture.md`, move the role row to `## Active` and set its stage to `Applied <YYYY-MM-DD>`. Then:
```
python3 "<repo root>/scripts/drip_runner/outreach_worklist.py" --pipeline "<clone>/_pipeline-fixture.md" > "<clone>/_worklist.txt"
```
Confirm the role appears (this exercises the Pass B reader without touching real state).

## Step 3.7 — LinkedIn preflight (main loop)
Invoke `linkedin-mcp-operations`. Handshake:
```
curl -s -o /dev/null -w '%{http_code}\n' -m 6 -X POST http://127.0.0.1:8765/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"0.1"}}}'
```
If not `200` → STOP the apply side; mark steps 4–7 `blocked` in the report; jump to Step 8. When you reach Step 8 after a blocked apply side, pass `--blocked-apply` to verify_artifacts.py so the four apply-side skills are marked blocked, not failed.

## Steps 4–7 — Apply sub-agents (sequential — one LinkedIn stream at a time, never parallel)
4. **find-contacts** → `<clone>/.contacts-ledger.md` (real LinkedIn, read-only).
5. **enrich-contacts** → updates the ledger with hooks (real LinkedIn, read-only).
6. **verify-emails** → `<clone>/Verified Emails.md` (real EmailFinder; degrade to inferred if unavailable).
7. **write-outreach** → `<clone>/Cold Outreach.md` + a Gmail draft via `create_draft` to the resolved recruiter. **NEVER send.** Capture the draft id + recipient.

## Step 8 — Verify + report (main loop)
1. Confirm the draft: `mcp__claude_ai_Gmail__list_drafts` with `query: "to:<recipient>"`; save the matched draft object to `<clone>/_draft.json`.
2. Run the verifier:
```
python3 "~/.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" --clone "<clone>" --company "<Company>" --worklist-out "<clone>/_worklist.txt" --pages <n> --title-leak <0|1> --draft-json "<clone>/_draft.json" --expected-recipient "<recipient>"
```
3. Write `<clone>/TEST REPORT.md` from the verifier JSON + each sub-agent's report + the PDF/gate/draft results. Use the same sections as `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`: summary table, per-skill detail, findings (your narrative on top of the verifier's deterministic pass/fail), environment notes, cleanup record (the Gmail draft id + a one-line "delete in Gmail Drafts if unwanted").

## Cleanup
Real data is untouched, so the clone folder IS the test record (commit it if wanted). Surface the Gmail draft id for deletion. Nothing to restore.
