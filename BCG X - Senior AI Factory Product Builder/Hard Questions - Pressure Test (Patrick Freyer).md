# Hard Questions — Pressure Test (Patrick Freyer)

**What this is.** The earlier `Resume Deep-Dive Question Bank` covers what a sharp builder asks. This file is the *next two levels down* — the questions that separate "I built this" from "I understand this." They're deliberately uncomfortable. The point isn't to have a slick answer for each; it's to find the spots where your understanding is thin and **go deepen them before the 16th.**

**How to use.** Take one bullet. Answer each question out loud, cold. When you hit one you can't answer cleanly, stop — that's the concept to go study. The `→` notes say *what a strong answer must grapple with*, not the answer itself. Don't memorize; understand.

**The honest-framing rule still applies** (`Honest Framing` file): when a question exposes something you didn't build or test, run *did → gap → would*. A precise "here's the experiment that would settle it" beats a bluff every time. Patrick is testing depth of reasoning, not whether you happened to build everything.

---

## 1. Self-Service Analytics Agent (4 sub-agents · 8 rules · 23 golden cases · 67 tables)

1. Four sub-agents, each an LLM call, on every question. Give me the worst-case token and latency cost for one complex query — and the query volume at which this is economically indefensible versus deterministic templates or just staffing an analyst.
   → *Strong answer has real order-of-magnitude numbers and a break-even argument, not "it's worth it."*
2. The Context Researcher retrieves relevant tables from 67. High recall but low precision floods the Drafter's window and induces the exact context rot your architecture exists to avoid. What's your precision/recall operating point today, and how do you know it's right?
   → *Must show awareness that retrieval tuning, not sub-agent count, is the real lever — and admit if the operating point is untuned.*
3. Your Devil's Advocate is the same base model with the same training priors as the Drafter. Isolating *context* doesn't isolate *priors*. If the schema naming misleads the Drafter into a plausible-wrong join, why wouldn't the critic make the identical error? What actually decorrelates the failure?
   → *This is the deepest one. A real answer: context isolation only catches context-induced errors, not model-induced ones; decorrelation needs a different model, a deterministic check, or external ground truth. If you can't decorrelate, the Devil's Advocate is partly theater — own that.*
4. 23 golden cases against a query space of hundreds of joinable paths across 67 tables. Estimate your actual coverage as a fraction. Then defend 23 as informative rather than security theater.
   → *Strong answer reframes: golden cases aren't coverage, they're regression anchors on the highest-traffic questions. Coverage is the wrong frame; catching known-important regressions is the right one.*
5. Result-match eval assumes a trustworthy golden answer. If the golden number came from a human analyst who made an error, your eval enshrines the error and "passing" means "agrees with a mistake." How do you establish ground truth independent of the analyst the agent is replacing?
6. "Only AI skill in active use by business teams." Is that because it's genuinely the best tool, or because it's the only one that got built and socialized? How would you separate real value from novelty and lack-of-alternative? What metric falsifies "it's just the only option"?

---

## 2. Hybrid Orchestrator (semantic layer ✕ agent, parallel)

1. You pay 2x compute on *every* query for a disagreement signal you act on only a minority of the time. Defend always-parallel over "run the agent, invoke the semantic layer only when agent confidence is low." What does always-on buy that conditional doesn't?
2. When the two disagree, an LLM adjudicates — but it has no ground truth and uses the same fallible reasoning that produced one of the two answers. Why is the adjudicator more than a third opinion with false authority? How is this better than escalating every disagreement to a human?
   → *Must confront that an LLM judge without ground truth is not an oracle. A defensible version: the judge isn't deciding truth, it's classifying the disagreement type (stale definition vs. hallucinated join vs. ambiguous question) and routing — that's tractable; deciding correctness isn't.*
3. The feedback loop lets a probabilistic system mutate the deterministic source of truth that hundreds of dashboards depend on. Walk me through, mechanically, why one confident-wrong agent answer cannot corrupt a definition downstream consumers trust. If your answer is "a human approves," then the loop isn't automated — so what is automated?
4. As the agent's coverage gets absorbed into the semantic layer, the disagreement signal shrinks and the orchestrator trends toward redundant. Is this system designed to obsolete itself? If yes, should it have been a one-time migration project rather than a standing system?
   → *A senior answer is comfortable saying "yes, partly — and that's fine; the standing value is drift detection as new tables/definitions appear." If you can't name the residual steady-state value, the design is suspect.*

---

## 3. Jira Resolution Agent (6-gate · FAISS+BM25+RRF/11k · 10-retry · 400+ tickets)

1. RRF assumes its two rankers are independently informative and needs a tuned k. Dense and sparse retrieval over SQL *text* are highly correlated — SQL is keyword-dense, so BM25 and embeddings often agree. Quantify what RRF actually adds over BM25 alone here, and tell me how you set k.
   → *If you can't say why fusion helps on this specific correlated corpus, it's cargo-culted. Honest move: "I used the standard hybrid+RRF recipe; I haven't ablated BM25-only — that's the test."*
2. 11k historical queries include wrong queries, deprecated schema, and one-off hacks, and your retriever treats them all as exemplars. What stops the agent from confidently reproducing a query that references a dropped column or encodes a past mistake? What's your corpus hygiene strategy?
3. The 10-retry self-healing budget assumes failures are diagnosable. But an LLM diagnosing its own SQL error can rationalize a wrong fix and "succeed." Show me the case where 10 retries converges on a confidently-wrong result that's *worse* than failing fast. How do you bound retry-induced confabulation?
4. 400+ tickets, no human knew it was an agent, you're the sole reviewer. Do you read every work log or sample? If you sample, what's your statistical confidence the unsampled tickets are correct? Be concrete — you may have shipped wrong answers nobody flagged precisely because the output looked authoritative.
   → *This is the integrity crux. Strong answer states the real review rate and accepts the implied risk honestly, then names the eval that would replace spot-review.*
5. Your headline is "30–60 min → under 10 min," but the 10 includes *your* review. As volume grows your review time becomes the very bottleneck you claim to have removed. At what ticket volume does this break, and what's the plan that isn't "Kanu reviews faster"?
6. MCP is your audit boundary — but the tools you expose define the capability surface. If you exposed a general SQL-execution tool, the boundary is just logging, not constraint. What is actually *constrained* at the MCP layer versus merely *recorded*?
   → *Must distinguish authorization (can't) from observability (we'll see it later). If everything is observability, say so.*

---

## 4. Recruitment Automation (280k panelists · zero dup · 29 categories)

1. Zero-duplicate via check-then-write against an allocations table is a textbook race: two concurrent runs both pass the check before either writes. You said you serialize — serialization caps throughput. Defend serial execution at 280k scale, or show me the isolation level / locking / unique-constraint that makes concurrent runs safe without serializing.
   → *The clean answer is a DB-level uniqueness constraint making the duplicate physically unrepresentable, not application-level checking. If you relied on app-level checks, own it.*
2. Stratified sampling hits quotas, but if the sampling frame (who's in the 68-table platform) is itself biased, you get a quota-correct but unrepresentative panel. How do you reason about representativeness versus quota-hitting? What bias survives stratification?
3. Panelists belong to multiple categories with different targets — this is a constrained allocation problem. Naive per-category sampling double-counts or starves categories. Is your allocation a real optimization (min-cost flow / LP) or greedy? Give me the input where greedy produces an infeasible or skewed allocation.

---

## 5. Headless KPI Monitor (6h cron · BigQuery state · event-driven v2)

1. You chose BigQuery as the agent's state/checkpoint store. BigQuery is analytical, not transactional — no row locks, streaming-insert visibility lag, slow single-row writes. Defend it over an actual transactional store. Exactly what breaks if two cron ticks overlap and both read-then-write state?
   → *A strong answer concedes BigQuery is wrong for transactional checkpointing and either justifies it pragmatically (low concurrency, idempotent ticks) or names what they'd move to. Don't defend it as correct if it isn't.*
2. LLM root-cause analysis turns correlation in the underlying tables into a confident causal story for *any* breach. A plausible-wrong root cause sends humans down the wrong path — strictly worse than alerting the breach with no cause. How do you keep it from confabulating causation? Why attach a cause at all?
3. v2 lets PMs define executable event types as BigQuery rows with no deploy and no code review. That's a non-engineer-editable code path — an injection and footgun surface. What validates a registry row before the cron acts on it? What's the blast radius of a malformed or adversarial row?
4. A 6-hour cron means up to 6 hours of detection latency — an eternity for a real incident. Why cron over event-driven/streaming from the start, and what did that latency cost in an actual breach you've seen?

---

## 6. Power BI dashboards · 7. Innovare risk model
*Low-priority, pre-agent. Expect at most one question each. One crisp answer, then pivot to the agent work. Don't let either eat time.*
- Dashboards: "top 1.4%" by usage or by craft? (Real adoption numbers, one breath, move on.)
- Innovare: how did you avoid leakage / validate the logistic model? (One answer, move on.)

---

## 7. Persona-Driven Donation Experiment (multi-LLM · 500+ · 15%)

1. Was 15% the lift over control or absolute, and what was N per arm? Give me the confidence interval. Was the study powered a priori to detect that effect, or is 15% a post-hoc finding you're presenting as a result?
   → *If you can't speak to power and CI, present it as directional, not as a clean causal result. Overclaiming a stat to a quantitative interviewer is the trap.*
2. "Two models for variance control" isn't variance control — model identity is a confound unless you randomized assignment and analyzed within model. Did the effect hold within *each* model, or only pooled? If pooled only, what do you actually know?
3. Steelman the case that an adaptive-persona system optimized to move people off their stated beliefs at scale shouldn't be built at all. (Patrick may probe the ethics, not the tech — have a real, non-defensive answer.)

---

## 8. RAG-to-Proposal Generator (FTI · −30%)

1. Hallucinated credentials — claiming firm expertise that doesn't exist — is the lethal failure for proposal-gen, and your own notes mark the mitigation unverified. Right now, defend this as deployable to a paying client given you can't state how it prevents that.
   → *Resolve the real mitigation before the 16th. If there genuinely wasn't one, say "for a capstone the guardrail was human review before anything left the building; productionizing needs retrieval-only-from-validated-library + per-claim citation."*
2. "−30% proposal time" — measured as time-to-first-draft, or end-to-end including the editing a fluent-but-wrong draft induces? A bad draft can cost more to fix than a blank page. How do you know *net* time dropped, not just time-to-first-draft?

---

## 9. Live Text-to-SQL Copilot (public · Gemini 2.5 · live BigQuery)

1. A stranger on the internet triggers generated SQL against your live BigQuery. Walk me through, right now, why this isn't a cost-bomb, an exfiltration path, or an injection vector. If your answer is "read-only creds and a cost cap," prove the creds are actually scoped and the cap actually exists — or concede it's a demo with real risk.
   → *Honesty wins live: "it's a demo on a contained dataset with read-only creds; I would not expose it on sensitive data without query cost limits, row caps, and an allowlist." Don't oversell safety you didn't verify.*
2. Gemini 2.5 here, Claude in your day job. Give me the real decision driver. "It's what I reached for" is a tell; a capability/cost/latency reason is a builder.

---

## 10. Skills section (where overclaiming hides)

1. You list both ChromaDB and FAISS. Two vector stores reads like accretion, not design. When do you reach for each, and why does the system need both?
2. "Multi-model routing across providers" — what's the routing policy: cost, latency, capability? Static rules or learned? And a prompt tuned for Claude underperforms on Gemini — how does your routing handle provider-specific prompt sensitivity, or does it silently degrade?
3. "Context engineering" is on your resume as a skill. Define it in one sentence such that it excludes prompt engineering. Then give the single highest-leverage context-engineering decision you've made and the one that backfired.
   → *If you can't name one that backfired, you haven't pushed the technique hard enough — have a real one.*

---

## The five questions to be unshakeable on (highest probability × highest damage)

1. **Devil's Advocate correlated-failure** (1.3) — your flagship architecture; if the critic can't catch model-induced errors, know exactly what it does and doesn't buy.
2. **Sole-reviewer / silent-wrong at 400+ tickets** (3.4) — the integrity question; have the real review rate and the honest risk.
3. **Probabilistic system mutating the semantic source of truth** (2.3) — name the human gate precisely, or concede it's not automated.
4. **Registry-as-injection-surface in KPI v2** (5.3) — validation + blast radius.
5. **Live demo query safety** (9.1) — you may be asked to run it; don't oversell safety.

For each: write your real answer, find the weak link, study it, re-answer. That loop is the prep.

---

*Questions are probes, not claims about what you built. Facts referenced come from `Kanu Madhok Resume - BCG X Senior AI Factory.md`. Pair with `Honest Framing` for how to answer when a probe lands on something untested.*
