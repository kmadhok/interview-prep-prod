# Resume Deep-Dive Question Bank — BCG X Round 2 (Patrick Freyer)

**Purpose:** Patrick is a builder. He'll take your resume bullets and probe *how you think* — the decisions behind each build, and where your agent-building process has gaps. This file pre-stages, for every resume point, the questions a sharp builder would actually ask, grouped by theme (architecture, evaluation, governance, failure modes, cost/latency, scaling). Each cluster ends with **the gap he'll hunt** and **your line** — the honest, strong answer or owned-gap.

**How to drill this:** pick a bullet, read the questions cold, answer out loud, *then* check the steer. The goal isn't memorizing answers — it's being unsurprised. If a question makes you pause longer than 3 seconds, that's the one to rehearse.

**Cross-cutting tells to keep landing:** "context engineering, not prompt engineering" · "today I'm the gate; next version moves it to [mechanism]" · "the failure mode I worry about most is confident-wrong" · "I used X over Y because Y would've cost me the audit boundary" · "it's live if you want to try it."

---

## How Patrick probes (read this first)

A builder doesn't ask "what did you build." He asks **"why that way, and what breaks."** Expect this shape on every bullet:

1. **Decision** — "Why sub-agents instead of one prompt? Why MCP instead of direct DB access?"
2. **Alternative** — "What would you have lost going the simpler route?"
3. **Evidence** — "How do you *know* it works? What's the failure you've actually seen?"
4. **Boundary** — "Who can it touch? What happens when it's wrong? Who's accountable?"
5. **Next** — "What's the weakest part, and what would you build next?"

If you only answer #1, he'll keep digging until you produce #3 and #4 yourself. Lead with them.

---

## 1. Self-Service Analytics Agent (67 tables · sub-agent orchestration · 8 rules · 23 golden cases)

**Architecture**
- Why four sub-agents (Context Researcher → SQL Drafter → Validator → Devil's Advocate) instead of one well-prompted model with tools?
- Why is the Devil's Advocate a *separate* context window? What specifically does context isolation buy you that a single critique pass wouldn't?
- How does the Context Researcher decide *which* of 67 tables are relevant? What happens when it pulls the wrong subset — does the error surface or propagate silently?
- Where does schema/business-definition knowledge live — in the prompt, in retrieval, in a static context file? How does it stay current as tables change?

**Evaluation**
- 23 golden-query cases over 67 tables feels thin. How did you choose those 23? What's *not* covered, and how would you know if coverage is the problem?
- You evaluate on result-match, not SQL-match, because there are multiple right queries. How do you define "result matches" — exact rows, aggregate equality, tolerance? What about non-deterministic ordering or nulls?
- When a golden case fails after a change, how do you localize it to a sub-agent? Is the eval per-stage or end-to-end only?
- How often does the golden set get refreshed, and who owns it? (Static golden sets decay as the data changes.)

**Governance / access**
- Who can run this, and on what data? Does the agent run with one service account's permissions or the asking user's? How do you stop someone from getting an answer over a table they shouldn't see?
- Is there row/column-level security, or does the agent see everything the service account sees? How would you add per-user scoping?
- Audit: if a business leader makes a decision off an answer, can you reconstruct exactly which tables, joins, and rows produced it?

**Failure modes / cost**
- What's the worst wrong answer this has produced, and what did you change because of it?
- "Confident-wrong — clean SQL on a stale flag." How does the agent catch a freshness problem the SQL can't see?
- Four sub-agents per question = multiple LLM calls. What does a question cost in tokens/latency, and where would you cut if you had to halve it?

> **Gap he'll hunt:** eval coverage (23 cases) and per-user data permissions. **Your line:** "23 is the regression floor, not the ceiling — it's the set that's caught real regressions; I grow it from production misses, not theory. On access, today it runs on a scoped service account; the honest next step is per-user scoping at the MCP boundary so the agent inherits the asker's permissions." Own it, name the next move.

---

## 2. Hybrid Orchestrator (CubeJS semantic layer ✕ agent, parallel routing)

**Architecture**
- Why route to both backends in parallel instead of using the semantic layer as the source of truth and the agent only as fallback?
- When they disagree, how does the orchestrator decide which is right *today*? Walk me through the reasoning step concretely.
- What feeds back into the semantic layer — a proposed definition, a flag for a human, an auto-commit? Who approves a definition change?
- Doesn't this create a circular trust problem — the agent refines the layer it's also being checked against?

**Evaluation**
- How do you evaluate the *orchestrator's* judgment, separate from each backend's correctness? When it picks the wrong winner on a disagreement, how do you catch that?
- Silent agreement — both backends wrong the same way — defeats parallel routing. How do you detect it?

**Governance**
- A wrong auto-refinement corrupts the semantic layer for everyone downstream. What's the blast radius, and what gate sits before a definition change lands?

> **Gap he'll hunt:** the feedback loop's safety — can a bad agent answer poison shared definitions? **Your line:** "Discrepancy review is human-led today — the loop proposes, a human authors. The next version proposes the refinement and a human approves rather than authors. I deliberately kept the human as the gate on anything that mutates shared state." This is your "author → gate" theme; use it.

---

## 3. Autonomous Jira Resolution Agent (6-gate · MCP · FAISS+BM25 over 11k queries · 10-retry)

**Architecture**
- Walk me through the 6 gates. Which one fails most, and what happens when it does?
- Why MCP over giving the agent direct BigQuery credentials? (Audit boundary — say it.)
- FAISS + BM25 + RRF over 11,000 historical queries — why hybrid retrieval instead of pure vector? What does BM25 catch that embeddings miss here?
- 11k queries is a lot of prior art but also a lot of *bad* prior art. How do you keep it from retrieving and repeating a historically wrong query?
- The 10-retry self-healing budget — what does it diagnose between retries? How do you stop it from burning 10 retries on an unfixable request?

**Evaluation**
- "Stakeholders never knew an agent was answering them." That's great adoption — but how do you *know* the 400+ answers were right, if no human flagged them as agent-generated?
- What's your sampling/audit rate on closed tickets? Has a wrong answer shipped, and how did you find out?
- 8 categories — does accuracy vary by category? Which category is weakest and why?

**Governance**
- The agent answers data-readiness questions that influence other people's work. If it's wrong, who's accountable — you, the agent, the stakeholder? How is that handled today?
- Provenance: for any closed ticket, can you reproduce the exact context, SQL, and decision path?

**Failure / scale**
- This automated *your* queue. What happens to it when you leave the team — who maintains the context layer and retrieval index?
- The retrieval index over 11k queries grows. How does retrieval quality hold as it hits 50k?

> **Gap he'll hunt:** silent-correctness — adoption without a visible human check looks like flying blind. **Your line:** "The work log is the check — every ticket leaves a reproducible artifact (SQL, table, join), and I'm the gate reviewing those, not the stakeholder. The risk I'm managing is exactly confident-wrong, which is why eval is moving to process-level golden regression, not output spot-checks." Turn the adoption strength into a governance answer.

---

## 4. Recruitment Automation (20 workflows · 68 tables · 280k panelists · zero duplicates)

**Architecture**
- Is this agentic or deterministic? (Be clear it's largely deterministic — and why that's the *right* call here, not a lesser one.)
- "Agent where input varies, deterministic where I can verify." Why does recruitment sit on the deterministic side?
- Stratified sampling enforcing 29-category quotas at the SQL layer — why enforce in SQL vs. in application code?

**Evaluation / governance**
- Zero duplicates across 280k is a write-time guarantee. Walk me through the mechanism — what table, what check, what race condition could still slip a duplicate through under concurrency?
- If two recruitment runs fire near-simultaneously, can they both pass the dedup check and double-allocate? How is that prevented (locking, transactions, idempotency)?
- Panelist data is PII-adjacent. What governs who can run a recruit and what fields the pipeline touches?

> **Gap he'll hunt:** concurrency/idempotency on the dedup guarantee, and why this *isn't* an agent. **Your line:** "I chose deterministic on purpose — the rule is verifiable, so an LLM would add risk without adding judgment. The dedup is a write-time check against a persistent allocations table; the honest edge case is concurrent runs, which I serialize today." Demonstrating you know *when not to use an agent* is a senior signal for a builder.

---

## 5. Headless KPI Monitor (6-hr cron · root-cause · Slack · BigQuery state · event-driven v2)

**Architecture**
- "No LLM-memory reliance — state persists to BigQuery." Why does that matter for a headless agent specifically? What breaks if you rely on the context window across cron ticks?
- If the LLM call fails mid-cycle, how does the next run know where to resume? Is each tick idempotent?
- v2's 3-tier event registry lets PMs add event types without code deploys. What stops a malformed registry row from breaking the whole cron? Where's the validation/sandbox?

**Evaluation**
- How do you evaluate root-cause *quality*, not just breach detection? A correct alert with a wrong cause is worse than no cause.
- Alert fatigue: how do you tune precision? What's the gate before a new event type goes live? (Zero false positives on 30-day backtest — say it.)

**Governance / reliability**
- Headless means no human watching in real time. What's the dead-man's-switch — how do you know the monitor itself is alive and not silently failing?
- Who gets paged if the monitor breaks vs. if a KPI breaches?

> **Gap he'll hunt:** observability of the agent itself (not just the KPIs) and registry-injection safety. **Your line:** "Decision logging in BigQuery is the eval substrate — every breach and root-cause is queryable, so the monitor's own behavior is observable, not just the KPIs. For v2, a registry row is validated and backtested before it goes live — a PM can add an event type, but it can't ship until it clears zero-false-positive on 30-day data."

---

## 6. Power BI dashboards (top 1.4% of 207k · Making a Difference Award)

- This is your pre-agent BI credential. Expect *at most* one question: "what made these top-percentile — usage or craft?" Answer in one breath (real adoption: 1,064 views, 22 recurring users; turnaround 1–24hr → 5–10min) and pivot back to the agent work. **Do not spend a walkthrough slot here.**

---

## 7. Persona-Driven Multi-LLM Donation Experiment (OpenAI + Gemini · 500+ · 15% lift)

- Why two models? (Variance control — if both produce the lift, the effect is the chatbot, not the model.)
- What was the *control* arm — static page, non-persuasive bot, no interaction? (Know this; it's the eval's validity.)
- This is your most ethically loaded build — persuading people. How did you think about consent/deception? A governance-minded interviewer may probe the ethics, not the tech.
- It's research-era. Mention only if he asks about experimentation or multi-model work; don't lead with it.

> **Gap:** experimental-eval validity (control design) and ethics framing. **Your line:** be ready to state the control arm precisely and the consent protocol. If you don't remember a detail, say "I'd have to check the protocol" rather than invent — honor code and honesty both matter.

---

## 8. RAG-to-Proposal Generator (FTI · AWS EC2 · −30% · Best in Show)

- This is the **forward-deployed shape** — client RFP in, deployed artifact out, fixed timeline, judged by partners. Patrick (forward-deployment focus) may like this one. Be ready to lead it if he goes client-delivery.
- Hallucinated credentials is the killer failure mode for proposal-gen (claiming expertise the firm lacks). How did you prevent it — retrieval-only from a validated library, citations, guardrails on certain sections? (Know your real answer here; there's a `[VERIFY]` in the master — fill it.)
- How did you measure −30%? Against what baseline, measured how?

> **Gap:** the credential-hallucination mitigation is marked unverified in your notes. **Resolve it before the 16th** — decide the true answer (citations? retrieval-only? human review?) so you're not caught hand-waving.

---

## 9. Innovare risk model (logistic regression · 10+ districts · retention +7%)

- Pre-GenAI, classical ML. Expect at most: "how did you validate the model / avoid leakage?" One crisp answer, then move on. Don't over-invest.

---

## 10. Live Text-to-SQL Copilot (Streamlit · Gemini 2.5 · LangChain RAG · BigQuery · auto-viz)

**This is your demo — offer it.** "It's live if you want to try it."

- Why Gemini 2.5 here vs. Claude (which you use daily via Wibey)? What drove the model choice for *this* surface?
- LangChain orchestrates the RAG — what does LangChain earn you here that a hand-rolled retrieval loop wouldn't, given you hand-roll elsewhere?
- It executes against *live* BigQuery, not a sandbox. What stops a generated query from being expensive or destructive? Read-only enforcement? Query cost limits? Injection?
- Auto-viz picks chart type from result shape — what's the rule, and where does it pick wrong?
- Eval is admittedly lighter ("does it survive a live stranger"). If you productionized this, what's the first eval layer you'd add? (Abstention on low-confidence/ambiguous queries — say it.)

> **Gap he'll hunt (live, in real time):** query safety on live execution. Be ready: "read-only credentials, cost guardrails" — and if those aren't fully there, *say so* before he finds it by asking you to run something. Honesty on a live demo reads as senior; spin reads as junior.

---

## Cross-cutting "how do you build with GenAI" questions (apply to any bullet)

These are the meta-questions a builder uses to find your ceiling. Have a real point of view, not a survey.

**Evaluation philosophy**
- "How do you decide an agent is good enough to ship?" → the gate, not the vibe.
- "Static golden sets decay. How do you keep eval honest as data drifts?"
- "What's the difference between observability and evaluation in your stack?"

**Context engineering**
- "How do you manage the context window on a long-running agent?" → externalize memory to artifacts.
- "When do you reach for RAG vs. fine-tuning vs. just a bigger context?" → have a clear heuristic.
- "How do you keep retrieval quality from degrading as the corpus grows?"

**Governance / security (his AiAssist home turf — be ready)**
- "How do you control what an agent is allowed to see and do?" → MCP as the control/audit boundary.
- "How do you handle PII or sensitive data going to an LLM?" → *this is exactly his AiAssist problem (redact before the model sees it).* If you don't redact today, say how you'd add it — and connect to his work if he raises it.
- "Who's accountable when an agent is wrong in production?"

**Architecture judgment**
- "When do you *not* use an agent?" → recruitment automation is your proof you know the line.
- "MCP vs. a plain tool call — when is the abstraction worth it?" → reusable across agents + worth a stable contract.
- "Build vs. buy for [retrieval / orchestration / eval]?"

**Scaling & ownership**
- "Who maintains these after you? What's the bus-factor?" — you're a team of one on most of this; have an honest answer.
- "How would this change if it had to serve 10x the users / run in a regulated environment?"

---

## Your real gaps — rehearse owning these (he WILL find them)

Patrick is hunting for where your agent-building process is thin. These are the honest soft spots in the submitted resume. Don't hide them — **own + name-the-next-move** beats getting cornered.

1. **Eval breadth.** Golden sets (23 cases, 8 rules) are a floor, not a framework. No mention of regression CI, automated eval on every change, or coverage metrics. → "Eval is gate-based and grows from production misses; the next investment is process-level regression in CI."
2. **Per-user access control / multi-tenancy.** Agents largely run on scoped service accounts, not per-user permissions. → "Next step is scoping at the MCP boundary so the agent inherits the asker's permissions."
3. **PII / sensitive-data handling.** No explicit redaction or data-governance layer named. (Patrick's literal specialty.) → know how you'd add pre-model redaction; bridge to his AiAssist if natural.
4. **Cost / token economics.** No cost monitoring mentioned; multi-sub-agent flows are token-heavy. → have rough per-question cost and where you'd trim.
5. **Concurrency / idempotency.** Dedup and cron resume rely on it but it's not proven at scale. → name the serialization/transaction approach honestly.
6. **CI/CD & testing for agents.** No automated test/deploy pipeline for the agents named. → how you'd version, test, and roll back an agent change.
7. **Bus-factor / maintenance.** You're a solo builder on most of this. → who owns it after you, how it's documented.
8. **LangGraph / framework depth.** Resume names LangChain (real) but not LangGraph. Don't claim it if asked — "I've built the orchestration patterns by hand and with LangChain; haven't shipped on LangGraph specifically."

**The meta-move for all eight:** a senior builder is *defined* by knowing their system's weak points. Volunteering "here's the part I'd harden next" reads stronger than a clean answer that pretends there's no gap. That is the thing Patrick is actually testing.

---

*Facts pulled from the submitted resume (`Kanu Madhok Resume - BCG X Senior AI Factory.md`) and root `AI Build Walkthrough - Master.md`. Where the master has `[VERIFY]` placeholders (FTI credential-mitigation, donation-experiment control arm), resolve them before 6/16.*
