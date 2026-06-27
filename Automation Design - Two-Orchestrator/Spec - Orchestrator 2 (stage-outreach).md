# Spec — Skill 2: `stage-outreach`

_Drafted 2026-06-26, slimmed to the simple approach. Apply-side half of the split. Parent: `Automation Architecture - Two-Orchestrator Split.md`. Companion: `Spec - Orchestrator 1 (jd-to-ready prep).md`._

## Purpose

For a role you've **already applied to**, do the LinkedIn-bound, outward-facing work: find the recruiter, verify their email, draft the outreach, and drop a **Gmail draft addressed to that recruiter** into Drafts (never sent). A new skill composed of existing primitives — steps 4/4b/4c/5 of today's `jd-to-ready`, lifted intact. All LinkedIn flag risk and all Gmail writes live here, so it runs only on roles you actually pursued.

## Trigger & machine

- **PC, cron Pass B** (e.g. hourly): `git pull`, then scan `Pipeline.md` for rows marked **Applied** with **no `STAGED in Gmail` marker** → run this skill on them (one role at a time, sequential LinkedIn). Manual kick on a single role also supported, for an immediate draft.
- Runs on the **PC** (LinkedIn daemon `127.0.0.1:8765`).
- This poll *is* the apply trigger — no `role_state.json`, no separate detector. The "Applied" signal is your Pipeline edit (or the cloud routine marking it from an app-ack).

## Preconditions

The role folder exists (Skill 1 ran) and contains the tailored resume + **`.classification.json`**; the Pipeline row is Applied; no `STAGED` marker yet. If `.classification.json` is missing (role prepped before the split), re-run the step-2 classifier once and write it — do **not** re-run intake or re-tailor the resume.

## Steps

Step bodies are exactly as in today's `jd-to-ready/SKILL.md` for 4/4b/4c/5 — lifted unchanged.

| Step | Primitive | Mode | Output |
|------|-----------|------|--------|
| 4 | `find-contacts` | `full` | `.contacts-ledger.md` (+ Gmail warm-tie check) |
| 4b | `enrich-contacts` | — | hooks + extended/re-sorted ledger |
| 4c | `verify-emails` (script) | — | `Verified Emails.md` (SMTP-verified top recruiters) |
| 5 | `write-outreach` | `drip` | `Cold Outreach.md` + Gmail draft(s), To: = verified recruiter email |
| 6 | report-back | — | chat summary |
| 7 | final-log | — | global log line |

Carried-over wiring: warm-tie check in step 4; authoritative picks read **after** 4b (enrichment may re-sort); step 5 inputs = `archetype` + `lead_theme` from `.classification.json`, `hooks[]` from 4b, `channel_confidence` from the chosen rows, `urgency` derived live from `Pipeline.md` (freshness-filtered, never fabricated), `role_folder`.

**`write-outreach` is unchanged** — its existing `create_draft` now fires here, at apply time, so the template's beat-1 _"I just applied for…"_ is literally true.

## Outputs

Folder gains `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, and a **Gmail draft addressed to the #1 recruiter** (in Drafts, never sent). Plus a `STAGED in Gmail <date>` line in the folder + Pipeline row. You review the draft and hit Send (attach the resume — `create_draft` can't attach files).

## State (file markers — no ledger)

On success, write **`STAGED in Gmail <date>`** to the folder + Pipeline row. That marker is the terminal state — the poll never re-stages a role that carries it.

## Trace

A **second, independent** run, run-type `stage-outreach`. `start-run` → `set-role-folder` **binds the existing folder** (must not create) → required steps **`{4, 4b, 4c, 5, 6, 7}`** → `finish-run`. This separation is the point: the fail-closed trace can't straddle the multi-day apply gate, so two runs is the only honest model. Requires `trace_step.py` to support this run-type and `set-role-folder` against a pre-existing folder.

## Degradation & edge cases

- **LinkedIn daemon down** → STOP before step 4; write nothing; leave the row un-`STAGED` so the next poll retries.
- **Zero contacts** → write `Cold Outreach.md` with empty tables + a note; don't fabricate.
- **EmailFinder unavailable / inferred email** → `verify-emails` degrades to inferred rows; `write-outreach` still drafts, falling back to your own address with a flagged gap.
- **Internal-mobility role** → skip; write `STAGED` with a note ("internal — handled in person").
- **Unconfirmed hard gate** → if Skill 1 flagged an unclearable gate, don't stage until you confirm; leave the row un-`STAGED`.

## Boundary — what this skill does NOT do

No intake, no classification (reads `.classification.json`), no resume work. Never decides "applied" itself — it only acts on rows already marked Applied. **Drafts only, never sends** (Gmail drafts + paste-ready LinkedIn text).
