---
name: two-orchestrator-e2e-test
description: Use this skill to run the full two-orchestrator end-to-end pipeline test — take ONE real role through all 8 skills (interview-prep-intake → classify → tailor-resume → PDF → apply-packet → [apply gate] → find-contacts → enrich-contacts → verify-emails → write-outreach) via sequential sub-agents in an isolated _jd-to-ready-test/ clone, verify each artifact deterministically with verify_artifacts.py, and write a TEST REPORT.md. Trigger on "run the e2e pipeline test", "end-to-end test the two-orchestrator pipeline", "test the whole jd-to-ready + stage-outreach flow on <role>". FULL LIVE RUN (real LinkedIn scraping + real Gmail draft, never sent). Does NOT touch real Roles/ or Pipeline.md. Do NOT trigger to file a JD (interview-prep-intake), prep a resume (jd-to-ready), or stage real outreach (stage-outreach).
---

# Two-Orchestrator E2E Test (full live, per-skill, isolated clone)

Runs one real role through all 8 pipeline skills, one sub-agent per skill, **sequentially**, in a throwaway clone. Real `Roles/` and `Pipeline.md` are never touched; the apply gate is simulated on a local fixture. The only real external side effects are unsent Gmail drafts and an upload to the `_test` Drive remote. Read root `AGENTS.md`/`CLAUDE.md` first; it overrides anything here.

`<repo root>` = the Interview Prep workspace root (cwd). Use `python3` (Windows: `py -3`).

**Test steps are numbered T0–T8** — deliberately NOT the real skills' step numbers. Each step header names the real skill step it exercises, so cross-reference by that annotation, never by the T-number.

## What this skill does NOT do
No real Pipeline/Roles writes. No `jd-to-ready` trace run (an open trace step trips the Stop hook on every async sub-agent yield; the trace contract is covered by `test_trace_step.py`). Never sends — Gmail `create_draft` only.

## T0 — Setup
1. Pick the target: a real `Company - Role` whose JD is available (an existing `Roles/<role>/Job Description.md`, a saved job, or pasted JD). Must be a real company (full-live apply side needs a LinkedIn presence).
2. Create `<repo root>/_jd-to-ready-test/<Company - Role> (e2e <YYYY-MM-DD>)/` (the clone).
3. Writing the JD to `<clone>/Job Description.md` is the intake sub-agent's job — for now, save the source JD to a scratch file that sub-agent will read.
4. Write `<clone>/_pipeline-fixture.md` — a minimal pipeline with the role under `## Considering / not yet applied`:
   ```
   ## Active

   | Role | Stage | Next action | Date | Contacts | Folder |
   |------|-------|-------------|------|----------|--------|

   ## Considering / not yet applied

   | Role | Stage | Next action | Date | Contacts | Folder |
   | **<Company> — <Role>** | Considering — not yet applied | — | — | — | — |
   ```
5. Every sub-agent prompt below MUST include: "Operate ONLY in `<clone>`. Do NOT touch real Roles/ or Pipeline.md. Do NOT run trace_step.py. Do NOT send anything." (T8 audits compliance mechanically — see the isolation audit.)

## T1–T3 — Prep sub-agents (sequential)
Launch a fresh `general-purpose` sub-agent per skill; wait for each, then run its verifier check before the next.

- **T1 — intake** (real: `interview-prep-intake`) → writes `<clone>/Job Description.md`. (Tell it to skip the Pipeline row — the fixture already has it.)
- **T2 — classify** (real: jd-to-ready Step 2) → writes `<clone>/.classification.json`. Give it the theme/archetype vocab from `.claude/skills/jd-to-ready/SKILL.md` Step 2.
- **T3 — tailor-resume** (real: `tailor-resume`) → writes `<clone>/Kanu Madhok Resume - <Company> <Short Role>.md` (canonical-only).

## T4 — PDF (main loop; real: jd-to-ready Step 3.5)
```
python3 "<repo root>/scripts/build_resume_pdf.py" "<clone>/Kanu Madhok Resume - <Company> <Short Role>.md"
```
Capture the `PAGES=<n> TITLE_LEAK=<0|1>` line. If the line is missing, still run the verifier without the `--pages`/`--title-leak` flags — it will surface the missing contract as a warn.

## T5 — apply-packet (main loop; real: jd-to-ready Step 3.7)
Run jd-to-ready's Step 3.7 (3.7a–3.7d: canonical posting + posted date, repost check, `.classification.json` update, `Application Answers.md`) in the **main loop**, then upload with the test remote passed as an **explicit flag**:
```
python3 "<repo root>/scripts/drip_runner/apply_packet.py" upload "<clone>" --remote-dir "gdrive:_test/Apply Queue e2e"
```
Do NOT rely on `APPLY_PACKET_REMOTE_DIR` env-var inheritance — the explicit flag cannot be lost across an agent boundary, and a forgotten env var would upload to the REAL Apply Queue. The verifier's `packet-remote-is-test` check is the backstop, not the guard. Writes `<clone>/Application Answers.md` + `<clone>/.apply-packet.json`. (Purging the test remote afterwards is listed in **Cleanup**.)

## T6 — Simulated apply gate + LinkedIn preflight (main loop; real: the Pass B gate)
1. **Gate:** in `<clone>/_pipeline-fixture.md`, move the role row to `## Active` and set its stage to `Applied <YYYY-MM-DD>`. Then:
```
python3 "<repo root>/scripts/drip_runner/outreach_worklist.py" --pipeline "<clone>/_pipeline-fixture.md" > "<clone>/_worklist.txt"
```
Confirm the role appears (this exercises the Pass B reader without touching real state).
2. **Preflight:** invoke `linkedin-mcp-operations`. Handshake:
```
curl -s -o /dev/null -w '%{http_code}\n' -m 6 -X POST http://127.0.0.1:8765/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"0.1"}}}'
```
If not `200` → STOP the apply side; mark the T7 skills `blocked` in the report; jump to T8. When you reach T8 after a blocked apply side, pass `--blocked-apply` to verify_artifacts.py so the four apply-side skills are marked blocked, not failed.

## T7 — Apply sub-agents (sequential — one LinkedIn stream at a time, never parallel; real: stage-outreach Steps 4/4b/4c/5)
- **T7.1 — find-contacts** (real: stage-outreach Step 4) → `<clone>/.contacts-ledger.md` (real LinkedIn, read-only).
- **T7.2 — enrich-contacts** (real: stage-outreach Step 4b) → updates the ledger with hooks (real LinkedIn, read-only).
- **T7.3 — verify-emails** (real: stage-outreach Step 4c) → `<clone>/Verified Emails.md` (real EmailFinder; degrade to inferred if unavailable).
- **T7.4 — write-outreach** (drip mode; real: stage-outreach Step 5) → `<clone>/Cold Outreach.md` + **two** Gmail drafts via `create_draft` — one to the resolved recruiter, one to the HM/peer-IC lead (the same-company double-send guard may collapse them to one). **NEVER send.** Capture each draft id + recipient.

## T8 — Verify + report (main loop)
1. **Confirm the drafts** (skip this sub-step on a blocked apply side — go straight to the verifier with `--blocked-apply` and no `--draft-json`):
   - `mcp__claude_ai_Gmail__list_drafts` for each recipient (`query: "to:<recruiter>"` and `query: "to:<lead>"`).
   - Normalize each matched draft to exactly this shape and save the array to `<clone>/_draft.json`: `[{"id": "<draft id>", "toRecipients": ["<email>"], "sent": false}]` — the verifier reads `toRecipients` at top level; raw MCP draft objects may not carry it. If the guard suppressed one draft, save the single-element array — the verifier accepts one or two.
   - **Never-sent proof:** run `mcp__claude_ai_Gmail__search_threads` with `in:sent to:<recruiter> newer_than:1d` (and the same for the lead). Both must return zero results; record this in TEST REPORT.md as the never-sent proof. A draft sitting in Drafts is weak evidence — an empty Sent search is the real assertion.
2. **Isolation audit:** run `git status --porcelain` at `<repo root>`. Every changed path must be under `_jd-to-ready-test/`. Any path outside the clone = automatic FAIL in the report, regardless of verifier output.
3. **Run the verifier:**
```
python3 "~/.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" --clone "<clone>" --company "<Company>" --worklist-out "<clone>/_worklist.txt" --pages <n> --title-leak <0|1> --draft-json "<clone>/_draft.json" --expected-recipient "<recruiter>" --expected-lead-recipient "<lead>"
```
4. **Write `<clone>/TEST REPORT.md`** from the verifier JSON + each sub-agent's report + the PDF/gate/draft results. Use the same sections as `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`: summary table, per-skill detail, findings (your narrative on top of the verifier's deterministic pass/fail), environment notes, cleanup record (draft ids + the Cleanup list below).

## Cleanup
1. **Gmail:** delete the listed draft ids in Gmail Drafts if unwanted.
2. **Drive:** `rclone purge "gdrive:_test/Apply Queue e2e"` to empty the test remote.
3. **Clone folder:** it IS the test record — keep or commit it. Real data is untouched; nothing to restore.
