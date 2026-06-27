# PC Handoff — Two-Orchestrator Split, Tasks 8 & 9

> **You are a fresh session on Kanu's always-on PC.** Tasks 1–7, 10, 11 of the two-orchestrator split are already built, tested, and committed on this branch (`worktree-two-orchestrator-split`). Your job is the two remaining tasks that can only be built/tested on the PC (LinkedIn daemon + live Gmail): **Task 8 (cloud routine → pure secretary)** and **Task 9 (PC cron Pass A & Pass B)**. This file is self-contained — you do not need the original chat.

## 0. Orient yourself first (do this before any edits)

```bash
git fetch origin
git checkout worktree-two-orchestrator-split
git pull
```

Then **read these, in order** — they are the source of truth, this handoff only summarizes:

1. `docs/superpowers/plans/2026-06-27-two-orchestrator-split.md` — the full implementation plan. **Task 8 = its "Task 8", Task 9 = its "Task 9".** Follow those task bodies; this file adds PC-specific ground truth + the things that changed during the Mac build.
2. `Automation Design - Two-Orchestrator/Spec - Applied Detector.md` — the spec Task 8 implements (ack ruleset, cadence split, monotonic guard, fail-loud nudge). This is the authority for Task 8's rules.
3. `Automation Design - Two-Orchestrator/Automation Architecture - Two-Orchestrator Split.md` — the "Build list" section (annotated with ✅/⏳ status) and the **two integration findings** at the bottom. Read the findings — one is a tripwire for Task 9.
4. `scripts/drip_runner/README.md` and `Automation Architecture - Drip System (Complete Reference).md` — how the existing PC runner + cloud routine work today.

**Verify the build you're extending is green** (the PC has no `.venv-test`; use the project's Python):

```bash
py -3 -m pytest .claude\skills\jd-to-ready\scripts\test_trace_step.py scripts\drip_runner -q
```

Expected: **58 passed**. (52 unit + 6 lifecycle integration.) If not, stop and investigate before building on top.

## 1. What is already built (do NOT rebuild these)

| Piece | File | Status |
|---|---|---|
| Trace run-types `jd-to-ready` / `stage-outreach` / `full` | `.claude/skills/jd-to-ready/scripts/trace_step.py` | ✅ tested |
| `--run-type` on `start-run`; `run_type` in state + summary | same | ✅ |
| `set-role-folder` binds an existing folder | same | ✅ |
| **Pass B worklist reader** | `scripts/drip_runner/outreach_worklist.py` | ✅ tested + live-smoke-validated |
| **Prepped-not-applied nudge reader** | `scripts/drip_runner/prepped_not_applied.py` | ✅ tested + live-smoke-validated |
| `jd-to-ready` SKILL recut to prep half (+ `.classification.json`) | `.claude/skills/jd-to-ready/SKILL.md` | ✅ |
| `stage-outreach` SKILL (new, apply side) | `.claude/skills/stage-outreach/SKILL.md` | ✅ |
| End-to-end lifecycle test | `scripts/drip_runner/test_lifecycle_integration.py` | ✅ |

**The two readers are the deterministic core of Pass B / the nudge — they exist and work. Task 9 only wires the SCHEDULERS that call them; Task 8 only edits the cloud prompt. No new Python logic should be needed for the readers.**

Reader CLIs (already validated against the live `Pipeline.md`):

```powershell
py -3 scripts\drip_runner\outreach_worklist.py --pipeline Pipeline.md
#   -> prints "Company<TAB>Role" for each Active row that is Applied & not STAGED (the Pass B worklist)

py -3 scripts\drip_runner\prepped_not_applied.py --roles-dir Roles --pipeline Pipeline.md --threshold-days 3
#   -> prints "Company<TAB>Role<TAB>ageDays" for prepped roles never applied/closed, older than N days (the nudge)
```

---

## TASK 9 — PC cron Pass A & Pass B (PowerShell ops)

**Do Task 9 before Task 8** — Task 9 is the PC half you can test end-to-end with the daemon; Task 8 touches live Gmail and is best done once the PC side is proven.

### Ground truth about the existing PC runner (verified on the Mac build)

- `scripts/drip_runner/run.ps1` — `param([ValidateSet('saved','email')][string]$Mode='saved')`. It does `git pull --rebase`, then picks the prompt file (`runner-prompt-saved.md` for saved, `runner-prompt.md` for email) and invokes Claude on it. This is the pattern Pass A/Pass B follow.
- `scripts/drip_runner/install-tasks.ps1` — registers **`LinkedInDaemon`** (at logon) and **`DripRunner`** (daily 05:00 Central, ENABLED, 3h limit, `MultipleInstances IgnoreNew`). Re-runnable.
- `scripts/drip_runner/runner-prompt-saved.md` — the saved-jobs prompt. Today it runs `jd-to-ready` **end-to-end** (the OLD monolith). Under the split it must run jd-to-ready **PREP-only** (the SKILL.md is already recut, so the skill itself stops at the apply gate — but the prompt's wording/expectations may still mention outreach/drafts; align them).

### 🚨 TRIPWIRE — fix this as part of Task 9 (Pass A)

`scripts/drip_runner/runner-prompt-saved.md` **line 20** currently instructs, at SAVE time:

> "On success: add the Pipeline.md row (`Considering - JD reviewed, not yet applied`) and **write `STAGED in Gmail <today's date>` in both the role folder and the Pipeline row**."

**Under the split this is wrong and will silently break apply-side staging.** Reason: `outreach_worklist.applied_not_staged` excludes any row carrying `STAGED in Gmail`. If a saved role gets that marker at save-time and Kanu later marks it Applied, the worklist will skip it → **`stage-outreach` never fires → outreach is silently never staged** for a role he applied to (the exact silent-failure the whole design fights).

**Fix:** remove the save-time `STAGED in Gmail` write from `runner-prompt-saved.md`. Under the new model the `STAGED` marker is written ONLY by `stage-outreach` (Pass B), ONLY after Kanu applies. Pass A's prompt should stop at: folder + resume + `.classification.json` + a `Considering` Pipeline row whose Next-action says *"Resume ready — apply on the ATS; outreach auto-stages once the row is marked Applied."* (It's harmless TODAY only because the worklist section-scopes to `## Active` and these are `Considering` rows — but it becomes a live bug the moment such a role is applied.)

### What to build (Task 9)

Follow the plan's Task 9 body. In short:

1. **Pass A (daily — prep on save).** Either confirm the existing `DripRunner`/`run.ps1 -Mode saved` path now (a) runs jd-to-ready PREP-only and (b) no longer writes the save-time STAGED marker — or add an explicit Pass A. Keep the `git pull --rebase` first, the 6-role cap, the `drip-runner:` commit prefix, per-role commit/push.
2. **Pass B (hourly — outreach on apply).** New path: `git pull --rebase` → `py -3 scripts\drip_runner\outreach_worklist.py --pipeline Pipeline.md` → for each `Company<TAB>Role` returned, resolve the folder under `Roles\` and invoke the **`stage-outreach`** skill on it, **one role at a time** (sequential LinkedIn — never parallel; see `linkedin-mcp-operations`). Commit `drip-runner:` + push. If the worklist is empty, no-op (don't commit).
   - `stage-outreach` opens its OWN trace run: `trace_step.py start-run --run-type stage-outreach ...` then `set-role-folder --role-folder <existing folder>` (binds, doesn't create). Required steps `{4,4b,4c,5,6,7}`.
3. **Register Pass B** in `install-tasks.ps1` as an hourly scheduled task, mirroring the `DripRunner` registration style (per-user trigger, `MultipleInstances IgnoreNew`, `git pull` first since multiple writers: Pass A + Pass B + cloud routine).

### How to verify Task 9 (manual — there is no unit test for PowerShell/LLM prompts)

- **Pass B idempotency (the critical property):** pick a role you've marked `Applied` in `Pipeline.md` with no `STAGED` marker. Run Pass B by hand. Confirm it (a) scrapes the recruiter, (b) creates a Gmail **draft** (never sent), (c) writes `STAGED in Gmail <date>` to the folder + Pipeline row. **Run Pass B a SECOND time** and confirm the now-STAGED role is **skipped** (no duplicate draft). This is the contract `test_staged_marker_removes_from_worklist_idempotent` proves at the reader level — verify it end-to-end with the real skill.
- **Pass A:** save a fresh job on LinkedIn, run Pass A, confirm it produces a prepped folder (resume `.md` + `.classification.json`) and a `Considering` Pipeline row with **NO** Gmail draft, **NO** contacts, and **NO** `STAGED` marker.
- **LinkedIn daemon down:** confirm Pass B stops before scraping and leaves the row un-STAGED (so the next poll retries) — per `stage-outreach` SKILL.md degradation rules.

---

## TASK 8 — Cloud routine → pure Gmail secretary

The cloud routine is an **external cloud scheduled agent** (a `/schedule` routine, id `trig_01Dhy19jRLQM6sggLQ4249rm` per the design docs) — its prompt is NOT a file in this repo. You edit it through the scheduled-agent UI (`/schedule`), using `Spec - Applied Detector.md` as the authority. Mirror any prompt text you settle on into the repo docs so it's reviewable.

Follow the plan's Task 8 body + `Spec - Applied Detector.md`. The four changes:

1. **Drop step-3 drafting.** The cloud routine must STOP drafting outreach. All drafting now happens on the PC via `stage-outreach` (which has the scraped contacts). The routine becomes: sweep Gmail → reconcile `Pipeline.md` → mark Applied from acks → detect sent drafts → archive rejections. **No drafting.** Add a one-line note that drafting moved to the PC's `stage-outreach`.
2. **Ack ruleset** (from `Spec - Applied Detector.md` §Channel 1): a thread marks a role `Applied` IFF (a) from the employer/ATS — greenhouse/lever/workday/icims/ashby/smartrecruiters/myworkdayjobs or the company's own domain, NOT a staffing agency/job board; (b) body matches an ack pattern ("thank you for applying", "your application has been received", etc.); (c) maps to an existing Pipeline row. **NOT acks:** LinkedIn/Indeed "application sent" alerts, staffing-agency mail, newsletters. An ack with **no matching Pipeline row → do NOT auto-create a role**; flag in the audit note for manual intake.
3. **Monotonic-state guard:** never downgrade a row already past `Applied` (interview/offer) because an old ack got re-swept. A rejection supersedes Applied → move Active→Closed, `git mv` folder to `_Archived/`, dated audit note.
4. **Fail-loud nudge:** after reconcile, run the nudge reader and surface its output in the report:
   ```powershell
   py -3 scripts\drip_runner\prepped_not_applied.py --roles-dir Roles --pipeline Pipeline.md --threshold-days 3
   ```
   For each line emit: *"<Company> — <Role>: resume built <N> days ago, no Applied mark and no ack seen. Did you apply? Mark the row to auto-stage outreach."*
   - **Note:** the nudge reader runs Python; if the cloud routine can't run `py -3` against the repo, compute the nudge on the PC (e.g., a daily Pass C, or fold it into Pass A's report) instead. Decide based on what the cloud agent can execute. The requirement is that the gap is made LOUD somewhere Kanu sees daily — not which machine prints it.
5. **Keep the no-op guard:** "if nothing changed, don't commit/push" so frequent runs stay silent. The spec also recommends raising the secretary cadence (hourly/30-min) once drafting is removed — optional, but it's what makes `applied` near-real-time.

### How to verify Task 8
- Re-read `Spec - Applied Detector.md` §Channel 1 / §Cadence / §Reconciliation / §Fail-loud and confirm each rule is in the prompt.
- Dry-run the routine against your real inbox once; confirm it marks Applied only on genuine employer acks, never auto-creates a role from an unmatched ack, never downgrades a past-applied row, and emits the prepped-not-applied nudge.

---

## When both are done

1. Run the full suite again on the PC: `py -3 -m pytest .claude\skills\jd-to-ready\scripts\test_trace_step.py scripts\drip_runner -q` → still **58 passed** (Tasks 8/9 add no Python unit tests; they're ops + prompt edits).
2. Update the build-list status in `Automation Design - Two-Orchestrator/Automation Architecture - Two-Orchestrator Split.md` (flip items 5/6/7 from ⏳ to ✅) and flip the design-folder "PARTIALLY BUILT" status lines to "BUILT".
3. Commit with the `drip-runner:` or `feat(...)` convention; push the branch.
4. **Then merge `worktree-two-orchestrator-split` → `main`** as one complete, live-tested unit (or open the PR). Only merge after you've live-tested Pass A, Pass B (incl. the idempotency re-run), and the cloud secretary against real Gmail + the LinkedIn daemon.

## Invariants — judge every change against these (from `Automation Architecture - Purpose.md`)
1. **Human-gated — never sends.** Drafts only. The send is always Kanu's.
2. **Protect the LinkedIn channel.** Expensive LinkedIn work only for jobs Kanu actually applies to (Pass B / apply-gated), never for the saved pile.
3. **No babysitting.** Apply + send are the only required human inputs.
4. **Fail loud, never silent.** The nudge exists because a dropped warm-outreach on a role he cared about is the worst failure.
5. **Truth from files that already exist.** No `role_state.json`; state = resume `.md` (prepped), Pipeline `Applied` token (applied), `STAGED in Gmail` marker (staged).
