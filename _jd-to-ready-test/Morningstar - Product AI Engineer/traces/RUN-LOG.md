# RUN-LOG — jd-to-ready live trace

**Run:** Morningstar — Product AI Engineer
**Sandbox:** `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/_jd-to-ready-test/Morningstar - Product AI Engineer/`
**Real JD (read-only):** `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Morningstar - Product AI Engineer/Job Description.md`
**urgency:** `none` (beat 3 omitted)
**jd_region:** Chicago, IL (hybrid, 4 days onsite). No remote.

Pre-flight: LinkedIn MCP port 8765 LISTEN, handshake HTTP 200 — healthy. Step 1 (intake) skipped — JD already filed.

---

## Step 2 — Classify JD (themes + archetype)

**prediction:** archetype = `FDE / client-facing` (JD overview literally says "Forward-Deployed AI Engineers" embedded in discovery team); 4–6 themes all with verbatim evidence, including `agents`, `end-to-end`, `experimentation`, `cross-functional`.

**actual:** archetype = `FDE / client-facing`. 6 themes, all verbatim: `agents`, `end-to-end`, `experimentation`, `cross-functional`, `business-translation`, `evaluation`. notes flagged title-vs-framing mismatch + Chicago 4-day hybrid hard gate + Claude Code/Cursor must-have. **prediction_met: true**

---

## Step 3 — tailor-resume (pipeline mode)

**prediction:** resume covers ≥4 of 6 themes; anchored on A1 + at least one of A3/A4/A5; includes F1 (FDE archetype); zero invented numbers / zero `[VERIFY]` leaks; filename `Kanu Madhok Resume - Morningstar Product AI Engineer.md`. Likely gap: no canonical match for "Claude Code/Cursor expert user" as a hard proof point (it's a skill, not an achievement).

**actual:** Wrote resume to sandbox. Picked A1, A3, A2, A5, A4, A6 (Walmart set) + U1 (experimentation) + F1 (FDE/consulting) + I1 (early career) + A7 (selected project). A1 anchored first; A3/A4/A5 all present. Themes covered: agents (A1/A2/A3/A5), end-to-end (A1/A4), experimentation (U1), cross-functional (A1/A2), business-translation (A1), evaluation (A1 23-case golden suite) = 6/6. Skills section surfaces Claude Code + Cursor (both in Canonical Skills "AI-assisted development" block) at the top per the JD must-have. Zero invented numbers, zero `[VERIFY]`, no `Resume Claims To Verify` content. **prediction_met: true** (resume covered all 6, not just ≥4).

gaps[] returned: `[]` (every JD theme matched a canonical achievement; Claude Code/Cursor is satisfied by the Canonical Skills block, so no gap).

---

## Step 4 — find-contacts (full mode)

**Inputs:** company=Morningstar, role_title=Product AI Engineer, jd (full text), jd_region=Chicago IL, archetype=FDE/client-facing, mode=full, role_folder=sandbox.

**Org map (Sub-step 0, from JD):** team = "Direct Platform discovery team"; parent_practice = "Morningstar Direct Platform" (Direct Platform business unit); function = product engineering / AI engineering. JD quote: "The Morningstar Direct Platform team is one of the largest business units" and "This role is embedded in our discovery team, working alongside Product Managers, UX designers, and researchers."

**prediction:** Real LinkedIn searches will return Morningstar TA + Direct Platform leaders. Expect ≥3 recruiters, some HMs (Director/VP Direct Platform / Product), and peer ICs (AI Engineer / Product Engineer). Email pattern likely `first.last@morningstar.com` → medium confidence. Risk: "discovery team" is too specific to match recruiter headlines; will fall back to company-wide recruiter search. Writes `.contacts-ledger.md`.

**actual:** 7 LinkedIn calls (4 searches + 3 drilldowns), all sequential, zero errors. Recruiter search #1 (location=Chicago) returned mostly Mumbai GCC — the `location` param was NOT honored. Re-ran with "Chicago United States" in keywords → strong Chicago recruiter pool. Peer-IC search was a **direct hit**: two people with the literal title "AI Product Engineer (Forward Deployed)" — Talha Mushtaq + Brayckner Bueres Torres, both Chicago. HM search found Steven Berger (Dir PM, AI Office — runs Morningstar MCP server + agentic, Anthropic Claude-for-Finance partnership). Drilldowns confirmed titles and surfaced 2 bonus on-target people (Thomas Aviles "Head of Advisor Software" via Talha's feed; Nikhil Suresh via Berger's post). NO public emails on any contact_info → all inferred from first.last@ pattern, Medium/Low. Ledger written: 5+ recruiters, 4 HMs, 6 peer ICs, all scored. **prediction_met: true** (≥3 recruiters ✓, HMs ✓, peer ICs ✓, pattern email ✓, fallback-to-keyword needed as predicted). Bonus: exact-title peer ICs exceeded expectation.

**find-contacts top_picks (pre-enrich):** recruiter=Brittany Giacomo (7), HM-by-practice=Steven Berger (7, practice 3), peer-IC=Talha Mushtaq (8.5, practice 3). recommended_lead = recruiter (Brittany Giacomo), big-firm heuristic.

---

## Step 4b — enrich-contacts

**prediction:** Scraping all ~9 recruiter rows' feeds will yield ≥1 real hook (Brittany already visibly reposted Anna Sherwood's Chicago hiring post during find-contacts). Likely surfaces Anna Sherwood as an on-target person via that repost — but she's already in the HM table, so she'd be a duplicate, not a new append. Expect mostly `no-activity`/noise for junior/off-region recruiters. Predict: ledger round-trips (same schema), ≥1 hook, possibly 0 genuinely-new appended people (most on-target signals point to people already in the ledger). jd_region (Chicago) must flow into Loc scoring of any appended person.

**actual:** Scraped 5 recruiter feeds (Brittany via her find-contacts drilldown; Jeanine, Corinne, Ashley, Shirley via posts-scrapes). 4 lower-ranked/off-region recruiters left unscraped with logged reason (bounded live run). 3 real hooks found (Brittany→Anna Sherwood eng/PM repost; Jeanine→Kishore Nair DAS Senior Architect req; Corinne→AI Solutions marketing req). **1 genuinely-new on-target person appended: Kishore Nair** (Head of Tech, Direct Advisory Suite — the advisor platform this role feeds) via Jeanine's repost — NOT a duplicate (he wasn't in the ledger). Scored 8/practice-2, no activity bonus, re-sorted into HM table below Berger (practice gate). jd_region Chicago flowed into his Loc=2. Ledger round-tripped: same 16-col schema, before=84 lines → after=98 lines (Kishore row + hooks[] + enrich gaps[] + re-sort note). Ashley/Shirley = no-activity for eng. **prediction_met: true** (round-trip ✓, ≥1 hook ✓ (got 3), jd_region into Loc ✓). Deviation from prediction: the new append was Kishore Nair (not Anna Sherwood, who WAS already in ledger as predicted).

**Authoritative top picks re-read from FINAL ledger:** recruiter=Brittany Giacomo (unchanged), peer-IC=Talha Mushtaq, HM=Steven Berger. Outreach targets Brittany Giacomo + Talha Mushtaq, both read from post-4b ledger.

---

## Step 5 — write-outreach (drip mode)

**prediction:** urgency=none → beat 3 omitted on all drafts. Lead with recruiter (Brittany Giacomo) using her real enrich hook (Anna Sherwood repost) as beat-1, FDE hook-bank line for beat 2, Claude Code/Cursor JD detail for beat 4. Second drip for peer-IC Talha Mushtaq (recommended_lead referral path) per section 4/4a, InMail channel (Low/Medium email → but recruiter has Medium email → email; Talha InMail). 8 drafts total, all 50–125 words (FU2 ≤40), zero banned phrases, every hook real (non-fabricated). Writes Cold Outreach.md.

**actual:** Wrote Cold Outreach.md: 2 drips × 4 = 8 drafts. Brittany (recruiter, email, §1/1a) beat-1 uses her REAL enrich hook (reposted Anna Sherwood's Chicago eng/PM post). Talha (peer-IC, InMail, §4/4a) beat-1 uses his REAL "just started as AI Product Engineer (Forward Deployed)" post. urgency=none → beat 3 omitted everywhere; both Hail Marys explicitly marked do-not-send-unless-real with bracketed placeholders. Word counts: Brittany 114/44/12/48, Talha 104/42/17/44 — all within the §1a/4a ranges (intro 50–125, FU1 ≤60, FU2 ≤40). Banned-phrase scan: 1 hit caught + fixed ("highest-leverage" → "highest-payoff" in a Notes line); final file CLEAN. **Both outreach targets (Brittany + Talha) were read from the POST-4b ledger.** **prediction_met: true.**

**Outreach targeted the post-enrichment #1 recruiter:** YES — Brittany Giacomo, the top recruiter row in the final (post-enrich) ledger. Enrich did not change the top recruiter (it appended an HM, Kishore Nair), so the target is provably from the final sort, not a stale pre-enrich capture.

---

## End-of-run verdict

- End-to-end: Steps 2→5 all completed (Step 1 intake skipped per harness; Steps 6/7 done as richer trace logging).
- All 4 prediction-bearing steps: prediction_met=true.
- 11 LinkedIn calls, all sequential, zero transport errors, zero retries needed.
- Ledger round-trip: PASS (same 16-col schema, 1 enrich row appended + re-sorted, hooks/gaps added).


