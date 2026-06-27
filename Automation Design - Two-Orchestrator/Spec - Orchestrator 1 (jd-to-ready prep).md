# Spec — Skill 1: `jd-to-ready` (prep)

_Drafted 2026-06-26, slimmed to the simple approach. Save-side half of the split. Parent: `Automation Architecture - Two-Orchestrator Split.md`. Companion: `Spec - Orchestrator 2 (stage-outreach).md`._

## Purpose

Turn a **saved LinkedIn job** into an **apply-ready resume**, doing only cheap, local, no-flag-risk work. Stops at the apply gate — no contact research, no outreach, nothing outward-facing. This is today's `jd-to-ready` with steps 4/4b/4c/5 removed and a `.classification.json` hand-off added.

## Trigger & machine

- **PC, cron Pass A** (e.g. daily): `get_saved_jobs` → for each new job `get_job_details` → run this skill.
- Runs on the **PC** because both the save-detection and JD fetch are LinkedIn-MCP calls. (Manual run on a single JD also supported.)
- Worklist = saved jobs whose `job_id` is not terminal in `saved_seen.json` and have no role folder yet.

## Preconditions

- A JD is resolvable (LinkedIn `job_id`, or an ATS URL via WebFetch).
- The role folder does **not** already exist. If it does → stop and ask (refresh / variant / skip). Never overwrite.

## Steps

Run 1 → 7; numbers stay aligned with today's `jd-to-ready` (4/4b/4c/5 are simply absent here). Step bodies are exactly as in the current `jd-to-ready/SKILL.md` — this spec only defines the boundary and the new artifact.

| Step | Primitive | Output |
|------|-----------|--------|
| 1 | `interview-prep-intake` | folder, `Job Description.md`, Pipeline row (`Considering — JD reviewed, not yet applied`), memory |
| 2 | inline classifier subagent | `themes[]` + `archetype` → **`.classification.json`** |
| 3 | `tailor-resume` (`pipeline`) | `Kanu Madhok Resume - <Company> <Short Role>.md` |
| 3.5 | `build_resume_pdf.py` + `verify_resume.py` | `…<Short Role>.pdf` |
| 6 | report-back | chat summary |
| 7 | final-log | `~/.claude/logs/jd-to-ready.jsonl` |

### New artifact — `.classification.json`

Step 2 already computes the classification for the resume; persist it so Skill 2 reuses `archetype` + top theme without re-classifying:

```json
{
  "themes": [ {"tag": "agents", "evidence": "<JD quote ≤25 words>"} ],
  "archetype": "agent-builder",
  "archetype_rationale": "<1–2 sentences>",
  "notes": "<subagent notes or empty>",
  "classified_ts": "2026-06-26"
}
```

Written to `<role folder>/.classification.json`. Same validated values passed to `tailor-resume` — just a write to disk, no new logic.

## Outputs

Folder contains: `Job Description.md`, the tailored resume `.md` + `.pdf`, `.classification.json`. Plus a `Considering` row in `Pipeline.md` and a memory entry. **Nothing in Gmail. No contacts. No outreach.**

Set the Pipeline row's **Next action** to something like _"Resume ready — apply on the ATS; outreach auto-stages once the row is marked Applied."_ so the apply poll and you both know prep is done.

## State (file markers — no ledger)

- **`prepped`** = the role folder contains a tailored resume `.md`.
- Also mark `saved_seen.json[<job_id>].status = "done"` so the saved-jobs sweep never re-ingests. ATS/email roles with no `job_id`: the existing folder is the dedup authority.
- No `role_state.json`. Skill 2's worklist keys off `Pipeline.md` (Applied) + the `STAGED` marker — see its spec.

## Trace

Its own run, run-type `jd-to-ready`, required steps **`{1, 2, 3, 3.5, 6, 7}`** → `finish-run`. Requires `trace_step.py` to support a run-type whose required-steps list excludes 4/4b/4c/5.

## Degradation & edge cases

- **Folder exists** → stop and ask (no overwrite).
- **Thin/unparseable JD** → still file it; flag `thin-jd-stub`.
- **PDF export unavailable** → `.md` is source of truth; log `export-unavailable`; continue.
- **Internal-mobility role** → prep the resume; note Skill 2 will be skipped (internal contacts handled in person).
- **Likely-unclearable hard gate** (e.g. TS/SCI) → prep resume; flag prominently so you can decide before applying.

## Boundary — what this skill does NOT do

No LinkedIn contact research, no email verification, no `write-outreach`, **no Gmail drafts**. Does not advance past `prepped`; everything after the apply gate is Skill 2's.
