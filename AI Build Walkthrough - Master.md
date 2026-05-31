
# AI Build Walkthrough — Master

**Purpose.** Cross-role reusable. The structured way Kanu talks about every AI/data project he's shipped. Built so that when an interviewer says *"walk me through an AI product you've shipped"* or *"tell me about your most interesting build,"* he has a memorized scaffold and pre-written ~4-minute talk tracks per project — not a sideways ramble through 5 projects in 90 seconds.

**Rule for future tailoring.** This file mirrors the discipline of `Resume Achievements Master.md`. Every quantified claim here comes from a **Verified proof point** in that file. If a fact isn't there, this file doesn't say it. Placeholders use `[VERIFY: ...]` — Kanu fills in or removes; we never invent.

**Source of truth precedence:** `Resume Achievements Master.md` for facts → this file for *shape and voice* → role-folder `AI Build Walkthrough - Cue Card.md` for *selection + role-specific tweaks*. Same precedence model as Story Bank → role `Interview Answers.md`.

---

## The 4-Beat Scaffold (memorize the beat names, not the words)

Every AI-build walkthrough fits this shape. ~4 minutes total. ~1 minute per beat.

1. **PROBLEM** — in dollars / hours / people. Not the tech.
2. **BUILD** — 3 architectural beats, name 1 real tradeoff.
3. **EVAL** — name the *gate*, not the philosophy. Own the gap if there is one. Name the abstain mechanism (or lack of one).
4. **ADOPTION + WHAT'S NEXT** — who uses it, what changed, what you'd build on top of it.

**The single sentence to lock in before every walkthrough:**

> "Problem in hours, build in three beats with one tradeoff, eval as a gate, close on adoption and what's next."

Say it 3× before every rep. It's the muscle memory.

---

## Universal anti-patterns

These are the ones Kanu actually does under pressure — name them out loud during drills so they stop showing up live.

- **Closing beat 1 on philosophy** ("I design my agents around observability and manageability"). That goes in beat 3 if anywhere. Beat 1 closes on the dollar/hour outcome.
- **Listing projects sideways in beat 4** without the through-line. The through-line is *"automating my role bought me the time to build these"* — say that first, then list 2–3 max.
- **Saying "I fundamentally believe"** about eval. Belief isn't eval. Technical interviewers pounce. Replace with a gate or own the gap explicitly.
- **Going past 4:30.** If a case interview comes after, the case is the protected segment. Don't eat it with rambling on a build walkthrough.
- **Skipping the abstain mechanism in beat 3.** If you don't have one, say so and name the next version. Don't pretend.
- **Listing tools instead of reasoning** ("I'd use LangChain, Pinecone, Claude, MCP"). Says nothing. Replace with *"I used X because Y; if Y weren't true I'd use Z."*

---

## Tells that signal builder-with-judgment (drop in naturally, don't force)

These land especially well with technical-deep interviewers (PhD scientists, ex-FAANG ICs, ML researchers). Tuned to read as builder phrases, not buzzwords.

- "Context engineering, not prompt engineering."
- "I went X over Y because Y would have been faster to build but I'd have lost the audit boundary."
- "Today, I'm the gate. The next version moves the gate to [mechanism]."
- "The failure mode I worry about most is [confident-wrong / silent-failure / stale-context]."
- "Stakeholders never knew an agent was answering them."
- "Automating my role bought me the time to build [the rest]."
- "Externalizing memory to artifacts — long-running agents lose coherence as the context window fills."
- "Eval changes as the data changes. A static golden set decays."

---

## Drill pattern

Run this 5× before any interview where AI-build walkthroughs will come up. Out loud. Phone timer.

1. Say the single sentence (*"Problem in hours, build in three beats with one tradeoff, eval as a gate, close on adoption and what's next."*) 3×.
2. Pick a project from this file.
3. Time yourself: 45 sec problem → 75 sec build → 75 sec eval → 45 sec adoption. Total ~4 min.
4. Hard-cut at 4 min even if not done. Better to stop mid-beat 4 than to ramble.
5. After each rep, self-score:
   - Did I land all 4 beats? (Y/N)
   - Did I name one tradeoff in beat 2? (Y/N)
   - Did I name a gate or own the gap in beat 3? (Y/N)
   - Did I close on adoption + a "what's next" in beat 4? (Y/N)
   - Did I land within 4:30? (Y/N)

5 of 5 yes = ready. Below = one more rep.

---

# Project Walkthroughs

Each entry pairs the canonical `Resume Achievements Master.md` ID, a one-line summary, and a pre-written ~4-minute walkthrough in Kanu's voice. **For role-specific interviews, the role's `AI Build Walkthrough - Cue Card.md` selects which 2-3 of these to lead with and any role-specific tweaks.**

---

## A3 — Autonomous Jira Ticket-Resolution Agent

**One-liner:** Production agent that took 400+ Walmart data-readiness tickets from 30–60 min per request (full day for complex ones) to under 10 min. Stakeholders never knew it was an agent.

**Best for:** Builder-credibility opener. Pairs ownership + scale + honesty about HITL gap. Strongest single walkthrough Kanu has.

### Beat 1 — PROBLEM (~45 sec)

> "In my role I'm the inbound queue for data-readiness and stewardship questions across our Customer Perception platform at Walmart. Since January 2025 I've taken 400+ tickets across 8 categories — each one runs 30 to 60 minutes, and the complex ones can take a full day. Conservatively that's about a month of work-days a year just answering the same shape of question. I built an agent that takes most of those to under 10 minutes, and the stakeholders on the receiving end never knew an agent was answering them."

**Why this opens strong:** dollars-equivalent up front (a month of work-days), real volume (400+ across 8 categories — both from verified proof points), honest range (30–60 min, sometimes a full day), and the close — *"stakeholders never knew"* — is the product-instinct line that earns immediate credibility.

### Beat 2 — BUILD (~75 sec)

> "It's a 6-gate pipeline — triage, context, plan, execute, validate, report. The two things that actually mattered architecturally:
>
> **One — context engineering, not prompt engineering.** I built an MCP server over the BigQuery platform plus a FAISS + BM25 retrieval layer over 11,000 historical SQL queries I'd written before. The agent doesn't get raw schema — it gets a curated context interface. I went MCP over giving the agent direct DB credentials because the MCP layer is where I enforce *what the agent is allowed to look at*. Direct credentials would have been faster to build but I'd have lost the audit boundary.
>
> **Two — permanent artifacts at every gate.** Every step writes to a work log — the SQL it considered, the table it picked, the join it made. I designed it that way because long-running agents lose coherence as the context window fills. Externalizing memory to artifacts kept the agent stable and gave me an audit trail. It also has a 10-retry self-healing execution budget — if a query fails, it diagnoses and retries before escalating."

**Why this lands:** Two architectural beats, not six. One real tradeoff named (MCP vs. direct creds — speed for audit). "Context engineering, not prompt engineering" reads as a builder phrase. All numbers verified.

### Beat 3 — EVAL (~75 sec)

> "Today, **I'm the gate.** I'm the human in the loop reviewing the work-log artifacts. I own that — it's not the end state, it's where I am now. I have a separate validator skill with sub-agents that re-execute the SQL, check the narrative against the work log, and verify the MCP was used correctly — but a partner shouldn't trust the answer just because the validator passed.
>
> The next version moves the gate to a golden-set regression. I'm building toward evaluating on the *process* the agent uses, not on SQL string-match, because there are usually 3 right SQL queries for any question. The agent ships an answer only when its process matches the golden process. If it doesn't, it abstains — kicks the ticket back with a 'need clarification' artifact instead of guessing.
>
> The failure mode I worry about most is confident-wrong — clean SQL on a stale flag. That's exactly the case the process-level check catches that observability alone misses."

**Why this lands:** Three high-signal moves — (1) owns the HITL gap honestly, (2) frames eval as a **gate**, not a philosophy, (3) names the **abstain mechanism**, and (4) names the failure mode (confidently wrong) directly. PhD-scientist interviewers reward this shape over any clean-but-hand-wavy answer.

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "Adoption — it's approved by Sr. Director and product leadership, and stakeholders don't know it's an agent.
>
> What I've done with the time it freed up is the more important answer. **Automating my role bought me the time to build the rest** — a self-service analytics agent over 67 BigQuery tables that's currently the only AI skill in active use by business teams on Data Ventures, a hybrid orchestrator that compares a CubeJS semantic layer against the agent in parallel and feeds discrepancies back to refine definitions, a headless KPI monitor on a 6-hour cron, and recruitment automation that replaced ~20 manual workflows. The Jira agent was the unlock."

**Why this closes strong:** Adoption first (Sr. Director + product leadership approval), then the **portfolio effect** — automating his role bought the time to build 4 more things. That's the principal-instinct close. All adoption claims are verified proof points.

---

## A1 — Self-Service Analytics Agent Over 67 BigQuery Tables

**One-liner:** Production sub-agent flow (Context Researcher → SQL Drafter → Validator → Devil's Advocate) over 67 BigQuery tables; the only AI skill currently in active use by business teams on Walmart Data Ventures.

**Best for:** Adoption-and-rigor evidence. Pairs the sub-agent orchestration story with explicit eval architecture (8 deterministic SQL rules, 23 golden-query test cases). Strong for technical-deep interviewers who want to hear about agent design beyond "I called Claude in a loop."

### Beat 1 — PROBLEM (~45 sec)

> "Walmart Data Ventures has the same bottleneck most analytics orgs do — business teams need answers, the analyst who knows the 67-table schema becomes the queue. A routine question would sit in someone's inbox for hours, sometimes a day. I designed and shipped a self-service analytics agent that lets the business teams ask the question themselves and get back a validated answer. It's currently the only AI skill in active use by business teams on Data Ventures."

### Beat 2 — BUILD (~75 sec)

> "Four sub-agents in a flow — Context Researcher gathers the schema and relevant historical patterns, SQL Drafter writes the query, Validator runs deterministic SQL rules against it, and a Devil's Advocate sub-agent challenges the output before it ships. Two architectural beats:
>
> **One — context-isolated validation.** The Validator and Devil's Advocate don't share the Drafter's context window. That's deliberate — if the same context that wrote the SQL also validates it, you get confirmation bias. Separate contexts catch hallucinated columns and bad joins that the drafter would defend.
>
> **Two — deterministic rules layered under the LLM.** I have 8 deterministic SQL rules that fire before the LLM ever sees the output — things like 'no SELECT *', 'every join needs a key', 'no cross-table aggregations without a date filter.' The LLM is fast but inconsistent; deterministic rules catch the dumb failures cheaply so the LLM-eval layer only handles the interesting ones."

### Beat 3 — EVAL (~75 sec)

> "Three layers, ordered cheapest-to-most-expensive:
>
> **One — the 8 deterministic SQL rules.** Catch structural mistakes before any LLM call. Free and fast.
>
> **Two — a 23-case golden-query evaluation suite.** Real business questions with known-good output. The agent passes when its result matches; the SQL itself can vary because there are multiple right queries for any question.
>
> **Three — human-in-the-loop validation at rollout.** Business team runs it, I review the trickier outputs in week one before stepping back. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs — that translation step is part of the eval loop, not separate from it.
>
> The gate to ship is: passes deterministic rules + passes the relevant golden case + Validator and Devil's Advocate both clear it. If any layer fails, it doesn't ship the answer — it escalates."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "Adoption — approved by Sr. Director and product leadership, **currently the only AI skill in active use by business teams on Data Ventures**, eliminated the analyst as the bottleneck for routine asks. What I'd build next on top of it is the hybrid orchestrator I already shipped — routing the same question through both the agent and a CubeJS semantic layer in parallel, comparing outputs, and feeding the disagreements back to refine the semantic-layer definitions over time. That's how the semantic layer gets smarter without anyone writing definitions by hand."

---

## A2 — Hybrid Orchestrator (Semantic Layer × Agent)

**One-liner:** Parallel-routing orchestrator that runs business questions through both a CubeJS semantic-layer skill and the context-engineered agent, reasons about disagreements, and feeds discrepancies back to refine semantic-layer definitions over time.

**Best for:** Systems-thinking and platform-instinct interviewers. Use when the JD emphasizes architecture, multi-component reasoning, or self-improving systems.

### Beat 1 — PROBLEM (~45 sec)

> "Semantic layers are great when the definition exists. Agents are great when it doesn't. At Walmart we had both — a CubeJS semantic-layer skill the DS and product team co-built, and the context-engineered analytics agent — but no one knew which to trust on any given question. So I built a hybrid orchestrator that runs the question through both in parallel and turns the disagreement itself into the signal."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — parallel routing, not sequential fallback.** Both backends get the question at the same time. Sequential would have been simpler but I'd have biased toward whichever ran first.
>
> **Two — disagreement as the input to a reasoning step.** When the two outputs match, ship. When they don't, the orchestrator reasons about *why* — is the semantic-layer definition stale, is the agent hallucinating a join, or is the question itself ambiguous?
>
> **Three — discrepancies feed back into semantic-layer definition refinement.** Every disagreement is a signal that a definition either doesn't exist or is wrong. Over time the semantic layer absorbs the agent's coverage. That's how the system gets smarter without anyone writing definitions by hand."

### Beat 3 — EVAL (~75 sec)

> "Eval here is two layers — the eval of each backend (A1's golden-query suite for the agent, definition tests for the semantic layer) plus the orchestrator's own eval on the *quality of the reasoning about disagreements*. The harder question is: when they disagree, which one is right? Today that's a human spot-check at low volume — I'm the gate. The next version uses the agent's process-trace against the semantic-layer definition's lineage to score which one had better grounding for that specific question.
>
> The failure mode I worry about most is silent agreement — both backends wrong in the same way. Parallel routing doesn't catch that. Mitigation is the third-source golden set: a question we know the answer to, asked periodically as a regression."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "It's the meta-layer on top of the analytics agent that the business teams actually use. What I'd build next is the auto-refinement loop — today the discrepancy review and definition-refinement is human-led; the next version proposes the refinement automatically and a human approves rather than authors. That moves the human from the bottleneck to the gate."

---

## A5 — Headless KPI Monitor + Event-Driven V2

**One-liner:** Production agent on a 6-hour cron that detects KPI threshold breaches, runs root-cause analysis, posts Slack alerts, and persists state to BigQuery so it has no LLM-memory reliance. V2 design is a 3-tier event-driven platform self-configuring through a BigQuery event registry.

**Best for:** Reliability-and-ops interviewers; FDE/SWE roles; anyone who'll ask "how do you make agents production-stable." The "no LLM-memory reliance" beat is the one most candidates can't articulate.

### Beat 1 — PROBLEM (~45 sec)

> "Analytics teams get pinged when a number moves the wrong way — but only after someone looks at a dashboard. I wanted the system to ping us first, with the root cause already attached. So I built a headless KPI monitor — runs every 6 hours on cron, detects threshold breaches against a defined KPI registry, runs root-cause analysis against the underlying tables, and posts the Slack alert with the diagnosis attached."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — headless cron, not interactive.** This isn't an agent a human triggers; it runs whether anyone's watching. That changes the design — no streaming, no partial-state UI, full transactions or full rollback.
>
> **Two — state persists to BigQuery, not to LLM memory.** Every decision the agent makes — which threshold breached, which root cause hypothesis it explored, what it posted — gets written to BigQuery. The agent has *no LLM-memory reliance*. If the LLM call fails mid-cycle, the next run picks up exactly where the last one stopped because state is durable.
>
> **Three — v2 is a 3-tier event-driven platform.** Three event classes — reactive events, threshold KPIs, PM-owned themes — self-configuring through a BigQuery event registry. New event types ship without code deploys; PMs add a row to the registry and the system picks it up on the next cron tick."

### Beat 3 — EVAL (~75 sec)

> "Two layers:
>
> **One — decision logging in BigQuery is the eval substrate.** Every breach detection and every root-cause output is queryable. I can ask 'how often does the diagnosis match what a human would have concluded' against any time window. That's end-to-end observability built into the data model, not bolted on.
>
> **Two — false-positive review on Slack alert volume.** If alert volume rises, that's a signal the thresholds need retuning, not that the agent is broken. The gate for shipping a new event type is: zero false positives on backtested 30-day data first.
>
> Failure mode I worry about most is alert fatigue — a noisy agent gets muted by humans, and then it might as well not exist. So I treat alert precision as a first-class metric, not an afterthought."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "It's in production today on the original cron-and-thresholds architecture. The 3-tier event-driven v2 is designed and being rolled out — the test for that one is whether a PM can add a new event type without engineer involvement. If that works, the platform scales linearly with org demand instead of with my time."

---

## A4 — Recruitment Workflow Automation

**One-liner:** Replaced ~20 distinct recruitment workflows (run by hand 1–2× weekly) with end-to-end automation on a 68-table BigQuery platform. Stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.

**Best for:** Demonstrating automation-of-self and end-to-end builder credibility outside the agent stack. Strong supporting walkthrough when the JD wants ops/data-engineering rigor beyond AI agents.

### Beat 1 — PROBLEM (~45 sec)

> "Part of my role at Walmart was running ~20 distinct recruitment workflows by hand, 1–2 times a week — picking the right panelists from a 68-table BigQuery platform for different research studies. Each workflow took about 3 hours, and the failure mode was duplicate panelists across overlapping recruits, which corrupts study integrity. I automated the whole set end-to-end. The 3-hour task now takes ~3 minutes of setup, I've recruited 280,000+ panelists across 29 categories, and the duplicate count is zero."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — stratified sampling pipelines, not random.** Recruitment quality depends on hitting category quotas — 29 categories with different size and demographic targets. Stratified sampling enforces the quotas at the SQL layer.
>
> **Two — zero-duplicate enforcement is structural, not opportunistic.** Every recruit checks against a persistent allocations table before assignment. That makes deduplication a write-time guarantee, not a downstream cleanup.
>
> **Three — setup-then-run, not parameter-tweak-then-rerun.** The ~3 minutes of setup is choosing the study config; the run itself is unattended. I optimized for *the analyst doesn't have to babysit the pipeline*, which is what made the time savings real."

### Beat 3 — EVAL (~75 sec)

> "Eval here is structural — zero duplicates across 280,000+ panelists is the headline metric, and it's enforced at write time so a regression would show up immediately. The other metric is category coverage: every run produces a coverage report against the 29-category targets. If any category undershoots, the run flags it before the recruit goes live.
>
> Failure mode I worry about most is silent panelist exhaustion — a category gets depleted over time and the sampling pipeline can't hit the target anymore. The mitigation is the coverage report flagging it early so we can refresh the panel before it breaks."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "It's the recruitment substrate for the research team — every study runs through it. What I'd build next is the auto-recruit loop: today a human picks the study config; the next version proposes the optimal recruitment plan given the study design and runs it after a one-click approval. Same shift as the orchestrator — move the human from author to gate."

---

## A7 — Live Text-to-SQL Copilot (Demo)

**One-liner:** Live-deployed text-to-SQL copilot — Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries + BigQuery execution + auto-visualization. Public demo URL.

**Best for:** "Show me what you can build outside your day job" prompts. Also useful as proof-of-claim for the agent stack listed on the resume — the demo is live and runnable mid-interview.

**Demo URL:** `https://sql-rag-frontend-simple-481433773942.us-central1.run.app/`

### Beat 1 — PROBLEM (~45 sec)

> "Most analytics teams have the same bottleneck — non-technical stakeholders need numbers, the one analyst who knows the schema becomes the queue. I wanted to prove that pattern out as a standalone, demo-able artifact — not tied to a specific employer's data. So I built and deployed a text-to-SQL copilot anyone can hit. You type a natural-language question, you get SQL, results, and an auto-generated chart back."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — Gemini 2.5 grounded on RAG over historical queries, not prompt-and-pray.** LangChain orchestrates retrieval of similar historical queries by embedding similarity, then Gemini generates the SQL with that context. The tradeoff is latency for accuracy — RAG adds retrieval time, but the model has prior examples to anchor on instead of inventing column names.
>
> **Two — live BigQuery execution, not a sandbox.** Real results, real auto-visualization. I made that call because a demo on synthetic data doesn't survive the first 'but what about the actual join semantics' question.
>
> **Three — auto-visualization layer picks chart type from result shape** — bar for categoricals, line for time series, table when nothing else fits. Small thing, but it's the difference between a query tool and a copilot."

### Beat 3 — EVAL (~75 sec)

> "Eval here is lighter than the production stack — it's a demo, I'm honest about that. The evaluation that matters for a demo is: does it survive a live stranger asking a question. So the eval is *runtime correctness against the live BigQuery* — if the SQL parses, executes, and returns the result shape the question implied, it passed. The harder eval — does the answer actually mean what the user thought they were asking — is open.
>
> The gap I'd close next is abstention. Today the copilot answers everything. The version I'd build next routes low-confidence queries — ambiguous joins, under-specified time windows — through a clarification turn instead of guessing."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "It's a demo, not a production deployment — I treat it as the artifact I use to show what a grounded LLM on a real schema can do, and the architectural pattern is the one I ported into the Walmart-internal agents. What I'd build next on top of it is a multi-turn version with session memory plus the abstention gate. The demo is live if you want to try it after the call."

---

## U1 — Persona-Driven Multi-LLM Donation Experiment (UChicago)

**One-liner:** Persona-driven multi-LLM chatbot (OpenAI + Gemini) for a 500+ participant donation experiment. Controlled A/B tests persuaded 15% to donate to an opposing cause.

**Best for:** Roles emphasizing experimentation, behavioral/causal work, or research rigor. Also useful as evidence of multi-model orchestration before it was standard.

### Beat 1 — PROBLEM (~45 sec)

> "This was a UChicago Data Science Institute research project under the Data & Democracy initiative. The question: can an LLM-driven chatbot change someone's mind on a politically-charged donation decision? The experimental subject was donating to an opposing cause. The constraint was statistical power — we needed real A/B arms, 500+ participants, and clean attribution to the chatbot interaction."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — persona-driven, not prompt-driven.** The chatbot persona was conditioned on the participant's stated views going in, so the persuasion strategy adapted. This was before persona-prompting was the standard pattern.
>
> **Two — multi-LLM (OpenAI + Gemini) for variance control.** Using two models reduced single-model artifact risk in the experimental result. If both models produced the same persuasion lift, the effect was the chatbot, not the model.
>
> **Three — controlled A/B across 500+ participants** — actual experimental design with treatment and control, not a vibe-check. That's what made the 15% figure publishable, not anecdotal."

### Beat 3 — EVAL (~75 sec)

> "Eval here is experimental, not engineering. The gate was statistical significance on the 15% persuasion lift between treatment and control arms. The harder eval was — did the chatbot persuade because of the argument, or because of the interaction itself. We addressed that with [VERIFY: control arm design — was the control a static page, a non-persuasive chatbot, or no interaction?].
>
> Failure mode I worry about most in this kind of experiment is participant gaming — people figuring out it's a study and answering for the experimenter rather than themselves. [VERIFY: any pre-registration / deception protocol details Kanu wants to mention.]"

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "The result fed into the Data & Democracy initiative's broader research on LLM persuasion. What I'd build differently now, with three more years of agent experience — a tighter persona-update loop where the chatbot revises its persona model based on participant responses mid-conversation, not just from a pre-conversation survey. That moves it from static-persona-chatbot to adaptive-persona-agent."

---

## F1 — RAG-to-Proposal Generator (FTI Consulting, UChicago Capstone)

**One-liner:** RAG-to-proposal generator for FTI Consulting, deployed on AWS EC2. Cut proposal time ~30%. Best in Show — UChicago MSADS Capstone.

**Best for:** Consulting / forward-deployed / client-facing roles. Demonstrates client-context-to-deployed-artifact in a fixed timeframe — exactly the shape of forward-deployed work.

### Beat 1 — PROBLEM (~45 sec)

> "FTI Consulting brought this to us as a UChicago MSADS capstone — their proposal team was spending significant time assembling new proposals from past materials, expert bios, and case studies. The ask: an AI tool that drafts a starting proposal given a client RFP. The capstone constraint was real — fixed semester timeline, a working deployed artifact at the end, judged by FTI partners."

### Beat 2 — BUILD (~75 sec)

> "Three architectural beats:
>
> **One — RAG over FTI's own proposal library and case studies**, not a generic LLM. The model's job was to *retrieve and recombine FTI's existing voice*, not to write from scratch. That kept the output on-brand.
>
> **Two — deployed on AWS EC2 for the final demo**, not just a notebook. The grading rubric included whether a partner could actually use it; a deployed endpoint made the demo real.
>
> **Three — proposal-section-aware prompting**, not single-shot generation. Different sections — exec summary, team bios, methodology, pricing — each got a tailored retrieval + generation step, because their structures and tone differ."

### Beat 3 — EVAL (~75 sec)

> "Eval here was time-to-first-draft measured against the baseline manual process. We got to ~30% reduction. The harder eval — did partners actually use the drafts — was answered at the demo: they did, with edits. That was the gate for Best in Show.
>
> Failure mode I worry about most in proposal generation is hallucinated credentials — the model claiming the firm has expertise it doesn't. The mitigation we built was [VERIFY: source citation? retrieval-only-from-validated-library? hard guardrails on certain section types?]."

### Beat 4 — ADOPTION + WHAT'S NEXT (~45 sec)

> "The artifact won Best in Show at the UChicago MSADS Capstone, judged by FTI partners. What I'd build next with three years of additional agent experience — the section-aware prompting becomes a sub-agent flow, with a Validator sub-agent fact-checking every credential claim against a verified-credentials registry before the draft ships. That converts the hallucinated-credentials failure mode from 'review-catches' to 'system-prevents.'"

---

# Project Selection Cheat-Sheet

Use this when building a role-specific cue card. Pick 2–3 walkthroughs, not all 7.

| Role archetype | Lead with | Backup | Skip |
|---|---|---|---|
| Consulting / Product Builder (BCG X, Deloitte FDE, McKinsey Implementation) | A3 (Jira agent — ownership + business impact + portfolio effect) | A1 (sub-agent rigor) or A7 (live demo) | I1, U1 (too academic for consulting close) |
| Agent Builder / Principal SWE (Walmart Agent Builder, agent-focused FAANG) | A3 (Jira agent) | A1 (sub-agent orchestration) + A5 (production agent on cron, no LLM-memory reliance) | A4, F1 (not agent-shaped enough) |
| Forward-Deployed Engineer (Anthropic FDE, Deloitte FDE) | A3 (Jira agent — embedded, shipped, adopted) | F1 (consulting deployment in fixed timeframe) | A5, A4 (less client-facing) |
| Data Science / Analytics platform | A1 (analytics agent over 67 tables) | A2 (hybrid orchestrator) | U1, F1 |
| Research / Experimental | U1 (persona-driven multi-LLM A/B) | A3 if they want production rigor too | A4, A6 |
| Generic technical screen / "tell me about a build" | A3 default (strongest single walkthrough) | A7 live demo as proof of agent stack claims | — |

---

# Anti-patterns specific to lower-tier walkthroughs

- **Don't lead with I1 (Innovare) or F1 (FTI) for senior AI roles.** They date Kanu's experience to pre-agent-era and signal earlier-career framing.
- **Don't lead with A6 (Power BI dashboards) for an AI role.** Mention as a one-line credential ("top 1.4% of Walmart's dashboards") if asked about BI background; do not spend a 4-min walkthrough slot on it.
- **Don't include more than one demo walkthrough.** A7 is the only deployable demo; the rest are internal. One demo + one or two internal builds is the right mix.

---

# How this file gets updated

- New shipped project → add a new walkthrough section here using the same 4-beat structure. Pull every fact from `Resume Achievements Master.md`. If the fact isn't there yet, add it to the Master first.
- New role with a different archetype → update the selection cheat-sheet, don't add a new file.
- Walkthrough lands well in a real interview → note the interviewer's specific reaction in the role folder's `Post-Interview Debrief.md`; if the change generalizes (a phrasing tweak, a new tradeoff to name), promote it here.
- Walkthrough lands flat → same, but invert. The anti-patterns section grows from real misses, not theory.
