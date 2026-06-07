# Mock Answer Rubric

**Role:** Walmart Principal Software Engineer — Agent Builder (R-2427839)
**Purpose:** Anchor what 5/5 looks like and what a realistic 3/5 sounds like, so mock practice has something concrete to grade against.

## How to use this file

When practicing out loud, Kanu answers cold. Then Claude grades against:

1. **The good answer** — does Kanu's response cover the same signal density? Same business-first framing? Same specificity?
2. **The bad answer** — is Kanu drifting toward any of these named failure modes?
3. **The grading checklist** — concrete signals the answer must hit to clear a 4/5.

A 3/5 isn't a wrong answer. It's a plausible answer that's missing the principal-level signal. Recognizing 3/5 in the moment is the whole point.

## Universal failure modes (watch for these on every question)

- **Tool-first thinking** — "I'd use LangGraph because…" before defining the user/problem.
- **No metric** — "It worked well" instead of "cut review time from 8 min to 30 sec."
- **Resume recitation** — Listing projects without a thesis or takeaway.
- **No tradeoff named** — Sounds like everything was easy. Principals name tradeoffs out loud.
- **"We" with no edges** — Can't tell what Kanu personally owned vs. the team.
- **Generic AI-isms** — "Guardrails, evals, observability" listed but not made concrete.

---

# Fast Warmups

## Q1: Tell me about yourself.

**Bad answer (3/5 — resume recitation):**
> I'm a Senior Data Analyst at Walmart Data Ventures. I have a master's in data science from UChicago. Before that I did consulting at FTI. At Data Ventures I've built a few agents — one for analytics, one for Jira triage, one for monitoring. I'm really excited about agents and LLMs and I think this role is a great fit because I want to do more agent work.

**Failure modes:** No thesis. Reads in chronological order. Doesn't explain *why* the work matters or what's distinctive. Ends with "I want to do more of this" — passive. Could be said by 50 other candidates.

**Good answer (5/5):**
> Short version: I'm a Senior Data Analyst at Walmart Data Ventures by title, but the work I actually do is build internal agents end-to-end. The flagship is a self-service analytics agent over 67 BigQuery tables that cut analyst time-to-insight from about an hour to ten minutes — approved by our Sr. Director and product leadership. On top of that I built Boon, a hybrid orchestrator that routes business questions through a Cube/JS semantic layer and the agent in parallel, reconciles disagreements, and feeds the deltas back to improve the semantic layer over time. I've also shipped a Jira triage agent that took average ticket handling from eight minutes to thirty seconds, and a headless API monitor that does root-cause analysis on a six-hour cron. The thread across all of it: I scope, build, deploy, and measure impact myself, and I treat "agent" as a means to a business outcome — sales lift, cost saved, time saved — not as the deliverable. That's why this role caught my eye.

**Why it's a 5:** Opens with thesis (title vs. actual work), three concrete proof points with metrics, names the principal-level pattern (end-to-end ownership, business-first), closes with a forward-looking hook tied to the JD language.

**Grading checklist:**
- [ ] Opens with a thesis, not chronology
- [ ] Names at least 2 shipped agents with quantified outcomes
- [ ] Frames work in business terms (time/cost/sales), not "I built X with Y stack"
- [ ] Bridges to *this* role explicitly
- [ ] Under 90 seconds

---

## Q2: Why this Agent Builder role?

**Bad answer (3/5 — generic enthusiasm):**
> I love this space — agents are the future of enterprise software, and Walmart's scale is exciting. I've been building agents in Data Ventures and I want to do it at a bigger scope. This team seems to be doing exactly the kind of work I want to do, and the low-code platform angle is interesting because it'll let me reach more users.

**Failure modes:** Buzzwords ("future of enterprise software"). No evidence of having read the JD. "Bigger scope" is vague. Doesn't say what Kanu brings or what's distinctive about *this* team vs. any other AI team at Walmart.

**Good answer (5/5):**
> Three reasons, in order. First, the role explicitly measures success by sales growth, cost savings, and time savings — not number of agents shipped. That matches how I already work. Every project I've delivered at Data Ventures has a number attached: 83% time reduction on insights, 280K+ questions auto-handled, top 3.4% dashboard adoption. I'm wired to think that way. Second, it's positioned as a generalist owning end-to-end — translating a business question into agent architecture, deploying, monitoring, influencing stakeholders. That's exactly the loop I run in Data Ventures, but Agent Builder lets me run it across merch and supply chain, where the dollar stakes are an order of magnitude bigger. Third, the low-code/no-code platform piece — most "AI for business users" tools fail because they're either too restrictive or too unsafe. I want to work on the version that gets the tradeoff right, and I have strong opinions about what that looks like.

**Why it's a 5:** Cites JD language back to them. Three reasons with substance, not platitudes. Each reason ties to a Kanu data point. Last reason shows opinionated thinking — a principal-level signal.

**Grading checklist:**
- [ ] References specific JD language (sales/cost/time, end-to-end, low/no-code)
- [ ] Each "reason" backed by a Kanu data point
- [ ] At least one opinionated take (signals principal-level thinking)
- [ ] No buzzwords ("future of," "exciting space")
- [ ] Under 90 seconds

---

## Q3: Your title is Senior Data Analyst — why are you ready for Principal Software Engineer?

**Bad answer (3/5 — defensive):**
> I know the title says analyst but I've really been doing engineering work — building agents, writing FastAPI services, working with Cloud Run, GCP. The analyst title is just because Data Ventures hired me into that role, but the work I do is more like a senior engineer's.

**Failure modes:** Defensive posture. Treats the question as a challenge instead of as a fair signal check. Doesn't address *Principal* specifically — only "more than analyst." No evidence of scope or influence beyond own output.

**Good answer (5/5):**
> Fair question. The title is a contracting artifact — Data Ventures hired analysts and product folks first, and there wasn't an engineering ladder yet — but I'll answer the substance. Principal-level isn't seniority, it's three things: end-to-end ownership of ambiguous problems, technical leverage beyond your own output, and credibility with non-engineering stakeholders. I've done all three. End-to-end: I scoped, built, and shipped the analytics agent and Boon without an engineering manager handing me a spec — I had to convince product leadership the design was right. Leverage: the Jira triage agent didn't just save my time, it replaced ~20 distinct recurring reports for the product org and now handles 280K+ questions across 29 categories. I built the lever, others use it. Stakeholder credibility: my dashboards are in the top 3.4% of 207,000 at Walmart and I won a Make a Difference Award — that's adoption signal from people who don't care about my title. What I'd be growing into at Principal is platform thinking — turning my agent-building reflexes into reusable primitives others can apply. That's exactly the leap this role is asking for, and it's why I want it.

**Why it's a 5:** Acknowledges the question fairly, then reframes it on Kanu's terms. Defines "principal" with a 3-part rubric and provides evidence for each. Closes by naming the growth edge honestly — shows self-awareness, not arrogance.

**Grading checklist:**
- [ ] Acknowledges the question without defensiveness
- [ ] Defines "principal" before claiming to be one
- [ ] Evidence for each pillar of the definition
- [ ] Names a growth edge (self-awareness)
- [ ] Doesn't bash the title or the org

---

## Q4: What did you ship in the last 90 days?

**Bad answer (3/5 — laundry list):**
> A lot. I've been working on Boon — the hybrid orchestrator — and improving the analytics agent. I added some new BigQuery tables to the agent's context, fixed some prompt issues, and worked on the Jira triage agent. I also did some Power BI work for product partners.

**Failure modes:** No prioritization. No outcomes. Reads like a status update. Doesn't show what *mattered* or what was hard.

**Good answer (5/5):**
> Three things, ranked by impact. One, I designed and shipped Boon — the parallel orchestrator that routes business questions through both the Cube/JS semantic layer and the agent, then reconciles disagreements. The interesting bit isn't the parallelism, it's the feedback loop: every disagreement becomes a candidate definition for the semantic layer, so the system gets more deterministic over time instead of more dependent on the LLM. Two, I expanded the analytics agent's context coverage and tightened its validation layer — it now covers 67 tables, and we cut a class of hallucinated joins by adding source-of-truth checks before answer return. Three, the API monitor migration to event-driven triggers — replaced fixed cron with BigQuery event triggers so we're not paying for idle 6-hour cycles. If I had to pick one thing I'm proudest of, it's Boon, because it's the first thing I've built that's designed to make itself less necessary.

**Why it's a 5:** Prioritized. Each item has a "what made it interesting" sentence — not just description. Last line is principal-level — building things that reduce their own surface area is a senior-engineering instinct.

**Grading checklist:**
- [ ] Prioritized (most impactful first)
- [ ] Each item has a "why it mattered" beyond what it does
- [ ] At least one tradeoff or design insight surfaced
- [ ] Picks a favorite and says why — shows judgment
- [ ] Under 2 minutes

---

# Behavioral Reps

## Q5: Tell me about a time you owned a problem end to end with no clear support.

**Bad answer (3/5 — no obstacle named):**
> The analytics agent. I built it from scratch — designed the architecture, picked the LLM, wrote the prompts, integrated with BigQuery, deployed it. I worked with product partners to figure out what they needed, and shipped it. It saved them a lot of time.

**Failure modes:** No friction in the story — sounds like everything went smoothly, which means either it did (and the story is boring) or Kanu is hiding the hard part. No specific decision made under uncertainty. "Saved them a lot of time" — no number.

**Good answer (5/5):**
> Data Ventures analytics agent. The setup: product partners were waiting one to twenty-four hours for ad-hoc data pulls and the analyst team was the bottleneck. There was no roadmap for this and no one above me had built an LLM agent before. I'll skip the easy parts and go to the hard one. The first version hallucinated joins across our 67-table model — confident wrong answers, which is worse than no answer for an analytics tool. I had two options: keep iterating on prompts, or redesign the context layer. I picked the second, even though it meant throwing away two weeks of work, because confident-wrong was a trust-killer and I knew product leadership would never adopt a 90%-accurate agent. I rebuilt the context model with explicit table-relationship metadata, added a validation sub-agent that checks every generated SQL against source-of-truth schemas before return, and added a confidence threshold below which the agent says "I'm not sure, here's what I'd check." That version got Sr. Director and product leadership approval and we measured 83% reduction in time-to-insight — about an hour down to ten minutes. Takeaway: trust is the actual product in internal agents. I'd rather ship slower with no confident-wrongs than fast with occasional ones.

**Why it's a 5:** Names the bottleneck (1-24 hr wait), names the failure (hallucinated joins), names the decision (throw away two weeks), names the principle (trust is the product). Result is quantified. Closes with a principal-level takeaway.

**Grading checklist:**
- [ ] Bottleneck/cost-of-inaction named upfront
- [ ] Specific obstacle described, not glossed
- [ ] Specific decision under uncertainty, with alternative named
- [ ] Quantified result
- [ ] Takeaway that's transferable, not just "I learned to be careful"

---

## Q6: Tell me about a time you challenged a senior stakeholder's preferred direction.

**Bad answer (3/5 — vague and conflict-averse):**
> A product partner wanted the agent to autonomously update dashboards based on user questions. I told them I thought that was risky because if the agent got it wrong, it would propagate bad data. We talked about it and they agreed to do it as recommendations first. So we went with recommendation-only.

**Failure modes:** Sanitized. No stakes, no real disagreement. "We talked about it and they agreed" — doesn't show *how* Kanu changed their mind. No principle articulated beyond "risky."

**Good answer (5/5):**
> Boon, actually. The initial product ask was a single agent that just answers business questions directly — fast, cheap, simple. A Sr. Director on the product side wanted to ship that and iterate. I pushed back: a single agent against 67 tables would either hallucinate joins or be too narrow to be useful, and we'd burn trust before we got it right. I proposed a parallel architecture instead — the agent answers, but a Cube/JS semantic layer also answers, and a third component reconciles disagreements. Higher upfront cost, slower v1, more moving parts. The pushback I got was reasonable: "you're overbuilding, we don't even know if anyone will use it." My counter was — and I had to bring evidence — every disagreement between the two backends is free training data for the semantic layer, which is the long-term asset. The agent gets worse over time as the schema drifts; the semantic layer gets better. I sketched the feedback loop on a whiteboard, walked them through what month six looks like under each design, and committed to a v0.5 that they could kill if it didn't show value in six weeks. They greenlit it. It shipped, the feedback loop works as intended, and the semantic layer is now better-defined than before we started. What I'd do differently: I waited too long to bring the diagram. Once the diagram existed the conversation took 15 minutes.

**Why it's a 5:** Real disagreement (both sides had good points). Names the senior person's reasonable counterargument. Shows how Kanu *won* the argument (evidence, time horizon, committable milestone). Closes with self-criticism — "I waited too long to bring the diagram" is a principal-level reflection.

**Grading checklist:**
- [ ] Names both sides' positions fairly
- [ ] Specific evidence/framing used to change minds
- [ ] Names what was at stake (cost, time, trust)
- [ ] Self-criticism at the end — what would you do differently
- [ ] Doesn't end with "and I was right" — ends with a lesson

---

## Q7: Tell me about a time you built something users actually adopted.

**Bad answer (3/5 — adoption without insight):**
> The analytics agent. Product partners use it daily now. It cut their time-to-insight significantly. The Sr. Director and product leadership approved it.

**Failure modes:** Adoption claimed but not explained. *Why* did they adopt — what about the design earned the adoption? This is the question that separates "I built something" from "I built something people use."

**Good answer (5/5):**
> The analytics agent has the strongest adoption story but the more interesting one is the Jira triage agent. Context: product partners were filing ~50 tickets a month into the analyst queue, average review and triage was 8 minutes per ticket, and a lot of them were repeat questions disguised in different language. I built an autonomous triage agent that categorizes the ticket, retrieves the answer if it's a known category, and responds in the thread. The adoption signal I care about isn't that it ran — it's that product partners *stopped routing around it*. The first version had a 70% acceptance rate and 30% of users were still tagging the analyst team directly. I dug into the rejections, found two patterns: agent answers were too long, and the agent was answering tickets it should have escalated. I cut answer length by 60% and added a confidence threshold that auto-escalates anything ambiguous. Acceptance climbed past 90%, the workaround behavior stopped, and we've now processed 280K+ questions across 29 categories with zero duplicates needing rework. The lesson: adoption is a debugging signal. When users route around your tool, that's the bug.

**Why it's a 5:** Pivots from the obvious answer to the better story. Distinguishes "it ran" from "it was adopted." Specific failure mode (users routing around it) and specific fix. Takeaway is reusable.

**Grading checklist:**
- [ ] Distinguishes "deployed" from "adopted"
- [ ] Names specific adoption metric, not just usage count
- [ ] Names a moment when adoption *didn't* happen and how you debugged it
- [ ] Takeaway about what adoption actually requires

---

## Q8: Tell me about a time you simplified an overcomplicated process.

**Bad answer (3/5 — process-tweak, not redesign):**
> The Jira triage process used to take 8 minutes per ticket. I built an agent that does it in 30 seconds. So I simplified it from an 8-minute manual process to a 30-second automated one.

**Failure modes:** This isn't simplification, it's automation. The question is asking about complexity, not throughput. Misses the chance to show systems thinking.

**Good answer (5/5):**
> The recurring on-call reports we ran for product partners. There were about 20 distinct reports, each on its own cadence, each requiring 2-4 hours of analyst time per cycle. I looked at them and realized they were all variants of the same five questions, just sliced differently. Instead of building 20 automations, I built one — the analytics agent — with a context layer that knows how to answer any of those five questions across any slice the user asks for. We went from 20 recurring artifacts to one self-service tool, and analysts stopped being a serialized bottleneck. The hard part wasn't the build, it was getting product partners to give up their custom report. I did that by autopopulating their first month of reports from the agent so they had something concrete to compare to. The simplification wasn't "automate 20 things faster" — it was "you don't need 20 things, you need one." That reframe is what unlocked the build.

**Why it's a 5:** Shows systems thinking — collapsed 20 things into one by finding the underlying pattern. Names the people-problem (getting partners to give up custom reports) and how it was solved. Distinguishes simplification from automation.

**Grading checklist:**
- [ ] Shows real simplification (fewer moving parts), not just automation
- [ ] Names the underlying pattern that was hiding
- [ ] Addresses the human side (getting people to accept the change)
- [ ] Reframe stated explicitly

---

## Q9: Tell me about a time you failed.

**Bad answer (3/5 — humble brag):**
> The first version of the analytics agent hallucinated joins. I had to rebuild the context layer. It was a setback but I learned a lot about validation, and the rebuilt version worked great.

**Failure modes:** "Failure" that was actually a heroic redemption arc. No actual cost paid. No durable change in behavior.

**Good answer (5/5):**
> Innovare, my internship. I built a text-to-SQL copilot for non-technical staff — Streamlit, Gemini, RAG over historical queries, BigQuery execution. Technically it worked. Almost no one used it. I shipped it, demoed it, and assumed adoption would follow. It didn't. I learned about three weeks in that the people I'd built it for didn't think of their work as "querying" — they thought of it as "asking Sarah from analytics for a number." The interface I gave them was solving the wrong problem. By the time I figured this out, the internship was almost over and I didn't have time to redesign. The cost was real — three months of work that didn't move the needle, and a team that was a little more skeptical of "AI tools" the next time someone pitched one. What I changed permanently: I don't build agents anymore without doing at least three user interviews where the question is "what do you do today" — not "would you use this if it existed." The Jira triage agent at Data Ventures got built right because I spent two days shadowing the analyst on-call rotation before I wrote a line of code. That habit is downstream of Innovare.

**Why it's a 5:** Real failure with real cost (three months, eroded trust). Specific root cause (built for wrong unit-of-work). Permanent behavior change (3-interview rule), and evidence that behavior change stuck (Jira triage success).

**Grading checklist:**
- [ ] Real cost paid (not a hidden success)
- [ ] Specific root cause named
- [ ] Permanent change in behavior, not just "I learned"
- [ ] Evidence the change actually stuck in later work

---

## Q10: Tell me about a time you automated yourself out of a repeated workflow.

**Bad answer (3/5 — what, not why):**
> The Jira triage agent. I was spending 8 minutes per ticket reviewing and routing them. I built an agent that does it autonomously, freeing up my time for higher-value work.

**Failure modes:** "Higher-value work" is a phrase, not evidence. Doesn't show the *judgment* about when to automate vs. when to keep manual.

**Good answer (5/5):**
> Jira triage is the obvious one but the more interesting one is the on-call reports. I had a Friday afternoon ritual: pull 20 reports, format them, send them to product partners. Three to four hours, every week. I could have just scripted the SQL. What I did instead was harder — I asked, "if I automate this report, does anyone notice or care?" For about half of them the answer was no. Those got deleted, not automated. The remaining ones got rolled into the analytics agent's context so they could be self-served instead of pushed. The principle I apply now: before you automate a task, kill it. Most repeated workflows are repeated because nobody questioned whether they should exist. Automating them encodes the assumption that they should. I'd rather burn a week proving a workflow is dead than spend a year maintaining its automated zombie.

**Why it's a 5:** Shows judgment, not just execution. Names a counter-intuitive principle ("before you automate, kill it"). Generalizable — a principal-level instinct, not a one-off automation story.

**Grading checklist:**
- [ ] Shows judgment about *whether* to automate, not just how
- [ ] Names something killed, not just automated
- [ ] Articulates a transferable principle
- [ ] Doesn't claim credit for "freeing up time" — names what the freed time enabled

---

## Q11: Tell me about a time ambiguity was high and you had to move anyway.

**Bad answer (3/5 — abstract):**
> When I started the analytics agent project, the requirements weren't clear. I just started building and iterating. I shipped a v1, got feedback, and improved it.

**Failure modes:** "Just started building" doesn't show how Kanu made decisions under ambiguity. No artifact of progress (what did v1 contain? what was the riskiest assumption?). No principle.

**Good answer (5/5):**
> Boon's day one. Product leadership wanted "an agent that answers business questions" — no spec, no scope, no defined success metric. I had two failure modes to worry about: build too much before validating any of it, or build the wrong thing fast. What I did: I wrote down the three riskiest assumptions on a sticky note. One, that the semantic layer and the agent would actually disagree often enough to be useful — if they always agreed, parallel was a waste. Two, that we could reconcile disagreements automatically without burning a human reviewer per question. Three, that product partners would trust a reconciled answer more than a single-source answer. I built the cheapest possible test for each. For assumption one I ran 50 historical questions through both backends offline — disagreement rate was 18%, high enough to justify the architecture. Two, I prototyped reconciliation with a single GPT-5 call on disagreement-only — worked for 80% of cases, escalation for the rest. Three I validated by walking product partners through three reconciled-vs-single-source examples and asking which they'd trust. The pattern: when ambiguity is high, optimize for assumption-killing cheaply, not for hitting milestones. Once the assumptions are tested, the milestone falls out.

**Why it's a 5:** Shows a *method* for moving under ambiguity (named riskiest assumptions, built cheapest tests for each). Numbers for each test. Generalizable framework.

**Grading checklist:**
- [ ] Names a method, not just "I iterated"
- [ ] Lists actual unknowns at the start
- [ ] Cheapest-possible test for each unknown
- [ ] Numbers from the tests, not vibes
- [ ] Transferable principle stated

---

## Q12: Tell me about a time you had to influence non-technical stakeholders.

**Bad answer (3/5 — generic communication advice):**
> When I pitched the analytics agent, I avoided technical jargon and focused on the business outcome. I talked about how much time it would save and what kind of questions it could answer. The Sr. Director got it and approved the project.

**Failure modes:** Sounds like a chapter from a communication book. No specific moment of friction, no specific reframe, no evidence that the influence was hard.

**Good answer (5/5):**
> Boon's pitch to a Sr. Director who is — fairly — skeptical of LLM-heavy systems. He'd seen demos that didn't survive production and didn't want to fund another one. My job was to explain why a parallel architecture would actually *reduce* LLM dependency over time, not increase it. The instinct was to walk him through the architecture diagram. I tried that. He glazed over at "reconciliation layer." So I scrapped that and made it about him: "imagine you ask the system 'why did sales drop in Q3' a year from now. In design A, every answer goes through the LLM and you're trusting it. In design B, the LLM and the semantic layer answer in parallel, and most questions a year from now will be answered by the semantic layer — because every disagreement we've seen has improved it. The LLM is training wheels, not the bike." That metaphor landed. He approved the design. The principle: non-technical stakeholders don't need to understand the architecture, they need to understand which problem you're solving for them — and which one they get to stop worrying about. I lead with the second.

**Why it's a 5:** Shows a specific moment where the first attempt failed and the second worked. Names the reframe verbatim. Articulates a principle about influence that's specific to executive contexts.

**Grading checklist:**
- [ ] Specific moment where influence was hard (not "I explained it well")
- [ ] First attempt that didn't work, named explicitly
- [ ] Specific reframe that did work
- [ ] Transferable principle about non-technical communication

---

# Technical and Agent Design Reps

## Q13: Describe the Data Ventures analytics agent architecture.

**Bad answer (3/5 — stack list, not architecture):**
> It's a Cloud Run service that uses Claude via Vertex. Users ask questions in natural language, the agent generates SQL against BigQuery, runs it, and returns the answer. There's a validation layer that checks the SQL before execution. I use RAG over our table schemas. It's deployed on GCP.

**Failure modes:** Stack list, not architecture. No layers, no flow, no design decisions named. Doesn't explain *why* the design is the design.

**Good answer (5/5):**
> I'll walk it as four layers and a design choice. Intake: a chat interface for analysts, plus a webhook trigger for the Jira triage agent that pipes ticket text into the same backend. Context: a retrieval layer over our 67-table BigQuery model, but the key trick is that I don't retrieve raw schemas — I retrieve *table-relationship metadata* I context-engineered specifically so the model knows how tables join, what the canonical filters are, and what definitions to use. This is the difference between the agent generating plausible SQL and correct SQL. Reasoning: a planner agent breaks the question into sub-questions, dispatches to specialist sub-agents for SQL generation and result interpretation, and a validator sub-agent checks every generated SQL against source-of-truth schemas before it runs. I kept those separate because the failure modes are different — the SQL agent can hallucinate joins, the interpreter can over-claim causality. Different failures need different guards. Tools: BigQuery query execution, with a confidence threshold that returns "I'm not sure, here's what I'd check" below threshold instead of guessing. Output: answer plus the SQL plus the source tables, so the analyst can verify and the agent earns trust over time. The design choice I'll defend: I context-engineered the table model instead of dumping schemas into the prompt because prompt engineering scales linearly with context size and breaks above a certain table count. Context engineering is a one-time investment that scales sublinearly. We're at 67 tables now and the same model would work at 200.

**Why it's a 5:** Four named layers + a design-choice defense. Names *why* sub-agents exist (different failure modes). Names the context-engineering distinction explicitly. Scaling argument shows principal-level thinking.

**Grading checklist:**
- [ ] Four layers minimum: intake, context, reasoning, output
- [ ] Sub-agents justified by *different failure modes*, not "modularity"
- [ ] Validation layer explained as source-of-truth check, not "we have guardrails"
- [ ] Context engineering vs prompt engineering explicitly named
- [ ] At least one design choice defended with a scaling argument

---

## Q14: Why did you use sub-agents instead of one agent with tools?

**Bad answer (3/5 — modularity word):**
> Modularity. Each sub-agent has its own focus area and can be improved independently. It's easier to debug.

**Failure modes:** "Modularity" is the buzzword version of the right answer. Doesn't get specific about *which* failures sub-agents catch that a single agent wouldn't.

**Good answer (5/5):**
> Three concrete reasons, not modularity-the-word. One, different failure modes need different prompts and different evals. The SQL-generation sub-agent fails by hallucinating joins, so its prompt and eval set are about join correctness. The result-interpretation sub-agent fails by over-claiming causality, so its prompt and eval set are about causal hedging. If those were one agent, one eval set, I couldn't push on either failure mode independently. Two, the validator sub-agent has to be allowed to *contradict* the SQL agent — that's its job. A single agent can't reliably catch its own bullshit because the same chain of reasoning that produced the bad SQL is going to rationalize it. Sub-agents let me build adversarial structure on purpose. Three, latency and cost. The validator runs a cheaper model on a smaller context. A single agent would force every question through the most expensive path. The general principle: sub-agents are worth the orchestration cost when failure modes are different *or* when adversarial review is required. They're not worth it for cosmetic separation.

**Why it's a 5:** Three concrete reasons with specific failure-mode pairings. The "adversarial structure" framing is principal-level. Closes with when *not* to use sub-agents — shows judgment.

**Grading checklist:**
- [ ] Names specific failure modes the sub-agents catch
- [ ] Mentions adversarial structure / self-review limits of single-agent designs
- [ ] Cost/latency justification included
- [ ] Names when sub-agents are *not* worth it

---

## Q15: How do you evaluate whether an agent is working?

**Bad answer (3/5 — eval-as-checkbox):**
> I have a golden eval set with about 50 historical questions, and I check accuracy against expected answers. I also monitor user feedback and acceptance rate.

**Failure modes:** Names the right components but doesn't show how they fit together or what they catch. No layered approach.

**Good answer (5/5):**
> Three layers, because no single metric catches every failure. Offline golden cases — about 200 historical questions where I know the right answer, run on every prompt or model change. This catches regressions on known patterns. Shadow mode — for any new feature, I run the new path in parallel with the existing path on live traffic and diff the outputs offline. Catches things the golden set didn't anticipate. Online metrics — acceptance rate, override rate, escalation rate, and the one I care about most, *route-around rate*. Route-around is when users go back to the manual path even though the agent is available. That's the actual adoption signal. Acceptance rates can be high while route-around is also high — people grudgingly accept what the agent gives them but secretly do it themselves too. I learned this from the Jira triage agent. The hierarchy I apply: golden eval is necessary but not sufficient. Shadow is necessary for any nontrivial change. Online behavior is the only thing that tells you the agent is actually doing what you wanted. Bonus layer for high-stakes agents: a "confident-wrong" rate — cases where the agent expressed high confidence and was wrong. That number must trend to zero or the agent isn't trustworthy regardless of overall accuracy.

**Why it's a 5:** Three (then four) named layers, with what each catches and what it misses. The route-around insight is original and specific to Kanu's experience. Confident-wrong rate is principal-level.

**Grading checklist:**
- [ ] At least three layers (offline, shadow, online)
- [ ] Names what each layer catches and misses
- [ ] Mentions a non-obvious adoption metric (route-around, override, etc.)
- [ ] Names confident-wrong as separate from accuracy

---

## Q16: How do you prevent hallucinated SQL or bad actions?

**Bad answer (3/5 — keyword soup):**
> Guardrails. I use a validation layer that checks the SQL before execution. I have prompt-engineering best practices like few-shot examples. I also have confidence thresholds and human-in-the-loop for high-stakes actions.

**Failure modes:** All the right words, none of the specifics. Doesn't say *what* the validation layer checks against, what counts as "low confidence," what triggers HITL.

**Good answer (5/5):**
> Four layers, ordered by where they catch the failure. One, context shaping — I retrieve table-relationship metadata, not raw schemas, so the model has the right primitives to reason about joins instead of guessing. This prevents the failure rather than catching it. Two, structural validation — every generated SQL is parsed, the referenced tables and columns are checked against source-of-truth schemas, and any join key not in the relationship metadata triggers rejection. This catches hallucinated joins deterministically. Three, semantic validation — a sub-agent reviews the generated SQL against the question and answers a structured prompt: "does this query answer this question? what would it miss?" If the answer flags anything, escalate. Four, confidence threshold on output — if any layer flagged uncertainty, the agent returns "I'm not sure, here's what I'd check" instead of an answer. The non-obvious principle: every layer must be allowed to *abstain*. Hallucinations come from forcing an answer when the model doesn't know. If your system has no abstain action, you'll always get hallucinations on the long tail.

**Why it's a 5:** Four layers ordered by *where* they catch failure (prevent vs detect vs hedge). The abstain principle is the key insight — principal-level.

**Grading checklist:**
- [ ] At least one layer that *prevents* hallucination (context shaping), not just detects
- [ ] Structural validation specifics (parse, check against schemas)
- [ ] Semantic validation as a separate step
- [ ] Abstain action explicitly allowed in design

---

## Q17: When would you not use an LLM?

**Bad answer (3/5 — predictable):**
> When the task is deterministic. Like if you can write a SQL query, just write the SQL query. LLMs are for ambiguous or language-heavy tasks.

**Failure modes:** Correct but generic. Could be said by anyone who's read a blog post.

**Good answer (5/5):**
> Three categories where I push back hard against LLM use. One, stable structured logic — anything with a clear rule like "if backorder > 7 days AND vendor in tier-1, escalate" doesn't need an LLM. It needs a SQL view or a workflow. LLMs are slower, more expensive, and less inspectable than a deterministic rule for the same outcome. Two, high-stakes irreversible actions — anything where a wrong answer costs money or trust we can't recover. I'd rather have the LLM draft and a human approve than have the LLM execute. Three, the sneaky one: tasks where the *input* is messy but the *decision* is simple. People reach for an LLM because the input is unstructured email or PDF, but if the underlying decision is "is this customer eligible for refund yes/no," the right architecture is LLM-for-parsing into structured fields, then deterministic logic for the decision. Don't let the LLM hold the decision just because it held the parsing. The general rule: use the LLM for the part that needs language understanding and nothing more. Every extra responsibility you hand it is a place errors compound.

**Why it's a 5:** Three categories with specific examples. The "parse with LLM, decide with rules" pattern is principal-level — most candidates miss it. Closes with a transferable rule.

**Grading checklist:**
- [ ] At least three distinct categories named
- [ ] Includes the parse-vs-decide split (sneaky case)
- [ ] Mentions reversibility/stakes as a category
- [ ] Closes with a rule, not a list

---

## Q18: What is the difference between a workflow and an agent?

**Bad answer (3/5 — textbook):**
> A workflow is deterministic — a fixed sequence of steps. An agent is non-deterministic — it decides what to do based on context. Agents have tools and reasoning, workflows just execute.

**Failure modes:** Definitionally correct but doesn't show when to choose which. Tells the interviewer what's in a textbook.

**Good answer (5/5):**
> Mechanically: workflow is "fixed sequence, branches resolved at design time," agent is "tools available, sequence resolved at runtime." But the more useful framing is when to pick which. Workflow is right when the steps are stable, the branches are knowable in advance, and you need auditability. Agent is right when the input space is too large to enumerate or when the synthesis required is language-shaped. The trap I've watched people fall into: defaulting to "agent" because it sounds modern. Most enterprise problems are workflow problems with one LLM-shaped subtask inside them. That's not an agent, that's a workflow with a smart node. I'd rather have a deterministic seven-step process with one LLM call I can monitor than a seven-tool agent making seven decisions I can't audit. At Data Ventures, the Jira triage agent is actually a workflow with two LLM nodes inside it — categorize, then retrieve-or-escalate. Calling it an "agent" was marketing. The orchestrator Boon is closer to a real agent because the parallel paths and reconciliation logic require runtime decisions. The distinction matters because the right design follows from it.

**Why it's a 5:** Names the practical trap. Has the confidence to say "calling it an agent was marketing." Concrete examples from own work showing each pattern.

**Grading checklist:**
- [ ] Mechanical distinction stated cleanly
- [ ] Names the "when to choose which" question explicitly
- [ ] Calls out the default-to-agent trap
- [ ] Examples from own work showing each pattern

---

## Q19: What is the difference between prompt engineering and context engineering?

**Bad answer (3/5 — surface):**
> Prompt engineering is how you write the prompt — instructions, examples, formatting. Context engineering is about what information you give the model — retrieval, system prompts, history.

**Failure modes:** Correct but flat. Doesn't say which is more durable, when to invest in each, or what breaks at scale.

**Good answer (5/5):**
> Prompt engineering is local: write better instructions for one model on one task. Context engineering is structural: design the information architecture the model operates inside. The reason the distinction matters is that prompt-engineering wins are fragile — they break when the model changes, when context grows, when you swap providers. Context-engineering wins compound, because you're building a representation of the domain that any model can reason over. At Data Ventures, the analytics agent's prompt is maybe forty lines. The context model behind it — the table-relationship metadata, the canonical-filter definitions, the join-key registry — is the thing that actually makes the agent work. When we moved from Gemini to Claude on the SQL sub-agent for cost reasons, the prompt needed minor tweaking. The context model didn't change at all. That's the test: if you swapped the model tomorrow, what would break? If it's the prompt, you have a prompt-engineering system. If almost nothing breaks, you have a context-engineered one. Principal-level work is mostly the second.

**Why it's a 5:** Clear mechanical distinction, then the durability argument, then a real switching-cost story as evidence. The "swap the model tomorrow" test is a sticky framing.

**Grading checklist:**
- [ ] Names local vs structural distinction
- [ ] Argues context-engineering wins compound
- [ ] Real example of model swap to demonstrate durability
- [ ] States the test ("if you swapped the model tomorrow…")

---

## Q20: How would you design memory for an enterprise agent?

**Bad answer (3/5 — tech recital):**
> Vector store for long-term memory, session context for short-term, summarization for compaction. Use embedding-based retrieval over past conversations.

**Failure modes:** Lists components, doesn't address governance, staleness, or the question of whether memory should exist at all.

**Good answer (5/5):**
> First principle: most enterprise agents shouldn't have agent-level memory at all. The data is in source systems. Build agent state from source-of-truth on every call instead of caching it in the agent. The headless API monitor I built does exactly this — state persists to BigQuery, not in the LLM context, so the agent has no memory dependence and the state is queryable and auditable independently. That's the default I push for. Where you do need memory: scope it tightly. User-level preferences ("show me by region first") are fine to persist. Session-level context to avoid re-asking is fine. Agent-level "what did I do last week" memory is a trap — it drifts, it's hard to audit, and it makes the agent's behavior non-reproducible. If I had to design real memory, four properties: scoped (per-user, per-task, not global), expirable (TTL by default, not infinite), inspectable (a human can read what the agent remembers about a thing), and overwritable (correctable when wrong). And one anti-pattern: never let the LLM decide what to remember. Always have a deterministic rule for what writes to memory and what doesn't. Otherwise you've built a system whose behavior depends on undocumented model-internal heuristics, which is a debugging nightmare.

**Why it's a 5:** Opens with a contrarian-but-correct take (most agents don't need memory). Real example from own work. Four-property framework. Names a sharp anti-pattern.

**Grading checklist:**
- [ ] Questions whether memory should exist before designing it
- [ ] References source-of-truth-on-every-call alternative
- [ ] Properties of good memory enumerated (scope, expire, inspect, overwrite)
- [ ] Names anti-pattern (LLM decides what to remember)

---

# Principal-Level Reps

## Q21: What makes your work principal-level versus senior engineer-level?

**Bad answer (3/5 — adjectives):**
> Senior engineers solve problems that are given to them. Principal engineers identify the right problems to solve and operate cross-functionally. I think I've been doing principal work because I scope my own projects and influence stakeholders.

**Failure modes:** Defines principal by adjective ("strategic," "cross-functional") instead of by mechanism. Self-promotion without proof.

**Good answer (5/5):**
> Three mechanisms, with evidence. One, scope discovery — senior engineers execute against a defined scope, principals find the right scope. The Jira triage agent wasn't on a roadmap. I saw analyst time going to triage, saw the underlying repeat-question pattern, and convinced product leadership it was worth the build. Two, leverage — senior engineers produce output, principals produce systems that produce output. Boon's reconciliation feeds discrepancies back into the semantic layer, which means every disagreement makes the platform smarter without me writing more code. The Jira triage agent's pattern library can extend to other categories without my involvement. Three, cross-org credibility — senior engineers earn trust within engineering, principals earn it across business functions. My dashboards rank top 3.4% of 207,000 at Walmart and I won a Make a Difference Award; product leadership has signed off on agents I designed; the analyst team adopts what I ship. The honest growth edge: I haven't yet operated a platform with multiple owners. Agent Builder is that step — moving from "I build agents others use" to "I build the system others build agents with." That's the principal step, and it's why I want this role.

**Why it's a 5:** Three mechanisms (not adjectives), each with evidence. Honest about the growth edge. Frames the role itself as the next step.

**Grading checklist:**
- [ ] Mechanisms, not adjectives
- [ ] Evidence for each mechanism
- [ ] Honest about a growth edge
- [ ] Names what this role uniquely offers

---

## Q22: If you joined, what mechanism would you put in place so the second agent ships faster than the first?

**Bad answer (3/5 — vague "platform"):**
> I'd build a template library and shared infrastructure so the second agent doesn't have to redo the work the first one did. Things like prompt templates, eval frameworks, and common tools.

**Failure modes:** Vague-platform answer. Doesn't pick a specific mechanism, doesn't address the social side (other people will build agent #2), doesn't address what *won't* be in the platform.

**Good answer (5/5):**
> One concrete mechanism: a "starter pack" — opinionated default config a new agent inherits unless explicitly overridden. Five things in the pack. One, owner field — required, no agent ships without a named human accountable for it. Two, an eval-set scaffold — every agent starts with at least ten golden cases, no agent goes to prod without them. Three, tool allowlist — empty by default, additions require explicit approval. Four, an observability hook — every tool call and every LLM call goes to the same trace store with the same schema, so any agent's behavior can be debugged in the same dashboard. Five, a kill switch — single flag flips the agent into recommendation-only mode. The reason this works isn't the templates themselves, it's that it makes the safe path the easy path. Most "speed up agent 2" attempts fail because the platform becomes a constraint people work around. A starter pack is opt-out by default — you can deviate, but you have to argue for it. Half the time the argument exposes that you didn't need to deviate. Three months from launch, the second agent should ship in less than half the time of the first. If it doesn't, the starter pack is wrong and I'd redesign it.

**Why it's a 5:** Picks one specific mechanism. Five concrete pack contents. Articulates the social-design principle (opt-out makes safe path easy). Names the success metric and the rollback condition.

**Grading checklist:**
- [ ] One specific mechanism named (not "I'd build a platform")
- [ ] Concrete contents listed
- [ ] Addresses the social-engineering dimension
- [ ] Success metric stated
- [ ] Rollback/redesign condition stated

---

## Q23: How would you decide which agent use case to build first?

**Bad answer (3/5 — generic prioritization):**
> Highest impact, lowest risk. I'd look at use cases that save the most time or generate the most value, and pick the one that's most achievable in the first 90 days.

**Failure modes:** Recites a 2x2 without showing how it's applied. No criteria, no example.

**Good answer (5/5):**
> I'd score candidates on four dimensions and pick the top one. One, reversibility — if the agent is wrong, can the action be undone cheaply? I want a high score here for the first agent. The wrong first agent kills trust for the whole program. Two, volume — high-frequency tasks compound time savings and produce eval data fast. A low-frequency task gives you no signal for months. Three, ground-truth availability — can I measure if the agent is working? If I can't tell whether a recommendation was right or wrong, I can't improve the system. Four, stakeholder appetite — is there a partner team eager to be the first user? The wrong stakeholder makes the first agent fail even if the build is fine. A use case that scores high on all four is something like supplier chargeback dispute triage — reversible (it's triage, not adjudication), high volume, has historical resolution data as ground truth, and chargeback teams have real pain. I would *not* start with autonomous pricing or autonomous merchandising decisions, even though those are higher-dollar, because they fail the reversibility test. Worst-case for triage is "we routed wrong, fix it." Worst-case for autonomous pricing is "we lost margin and a vendor is upset."

**Why it's a 5:** Four named criteria, applied to a specific Walmart-realistic example, plus an explicit anti-example showing the criteria filter. Principal-level prioritization.

**Grading checklist:**
- [ ] At least four criteria named
- [ ] Criteria applied to a Walmart-realistic example
- [ ] Counter-example (what *not* to start with) included
- [ ] Reversibility is at the top, not low-priority

---

## Q24: What would your first 30/60/90 days look like?

**Bad answer (3/5 — generic onboarding plan):**
> First 30: learn the team, the platform, and the domain. Talk to stakeholders. Identify use cases. Days 30-60: pick a use case and start building. Days 60-90: ship the first agent and start the second.

**Failure modes:** Could be said by any candidate for any role. No domain specifics, no risks named, no surprising choices.

**Good answer (5/5):**
> 30 days: learn by shipping. I don't believe in pure-listening onboarding because you can't tell who's right when stakeholders disagree until you've built something. So week one, meet every panelist and ten downstream users — merchandising and supply-chain operators if I can get them. Week two, sit in on existing Agent Builder workflows end-to-end, including the parts that fail. By day 30 I want a written "what is broken, what is working, what is being asked for" doc and one ten-line agent in production solving a small real problem, so I've used the platform as a builder, not just heard about it. 60 days: pick the first real use case using the four criteria — reversibility, volume, ground truth, stakeholder appetite — and start it. Parallel: identify the three things in the platform that the second agent would benefit from being templatized (eval scaffold, tool allowlist, owner-required), and start building those alongside, so by the time agent two starts they exist. 90 days: agent one in shadow mode with real users, agent two scoped and starting. By this point I should be able to show two charts: time-to-build trend (agent one's actual hours vs. agent two's projected hours) and adoption signal on agent one (route-around rate, escalation rate). If those two charts don't show the right direction, the platform thesis is wrong and I'd say so out loud. The thing I won't do in 90 days: announce a grand platform vision. The vision falls out of two or three real agents. Pretending to have it on day one is theater.

**Why it's a 5:** Specific actions per period. Has an opinion ("learn by shipping"). Names the two trend charts that prove the work. Names what *won't* be done. Closes with a sharp anti-pattern.

**Grading checklist:**
- [ ] Specific actions per period, not "learn, then build"
- [ ] Names what proves the work is going right (specific metrics)
- [ ] Names something explicitly not in the plan
- [ ] One opinionated framing ("learn by shipping" or similar)

---

## Q25: How would you make Agent Builder usable by non-technical builders?

**Bad answer (3/5 — UX hand-waving):**
> Templates, good UX, natural-language interfaces, documentation. Make it easy to start with examples and customize. Provide guardrails so they can't break things.

**Failure modes:** Lists the right surface features without the design principle behind them. No specifics, no tradeoff named.

**Good answer (5/5):**
> The framing I'd push back on first: "non-technical" is a misleading label. The actual users are domain experts — merchandisers, supply-chain operators, store managers — who know their problem better than I do and who don't want to know how the agent works under the hood. The platform's job is to let them express *the decision they want made* and trust the platform to express it as an agent. Three concrete design choices that follow from that. One, natural language where the input is genuinely fuzzy ("escalate if this looks like a vendor onboarding issue"), structured fields where safety matters ("approval required for actions touching $X"). The mistake is using natural language everywhere because it's friendly — that's where you get unsafe automations. Two, opinionated templates beat blank canvases. A merchandiser shouldn't see "build an agent." They should see "build a triage agent" or "build a recurring digest" with the template's required fields already laid out. Three, every agent has the same five things visible: owner, tool allowlist, eval set, kill switch, observability link. Not optional, not tucked behind menus. Visible. The deeper principle: making a platform safe for non-technical builders isn't about restricting them, it's about making the safe choices the default. A blank canvas with "you can do anything" is the dangerous design. A template with sensible defaults and visible governance is the safe one. Counter-intuitive but true: more opinionated platforms are safer *and* faster.

**Why it's a 5:** Reframes "non-technical" first. Three design choices, each with rationale and an anti-pattern. Closes with the safe-by-default principle.

**Grading checklist:**
- [ ] Reframes "non-technical" to "domain expert"
- [ ] NL vs structured-field split with rationale
- [ ] Opinionated templates over blank canvas
- [ ] Five visible governance items named
- [ ] Closes with a principle, not features

---

# Curveballs

## Q26: Are you willing to relocate to Bentonville?

**Bad answer (3/5 — equivocation):**
> Yes, I'm open to it. I'd want to discuss the timing and logistics — my current setup is in Chicago — but I understand the role is based in Bentonville and I'm willing to make that work.

**Failure modes:** Hedged. "Open to it" reads as "no, but I'm trying not to say no." Even if it's a yes, it sounds like a maybe.

**Good answer (5/5):**
> Yes. I've thought about it specifically because this is the kind of role that only works in person at this stage of an agent program. You need to be in rooms with merchandising and supply-chain leaders, not on Zoom with them. If the offer comes, I'll move. The logistics question I have is timing — I'd want a reasonable window to wrap up Data Ventures cleanly without leaving things broken — but that's not a "willing to" question, it's a "when by" question.

**Why it's a 5:** Direct yes. Shows Kanu has actually thought about *why* the role needs in-person presence. Reframes the only logistic concern as scheduling, not willingness.

**Grading checklist:**
- [ ] Answer is "yes" in the first sentence
- [ ] Shows reasoning about *why* in-person matters for this role
- [ ] Any logistic concern is framed as schedule, not commitment
- [ ] No hedging language ("open to," "willing to make it work")

---

## Q27: What concerns do you have about this role?

**Bad answer (3/5 — fake-concern):**
> Honestly, very few. I'm excited about the role. Maybe the main concern is just making sure I have the right support to be successful, since it's a new team.

**Failure modes:** "No real concerns" is the answer that signals not having thought about it. Sounds rehearsed.

**Good answer (5/5):**
> Three real ones, in order of how much they'd shape my decision. One, platform constraints — most low-code agent platforms force tradeoffs I wouldn't choose. I'd want to know how flexible the platform is when an agent's architecture wants to break out of the template. If the platform can't express a parallel-reconciliation pattern like Boon, that's a real constraint. Two, ROI attribution in a messy domain — measuring agent impact on sales lift, cost savings, or time savings is hard when the system isn't isolated from a hundred other variables. I'd want to know how the team has decided to measure success so I'm not signing up for an unmeasurable goal. Three, scope of "Agent Builder" — is the role primarily building agents for the org, or building the platform others use to build agents? Both are great, but they're different jobs, and I'd want to know which the team weights heavier in the first year. Those are the things I'd want to talk through, not deal-breakers — they're shaping my questions during the interview, not my willingness to take the role.

**Why it's a 5:** Three substantive concerns that reflect actually thinking about the role. Each one is technical or strategic, not personal. Closes by reframing concerns as questions, not objections.

**Grading checklist:**
- [ ] At least two substantive concerns
- [ ] Concerns reflect actual reading of JD / role nuance
- [ ] None are personal/comp/lifestyle — all role-content
- [ ] Closes by treating concerns as questions, not objections

---

## Q28: Why should we hire you over someone already in supply chain engineering?

**Bad answer (3/5 — apologetic):**
> I know I don't have direct supply chain background, but I learn fast and I can pick up the domain quickly. My agent-building skills transfer, and I'd partner closely with people who do have the domain expertise.

**Failure modes:** Defensive framing — argues from weakness. Doesn't make a positive case. "I'll learn" isn't a differentiator.

**Good answer (5/5):**
> Two distinctions matter. One, this role isn't supply chain engineering with agents on top — it's agent building applied to supply chain. The center of gravity is the agent platform, not the domain. The right hire knows how to scope agents end-to-end, design context and validation layers, run evals against business outcomes, and influence non-technical stakeholders. I do all four daily. A pure supply chain engineer would have to learn the agent half, which is harder and slower to learn than the domain half. Two, "doesn't know supply chain" is overstated for someone coming from Data Ventures. I've spent eighteen months building analytics tooling for product partners whose questions are about merchandising, vendor performance, on-shelf availability, replenishment. I know the questions; I don't have ten years of operator instinct yet. That's a 90-day gap, not a year-long gap, and I'd close it the way I close any domain gap — three to five operator shadow sessions in the first month. The positive case: I'm not a domain hire and I'm not a generic ML hire. I'm someone who has shipped agents end-to-end against real business outcomes, and that combination is what the JD actually asks for.

**Why it's a 5:** Reframes the question — argues the role is agent-first, not domain-first. Concedes the domain gap honestly, sizes it (90 days), and has a plan. Closes with a positive thesis.

**Grading checklist:**
- [ ] Reframes the role's center of gravity
- [ ] Concedes the gap without being defensive
- [ ] Sizes the gap and names a plan to close it
- [ ] Closes with a positive thesis, not "I'll learn fast"

---

# System Design Reps

## Q29: Design an Inventory Exception Handling Agent

(Stockouts, phantom inventory, demand spikes, replenishment mismatches)

**Bad answer (3/5 — jumps to architecture):**
> I'd build an agent that ingests inventory event streams, classifies the exception type using an LLM, retrieves context like sales history and replenishment data, and recommends an action. It would have tools to query the inventory system, the forecasting model, and send Slack notifications. I'd use Claude as the planner with sub-agents for each exception type.

**Failure modes:** Skipped the entire problem-definition layer. No user, no decision, no bottleneck, no metric. Architecture without justification. Every senior engineer can produce this answer.

**Good answer (5/5):**

**Step 1 — Clarify the workflow.**
"Before I design, three questions. Who is the user — a store associate looking at a specific aisle, a category planner looking across hundreds of items, or a supply-chain operator looking across DCs? They have different latency tolerances and different decision rights. Two, what's the cost of being wrong — a false positive ('there's a stockout that isn't real') wastes an investigation hour; a false negative ('we missed a real stockout') costs sales. Asymmetric. Three, what's broken today — are exceptions missed, caught late, or caught but routed wrong? Let me assume for this design: the primary user is the category planner; the bottleneck is that exceptions are caught late (4-12 hours after event); false-negatives are the more expensive failure."

**Step 2 — Define success.**
"Time-to-detection (currently 4-12 hr, target <30 min for high-priority exceptions). False-negative rate (today unknown — we'd need to instrument). Action acceptance rate (do planners trust the recommendations). And cost per exception handled — because the system has to be cheaper than the analyst time it replaces."

**Step 3 — Should this be an agent?**
"For the *classification and synthesis* layer, yes — exception explanation requires synthesizing inventory data, forecast data, replenishment data, and natural-language context (vendor delays, weather, promo overlap). That's language-shaped. For the *trigger and action* layer, no — exception detection should be deterministic (threshold-based rules on inventory delta vs. forecast). The agent enriches and recommends; the rules detect and act. Don't let an LLM decide whether something is an exception."

**Step 4 — Architecture, in four layers.**
"Intake: BigQuery event triggers on inventory delta — like the headless monitor architecture I built at Data Ventures. Fixed thresholds for known exception types, ML-based anomaly detection for unknown patterns. Both fire into the same event queue. Context: retrieval over the affected SKU's recent sales, forecast, replenishment status, vendor history, store-level promos, weather if relevant. Critically, source-of-truth: the agent retrieves, doesn't memorize, so it always reasons over current state. Reasoning: planner agent classifies the exception (stockout, phantom, spike, mismatch) and dispatches to a specialist sub-agent per type. Each sub-agent has its own prompt and eval set because the failure modes differ — phantom inventory is detected differently than a demand spike. A reconciliation/validation sub-agent reviews the output for evidence-claim alignment before return. Output: a structured recommendation (action, evidence, confidence) plus a draft Slack/dashboard notification to the planner. *Recommendation only* on day one — never autonomous action."

**Step 5 — Guardrails.**
"Tool allowlist — read-only access to inventory, forecast, replenishment systems; no write access to anything until v3. Confidence threshold below which the agent says 'I see something unusual, here's the data, you decide' instead of recommending. Source-of-truth check before every recommendation — agent's data must match the inventory system at recommend time. Audit trail on every recommendation. Kill switch on the whole agent."

**Step 6 — Evals and observability.**
"Offline: 200 historical exceptions where I know the right action — run on every prompt change. Shadow mode: agent runs in parallel with current analyst workflow for 30 days, no actions taken, diffs logged. Online metrics: detection latency, recommendation acceptance rate, override rate, false-positive rate, false-negative rate (the hard one to measure — would need to instrument with periodic deep audits)."

**Step 7 — Rollout.**
"Phase 1 (weeks 1-4): recommendation-only for one category with one planner. Measure acceptance, override patterns. Phase 2 (weeks 5-8): expand to one full DC. Phase 3 (weeks 9-12): expand to one banner, automate the lowest-risk action class (re-routing replenishment requests, fully reversible). Phase 4: gated by data — if false-negative rate is below threshold and acceptance is above threshold, expand action authority. If not, stop and redesign. The thing I won't do: ship autonomous restocking on day one. The cost of being wrong is too asymmetric."

**Why it's a 5:** Follows the scaffold without sounding mechanical. Clarifies users and cost-asymmetry before architecting. Explicitly splits deterministic detection from LLM-driven synthesis. Names what's *not* in v1. Closes with a gating condition for expanding scope.

**Grading checklist:**
- [ ] Clarifying questions on user/cost/bottleneck *before* architecture
- [ ] Splits deterministic from LLM responsibilities explicitly
- [ ] Sub-agents justified by different failure modes
- [ ] Recommendation-only in v1 (reversibility prioritized)
- [ ] Rollout phases with explicit gating conditions
- [ ] Names what's *not* in v1

---

## Q30: Design an Agent Regression Monitoring System

**Bad answer (3/5 — feature list):**
> I'd build a CI pipeline that runs a golden eval set on every prompt or model change. If any case fails, the deployment is blocked. I'd also have online metrics like accuracy and acceptance rate to monitor for drift. Plus alerting if metrics drop.

**Failure modes:** Lists CI features without addressing the hard parts: silent failures, distinguishing model regression from data drift, deciding when to roll back vs. accept a regression as new-normal.

**Good answer (5/5):**

**Step 1 — What are we monitoring for, specifically?**
"Three categories of regression, each detected differently. One, *known-pattern regression* — the agent gets worse at things it was previously good at. Detected by offline golden cases. Easy. Two, *silent failure regression* — the agent's outputs are still plausible but subtly worse (confidence stayed high, accuracy dropped). Detected by shadow comparison or by adversarial eval cases. Hard. Three, *drift regression* — the agent is unchanged but the world changed: schema drift, data distribution change, new question types. Detected by online metrics on the agent's own behavior, not by comparing to a fixed ground truth. Each needs its own detector."

**Step 2 — Architecture.**
"Versioned artifact registry — every prompt, every model, every retrieval index, every eval set has a version, and every agent deployment is tagged with the exact versions it ran with. Without this, you can't tell what regressed. Offline regression suite — golden cases pinned to known correct outputs, run on every change to any artifact. CI blocks deployment on regression. Shadow comparison — old version and new version run in parallel on a sampled portion of live traffic, outputs diffed structurally (not just final text — intermediate sub-agent outputs too). Diffs flagged when structurally different even if both are arguably correct, because that's where silent regression hides. Online metric layer — acceptance rate, override rate, escalation rate, route-around rate, latency, cost. All segmented by question type, because aggregate metrics hide segment regressions. Failure clustering — collected failures are clustered weekly to find emerging patterns. A new cluster means a new failure mode that needs a new golden case."

**Step 3 — Guardrails for the monitor itself.**
"The monitor must be allowed to be wrong without blocking everything. Hard-fail on golden eval below a threshold; soft-warn on shadow diffs (alert, but don't block). Otherwise the monitor becomes a deployment-blocker that gets bypassed. I want it to be cheap to ship and cheap to roll back, not cheap to ignore."

**Step 4 — Rollback strategy.**
"Rollback must be boring. Every artifact is versioned, every deployment is tagged, every rollback is a single tag flip. Rollback time target: under 60 seconds. The biggest mistake teams make is treating rollback as an emergency procedure — it should be the most-practiced thing the team does. Rolling back is data; staying broken is panic."

**Step 5 — The deep insight.**
"Eval sets themselves regress. The golden set you wrote a year ago doesn't represent today's traffic. So the monitor needs to monitor its own evals — every quarter, sample live traffic, manually grade a hundred cases, and check whether the golden set still represents the live distribution. If it doesn't, the eval set needs new cases. Most regression-monitoring systems fail because the evals quietly become irrelevant."

**Why it's a 5:** Names three distinct regression types with three distinct detectors. The version-everything insight is principal-level. Soft-warn vs hard-fail distinction shows operational maturity. Eval-sets-themselves-regress is the deep insight most candidates miss.

**Grading checklist:**
- [ ] Three regression types named (known-pattern, silent, drift)
- [ ] Different detector per type
- [ ] Version registry for prompts, models, indexes, eval sets
- [ ] Soft-warn vs hard-fail distinction
- [ ] Rollback as a boring, practiced thing
- [ ] Eval sets themselves regress — meta-insight

---

# Quick-Reference Grading Cheatsheet

When grading any answer, ask in this order:

1. **Did it start with the business problem, not the tool?** If they led with stack names, that's a 3.
2. **Are there numbers?** Time saved, cost reduced, acceptance rate, volume — pick one. No numbers, max 3.
3. **Did they name a tradeoff?** Principal-level answers say "I chose X over Y because Z." Senior answers just say "I chose X."
4. **Did they name what's *not* in the design / *not* in scope?** Naming what you won't do is a stronger signal than naming what you will.
5. **Did they close with a transferable principle?** "The lesson is X" — not just "and then it worked."
6. **Did they earn the word "principal"?** Mechanism, leverage, cross-org credibility. Not adjectives.

If three or more of these are missing, the answer is below 4. Redo it.

---

# Practice Loop

For each mock session:

1. Pick 3-5 questions from this file. Don't tell yourself which ones in advance — Claude picks at random.
2. Answer cold, on the clock (90 sec behavioral, 2-4 min technical, 8-12 min system design).
3. Claude grades using the rubric for that question and the cheatsheet above.
4. Anything below 4 — redo immediately. Don't move on.
5. After every session, jot one line: which failure mode showed up most? That's the thing to drill next time.
