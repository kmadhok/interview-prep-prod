# 6-Day Prep Schedule — Walmart Principal Data Analyst (R-2490148)

**Interview:** Friday, May 29, 2026 · **Prep window:** Sat May 23 → Thu May 28 (6 days)

## The situation in one paragraph

The recruiter said the 5/29 round was a HackerRank coding assessment. It is now clear it is also a **panel interview** — three interviewers: Sowjanya Reddy (Senior Manager, likely the hiring manager), Lakshman Rajagopal (Sr Manager, Data Analytics — the practitioner/peer voice), and Wei Jia (Data Science Lead, runs Walmart's GenAI strategy — the technical visionary). How the coding and the panel fit together is still unknown, so **Step 1 below is non-negotiable: confirm the format with the recruiter today.** Until that reply lands, this plan assumes a roughly 55/45 split between coding prep and panel/story prep. Adjust once you know more.

## How effort is weighted

- **Coding (~55%)** — front-loaded onto the weekend and Memorial Day, because skill-building needs runway. Heaviest on data-structures/algorithms (rustiest area for a working analyst), solid on SQL (your home turf — confidence reps, not learning), lighter on pandas (closest to your day job).
- **Panel / story (~45%)** — built mid-week, because it is recall and rehearsal rather than new skill. The centerpiece is a tight AI-augmented-analytics story for Wei Jia, plus craft/speed stories for Lakshman and motivation/coaching stories for Sowjanya.
- **Calendar note:** Monday May 25 is Memorial Day — if you have it off, it is a third heavy block. If you have to work it, shift its load into the Sat/Sun blocks and treat Mon as an evening day.

---

## STEP 1 — Send this to the recruiter today (Saturday, via Teams)

Do this before any prep. It is the single highest-leverage thing you can do, and it is the exact lesson from the Agent Builder panel — never walk into a format the recruiter didn't brief. Monday is Memorial Day, so even sent today she will not see it until Tuesday — which leaves only Tue/Wed/Thu for a reply. Send it now.

> Hi [Recruiter name] — quick question ahead of Friday's interview for the Principal Data Analyst role (R-2490148). I'd originally understood it as a HackerRank coding assessment, but I've since learned there's a panel too, and I want to prep the right way. Could you help me understand how it's structured?
>
> A few specifics if you have them:
> - Is the coding done live with the panel, or separate from the panel discussion?
> - Roughly how's the time split, and how many coding questions should I expect?
> - Will it use SQL, Python, or both — and are AI tools allowed during that part?
> - Anything I should prepare or bring beforehand?
>
> Thanks so much!

When the reply lands (hopefully Tue/Wed), revisit this plan: if coding is a small live portion, shift weight to panel prep; if there's a prepare-something ask, that becomes the top priority immediately.

---

## Day 1 — Saturday May 23 (heavy block, ~4–5 hrs)

**Coding (~2.5 hrs)**

- Send the recruiter message above. First thing.
- Set up your environment: a HackerRank practice account, a **bare code editor with no Copilot/Cursor**, and a SQL practice surface (HackerRank's SQL track, or DB Fiddle / LeetCode's database problems).
- Diagnostic run — find your rust level: 2 easy data-structures problems, 1 pandas wrangling problem, 2 SQL queries. Time each one. Note where you stall — that tells you where Tue/Wed reps should go.

**Panel (~1.5 hrs)**

- Re-read the JD slowly. For each of the 5 must-have skills, write down the one project of yours that proves it.
- Skim the root `Master Story Bank.md` and shortlist 5–6 stories that could carry the panel.

## Day 2 — Sunday May 24 (heavy block, ~4–5 hrs)

**Coding (~3 hrs)**

- Data-structures focus (your rustiest area): arrays, strings, hashmaps/dictionaries, two-pointer. 8–10 easy-to-medium problems, bare editor, timed.
- SQL block: joins (inner / left / self), aggregations, GROUP BY / HAVING. 6–8 queries.

**Panel (~1.5 hrs)**

- Draft the **Wei Jia story** — your AI-augmented-analytics walkthrough, built around the NL-to-SQL Copilot demo (see root `Demo Portfolio.md`). 2–3 minutes spoken: the problem, what you built, the agent design, the impact. Wei Jia built an "Analytic Agent" for root-cause analysis and a "Copilot Chatbot" — your demo is the same idea, so connect it explicitly to "moving the team from static reporting to AI-augmented analytics." Say it out loud twice.

## Day 3 — Monday May 25 (Memorial Day — heavy block if off, ~4–5 hrs)

**Coding (~3 hrs)**

- SQL: window functions (ROW_NUMBER, RANK, LAG/LEAD, running totals), subqueries, CTEs, top-N-per-group. 6–8 queries.
- pandas: groupby/agg, merge, pivot, handling missing data. 6–8 problems.
- Data-structures: keep the reps going — sliding window, sorting, counting/frequency, basic recursion. 6–8 problems.

**Panel (~1.5 hrs)**

- Adapt your **Tell Me About Yourself** from the root `Tell Me About Yourself - Master.md` into a cue card for this role (save it in this folder as `Tell Me About Yourself - Cue Card.md`). Tune the closing line toward AI-enabled analytics. Rehearse it.
- **Mid-prep checkpoint:** by tonight the data-structures rust should be lifting. If it isn't, reweight Tue/Wed evenings toward DS.

## Day 4 — Tuesday May 26 (workday, evening ~2–3 hrs)

**Coding (~1.5 hrs)**

- Timed mixed set under a clock: 1 data-structures + 1 SQL + 1 pandas problem in ~45 minutes, then review. This rehearses the *shape* of the assessment, not just the topics.

**Panel (~1 hr)**

- Prep STAR stories for the two craft/manager lenses. For **Lakshman**: speed and end-to-end delivery — a time you took something from ambiguous problem to delivered solution fast. For **Sowjanya**: why this role and why the internal move, handling ambiguity, stakeholder management, and a coaching/mentoring example (the JD leans hard on "advise and coach other analysts"). Pick 4–5 stories from the Story Bank; write tight bullets, don't script.

## Day 5 — Wednesday May 27 (workday, evening ~2–3 hrs)

**Coding (~1.5 hrs)**

- Target the weakest area from Tuesday's timed set — 6 or so problems there. Quick refresh of anything SQL that felt slow.

**Panel (~1 hr)**

- Write your **questions to ask each panelist** — something specific for Sowjanya (team/role), Lakshman (the analyst craft and what "good" looks like), and Wei Jia (where the GenAI roadmap is headed).
- Rehearse the Wei Jia demo story and TMAY out loud.
- Check whether the recruiter has replied — if the format news changes anything, adjust tomorrow's mock.

## Day 6 — Thursday May 28 (workday, evening — lighter, ~2 hrs)

- **One full timed 60-minute mock** in real conditions: bare editor, no AI, 3–4 mixed problems. Then a light review only — do not cram new material the night before.
- One clean spoken run of TMAY + the Wei Jia story + 2 STAR stories.
- Logistics: confirm the interview time and time zone, test the HackerRank / video setup, check camera, mic, and internet, have the join link ready. Lay out water and a notebook. Early night.

## Interview Day — Friday May 29

- Light warm-up only: 1–2 easy problems to get your hands moving, and one read-through of your TMAY cue card and the Wei Jia story. No new material.
- During the coding: **bank the easy points first** — do the SQL/pandas you're fluent at fast, lock in the score, then spend remaining time on the hard problem. **Stuck rule:** if you're 8–10 minutes into a problem with no traction, move on and come back.
- If anyone is on the call, **talk through your approach out loud** — it earns partial credit and opens the door to hints.

---

## Quick reference — what each panelist is testing

- **Sowjanya Reddy (Senior Manager / likely hiring manager):** motivation, role fit, working style, handling ambiguity, stakeholder management, coaching mindset, Principal-IC-level ownership.
- **Lakshman Rajagopal (Sr Manager, Data Analytics — peer/practitioner):** hands-on craft — SQL depth, dashboarding, delivery speed, end-to-end ownership. You both worked at Walmart in May 2023 — a natural warm opener.
- **Wei Jia (Data Science Lead — GenAI strategy):** technical depth on AI-augmented analytics, LLMs, agentic systems. Your NL-to-SQL Copilot demo is your strongest card here.

## Reusables to pull from (root folder)

- `Master Story Bank.md` — STAR stories; select and tailor, don't rewrite.
- `Tell Me About Yourself - Master.md` — copy the closest archetype into this folder as the cue card.
- `Demo Portfolio.md` — canonical NL-to-SQL Copilot description, URL, and talking points.
