# Determinism Audit — Pipeline Skills (Plan 3, Task 3)

Spec: docs/spec/productionalization-v1.md (workstream 3, Decision 7, success criterion 3).
Principle: before any skill step is LLM reasoning, justify why it can't be a
deterministic tool. Classification below: **tool** (already a deterministic
call), **LLM-judgment** (genuinely probabilistic — language, ranking,
interpretation; stays LLM), **extract** (LLM-instructed today but mechanical —
move to a script).

The trace makes drift visible: `tool_event` count vs step count per run is the
tool/LLM ratio (rendered in `runs/<run-id>/report.md`).

## Classification

| Behavior | Step | Class | Notes |
|---|---|---|---|
| intake | parse JD from paste/email | tool (partial) | `scripts/drip_runner/job_parser.py` covers email/paste; free-form paste fallback stays LLM-judgment |
| intake | role-folder naming + creation | **extract** | naming rule is fixed (`Company - Role Title`, collision check) — prose-instructed today |
| intake | write Job Description.md | LLM-judgment | cleaning a messy JD into a reading copy is language work |
| intake | Pipeline row insert | **extract** | fixed table shape; hand-edited by LLM today in 3 skills |
| intake | memory update | tool-adjacent | harness memory write; no-op gap on headless runs (existing rule) |
| classify | themes + archetype | LLM-judgment | the routing decision — core judgment |
| classify | .classification.json write + vocab check | **extract** (validator) | schema/vocab enforcement is mechanical; today the LLM self-checks |
| tailor-resume | bullet selection + tailoring | LLM-judgment | core language/ranking work |
| tailor-resume | canonical-only provenance | **extract** (checker) | grep-class check against Resume Achievements Master; today prose-enforced |
| tailor-resume | filename | tool | `config.resume_filename()` (landed in plan 1) |
| resume-export | PDF render + layout verify | tool | `build_resume_pdf.py`, `verify_resume.py` |
| resume-export | vision verification | LLM-judgment | visual gold-standard comparison |
| apply-packet | packet build + upload | tool | `apply_packet.py` |
| apply-packet | posted-date resolution | LLM-judgment + tool | WebFetch + interpretation of ATS pages |
| apply-packet | ATS answers from Application Profile | LLM-judgment | mapping profile facts onto arbitrary form questions; zero-invention contract enforced by eval |
| find-contacts | LinkedIn searches | tool (MCP) | sequential-only invariant |
| find-contacts | candidate scoring | LLM-judgment | fuzzy titles/org matching against rubric |
| find-contacts | ledger write + sort | **extract** (deferred) | table emit/re-sort is mechanical; medium value |
| enrich-contacts | activity reading | tool (MCP) + LLM-judgment | hook quality is judgment |
| enrich-contacts | ledger append/re-sort | **extract** (deferred) | same ledger helper as above |
| verify-emails | EmailFinder calls | tool | cached |
| verify-emails | Verified Emails.md write | **extract** (deferred) | fixed format, small |
| write-outreach | drafting | LLM-judgment | core voice/taste work |
| write-outreach | format check | tool (partial) | format-check step exists; linter candidate deferred |
| write-outreach / stage-outreach | STAGED marker write | **extract** | invariant-critical ("never write STAGED except from stage-outreach on Applied") — exactly what a guarded tool should own |
| write-outreach | Gmail draft creation | tool (MCP) | draft-never-send invariant |

## Extraction list

**Task 4 (extract now — highest leverage, invariant-bearing):**

1. `scripts/pipeline_row.py` — add-considering / mark-applied / append-staged-marker
   operations on `workspace/Pipeline.md`. Consumers: intake, track-application,
   stage-outreach. Owns the STAGED invariant (refuses to append STAGED to a row
   not marked Applied) and the table shape.
2. `scripts/role_folder.py` — canonical folder name from company+role
   (sanitization, collision detection, `workspace/Roles/` vs `_Archived/`
   awareness). Consumer: intake (+ e2e clone naming).

**Deferred (listed, not extracted in v1 — value < churn right now):**

- Ledger emit/re-sort helper (find-contacts/enrich-contacts) — wait until the
  ledger format survives a few more live runs.
- Classification validator as a runtime tool — the eval verifier covers the
  same check post-hoc; promote only if classify drift shows up in eval history.
- Verified Emails writer, outreach format linter — small, low churn.

## Ratio baseline

After Task 4 lands, a healthy jd-to-ready run should show ≥1 tool_event for
every LLM-judgment step except classify/report-back (pure judgment). Eval
history (clause pass rates + tool/LLM ratio from traces) is the drift signal.
