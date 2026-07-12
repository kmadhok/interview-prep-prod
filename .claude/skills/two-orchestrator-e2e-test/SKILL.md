---
name: two-orchestrator-e2e-test
description: Run the two-orchestrator pipeline contract test in an isolated clone. Local fixture clauses always run; LinkedIn/Gmail live-only clauses are BLOCKED when their MCPs are unavailable. Never touches real Roles/Pipeline and never sends.
---

# Two-Orchestrator E2E Test (contract-driven, isolated clone)

Runs one fixture role through all behaviors in a throwaway clone. Real
`Roles/` and `Pipeline.md` are never touched. By default there are **no
external side effects**. `evals/<behavior>/contract.md` is authoritative;
`verify_artifacts.py` delegates to those verifiers and preserves its legacy
CLI/report shape.

`<repo root>` = the directory containing `profile.yaml` (cwd); the workspace files live under `<repo root>/workspace/`. Use `python3` (Windows: `py -3`).

**Test steps are numbered T0–T8** — deliberately NOT the real skills' step numbers. Each step header names the real skill step it exercises, so cross-reference by that annotation, never by the T-number.

## What this skill does NOT do
No real Pipeline/Roles writes, sends, production Drive uploads, or implicit
LinkedIn/Gmail calls. Every primitive uses a closed `--run-type primitive`
trace in the isolated clone's `TRACE_RUNS_DIR`: start, begin with
`--contract-clauses`, end with verifier `--clause-results`, then finish before
yielding. Live-only results are `BLOCKED`/`NOT_RUN`, never synthesized PASS.

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
5. Every worker prompt MUST include: "Operate ONLY in `<clone>`. Do NOT touch
real Roles/ or Pipeline.md. Use closed primitive traces under the clone. Do
NOT send anything."

## T1–T3 — Prep sub-agents (sequential)
Launch a fresh `general-purpose` sub-agent per skill; wait for each, then run its verifier check before the next.

- **T1 — intake** (real: `interview-prep-intake`) → writes `<clone>/Job Description.md`. (Tell it to skip the Pipeline row — the fixture already has it.)
- **T2 — classify** (real: jd-to-ready Step 2) → writes `<clone>/.classification.json`. Give it the theme/archetype vocab from `.claude/skills/jd-to-ready/SKILL.md` Step 2.
- **T3 — tailor-resume** (real: `tailor-resume`) → writes `<clone>/<user_name> Resume - <Company> <Short Role>.md` (user_name from profile.yaml; canonical-only).

## T4 — PDF (main loop; real: jd-to-ready Step 3.5)
```
python3 "<repo root>/scripts/build_resume_pdf.py" "<clone>/<user_name> Resume - <Company> <Short Role>.md"
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
2. **Optional live preflight:** only when the user explicitly requests a live
run, invoke `linkedin-mcp-operations`. Handshake:
```
curl -s -o /dev/null -w '%{http_code}\n' -m 6 -X POST http://127.0.0.1:8765/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"0.1"}}}'
```
If unavailable, do not attempt LinkedIn. Run local contact fixtures and mark
only each contract's live-only clause `BLOCKED`. `--blocked-apply` remains for
backward compatibility when the entire apply side did not run.

## T7 — Apply sub-agents (sequential — one LinkedIn stream at a time, never parallel; real: stage-outreach Steps 4/4b/4c/5)
- **T7.1 — find-contacts** → build `<clone>/.contacts-ledger.md` from fixture evidence; live LinkedIn identity clause is BLOCKED when unavailable.
- **T7.2 — enrich-contacts** → update the ledger with fixture hooks/provenance; live activity clause is BLOCKED when unavailable.
- **T7.3 — verify-emails** (real: stage-outreach Step 4c) → `<clone>/Verified Emails.md` (real EmailFinder; degrade to inferred if unavailable).
- **T7.4 — write-outreach** → `<clone>/Cold Outreach.md` plus normalized
`<clone>/.drafts.json` fixture records with `sent:false`. Gmail Draft/Sent
evidence is a separate live-only clause.

## T8 — Verify + report (main loop)
1. **Confirm the drafts** (skip this sub-step on a blocked apply side — go straight to the verifier with `--blocked-apply` and no `--draft-json`):
   - `mcp__claude_ai_Gmail__list_drafts` for each recipient (`query: "to:<recruiter>"` and `query: "to:<lead>"`).
   - Normalize each matched draft to exactly this shape and save the array to `<clone>/_draft.json`: `[{"id": "<draft id>", "toRecipients": ["<email>"], "sent": false}]` — the verifier reads `toRecipients` at top level; raw MCP draft objects may not carry it. If the guard suppressed one draft, save the single-element array — the verifier accepts one or two.
   - **Never-sent proof:** run `mcp__claude_ai_Gmail__search_threads` with `in:sent to:<recruiter> newer_than:1d` (and the same for the lead). Both must return zero results; record this in TEST REPORT.md as the never-sent proof. A draft sitting in Drafts is weak evidence — an empty Sent search is the real assertion.
2. **Isolation audit:** run `git status --porcelain` at `<repo root>`. Every changed path must be under `_jd-to-ready-test/`. Any path outside the clone = automatic FAIL in the report, regardless of verifier output.
3. **Run the verifier:**
```
python3 "~/.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" --clone "<clone>" --company "<Company>" --worklist-out "<clone>/_worklist.txt" --pages <n> --title-leak <0|1> --draft-json "<clone>/_draft.json" --expected-recipient "<recruiter>" --expected-lead-recipient "<lead>" --trace-runs-dir "<clone>/runs"
```
`--trace-runs-dir` is optional only for backward compatibility with historical
test records. New contract-driven runs must supply it; a missing or incomplete
primitive trace for any of the nine behaviors fails the E2E report.

For a fully local run with no external services:
```
python3 evals/run_eval.py --all --workspace "<fixture-workspace>"
python3 evals/verify_behavior_traces.py --runs-dir "<fixture-workspace>/runs"
```
LinkedIn/Gmail live clauses may be `BLOCKED`/`NOT_RUN`; both commands still
require every local artifact clause and every behavior trace to be present.
4. **Write `<clone>/TEST REPORT.md`** from the verifier JSON + each sub-agent's report + the PDF/gate/draft results. Use the same sections as `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`: summary table, per-skill detail, findings (your narrative on top of the verifier's deterministic pass/fail), environment notes, cleanup record (draft ids + the Cleanup list below).

## Cleanup
1. **Gmail:** delete the listed draft ids in Gmail Drafts if unwanted.
2. **Drive:** `rclone purge "gdrive:_test/Apply Queue e2e"` to empty the test remote.
3. **Clone folder:** it IS the test record — keep or commit it. Real data is untouched; nothing to restore.
