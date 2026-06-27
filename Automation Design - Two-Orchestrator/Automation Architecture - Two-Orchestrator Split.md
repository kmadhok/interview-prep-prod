# Automation Architecture — Two-Orchestrator Split (apply-gated outreach)

_Drafted 2026-06-26, revised to the simple approach. Design for splitting the monolithic `jd-to-ready` run into two apply-gated skills so contact research + Gmail drafts only happen for jobs Kanu actually applies to. Diagrams: `Automation Architecture - Diagrams.md`. Specs: `Spec - Orchestrator 1 (jd-to-ready prep).md`, `Spec - Orchestrator 2 (stage-outreach).md`. Status: design agreed, not yet built._

## The decision

Today `jd-to-ready` runs all 7 steps in one shot on **every saved job** — including the expensive, flag-risky LinkedIn research and the outward-facing Gmail drafts. That burns LinkedIn budget and piles up drafts for jobs Kanu never applies to.

**Split it at the apply gate into two skills, with all LinkedIn research on the post-apply side:**

| | Skill 1 — `jd-to-ready` (prep) | Skill 2 — `stage-outreach` (new) |
|---|---|---|
| **Fires on** | job saved (daily cron) | row marked Applied (hourly poll) |
| **Steps** | 1 intake · 2 classify · 3 resume · 3.5 PDF | 4 find-contacts · 4b enrich · 4c verify-emails · 5 write-outreach (+Gmail draft) |
| **LinkedIn?** | only the trigger/JD fetch | yes (research) |
| **Gmail?** | no | yes (draft, never sent) |
| **Produces** | resume `.md`+`.pdf`, `.classification.json` | `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, Gmail draft to recruiter |

The primitives don't change — only the compose layer is recut. `write-outreach` is **untouched**: its `create_draft` now fires inside Skill 2, i.e. at apply time, which also makes the template's beat-1 _"I just applied for…"_ true.

## Both skills run on the PC — and why the cloud can't take more

The PC is the only LinkedIn-capable machine, and **every entry point is a LinkedIn-MCP call**: detecting a save (`get_saved_jobs`) and fetching the JD (`get_job_details`) are daemon-bound, just like contact scraping. So the cloud can't *start* either flow. Moving the cheap downstream steps (resume, verify, draft) to the cloud would only split a dependency chain across machines connected by git + two schedules — more architecture, not less. The rule: **don't split a dependency chain across machines.** Keep each chain whole on the PC.

The cloud routine keeps the one job it can do daemon-free: the **Gmail secretary** — sweep inbox → reconcile `Pipeline.md`, detect sent drafts, archive rejections. (It **drops its step-3 drafting**; all drafting moves to Skill 2, which has the contacts.)

## State = file markers (no ledger)

No `role_state.json`, no separate apply-detector. State is read from files that already exist:

| State | How it's read | Set by |
|---|---|---|
| `saved` | in LinkedIn saved list, no folder / not in `saved_seen.json` | you (LinkedIn Save) |
| `prepped` | role folder has a tailored resume `.md` | Skill 1 |
| `applied` | Pipeline row marked **Applied** | you (or cloud routine, from an app-ack) |
| `staged` | `STAGED in Gmail <date>` in folder + Pipeline row | Skill 2 |

Worklists are plain reads:
- **Skill 1** (daily): saved jobs not terminal in `saved_seen.json` with no folder.
- **Skill 2** (hourly): Pipeline rows marked Applied with **no `STAGED` marker**.

The hourly poll *is* the apply trigger — it reads the "Applied" signal you (or the cloud routine) already write, and directly kicks Skill 2. `saved_seen.json` stays exactly as it is (ingestion dedup); nothing new is added.

## Topology

```
PC cron:
  Pass A (daily)  — get_saved_jobs → get_job_details → Skill 1 (resume) → commit/push
  Pass B (hourly) — git pull → Pipeline rows "Applied" & not "STAGED"
                    → Skill 2 (find recruiter → verify email → Gmail draft to recruiter) → commit/push

Cloud routine (2×/weekday, unchanged minus drafting):
                    Gmail → reconcile Pipeline, detect sends, archive rejections → push
```

After you apply and mark the row Applied, the next hourly pass scrapes the recruiter, verifies their email, and drops a Gmail draft addressed to them. You review and send. Manual kick of Skill 2 is available when you want the draft immediately.

## The hand-off is free; the trace split is mandatory

- **Hand-off:** the skills talk through disk artifacts that already persist (`.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`). The only new artifact is `.classification.json`, so Skill 2 gets `archetype`/`lead_theme` without re-classifying. No in-memory state crosses the gate.
- **Trace:** two independent traced runs, not one. The current trace is fail-closed (one active run, required steps must close before `finish-run`) and **cannot stay open across the multi-day apply gate** — so the split isn't just tidy, it's what the observability layer already requires.

## Build list

1. **`jd-to-ready` SKILL.md** — remove steps 4/4b/4c/5; add the `.classification.json` write; trim required-steps to `{1,2,3,3.5,6,7}`.
2. **`stage-outreach` SKILL.md** (new) — steps 4/4b/4c/5/6/7, reading folder + `.classification.json`; required-steps `{4,4b,4c,5,6,7}`; binds trace to an existing folder.
3. **`write-outreach`** — no change.
4. **`trace_step.py`** — two run-types (`jd-to-ready` / `stage-outreach`) with different required-steps lists; allow `set-role-folder` against an existing folder.
5. **PC cron Pass A** — saved-jobs sweep → Skill 1 (extend the existing drip runner, minus outreach).
6. **PC cron Pass B** — hourly `Pipeline.md` poll (Applied & not STAGED) → Skill 2. A tiny deterministic worklist reader (no LLM) over Pipeline.md; pytest-covered like `dedupe.py`.
7. **Cloud routine** — drop step-3 drafting; keep sweep/reconcile/send-detect/archive.
8. **Docs** — update `Automation Architecture - Drip Runner.md` + the Drip Runner README to this two-skill model.

## Risks / open questions

- **Applied-but-not-recorded.** If you apply but never mark the row Applied, Skill 2 never fires. Mitigation: the cloud routine already marks Applied from Gmail app-acks; manual marking is the backstop.
- **Draft latency.** The hourly poll means the draft appears up to ~an hour after you mark Applied. Use the manual kick when you want it now.
- **Stale resume at apply time.** Resume is built on save; if `Resume Achievements Master.md` changed before you applied, it could be slightly behind (JD is static, so themes stay valid). Flag in Skill 2's report if the resume predates the last Master edit.
- **Cloud step-3 drafting.** Retired here so there's one drafter (the PC). The `STAGED` marker is the safety net during any overlap. Alternative: keep it as a folder-contacts-only fallback — open.
- **Multiple repo writers** (PC passes + cloud routine) — `git pull` first; `drip-runner:` commit prefix.
