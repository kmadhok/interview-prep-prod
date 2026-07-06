# Round 2 Prep Plan — BCG X (Senior) AI Factory Product Builder

**Interview:** Tuesday, June 16, 2026 · 12:00 PM ET (11:00 AM CT) · Zoom `bcg.zoom.us/j/94249303795`
**Interviewer:** Patrick Freyer — LinkedIn (verified 6/10): "Applied AI (Forward Deployment) Leader @BCG"; Head of Applied AI (Forward Deployment) Europe since Oct 2025; founded BCG's Forward Deployment pod Jul 2025. (BCG email listed "Consultant" — LinkedIn supersedes.)
**Format (Reilly, 6/8):** "A deeper conversation about your background and experience building AI products. **No additional assessments or whiteboarding.**"
**Honor code still applies:** no AI tools / external resources live; keep content confidential; destroy notes after.

> **One-line strategy:** Round 1 (Maan, PhD scientist) rewarded *rigor*. Round 2 (Patrick, builder-shipper) rewards *shipped products with real users and a product instinct*. Same projects, different emphasis: lead with adoption, commercialization-style thinking, and the live demo — not eval theory.

---

## 1. Who Patrick is — and why it changes the round

Patrick is a **GenAI builder and shipper**, not an academic. Public signal is consistent across his own site, GitHub, and posts:

- Describes himself as a **"Generative AI Builder, Developer, and Strategist."** Builds and *publishes* apps across podcasts, health, and forestry — i.e. he ships and maintains real products, not demos.
- Built **AiAssist** — a secure LLM service for iOS/macOS that **detects and redacts sensitive information before requests hit the LLM**. Reportedly hit ~10k users in its first week and was commercialized.
- Background: **Yale**, prior **investment banking at UBS (London)** → BCG (~5 yrs). Business-to-builder arc, not CS-PhD arc.
- Runs a personal site with **his own AI assistant** as a contact channel and even a personal flights tracker — he automates his own life with the same tools he'd deploy for clients. Also shipped **Synthorated.com** — personalized AI-generated podcasts, built in public, weeks of late-night coding.
- **Title CONFIRMED (LinkedIn, 6/10):** "Applied AI (Forward Deployment) Leader @BCG." Founded the Forward Deployment pod (Jul 2025, "created the rapid build function of BCG"), Head of Applied AI Europe since Oct 2025, started the team in Denver, scaled Europe, now expanding globally. You're talking to **the person who built and runs the function you're applying into** — not a line interviewer. He hires "strategise, develop, test and refine all in one" profiles.

**Fresh post intel (last 3 months — use as rapport bridges, never quote his posts at him):**

- **MCP post:** "The question isn't 'which framework' anymore — it's 'which MCP servers do we need and what governance?'" → your *"MCP layer is where I enforce what the agent is allowed to look at"* line is now a **direct hit**, not just an AiAssist bridge. If governance comes up, this is your strongest moment.
- **Embed-in-workflow post:** he champions "AI that meets users where they already work (email, existing data systems, PowerPoint)" → identical to your *"don't build a destination, embed in the workflow"* V1-RAG lesson. He will recognize this instinct as his own.
- **Claude Code:** his team reshares describe using **Claude Code daily** and presenting at an Anthropic stand → you use **Wibey (Walmart's internal Claude Code fork) daily**. Natural, specific tooling rapport — say "Walmart's internal fork of Claude Code," don't assume he knows "Wibey."
- **Dev-pipeline post:** "testing merged into building… production became the test lab… the best software tests itself" → aligns with your A5 production-stability beat (state persisted, headless cron, no LLM-memory reliance).
- **AI-news agent:** he ships a weekly AI recap "researched, curated, and produced entirely with an AI agent" — co-built with Claude. He values agents that ship artifacts, not chat.
- **India trips:** ran hackathon-style trainings (idea → working prototype in an afternoon; "build, break, rebuild until it works"). Speed-to-working-thing is his core hiring filter.
- **Mutual connections:** Bharath and Xingchen (Lulu) — only mention if genuinely relevant.

**What this means for your prep, concretely:**

1. **This is builder-to-builder.** Talk like a peer who ships, not a candidate explaining a résumé. He'll smell theater instantly because he does this work himself.
2. **Adoption and users beat architecture diagrams.** With Maan you led with the eval gate. With Patrick, lead with *"stakeholders never knew an agent was answering them"* and *"the only AI skill in active use by business teams."* Real usage is his currency.
3. **The live demo is now an asset to lean toward, not hold back.** Patrick ships and publishes apps — "here's a URL you can hit right now" is a language he speaks. (With Maan it was a tertiary; with Patrick keep it close and offer it.)
4. **You have a genuine rapport bridge: data governance at the model boundary.** His AiAssist redacts sensitive data *before* it reaches the LLM. Your Jira agent uses the **MCP layer as the control boundary — "where I enforce what the agent is allowed to look at."** Same instinct, different surface. If governance/security/PII comes up, connect them — don't force it, but it's real.
5. **No whiteboard / no case.** Reallocate all the round-1 case-drilling time into *project narratives, product thinking, and genuine conversation.* The new failure mode isn't a blank whiteboard — it's **rambling** in an open conversation. Tight stories, then let it breathe.

---

## 2. What to lead with (project selection for Patrick)

Pull from root `AI Build Walkthrough - Master.md`. For Patrick, the order shifts toward shipped + demoable:

| Slot | Project | Why for Patrick |
|---|---|---|
| **Lead** | **A3 — Jira Resolution Agent** | Shipped, adopted, "stakeholders never knew," portfolio-effect close. Strongest builder-credibility story you have. |
| **Second** | **A1 — Self-Service Analytics Agent** | "Only AI skill in active use by business teams." Adoption is the headline, sub-agent design is the depth he can probe. |
| **Demo-forward** | **A7 — Live Text-to-SQL Copilot** | Offer it: *"It's live if you want to try it."* A shipper respects a runnable URL. Pattern-matches to how he works. |
| **In pocket** | **F1 — FTI capstone** | Now *more* relevant than for Maan: client RFP → deployed artifact in a fixed timeline = the literal shape of forward-deployed work. Use if he goes consulting/client-delivery. |
| **Skip** | I1 (Innovare), U1 (donation experiment) | Too early-career / too academic for a builder-shipper close. |

**Close every walkthrough on the through-line:** *"Automating my role bought me the time to build the rest."* That's the line that reads as principal-level product judgment to someone who builds compulsively.

---

## 3. Phrases & hooks tuned to a builder-shipper (drop naturally, don't force)

- *"Don't build a destination, embed in the workflow."* — your V1-RAG failure lesson; pure product instinct, his home turf.
- *"Stakeholders never knew an agent was answering them."* — adoption as invisible UX.
- *"The MCP layer is where I enforce what the agent is allowed to look at."* — bridges to his AiAssist redaction instinct.
- *"Automating my role bought me the time to build the rest."* — portfolio effect / leverage.
- *"It's live if you want to try it."* — demo-forward confidence.
- *"I optimized for the analyst not having to babysit the pipeline."* — shipper's definition of done.
- *"I use Walmart's internal fork of Claude Code daily — most of my builds start there."* — tooling rapport; his team lives in Claude Code.
- *"The framework question matters less than which MCP servers you trust and what governance sits on them."* — his own publicly stated view; arrive at it independently from your Jira-agent experience.

**Avoid:** leading with eval philosophy, "I fundamentally believe," tool-listing ("LangChain, Pinecone, Claude…"). Replace tool lists with *"I used X because Y; if Y weren't true I'd use Z."*

---

## 4. Likely conversation arcs (no case, so prep these instead)

Because it's conversational, expect open prompts rather than a structured case. Have a crisp first 30 seconds for each:

1. **"Walk me through something you've built."** → A3, 4-beat scaffold, ~4 min, hard stop.
2. **"Why BCG X / why forward deployment?"** → the work you already do (biz/tech generalist, end-to-end, first-principles) at the scope it was sized for; you want to build AI products consultants actually adopt, embedded with the client, not slideware.
3. **"What's the hardest part of getting people to actually use what you build?"** → the V1-RAG failure → embed-in-workflow lesson; adoption mechanics (2-team pilot → weekly-active gate → scale).
4. **"How do you make agents production-stable?"** → A5 (no LLM-memory reliance, state persisted, headless cron) — the beat most candidates can't articulate.
5. **"How do you think about data governance / sensitive data with LLMs?"** → MCP-as-control-boundary; grounded answers (can only cite what the SQL returned); abstain over guess. (Natural bridge to his AiAssist work if he raises it.)
6. **"What would you build next / where's the field going?"** → move the human from author to gate; process-level eval; self-improving semantic layer. Have one genuine opinion, not a survey.
7. **"Tell me about yourself."** → the 60-sec builder TMAY (below).

---

## 5. Day-by-day plan (June 8 → June 16)

You already have a deep round-1 base (cheat sheet, walkthrough cue card, technical Q&A, architecture breakdown). This round is **re-tuning, not rebuilding** — lighter lift, but the conversational format needs reps in dialogue, not monologue.

**Mon Jun 8 (today) — confirm + orient (20 min)**
- Reply-all **"I will"** to the confirmation email (attendance + honor code). *Highest priority — do today.*
- Read this plan + skim Patrick's LinkedIn/site once so his profile is in your head, not on a page.

**Tue Jun 9 — re-tune the openers (45 min)**
- Rewrite your TMAY for a *builder* audience (not the scientist version). Land the close on "build AI products consultants actually adopt."
- Re-rank your walkthroughs to the table in §2. Update `AI Build Walkthrough - Cue Card.md` with Patrick tweaks (or note them here).

**Wed Jun 10 — A3 + A1 drills (45 min)**
- Run the Master drill: 3× A3, 2× A1. Out loud, phone timer, hard cut 4:00. Self-score the 5-question rubric. Goal: 4/5 yes on 3 consecutive A3 reps.
- Emphasis shift vs. Maan: open and close on **adoption**, not eval.

**Thu Jun 11 — demo + governance (45 min)**
- Run the live demo yourself end-to-end so you can drive it smoothly if asked. Confirm the URL is up: `https://sql-rag-frontend-simple-481433773942.us-central1.run.app/`
- Draft the 2-sentence governance bridge (MCP control boundary ↔ his AiAssist instinct). Don't memorize — internalize.

**Fri Jun 12 — conversational reps (45 min)**
- This is the key new rep type. Practice arcs 2–6 from §4 as *answers in a conversation*, not speeches: ~60–90 sec each, then a hook back to him ("…is that close to how AI Factory thinks about it?").
- Record one and listen for rambling. Cut anything past 90 sec.

**Sat Jun 13 — light, optional (30 min)**
- One full A3 + one conversational arc. Don't overtrain. Rest the voice.

**Sun Jun 14 — finalize questions + cheat sheet (30 min)**
- Lock your 3 questions for Patrick (§6). Build a glance-only day-of cheat sheet (triggers + first words, like the round-1 one).

**Mon Jun 15 — last reps (30 min)**
- 2 reps total: 1× A3, 1× "why BCG X." Stop by evening. Confirm tech (camera, mic, quiet room, charged).

**Tue Jun 16 — day of**
- Zoom 5 min early. Glance at cheat sheet, don't read. Open every story on the *problem in hours/dollars*, not architecture.
- Offer the demo if it fits. Be a peer, not a candidate.
- Thank-you note to Patrick (and cc the recruiting team) within 24h.

---

## 6. Questions to ask Patrick (pick 3, tuned to him)

1. "You built the Forward Deployment function from scratch and scaled it from Denver to Europe and now globally. As it scales, what separates the builders who thrive in it from ones who don't?" *(he founded the function — let him talk about it; the answer tells you exactly what he's screening for)*
2. "When you forward-deploy, what separates a build that the client team keeps using after you leave from one that quietly dies?" *(adoption — your core thesis, and his lived experience)*
3. "What's an AI Factory pattern or internal tool you've shipped that you wish more of the org used?" *(invites a builder-to-builder exchange; reusable from round 1, still strong)*
4. *(Spare)* "Your team runs idea-to-prototype-in-an-afternoon hackathons with clients. How do you keep those prototypes from dying after the workshop high wears off?" *(speed + adoption in one question; grounded in his India work without quoting his posts)*

*Avoid* re-asking the Maan questions verbatim — Patrick's a different person; lead with the AiAssist/forward-deployment angle that's specific to him.

---

## 7. Day-of guardrails

- **New failure mode is rambling**, not a blank whiteboard. Tight stories (≤4 min builds, ≤90 sec conversational answers), then hand the ball back.
- **Pause 3 seconds before answering.** Structured-slow beats fast-rambling.
- **Lead with the business problem**, close on adoption, name one tradeoff, offer the demo.
- **His title is confirmed** (Forward Deployment Leader / Head of Europe) — you can reference his function naturally, but don't recite his LinkedIn at him. Know it; don't perform it.
- Honor code: no AI tools, no second screen, no notes you'd keep.

---

*Sources for Patrick intel: his personal site (patrickfreyer.com), his full LinkedIn profile + recent posts (pulled 6/10 — title now verified), and recruiter email (Reilly, 6/8). Substance content pulls from root `AI Build Walkthrough - Master.md` and round-1 `Interview Cheat Sheet.md`.*
