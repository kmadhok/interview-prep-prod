---
name: find-contacts
description: Find recruiters, hiring managers, or team members at a target company using the LinkedIn MCP. Use when the user wants to identify who to reach out to at a specific company for a role. Runs standalone (quick shortlist) or as a step inside jd-to-ready (full 5+5 with email inference).
---

# Find Contacts

Identify the right people to contact at a target company — **and specifically the recruiters who support the team the role sits in**, not just any recruiter at the company. This is the single authoritative definition of contact research — `jd-to-ready` calls this skill rather than reimplementing it.

**Core principle (team-aware search).** At a large employer (Deloitte, Google, Amazon) there are hundreds of recruiters; only a few support the specific practice/team that owns the req. A flat "recruiter at <company>" search surfaces generalists who can't move the application. This skill first maps the role into the org — team → parent practice → function — then searches for recruiters who support *that* team. Example: the Deloitte "AI & Analytics Innovation" role sits in the **Strategy & Transactions** practice (the JD says so: "AI & Analytics CoE within Strategy & Transactions"); the right recruiter is one who recruits for Strategy & Transactions (e.g. linkedin.com/in/ab-recruiting/), not a general Deloitte recruiter.

**LinkedIn discipline:** call `mcp__linkedin__*` tools directly, one at a time — sequential, never parallel (the scraper is not concurrency-safe). No caps, no delays. See `linkedin-mcp-operations` for the transport invariant and the per-op reference. If a call errors, follow that skill (sleep 3, retry once, then stop and diagnose).


## Standalone trace (mandatory when invoked directly)

When this skill runs **standalone** (not as a step inside `jd-to-ready` or `stage-outreach`), it must trace itself. When it runs **inside an orchestrator, skip this section entirely** — the orchestrator's run owns the step events (never open a second run).

```bash
python3 "<repo root>/scripts/trace_step.py" start-run --run-type primitive --skill find-contacts --company "<company>" --role "<role>"
python3 "<repo root>/scripts/trace_step.py" begin --step main --primitive find-contacts --mode standalone --prediction "<one-line checkable claim>" --reason "<why the user invoked this now>" --sources '[".claude/skills/find-contacts/SKILL.md", "<role folder>/Job Description.md"]'
# ... do the work ...
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 "<repo root>/scripts/trace_step.py" end --step main --primitive find-contacts --mode standalone --status "ok|partial|failed" --prediction-met "true|false|partial|unknown" --produced '["<files written>"]' --gaps '<gaps or []>' --failure-pattern "" --tokens "$UNKNOWN_TOKENS"
python3 "<repo root>/scripts/trace_step.py" finish-run --status "<same status as the end event: ok|partial|failed>" --gaps '<gaps or []>' --files-written '["<files written>"]'
python3 "<repo root>/scripts/render_run_report.py" "<repo root>/runs/<run-id>"
```

Adjust `--sources` to the files actually read this run; the ones above are this skill's canonical inputs. Mention the rendered report path in your summary.

## Contract

**Modes:** `shortlist` (default) | `full`

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `company` | yes | The real employer. Disambiguate vendor/subsidiary names (e.g. "Cohere Health" ≠ "Cohere"). |
| `role_title` | yes | The target role; drives peer-IC title variants and seniority match. |
| `jd` | yes | The JD text (or path). Read to map the role into the org structure — team, parent practice, function — for team-aware recruiter search (Sub-step 0). |
| `jd_region` | `full` mode | Cities/locations from the JD. Drives the location ranking factor. In `shortlist`, infer or skip. |
| `archetype` | no | Role archetype; tunes the peer-IC title search (e.g. FDE → also search "Solutions Engineer"). |
| `mode` | yes | `shortlist` (1 combined table, no email inference) or `full` (three tables, email inference, confidence). Default `shortlist`. |
| `role_folder` | `full` mode | Only `full` records the tables for downstream outreach. |

**Outputs**
| What | When | Where |
|------|------|-------|
| Ranked contact table(s) | always | returned to caller / chat. `shortlist` = one combined table (~5 people). `full` = **three separate tables: Recruiters (5), Hiring Managers (3–5), Peer ICs (3–5)** |
| `.contacts-ledger.md` | `full` mode | **the shared scored-ledger artifact** written to `<role_folder>/.contacts-ledger.md` (Sub-step 2 schema). `enrich-contacts` reads, appends activity-surfaced rows, re-sorts, writes back; `write-outreach` reads its top rows. Each row carries email + confidence so downstream skills don't re-derive. |
| _(inferred emails only)_ | `full` mode | Each ledger row carries a pattern-inferred email + confidence. Verification of the top picks (and writing `Verified Emails.md`) is done downstream by jd-to-ready **step 4c** (`verify-emails` + EmailFinder.dev), not here. |
| `top_picks` | `full` mode | the #1 of EACH category (top recruiter + top HM + top peer-IC) **as read from the top of the ledger**, each flagged, plus a `recommended_lead` hint (see "Who to lead with" below). Each pick carries its inferred email + confidence. After `enrich-contacts` re-sorts the ledger, the authoritative top_picks are the post-enrichment top rows. |
| `gaps[]` | always | **Cross-skill gap schema** (shared by all primitives): list of `{source: "contacts", kind, detail}` objects — e.g. `{source: "contacts", kind: "thin-results", detail: "only 2 plausible HMs found"}`, `{source: "contacts", kind: "no-email", detail: "<name>: InMail only"}`. `source` lets jd-to-ready merge resume-gaps + contact-gaps into one step-6 report / step-7 log without a schema clash. Empty `[]` if none. |

**Standalone:** `find-contacts(company, role_title, jd, mode: shortlist)`
**Pipeline (from jd-to-ready):** `find-contacts(company, role_title, jd, jd_region, archetype, mode: full, role_folder)`

## Who to lead with (recruiter vs HM vs peer-IC)

The three categories have different leverage, and which one to *lead* outreach with flips by company type. Surface all three; recommend a lead via `recommended_lead`:

- **Recruiter** — controls the pipeline (gets you screened). Almost always worth contacting. With the org-aware search (Sub-step 0) these are practice-aligned, high-leverage.
- **Hiring manager** — controls the decision. High payoff if they reply, but at large firms they're swamped and hard to identify, and often route you back to the recruiter.
- **Peer IC** — controls nothing officially, but highest reply rate and often the best path to an internal *referral* (which can outweigh a cold recruiter email).

**`recommended_lead` heuristic (by archetype / company size):**
- **Big firm / enterprise** (Deloitte, Google, Amazon, large consultancies) → lead with the **practice-aligned recruiter**; use peer ICs for referrals; HMs are a low-yield bet.
- **Startup / small team** (seed–series-C, FDE roles at small AI labs) → lead with the **hiring manager** — they're reachable, they ARE the decision-maker, and there's often no dedicated recruiter for the role.
- This is a *hint*, not a forced choice — the user picks who `write-outreach` drafts for.

## Targets (three categories — `full` mode returns one table each)

1. **Recruiters / TA / sourcers (5)** — titles: Recruiter, Talent Acquisition, Sourcer, Talent Partner, Senior TA, TA Specialist, University Recruiter (last only if role is junior). **Prefer recruiters aligned to the role's parent practice** (Sub-step 0) over generalist company recruiters; then prefer location match to `jd_region` and engineering / AI / data backgrounds.
2. **Hiring managers (3–5)** — Director / VP / Head / Manager of the role's `team` or `parent_practice` (one level above the role). The decision-maker. Prefer the most specific practice match + `jd_region`.
3. **Peer ICs (3–5)** — people already in the exact role or a close variant (e.g. for "Forward Deployed Engineer, Prompt Specialist" also search "Solutions Engineer", "Prompt Engineer"). Highest reply rate; best path to a referral and honest role signal.

`shortlist` collapses these into one combined ~5-person table (recruiter-weighted). `full` returns all three tables separately.

`shortlist` returns one combined ranked table (~5 people). `full` returns three tables: Recruiters (5), Hiring Managers (3–5), Peer ICs (3–5).

## Process

**Sub-step 0 — Map the role into the org (do this FIRST).** Read the `jd` and determine where the role actually sits:
- **Team / group** — the immediate unit (e.g. "AI & Analytics Center of Excellence", "Direct Platform discovery team").
- **Parent practice / division** — the larger org the team rolls up to (e.g. "Strategy & Transactions", "Cloud AI"). **This is the key search term** — recruiters are usually aligned to the practice, not the sub-team.
- **Function** — engineering / data / product / consulting, for title matching.

How to find it:
1. **Read it from the JD if stated.** JDs often name the structure outright — e.g. "the AI & Analytics CoE *within Strategy & Transactions*", "embedded in our *Direct Platform discovery* team". Quote it.
2. **If not explicit, infer** from responsibilities, named partner teams, product area, and seniority — then **verify against the company's real org** before searching: use `mcp__linkedin__get_company_profile` / `search_people` to confirm the practice name as the company actually labels it (e.g. confirm Deloitte calls it "Strategy & Transactions", not "S&T Advisory"). If you can't confirm a team after inferring, record `{kind: "team-uninferred", detail: "could not map role to a specific practice; searched company-wide"}` in `gaps[]` and fall back to company-wide search.

Output of this step: `{team, parent_practice, function}` used to build the searches below.

**Sub-step 1 — Search (team-first, company-fallback).** Call `mcp__linkedin__search_people` once per query, sequentially.

> **Region goes in `keywords`, NOT the `location` param.** A live run found the MCP's `location` filter silently does nothing — `search_people(location: "Chicago")` returned mostly Mumbai/Madrid GCC results, which would then be Loc-scored against a US role and corrupt the candidate pool. So when the role is region-specific, **put the region text directly in the query string** (e.g. `"Strategy & Transactions" recruiter Deloitte "Chicago United States"`) rather than relying on `location:`. Treat any `location:`-filtered result set as unfiltered until proven otherwise — eyeball the first few locations; if they're off-region, the filter was ignored and you must add the region to `keywords` and re-search.

Queries:

*Primary — team/practice-specific recruiters (run first):*
- `"<parent_practice>" recruiter OR "talent acquisition" at <company>` — e.g. `"Strategy & Transactions" recruiter at Deloitte`
- `"<team>" recruiter at <company>` if the team has its own recruiting

*Widen ONLY if the primary yields < 2 plausible recruiters:*
- `"recruiter" OR "talent acquisition" at <company>` (flat company-wide — the old behavior, now the fallback)

*Hiring-manager search (its own table):*
- `"<team or parent_practice>" Director|VP|Head|Manager at <company>`

*Peer-IC search (its own table):*
- `"<exact role title or close variant>" at <company>`

(`shortlist` runs a single team-first search → one combined table. `full` runs the practice-recruiter search + the HM search + the peer-IC search, widening recruiters to company-wide if thin → three tables. ~4 searches in full mode.)

**Sub-step 2 — Rank via a SCORED LEDGER (no silent truncation).**

> **Why this is mandatory.** A search returns ~10–25 results; the best candidate is often NOT at the top of LinkedIn's order. Ranking by eyeballing the first few — or anchoring on a "2nd-degree connection" badge — silently drops better candidates lower in the list. (This skill once dropped a perfect Strategy & Transactions recruiter who was at search position #9, because the agent locked onto a 2nd-degree match at position #3.) The fix, per observability-driven design: **score every returned candidate explicitly, record the score, and gate the pick against the full list.** Every selection must be traceable to recorded evidence, not intuition.

**Score EVERY candidate the search returned** (all of them, not just the visible top), each on these factors:

1. **Practice / team match** — does the candidate's title/headline name the role's `parent_practice` or `team` (Sub-step 0)? This is **factor #1, highest weight.** "Risk and Strategy & Transactions" recruiter > generic "Recruiter, Deloitte". Score 0–3.
2. **Location match to `jd_region`** — same metro > same country > elsewhere. Score 0–2.
3. **Title specificity** — exact-function recruiter/HM/IC > generalist. Score 0–2.
4. **Tenure / recency** — actively in-role (6mo–4yr) > 8+ yrs (may have moved off) > departed. Score 0–1.
5. **Seniority match** — recruiter/HM band matches the role's level. Score 0–1.
6. **Exclude (hard filter, not a score)** — wrong same-named subsidiary, ex-employees, people on leave → drop with a reason.

**Connection degree / mutual connections / "2nd-degree" badges are a TIEBREAKER ONLY — never a ranking factor.** A warm path breaks ties between candidates with equal practice-match; it does NOT promote a weaker-practice-match candidate above a stronger one. (This is the exact bias that caused the position-#9 miss.)

**Emit the ledger (this is the shared artifact other skills build on).** Return it, include it in the step-7 evidence log, AND — in `full` mode — **write it to `<role_folder>/.contacts-ledger.md`**. This file is the single scored-ledger artifact for the role: `find-contacts` produces it; `enrich-contacts` reads it, appends activity-surfaced people scored on this same rubric, and re-sorts it; `write-outreach` reads its top rows. The rubric below (factors, weights, the Practice-evidence lock) is the **one definition** — any skill that appends rows applies it, never redefines it. Schema:

| Name | Category (recruiter/HM/peer-IC) | Practice (0-3) | Practice evidence (quote the title/headline) | Loc (0-2) | Title (0-2) | Tenure (0-1) | Snr (0-1) | Total | Conn-degree (tiebreak) | Source (search/enrich) | Provenance | Rank |
|------|---------------------------------|----------------|-----------------------------------------------|-----------|-------------|--------------|-----------|-------|------------------------|------------------------|------------|------|

(`Source` = `search` for keyword-search finds, `enrich` for activity-surfaced ones; `Provenance` cites the activity for `enrich` rows, empty for `search` rows. These two columns are what let `enrich-contacts` append onto the same file without ambiguity.)

**The "Practice evidence" column is mandatory and is the anti-intuition lock.** For the practice-match score you MUST paste the exact words from the candidate's title/headline that justify it — e.g. a 3 requires quoted text naming the practice ("*Risk and Strategy & Transactions*"); a 0 means quoting the generic title ("*Recruiter, Deloitte*" — no practice named). If you can't quote text supporting the score, the score is wrong. This makes a biased score visible: you cannot quietly score a strong match low, because the quote sits next to the number.

Score **all** of them — a candidate scored 0 and excluded still appears in the ledger with the exclude reason. Nobody gets dropped without a row.

**Completeness gate (before returning).** The chosen #1 in each table MUST be the candidate with the highest **practice-match** score across the *entire* scored list (ties broken by total, then connection-degree). If you pick a #1 that is NOT the top practice-match, you must record an explicit override reason in `gaps[]` as `{source:"contacts", kind:"rank-override", detail:"picked X over higher-practice-match Y because ..."}`. Silent overrides are forbidden — if the gate isn't satisfiable, that's a finding, not a default.

Pick per table (`full`): top 5 recruiters, top 3–5 hiring managers, top 3–5 peer ICs (by ledger Total, gated on practice-match). Or top ~5 overall (`shortlist`). If a table has fewer than its minimum plausible candidates, record `{kind: "thin-results", detail: "<which table>: only N found"}` in `gaps[]`.

**Sub-step 3 — Drilldown** (`full` mode). For the top picks (≤10 in full), call `mcp__linkedin__get_person_profile` once per URL, sequentially. Collect enriched records.

**Sub-step 4 — Email inference** (`full` mode). Infer email from the company's standard pattern (`first.last@`, `first@`, `flast@`). Confidence:
- **High** — verified from prior correspondence with the user or a public source.
- **Medium** — pattern matches multiple visible employees publicly.
- **Low** — guess; no verification.

**Never fabricate.** If no pattern can be inferred, leave email empty, mark "InMail only", and record `{kind: "no-email", detail: "<name>: InMail only"}` in `gaps[]`.

**Email confidence (`full` mode).** Each ledger row carries a pattern-inferred work email at Medium confidence (e.g. `first.last@<domain>`). This skill does NOT verify them — verification of the top 3 recruiters is a downstream concern owned by jd-to-ready **step 4c** (the `verify-emails` script + EmailFinder.dev), which writes `Verified Emails.md`. A `High (header-verified)` email already present from prior correspondence with the user (e.g. found in Gmail) should be kept as-is and is exempt from downstream re-verification.

**Sub-step 5 — Hand off to `enrich-contacts` via the ledger artifact** (`full` mode, recommended). Discovery by keyword search alone misses people the recruiters have *amplified* — a practice-aligned recruiter who reposts "we're hiring an AI Specialist Leader" has surfaced both a live req and its sourcer that no title search returns.

The hand-off is **artifact-based, not a callback**: this skill has already written the scored ledger to `<role_folder>/.contacts-ledger.md` (Sub-step 2). `enrich-contacts` then reads that file, scrapes each recruiter's activity, scores any new people it finds **on this skill's published rubric** (the Sub-step 2 schema + factor weights — it applies the rubric, it does not invent one), appends them as `Source: enrich` rows with provenance, re-sorts the ledger by Total (gated on practice-match), and writes the file back. The pipeline stays **linear** — `find-contacts` produces the ledger, `enrich-contacts` extends it; there is no loop back into this skill. (`hooks[]` from enrich go forward to `write-outreach` as the beat-1 trigger.)

So: ranking logic still lives in exactly one place — *this skill's rubric* — but it's now a published schema two skills write against, rather than a function one skill calls back into. The completeness gate and Practice-evidence lock apply to appended `enrich` rows identically: an activity-surfaced person earns no bonus for *how* they were found.

(Standalone `shortlist` runs skip the artifact + enrichment — it's a `full`/pipeline concern. Sequential LinkedIn discipline still applies downstream: `enrich-contacts` scrapes one recruiter at a time.)

## Output format

**`shortlist`** — one combined table:

| # | Name | Title | Location | Why this pick | LinkedIn |
|---|------|-------|----------|---------------|----------|

**`full`** — three separate tables (**Recruiters 5 · Hiring Managers 3–5 · Peer ICs 3–5**), each adding `Email (inferred)` and `Confidence` columns. Plus `top_picks` (the #1 of each table) and a `recommended_lead` hint per "Who to lead with". `write-outreach(drip)` drafts for whichever pick(s) the user chooses.

Any contact surfaced via `enrich-contacts` (Sub-step 5) appears in the ledger as a `Source: enrich` row with a `Provenance` note ("via <recruiter>'s repost of <author>, <date>") so the activity-derived path is traceable, not silently merged in. The rendered tables read from the (post-enrichment) ledger, so they reflect the final ranking.

## Hard rules
- Sequential LinkedIn calls only — never parallel (see `linkedin-mcp-operations`).
- Never fabricate a person, title, or email. Surface only what the MCP returns; mark inferred emails by confidence.
- If LinkedIn is unreachable and can't be recovered, return what you have with `gaps[]` noting contact research is incomplete — do not invent contacts to fill the table.
- **In `full` mode, the scored ledger MUST be written to `<role_folder>/.contacts-ledger.md` — this is a required output, not optional.** It is the canonical artifact `enrich-contacts` reads and `write-outreach` consumes; rendering the table in chat is not a substitute. (A live run wrote only ad-hoc snapshots and skipped the canonical file — don't.) Write the file before returning.
- Region goes in the search `keywords`, not the `location` param (the filter is unreliable — see Sub-step 1).

## Behavior contract

`evals/find-contacts/contract.md` is authoritative. Declare its clause IDs at
trace begin and record verifier-produced results at trace end. Without
LinkedIn MCP, only live-only clauses are `BLOCKED`/`NOT_RUN`; local ledger
clauses still run.
