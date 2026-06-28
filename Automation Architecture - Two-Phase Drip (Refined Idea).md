# Automation Architecture — Two-Phase Drip (Refined Idea)

_Working doc, started 2026-06-23. This is a **proposal / scratchpad**, not a "how it runs today" reference. The canonical current-state doc is `Automation Architecture - Drip System (Complete Reference).md`. We work through the sections below one at a time; nothing here is built until a section is marked **DECIDED → BUILT**._

---

## 0. The problem we're solving

Today the saved-jobs drip runs the **whole** `jd-to-ready` skill on every saved job, end-to-end, including the two cold-outreach Gmail drafts. So every morning the draft box fills with outreach for roles I haven't actually applied to (and may never apply to). The drafts pile up, go stale, and crowd the real ones.

**The insight:** outreach only matters *after* I've applied. Resume tailoring matters *at save time* (so it's ready the moment I want to apply). Those are two different moments — so split the pipeline at that seam.

---

## 1. The refined idea (one paragraph)

Saving a job kicks off a **resume phase** only: tailor + file the resume/PDF and add a "Considering" Pipeline row, then commit/push. **No contacts, no outreach, no drafts.** I review the resume and apply to the role myself. Once the system knows I've applied, it kicks off the **outreach phase**: contact research, email verification, and the two cold-outreach drafts. Net effect: the draft box only ever holds outreach for roles I've genuinely applied to.

```
SAVE on LinkedIn ──▶ [Resume Phase]  resume + PDF + "Considering" row + push
                          │
                          ▼
                     I apply myself
                          │
                          ▼
   apply signal detected ──▶ [Outreach Phase]  contacts + verify + 2 drafts
```

---

## 2. Sections to work through

Each section is independent enough to design and build on its own. Status legend: **OPEN** (not discussed) · **DECIDED** (approach chosen) · **BUILT** (implemented + tested).

| # | Section | What it covers | Status |
|---|---|---|---|
| A | Save-time **Resume Phase** | What the save-time run produces and where it stops | **DECIDED** |
| B | The **Apply Signal** | How the system learns I've applied (the trigger for Phase 2) | **DECIDED** |
| C | **Outreach Phase** | What runs after the apply signal, and its caps | OPEN |
| D | **Per-job state machine** | Ledger / Pipeline states that track "resume done, outreach pending" | **DECIDED** |
| E | **`jd-to-ready` phase split** | Adding a `--phase resume \| outreach` mode to the skill + trace | OPEN |
| F | **Scheduling / runner shape** | One daily task with two passes, or two tasks | OPEN |

---

## A. Save-time Resume Phase  — _status: DECIDED (2026-06-23) → **A1: Resume + PDF only**_

**Current:** runner calls `jd-to-ready` as one monolithic skill → all 7 steps incl. contacts + outreach drafts.

**Decision (A1):** the save-time run does the resume half only and stops before any LinkedIn contact work.

- **Steps that run at save time:** **1 intake** (`Job Description.md`), **2 classify** (themes/archetype — kept because tailor-resume depends on it), **3 tailor-resume** (mode `pipeline`), **3.5 resume-export** (PDF), Pipeline row, commit/push.
- **Steps deferred to the Outreach Phase (Section C):** 4 find-contacts, 4b enrich-contacts, 4c verify-emails, 5 write-outreach.

**Why A1:**
- Contact research is the heavy LinkedIn-scraping step and the main account-flag surface (the 6/run cap exists for it); the resume steps touch **no** LinkedIn at all.
- With manual-mark (Section B), many saved jobs never become applications — A1 spends **zero** scraping until I've committed by applying. That's the core point of the redesign.
- No latency cost: contacts/outreach only matter after I apply, and the daily Phase-B sweep produces them then.
- Bonus: the save-time run no longer depends on the LinkedIn daemon, so fewer failure modes in the morning batch.

**Cleanup this enables:**
- The Phase-A Pipeline row is just `Considering — JD reviewed, not yet applied` (optionally a `Resume staged <date>` note). **Drop the `STAGED in Gmail` marker** at save time — nothing is staged in Gmail anymore until the Outreach Phase. (The `STAGED in Gmail` convention moves to Phase B; see Section C.)
- Phase A needs its own trace open/close (it's now a partial run) — handled in Section E.

---

## B. The Apply Signal  — _status: DECIDED (2026-06-23) → **Manual mark only**_

**Decision:** The apply signal is a **manual mark in `Pipeline.md`** and nothing else. After I apply (any channel — LinkedIn, Greenhouse, Lever, company site), I set the role's Pipeline stage to `Applied`. A daily Phase-B pass finds roles that are `Applied` but have not yet had outreach staged, and runs the outreach phase on them. No scraper, no Gmail parsing, ever.

**Why this over the alternatives:**
- 100% reliable across **every** apply channel — most applies happen off LinkedIn, and only I always know I actually hit submit.
- Zero new scraping (no LinkedIn account-flag surface) and zero new fragile parsing.
- Exact role mapping — I'm editing the specific Pipeline row, so there's no fuzzy company→role matching to get wrong.
- Outreach is drafts-only, so the failure mode that matters is a *missed* apply (outreach never fires). Manual marking, done as part of my daily review loop, fully closes that.

**Rejected (recorded so we don't relitigate):**
- ⚠️ **Original idea was based on a false premise:** there is **no** existing Gmail automation that flips a role to `Applied`, and the old interview-stage Gmail reconciliation routine was **retired 2026-06-21** when the PC runner went live. So "the Gmail plugin already does this" is not true on two counts.
- **LinkedIn Applied-tab auto-detect** (exact `job_id` match; would need a small `get_applied_jobs` addition to the MCP fork) — viable and elegant, but only catches LinkedIn-known applies and adds a daily scrape. Not worth it given manual is reliable and free. _Parked, not chosen._
- **Gmail ack detection** — fuzzy company→role matching, many apps send no ack, from-scratch sweep. Rejected.

**Mechanics this locks in for downstream sections:**
- **Source of truth for "have I applied?" = the Pipeline row stage.** This pairs naturally with **D2** (derive phase from `Pipeline.md`, keep the ledger terminal-only) — see Section D.
- **Phase-B selection rule:** a role is ready for outreach when its stage says applied **AND** it has not yet been outreach-staged. After outreach, write a marker like `Outreach staged in Gmail <date>` to the row (mirrors the existing `STAGED in Gmail` convention) so the next sweep skips it.
- **⚠️ Matching gotcha — do NOT substring-match `applied`.** The Phase-A row reads `Considering — JD reviewed, not yet applied`, which *contains* the word "applied." The sweep must match a precise applied marker (e.g. stage **starts with** `Applied`, or a distinct token like `APPLIED ✓`), never a bare `applied` substring, or it will fire outreach on every freshly-staged role. Exact token TBD in Section D / implementation.

---

## C. Outreach Phase  — _status: OPEN_

**Triggered by:** whatever Section B decides.

- Steps that would run: **4 find-contacts** (mode `full`), **4b enrich-contacts**, **4c verify-emails**, **5 write-outreach** (mode `drip`) → the two Gmail drafts, plus a Pipeline note (`Outreach staged in Gmail <date>`).
- Pre-reqs: the role folder already exists from Phase A (intake + resume on disk).
- **Open:** its own per-run cap (how many newly-applied roles to outreach per run?), and whether contacts research re-runs from scratch or reuses anything from Phase A (only relevant if we picked A2).

---

## D. Per-job State Machine  — _status: DECIDED (2026-06-24) → **D2: Pipeline is the trigger; two stores split by pass**_

**Decision (Kanu's words):** _"I want the pipeline, and applied in the pipeline to be the trigger to do the rest of the jd-to-ready skill. I will deal with the process of applied being added to the pipeline."_

So: the `Applied` status in `Pipeline.md` is the single trigger for the Outreach Phase. **Kanu owns getting `Applied` into the Pipeline** (his manual step, consistent with Section B); the system only *reads* it.

**Two state stores, split by pass — no overlap:**

| Store | Owned/written by | Role |
|---|---|---|
| **Ledger** `scripts/drip_runner/saved_seen.json` | Pass A only | Memory of which saved `job_id`s the resume phase already handled or permanently errored. Stays **terminal-only** `{done, error, skipped}` — **no schema/`mark()`/test changes.** After Phase A files a role → `done` (= "resume phase complete + filed"). |
| **`Pipeline.md` Stage cell** | Phase A creates the row; **Kanu** marks `Applied`; Phase B appends the done/error marker | Source of truth for the apply→outreach half of the lifecycle. |

**Lifecycle (observable in the Pipeline Stage cell):**
```
NEW ──Phase A──▶ "Considering — JD reviewed, not yet applied"   (resume staged)
                          │
                   Kanu applies + marks
                          ▼
                  "Applied — …"                                  (outreach pending)  ◀── the trigger
                          │
                  ──Phase B──▶ "Applied — … · Outreach staged in Gmail <date>"   (done)
```

**Pass B selection rule:** Stage cell **starts with `Applied`** AND does **not** contain `Outreach staged`/`Outreach error`.
- "Starts with `Applied`" reuses the existing status vocabulary (`Application Operating System.md`) and dodges the Section-B substring trap (the resume-staged cell starts with "Considering", and its `not yet applied` is lowercase mid-string).
- **No new manual habit** — marking `Applied` is the status update Kanu already does.

**Mechanics locked in:**
- **Row → folder:** the Pipeline row's Folder wikilink points at `Roles/<Company - Role>/`, which already holds the JD + resume from Phase A. Phase B operates on the folder; it never needs the `job_id`.
- **Retry/error:** Phase-B failure leaves the row `Applied` with no marker → auto-retried next pass. To stop infinite retries, Phase B writes `Outreach error <date>: <reason>` (excludes it from the worklist + adds it to the failure alert); removing that note retries it. Selection predicate = _Applied AND not (Outreach staged OR Outreach error)_.
- **Edge case to guard in Phase B:** an `Applied` row whose folder lacks `Job Description.md` (e.g. hand-added, or pre-redesign) → skip + alert rather than crash.

**Why not D1/D3:** D1 (a non-terminal ledger status) would still have to read the Pipeline to learn about the apply, then mirror it into the ledger — pure duplication, plus loosening `mark()` and rewriting dedupe/tests. D3 (separate queue file) adds a third file for no gain. D2 is the least code and matches "Pipeline is the trigger."

**No conflict with Phase A's skip-checks:** Pass A's three checks (ledger `done` / Pipeline `job_id` dupe / folder exists) correctly skip an already-resume-staged role. Pass B doesn't use those checks at all — it scans for the `Applied` marker. The two passes never contend.

---

## E. `jd-to-ready` Phase Split  — _status: OPEN_

The skill is monolithic — no flag for partial runs. To split:

- Add a phase arg: `--phase resume` (steps 1, 2, 3, 3.5) · `--phase outreach` (steps 4, 4b, 4c, 5) · `--phase full` (today's behavior, default).
- **Trace contract gotcha:** `trace_step.py finish-run` is **fail-closed** against a fixed `REQUIRED_STEPS = [1,2,3,3.5,4,4b,4c,5,6,7]` — a partial run currently can't close as `ok`. So the split needs `required_steps` to become phase-dependent (overridable at `start-run`), or each phase becomes its own self-contained traced run.
- Docs to read before touching trace logic (per CLAUDE.md): `TRACEABILITY.md`, `TRACE_SCHEMA.md`, `TOKEN_ACCOUNTING.md`, `RUNBOOK.md`, `TRACE_TEST_PLAN.md`.

---

## F. Scheduling / Runner Shape  — _status: OPEN_

- F1 — **One daily task, two passes.** Extend the 05:00 `DripRunner`: pass 1 = new saves (Phase A), pass 2 = newly-applied roles (Phase B). One schedule, one LinkedIn daemon session.
- F2 — **Two tasks.** Separate task for outreach, tunable cadence/caps. More moving parts.

_Mostly an implementation detail; leaning F1. Decide after B and D._

---

## Suggested order to work through

1. **B (Apply Signal)** — it constrains D and C; decide the trigger first.
2. **A (Resume Phase scope)** — quick, mostly A1 vs A2.
3. **D (State machine)** — depends on B's choice (esp. B1/D2 pairing).
4. **C (Outreach Phase)** — caps + reuse, once D is set.
5. **E (skill phase split)** — the bulk of the code; needs A + C scopes locked.
6. **F (scheduling)** — last, wires it together.

---

## What we are explicitly NOT deciding yet

- Any code changes — this doc is design-only until sections flip to DECIDED.
- Touching the live drip runner or `trace_step.py`.
- The invariant **stays**: all outreach is a Gmail **draft**, never sent (Section C inherits this unchanged).
