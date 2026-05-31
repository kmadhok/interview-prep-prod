# Interview Prep Schedule — BCG X First Round

**Role:** BCG X — Senior AI Factory Product Builder
**Recruiter:** Ganna Volkova (NAMR Senior Recruiter)
**Interview:** **Mon 2026-06-01, 2:00 PM ET (1:00 PM CT) with Maan Hani, Principal** (confirmed by BCG 5/29)
**Zoom:** see `Messages with Recruiter.md` (5/29 confirmation email)
**Format:** ~60 min combined — **(1) behavioral**, **(2) technical / AI background**, **(3) case interview (whiteboarding)**.
**Case emphasis:** structuring ambiguous business problems, logical reasoning. Clarity > "perfect" answer.
**Honor code:** no external resources, no AI tools (ChatGPT, Gemini, Claude, etc.) during live case. Destroy notes after.

**Window left:** Fri 5/29 evening · Sat 5/30 · Sun 5/31 · Mon 6/1 morning. ~3 prep days.
**Today's reality:** Walmart Principal Data Analyst panel is TODAY 5/29. Don't try to prep BCG before that's done. Schedule below assumes BCG prep starts **Fri 5/29 evening** after the Walmart panel.

**Interviewer & format brief:** see `Interview with Maan.md` (merged file — interviewer background + segment-by-segment format + Zoom Whiteboard layout + questions to ask + time budget). TL;DR on Maan — PhD astrophysics (U. Victoria) → LinkedIn → BCG; recently promoted to Principal. Technical-deep, will respect rigor; cares about adoption + measurement, not architecture for its own sake. Don't lead with his bio; let it surface naturally if it does.

---

## Day 1 — Fri 2026-05-29 (evening, after Walmart panel) — Decompress + orient (45 min)

You just did the Walmart panel. **Tonight is not drill night** — it's a read-and-plan session. Energy will be low; that's fine.

- [ ] Re-read this schedule + `Interview with Maan.md` (10 min)
- [ ] Re-read the JD slowly. Highlight verbs you can map to a real project (10 min)
- [ ] From root `Master Story Bank.md`, pick the **4 STAR stories** you'll lead with. Mark them. Favor: shipped-an-AI-product, ambiguity-to-solution, end-to-end ownership, internal innovator / champion. **One should be a failure / what-I'd-do-differently** (10 min)
- [ ] From root `Demo Portfolio.md`, pick the **2 demos** for the technical segment (NL-to-SQL Copilot + one Walmart internal). Note the URL/visual you'd open if asked (10 min)
- [ ] Stop by 9pm. Sleep.

**End-of-day check:** Can you list, from memory, the 4 stories + 2 demos you'll lead with?

---

## Day 2 — Sat 2026-05-30 — Behavioral + technical talk track (120 min, split AM/PM)

### AM block (60 min) — Behavioral reps

These are 80% built in the root Story Bank. Today is **voice work** — practice out loud, not in your head. Structure: Situation → Action → Outcome, with a clear "what I'd do differently" beat on the failure story.

- [ ] Practice your **60-second opener** (TMAY — Consulting / Product Builder variant from root `Tell Me About Yourself - Master.md`) out loud, 5× (15 min)
- [ ] Copy that variant into `Tell Me About Yourself - Cue Card.md` in this folder. Tune the closing line for AI Factory specifically — emphasize *building AI tools consultants actually adopt* (10 min)
- [ ] **3 lead behavioral stories at 90 seconds each, 3× per story.** Open with the business problem in dollars/hours, close with the quantified outcome (25 min)
- [ ] **Failure story, 3×.** Include the "what I'd do differently" beat explicitly (10 min)

### PM block (60 min) — Technical / AI background talk track

Maan is technical-deep. **Don't dumb down architecture** — but frame every demo as: *what was broken → what I built → who uses it → what changed.* Adoption + business outcome bookends the architecture.

- [ ] Sketch a **3-bullet "AI work to date" arc** on paper. Order: most recent → most impactful → most BCG-relevant (10 min)
- [ ] **NL-to-SQL Copilot walkthrough**, out loud, 4 min max. Structure: problem framing → architecture (agent loop, LangChain, tool use, eval harness) → who uses it / what changed → what you'd build next. **3 reps** (20 min)
- [ ] **Walmart Data Ventures internal agent walkthrough**, out loud, 4 min max. Same structure. **3 reps** (20 min)
- [ ] **Tool-fluency check** — 30-second answers to: "How do you decide when to use Claude Code vs writing an MCP server?", "Where does your eval loop live?", "How do you handle hallucinations or low-confidence outputs?" (10 min)

**End-of-day check:** Can you walk a non-technical consulting lead through one of your AI builds in 4 minutes and end on adoption / business impact, not on architecture?

---

## Day 3 — Sun 2026-05-31 — Case interview drills (150 min) ⭐ highest leverage day

**This is the new muscle.** BCG cases are about **structure under ambiguity** — Maan wants to see how you decompose a problem out loud, where you'd dig deeper, what tradeoffs you'd flag. The AI Factory twist: cases will likely be product-shaped — *"BCG wants to build an internal AI tool that does X — how would you scope and build it?"*

**Universal structure — memorize this. Say it out loud at the start of every drill, and at the start of the live case.**

1. **Clarify** — restate the problem in your words, ask 2–3 scoping questions
2. **Frame** — sketch a 2×2 or tree of how you'll think about it (call it out loud as you draw)
3. **Prioritize** — pick the branch with the most leverage, say *why* (Pareto / reversibility / time-to-value)
4. **Solution** — what you'd build, who uses it, what data/integrations, what could go wrong
5. **Measure** — how you'd know it worked (dollars / hours / adoption %)

Maan is a PhD scientist — **he will notice if you skip "Measure."**

### Drills

- [ ] Read the JD's "What You'll Do" section once more, slow. Cases will live in this universe (10 min)
- [ ] Memorize the 5-step structure. Say it out loud 3× before the first drill (5 min)
- [ ] **Case 1 (30 min):** "BCG consultants spend ~6 hours/week building client-status decks from disparate inputs. Design an AI product to cut that in half. Walk me through it." Whiteboard on paper. Talk all 5 steps. 20 min speaking + 10 min review
- [ ] **Case 2 (30 min):** "BCG's internal benchmarking team wants an agent that pulls comparable-company financials and writes a one-page synthesis. How would you build it, and how would you validate it works?" Same structure. **Lean into the eval-strategy step — Maan will weight this**
- [ ] **Case 3 (30 min):** "A partner says 'consultants keep ignoring the AI tools we ship.' What's going on, and what would you build to fix it?" Product-adoption-shaped, not feature-shaped. **Practice resisting the urge to jump straight to a tool** — Maan as a Principal scopes adoption problems, not features
- [ ] **Self-review (15 min):** Where did you skip a step? Where did you jump to a solution before framing? Where did "Measure" feel weak? Note 2 patterns to watch tomorrow
- [ ] **Whiteboarding logistics check (5 min):** Confirm the medium (likely Zoom whiteboard given remote round). Have a blank Zoom whiteboard tab open Monday. Practice writing legibly with the mouse / trackpad

**End-of-day check:** On a fresh prompt, can you say the 5-step structure out loud and walk through it cleanly in ~15 min, ending on measurement?

---

## Day 4 — Mon 2026-06-01 (morning) — Light review + 1 mock + stop (90 min, then stop)

Interview is at **1:00 PM CT**. Plan to stop prepping by **11:30 AM CT** to eat lunch + decompress.

- [ ] **6:00am-ish wake. Coffee. Phone away** (until prep block starts)
- [ ] **8:30–9:00 — TMAY + opener** review (out loud, 3×). Check cue card is on screen (30 min)
- [ ] **9:00–9:15 — Re-read your 4 lead behavioral stories** (silently, fast) (15 min)
- [ ] **9:15–9:30 — Re-read the 5-step case structure.** Say it out loud 3× (15 min)
- [ ] **9:30–10:00 — One fresh case drill, 30 min max.** Use a prompt you haven't seen before (Google "internal AI tool product case interview" or invent one — e.g. "Design an AI tool to help BCG case teams find and adapt assets from past engagements"). Focus on opening structure + ending with Measure (30 min)
- [ ] **10:00–10:15 — Logistics check:** Zoom link tested, camera/mic working, desk clear, water, notepad + 2 pens for whiteboarding offline if needed, **JD + resume open in side tabs**, Maan brief open in another tab (15 min)
- [ ] **10:15–10:30 — Final review:** the 3 questions for Maan (cue card or sticky note next to monitor) (15 min)
- [ ] **10:30 — STOP.** Lunch, walk, shower, decompress. Don't open the schedule again.

### Day-of (12:55 PM CT)

- [ ] Be at the Zoom link 5 min early per BCG's instruction
- [ ] On the case: **say the 5-step structure out loud at the start.** It buys you 30 seconds to think and signals you're structured
- [ ] On the technical segment: open with the *business problem*, not the architecture
- [ ] Pause before answering. 3 seconds + structured beats 1 second + rambling
- [ ] Remember: you've actually built the thing they're hiring for. Talk like a peer, not a candidate

---

## After the interview

- [ ] Within 24h, send Maan + Ganna a personalized thank-you note. Reference one specific thing Maan said. Use the post-interview thank-you template from root `Outreach Templates.md`
- [ ] Write down every question Maan actually asked while it's fresh. Save to this folder as `Post-Interview Debrief.md`. If you advance, the next prep starts from that list

---

## What to skip

- LeetCode / DSA — not that kind of round
- Memorizing case answers verbatim — judged on structure, not content recall
- Reading the JD more than the times listed
- Cramming the day before (Sun is the last real drill day; Mon is taper)
- Learning a new framework you've never used (Profitability, M&A, etc.) — the 5-step structure above is enough

## If you fall behind

Skip in this order: Day 2 tool-fluency check → Day 2 failure-story extra reps → Day 4 fresh case drill (replace with re-reading Day 3 self-review notes).

**Never skip:** Day 3 cases (the new muscle), Day 4 logistics check + sleep.

## Confirmation reply to BCG

BCG asked you to **reply-all with "I will"** to confirm + acknowledge the honor code (no AI tools, destroy notes, no screenshots, etc.). Do this **today** if you haven't — locks the slot. Recipients: bcgxnamrrecruiting@bcg.com, volkova.ganna@bcg.com, meek.caroline@bcg.com, bethel.abbey@bcg.com.
