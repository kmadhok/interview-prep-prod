# Two-Orchestrator Split — End-to-End Live Test Report

**Date:** 2026-06-28
**Branch:** `worktree-two-orchestrator-split`
**Role under test:** Snowflake — Forward Deployed Analytics Engineer & AI Specialist (LinkedIn 4432116585)
**Run type:** FULL LIVE RUN (real LinkedIn scraping, real EmailFinder verification, real Gmail draft — nothing sent)
**Method:** one fresh sub-agent per individual skill, invoked **sequentially** across both orchestrators, each verified against its on-disk artifact.

---

## 1. What this test did

Walked one saved job through the entire two-orchestrator lifecycle, exercising **each constituent skill in isolation** (not the orchestrators as black boxes), so every skill produces an independently verifiable pass/fail:

```
PREP ORCHESTRATOR (jd-to-ready, fires on save)
  1. interview-prep-intake   → role folder + Job Description.md
  2. classify (step 2)       → .classification.json
  3. tailor-resume           → tailored resume .md
  3.5 PDF (step 3.5)         → resume .pdf  [orchestrator step, not a standalone skill]
  ── APPLY GATE: Pipeline row flipped Applied + moved to ## Active ──
APPLY ORCHESTRATOR (stage-outreach, fires on apply)
  4. find-contacts           → .contacts-ledger.md
  5. enrich-contacts         → ledger += hooks + missed people
  6. verify-emails           → Verified Emails.md
  7. write-outreach          → Cold Outreach.md + Gmail draft (unsent)
```

Each skill was run by a separate `general-purpose` sub-agent with a scoped prompt (no trace writes, no Pipeline edits except the gate, never send). LinkedIn calls were kept strictly sequential (one sub-agent at a time) per `linkedin-mcp-operations`.

### Setup / reset
The Snowflake folder already existed (fully staged under the **old monolith** on 2026-06-26, committed in `11c1b24`). To test from scratch:
- Backed it up to scratchpad + confirmed it was committed (restorable).
- Removed the folder (kept the Pipeline row to avoid corrupting the 60 KB file).
- Captured the JD as the "saved job" input.

### Cleanup (final state)
- `Pipeline.md` — **fully reverted** (`git checkout`); Snowflake back under *Considering / not yet applied*.
- Role folder — **kept the freshly regenerated package** (uncommitted working-tree changes).
- Gmail draft `r3844568421094993998` to `brad.mallmann@snowflake.com` — **kept, unsent.**
- A frozen snapshot of every produced artifact lives in `./produced-artifacts/` (durable even if the Roles-folder package is later reverted).

---

## 2. Result summary

| # | Skill | Result | Artifact | Verified by |
|---|-------|--------|----------|-------------|
| 1 | `interview-prep-intake` | ✅ PASS | `Job Description.md` (76 ln) | folder + file on disk |
| 2 | classify (jd-to-ready step 2) | ✅ PASS | `.classification.json` | JSON parse + vocab assertion |
| 3 | `tailor-resume` | ✅ PASS | resume `.md` (64 ln) | no `[VERIFY]` leak, canonical-only |
| 3.5 | PDF export (step 3.5) | ⚠️ PASS w/ gap | resume `.pdf` | `PAGES=2 TITLE_LEAK=0` |
| — | **Apply gate** | ✅ | Applied + moved to `## Active` | worklist surfaced it live |
| 4 | `find-contacts` | ✅ PASS | `.contacts-ledger.md` (85 ln) | 20 scored, lead verified, sequential |
| 5 | `enrich-contacts` | ✅ PASS | ledger → 99 ln | real hooks + 1 new person |
| 6 | `verify-emails` | ⚠️ PASS w/ bug | `Verified Emails.md` | 3 EmailFinder-verified **via workaround** |
| 7 | `write-outreach` | ✅ PASS | `Cold Outreach.md` + Gmail draft | draft confirmed unsent via `list_drafts` |

**Headline:** the pipeline runs end-to-end and every skill produced a correct artifact. The test's value is the **two real defects** (one production bug, one unbuilt-owner gap) plus four smaller observations below.

---

## 3. ISSUES — extreme detail

Severity key: 🔴 production bug (will silently misbehave) · 🟠 real gap (missing owner/step) · 🟡 minor / known-limitation.

---

### 🔴 ISSUE 1 — `find-contacts` ledger format is unparseable by `verify-emails`

**One line:** The ledger `find-contacts` writes cannot be parsed by `verify_emails.py`; run on the real ledger it parses **0 recruiters and an empty email pattern**, so `verify-emails` silently produces nothing. Both skills run inside `stage-outreach`, so apply-side email verification is broken on every real ledger.

**Where — consumer (`verify-emails`):** `.claude/skills/verify-emails/scripts/verify_emails.py`

Two hard requirements in the parser, both unmet by the real ledger:

1. **Email pattern line** — `parse_email_pattern()` (lines 125–136):
   ```python
   for line in text.splitlines():
       if not line.strip().startswith("**Email pattern:**"):   # line 127
           continue
   ```
   It requires a line literally beginning `**Email pattern:**`. If none, it returns `("", "")` → empty domain + pattern.

2. **Recruiter table headers** — `parse_recruiters()` (lines 165–173):
   ```python
   headers = [clean_header(cell) for cell in header_cells]
   if not {"name", "category", "rank"}.issubset(set(headers)):   # line 170
       continue
   return recruiters_from_table(lines[line_number + 1 :], headers, top)
   ```
   It scans for **one** table whose header columns include all of `name`, `category`, `rank`. Then `recruiters_from_table()` (lines 176–199) keeps only rows whose **`category` cell == `"recruiter"`** (lines 190–192). No matching header row → returns `[]` → zero recruiters → zero API calls.

**Where — producer (`find-contacts`):** the real ledger it wrote — `produced-artifacts/.contacts-ledger.md` (and live at `Roles/Snowflake …/.contacts-ledger.md`):

| What the parser wants | What the ledger actually has | Line in ledger |
|---|---|---|
| a line `**Email pattern:** first.last @ snowflake.com` | a heading `## Email pattern` + prose | line 12–13 |
| ONE table with a `Category` column | THREE separate tables: `## Recruiters (ranked)`, `## Hiring Managers (ranked)`, `## Peer ICs (ranked)` | lines 20, 39, 54 |
| header incl. `Name, Category, Rank` | `\| Rank \| Name \| Practice \| Practice evidence … \| Loc \| Title \| Tenure \| Snr \| Total \| Conn \| Source \| Email (inferred) \| Conf \| LinkedIn \|` | lines 22, 41, 56 |

So the column is **`Practice`, not `Category`**, and category is encoded by **separate section tables** rather than a column. The `{name, category, rank}` subset test fails on every table → `parse_recruiters` returns `[]`.

**Repro:**
```bash
python3 ".claude/skills/verify-emails/scripts/verify_emails.py" \
  --ledger "Roles/Snowflake - Forward Deployed Analytics Engineer AI Specialist/.contacts-ledger.md" \
  --emails-md /tmp/out.md
# → 0 recruiters parsed, empty domain/pattern, degenerate output
```

**How the test still got a PASS:** sub-agent #6 detected the mismatch, hand-normalized a copy in scratchpad (renamed `Practice`→`Category`, collapsed to one table, added a `**Email pattern:**` line), ran the **real** EmailFinder path against that, and wrote `Verified Emails.md` to the role folder. Brad Mallmann → `brad.mallmann@snowflake.com` **VERIFIED/High**. So the verification *backend* is healthy; only the *ledger contract* is broken.

**Impact:** In production `stage-outreach` (Pass B), step 4 (`find-contacts`) → step 4c (`verify-emails`) hands off via this exact file. Today verify-emails would parse 0 recruiters and emit an empty/degenerate `Verified Emails.md` with **no error** — a silent failure (violates the "fail loud, never silent" invariant). `write-outreach` would then fall back to inferred/own-address with a flagged gap, losing all real verification.

**Suggested fix (pick one):**
- **(A, preferred)** Make `verify_emails.py` parse the `find-contacts` schema: accept a `## Email pattern` heading, and read recruiters from the `## Recruiters (ranked)` table with a `Practice` column (treat section membership as category). Add a regression test with the real ledger shape as a fixture.
- **(B)** Make `find-contacts` *also* emit the legacy `**Email pattern:**` line + a unified `Category`-column table the parser already understands.
- Either way: add a **fail-loud guard** — if the ledger has contact tables but the parser extracts 0 recruiters, raise/print a visible error instead of writing an empty file.

---

### 🟠 ISSUE 2 — an Applied row must be MOVED to `## Active`; nothing does that yet (blocked on Task 8)

**One line:** Marking a Pipeline row `Applied` is not enough for Pass B to see it — the row must also physically live under `## Active`. The worklist correctly enforces this; the component that should relocate the row (the cloud secretary, Task 8) is **not built**.

**Live evidence:** After flipping Snowflake's status text to `Applied 2026-06-28` while it was still under `## Considering`, `outreach_worklist.py` did **not** list it. Only after moving the row into `## Active` did it appear.

**Where — the worklist (correct behavior):** `scripts/drip_runner/outreach_worklist.py`
- `active_section()` (lines 41–59) collects only lines under exactly `## Active` (line 55: `line.strip().lower() == "## active"`), stopping at the next `## ` heading.
- `applied_not_staged()` (lines 62–70) iterates **only** `active_section(...)`.
- This is deliberate (docstring lines 44–47): Considering rows are excluded by the `not yet applied` predicate, and Closed/On-hold rows have a different schema whose Date cell carries `Applied <date>` and would otherwise leak. Section-scoping is the clean structural exclusion. **Not a bug.**

**Where — the missing owner:** `scripts/drip_runner/runner-prompt.md` (the cloud Gmail secretary) is supposed to mark rows Applied from Gmail app-acks (per `Spec - Applied Detector.md`). A grep for `mark applied | move … active | relocate | ## Active` returns **nothing** — the secretary prompt was never updated (this is **Task 8 of the implementation plan, still unbuilt**). So no automated component performs the Applied→Active relocation. Today only a manual edit (or this test) moves the row.

**Impact:** When the cloud secretary is eventually wired to mark Applied, if it only edits the status cell in place (under Considering) and doesn't relocate the row, Pass B will never fire and outreach silently never stages.

**Suggested fix:** When building Task 8, the "mark Applied" step must **`git mv`/relocate the row from `## Considering` to `## Active`** as part of the same edit (and the monotonic-state guard already specified). Add this to the Task 8 ack/reconcile ruleset explicitly.

---

### 🟠 ISSUE 3 — legacy `STAGED in Gmail` markers on Considering rows (stale-data sweep needed)

**One line:** Pre-split Pipeline rows (filed by the old monolith drip-runner) carry `STAGED in Gmail <date>` on *Considering* rows. If such a role is later applied, the stale marker makes `row_is_staged()` true and Pass B silently skips it. The code path is **already fixed for new runs**; the residue is old data.

**Where — fixed going forward:** `scripts/drip_runner/runner-prompt-saved.md` line 20 now reads:
> "Do NOT write any `STAGED in Gmail` marker — this is the prep half only; the `STAGED` marker is written exclusively by the apply-side `stage-outreach` skill … (Writing it here would make the Pass B worklist silently skip the role once it's applied.)"

So new Pass A runs won't create the stale marker. This matches **integration finding #1** in `Automation Design - Two-Orchestrator/Automation Architecture - Two-Orchestrator Split.md` (lines 79).

**Live evidence:** The Snowflake row under test (filed 2026-06-26 by the old runner) carried `**STAGED in Gmail 2026-06-26**` on a Considering row. I cleared it during the test's Applied flip; the revert restored the original (stale) text, since that's the committed truth.

**Impact today:** Harmless *while* rows stay in Considering (the worklist section-scopes them out anyway). Becomes a silent suppressor the moment such a role is marked Applied **without** also clearing the marker.

**Suggested fix:** One-time sweep of `Pipeline.md` to strip `STAGED in Gmail …` from all `## Considering` rows. Optionally a guard in the Task 8 "mark Applied" step: when relocating a row to Active, drop any pre-existing STAGED marker so `stage-outreach` re-stages cleanly.

---

### 🟡 ISSUE 4 — the `jd-to-ready` Stop hook fights an async sub-agent harness

**One line:** Driving each skill through an async sub-agent means the orchestrator yields control between steps; if a `jd-to-ready` trace run is open, `jd-to-ready-stop.py` flags "trace incomplete" on every yield.

**Where:** `.claude/skills/jd-to-ready/hooks/jd-to-ready-stop.py` (737 B). It fires on Stop and reports open/missing steps when a trace run is active.

**What happened:** I opened a `jd-to-ready` trace run + step 1, then yielded to wait for the async intake sub-agent. The Stop hook fired: *"jd-to-ready trace incomplete for run jdtr-…; open step: 1; missing closed steps: 1, 2, 3, 3.5, 6, 7."* The trace contract expects open→close inside one continuous orchestration; an async, multi-turn, one-sub-agent-per-step harness cannot hold a step open across turns.

**Resolution in this test:** Aborted the orchestrator trace run and verified skill success by **artifact inspection** instead. The trace contract itself is independently green — `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py` = **15 passed**, including both run-types' `finish-run` closing on exactly their required steps.

**Impact:** None on production (the PC/cloud runners drive skills in the **main loop**, where open→close happens in one orchestration). It is purely a constraint on *this testing approach* — and a design input for the planned "testing skill": the harness should either (a) not hold a trace open across async sub-agents, or (b) run trace begin/end inside each sub-agent synchronously, or (c) verify the trace contract separately via its unit tests (what we did).

---

### 🟡 ISSUE 5 — tailored resume overflows to 2 pages

**One line:** `build_resume_pdf.py` rendered the Snowflake resume at `PAGES=2 TITLE_LEAK=0` — content doesn't fit one page even after auto-tightening to the 9 pt floor.

**Where:** `scripts/build_resume_pdf.py` on `produced-artifacts/Kanu Madhok Resume - Snowflake Forward Deployed Analytics Engineer.md` (64 lines). Contract line: `PAGES=2 TITLE_LEAK=0`.

**Impact:** Cosmetic but real — a 2-page resume for a one-page target. The skill correctly does **not** silently cut canonical bullets to win the page break (that's Kanu's tailoring call). `TITLE_LEAK=0` means no "Resume" title leaked. The `.md` is the source of truth, so this degrades gracefully.

**Suggested fix:** Trim one bullet (role-specific tailoring decision), then re-render. Not a code defect.

---

### 🟡 ISSUE 6 — `create_draft` cannot attach the resume PDF

**One line:** The Gmail MCP `create_draft` tool has no attachment parameter, so the tailored resume PDF must be attached by hand before the draft is sent.

**Where:** sub-agent #7 (`write-outreach`) logged this in the `Cold Outreach.md` `gaps[]`. The draft body says "Resume attached." but no file is attached.

**Impact:** The human-gated send step requires a manual attach. Acceptable (drafts are never auto-sent), but the gap must stay visible so Kanu doesn't send an unattached email.

**Suggested fix:** Keep the explicit "attach the PDF before sending" gap in `Cold Outreach.md` and the staging report. No code fix unless the MCP gains attachment support.

---

## 4. Environment notes

- **Platform:** Windows (`G:\projects\interview-prep`). Skills' reference paths point to the macOS workspace (`/Users/kanumadhok/…`); sub-agents correctly used the Windows root. No skill failed on path handling.
- **LinkedIn MCP:** daemon reachable — handshake `POST http://127.0.0.1:8765/mcp` returned **HTTP 200**. All LinkedIn calls across #4/#5 were sequential; zero transport errors.
- **Email verification backend:** `verify-emails` uses **EmailFinder.dev** (`.claude/skills/verify-emails/scripts/verify_emails.py` → `/api/find-email/person`), **not** the Hunter MCP. Bearer key `Email_Finder_Dev` present in workspace `.env`; 3 credits spent, results now cached.

## 5. Cleanup record

| Item | Action | How to fully restore |
|---|---|---|
| `Pipeline.md` | reverted to committed (`git checkout`) | already clean |
| Role folder (fresh package) | KEPT (uncommitted) | `git checkout -- "Roles/Snowflake - Forward Deployed Analytics Engineer AI Specialist"` |
| Old committed folder package | superseded in working tree; intact in git + scratchpad backup | as above |
| Gmail draft `r3844568421094993998` | KEPT, unsent | delete in Gmail Drafts if unwanted |
| This test record | new, untracked | `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/` |

## 6. Produced-artifact inventory (frozen in `./produced-artifacts/`)

- `Job Description.md` — intake output (76 ln)
- `.classification.json` — themes `[NL→SQL, agents, end-to-end, business-translation, platform, engineering-rigor]`, archetype `FDE / client-facing`
- `Kanu Madhok Resume - Snowflake Forward Deployed Analytics Engineer.md` / `.pdf` — tailored resume (canonical-only)
- `.contacts-ledger.md` — 20 scored contacts + enrich hooks (99 ln)
- `Verified Emails.md` — Brad/Cassie/Diane EmailFinder-verified
- `Cold Outreach.md` — recruiter email (Brad) + HM InMail (Hamin Oh)

### Gmail draft (evidence — unsent)
- **id:** `r3844568421094993998` · **to:** `brad.mallmann@snowflake.com` · **subject:** "Re: your data-foundation post — Walmart agent builder interested"
- **opening (uses Brad's real authored-post hook):** *"I read your post on the bottom of the stack quietly winning, that data quality, governance, and trust are the foundation enterprise AI runs on."*
