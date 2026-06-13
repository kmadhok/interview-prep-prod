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

*Note: this parallel design is **retired** as of June — questions below are still fair game as history (esp. 2.4, which actually happened). The current sequential, registry-driven architecture has its own section: **2b**.*

1. You pay 2x compute on *every* query for a disagreement signal you act on only a minority of the time. Defend always-parallel over "run the agent, invoke the semantic layer only when agent confidence is low." What does always-on buy that conditional doesn't?
2. When the two disagree, an LLM adjudicates — but it has no ground truth and uses the same fallible reasoning that produced one of the two answers. Why is the adjudicator more than a third opinion with false authority? How is this better than escalating every disagreement to a human?
   → *Must confront that an LLM judge without ground truth is not an oracle. A defensible version: the judge isn't deciding truth, it's classifying the disagreement type (stale definition vs. hallucinated join vs. ambiguous question) and routing — that's tractable; deciding correctness isn't.*
3. The feedback loop lets a probabilistic system mutate the deterministic source of truth that hundreds of dashboards depend on. Walk me through, mechanically, why one confident-wrong agent answer cannot corrupt a definition downstream consumers trust. If your answer is "a human approves," then the loop isn't automated — so what is automated?
4. As the agent's coverage gets absorbed into the semantic layer, the disagreement signal shrinks and the orchestrator trends toward redundant. Is this system designed to obsolete itself? If yes, should it have been a one-time migration project rather than a standing system?
   → *A senior answer is comfortable saying "yes, partly — and that's fine; the standing value is drift detection as new tables/definitions appear." If you can't name the residual steady-state value, the design is suspect.*

---

## 2b. Registry Semantic Layer — current architecture (from the code walkthrough)

*Unlike the rest of this file, these come with draft answers — the architecture is fresh enough that the answers aren't drilled yet. Source: `Work Artifacts/customer-voice-semantic-layer-code-walkthrough.md`. Compress each to ≤90 sec spoken.*

**1. "Your registry IS the bottleneck. Every new question type needs a YAML edit and a human gate. You've rebuilt the BI backlog you set out to kill — just renamed 'definition inserts.' Why is this better?"**
→ *The trap is defending throughput. The answer is about what compounds.*
> "The ticket backlog scaled with every question; the definition backlog scales with new *concepts*. Once a definition lands, every future phrasing of it is self-serve forever — coverage compounds, tickets never did. And the gap flags rank which definitions to write next by real demand. The old backlog never told me what to build; this one does."

**2. "One LLM call returning one JSON blob — you've built a slot-filler. What class of questions can this never answer, and what happens when a user asks one?"**
→ *Own the closed world proudly; don't pretend it's general.*
> "It's deliberately a closed-world parser. It can't do multi-hop reasoning, novel metrics, or anything outside the feasibility archetype — counts, rates, lists, rankings over panelists. When a question doesn't fit, the contract says omit the predicate and flag the gap — never guess. That boundary is the product: a trusted answer inside the boundary beats a plausible answer everywhere. The expansion path is new archetypes through the same compiler pattern, each governed the same way."

**3. "A question is 90% in-registry, 10% out. The model omits the unknown predicate and you return a number for a silently *narrower* question. Isn't that worse than no answer?"**
→ *The hardest one in this section. A silently narrowed cohort looks exactly like a right answer.*
> "Yes — a silently narrowed answer is the most dangerous output this system can produce, which is why the gap flag exists. The honest part: today that flag is reliable at the log level; the answer-surface needs to show 'here's what I applied, here's what I dropped' so the user sees the narrowing, not just me. That's the next fix, and it's display work, not architecture work — the information is already in the typed intent."

**4. "The gate rejects 'mael' unless the LLM happens to fix the spelling. So correctness depends on the model's charity — you've pushed fuzziness upstream, not removed it."**
→ *Concede the premise, then land the asymmetry.*
> "Contained, not eliminated — and the asymmetry is the design. If the model fumbles, the worst case is a rejection: loud, visible, recoverable. It is never wrong SQL: silent, trusted, corrosive. Model failure can cost an answer; it can't cost a wrong answer. And every rejection is logged, so misspellings that recur become synonym candidates — the deterministic surface grows from real usage."

**5. "SQLite vocab snapshots go stale. A brand launches Monday, your snapshot is from last month, the gate rejects a perfectly valid question. Your governance is now lying to users."**
→ *Name the tiering principle; concede the manual part.*
> "Staleness is the price of having no live dependency in the gate — and it should be tiered by churn rate. UPCs churn fastest, so they already bypass snapshots for a live BigQuery check. Product hierarchy and brands belong on a scheduled refresh; demographics are near-static. Today the snapshot refresh is manual — the fix is boring automation, and the failure mode is at least the safe direction: a false rejection, not a false answer."

**6. "The UPC existence check only runs with --run or --dry-run. SQL-only mode happily compiles SQL for a fake UPC — the exact bogus zero you claim to prevent."**
→ *He's read the design carefully if he gets here. Reward it with precision.*
> "Right — the invariant is 'no *executed result* from an unvalidated UPC,' and every path that returns a number passes the checker, because checking requires a warehouse round-trip and SQL-only mode is offline by definition. The sharp edge: someone hand-running SQL-only output bypasses the protection. If that became a real usage pattern, the fix is making validation mandatory in any path that emits SQL, not just paths that execute it."

**7. "Your prompt example says 'male'→'M'; your registry says 'Male'. You shipped a contract that contradicts its own source of truth. What does that say about your testing?"**
→ *Same wart as the talk-track §5 answer — keep the two consistent.*
> "It says the prompt builder isn't 100% generated — one hand-written example drifted while everything generated from the registry stayed correct. No user-facing harm, because the gate trusts the registry, not the prompt — that's defense in depth doing its job. But the fix is real: generate the examples from the registry too, and a CI check that any literal value in prompt text validates against the registry. It's on the list."

**8. "You retired the reconciliation agent because grading was 'offline value.' So now nothing grades production answers at all. You went from double-checked to unchecked and call it progress."**
→ *Don't let "unchecked" stand. Then volunteer the gap before he finds it.*
> "Not unchecked — unscheduled. Everything needed to re-grade is persisted: question, raw model JSON, canonicalized intent, SQL, result. The grading loop moved from the hot path to the logs, where it costs nothing per-request and can run at any cadence. What I removed was 2x compute and latency, not scrutiny. The honest gap: the offline grader isn't built yet — today it's me on the logs. That's exactly what the golden intent set turns into."

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

## 11. Patrick-specific: the forward-deployed lens on the semantic layer

*Patrick founded BCG's Forward Deployment function. His frame isn't "is this architecture clever" — it's "does this survive contact with a client, without you." These map his confirmed theses (MCP governance, embed-where-users-work, build-break-rebuild, AiAssist redaction) onto your system. Draft answers included; compress to ≤90 sec.*

**P1. "You built this for one team, with you as the human gate. I drop you into a client and you leave in 12 weeks. Who's the gate when you're gone?"**
→ *The forward-deployed killer question. 'Train the client' is hand-waving unless you name the artifacts.*
> "The gate transfers because it's defined by artifacts, not by me: the registry, the gap log, and the approval workflow. The handover is the business owner of each metric approving definitions in their domain — which is already the scaling design at Walmart, not a pivot for the client. Plus a triage runbook — no-match means coverage gap, wrong-match means fix the definition — and the regression suite that runs on every definition change. The one thing I'd refuse to soften in handover is the abstain-over-guess contract. That's what makes the system safe to hand to a gatekeeper less paranoid than me."

**P2. "Day one at a client there's no registry, no Kanu who knows the tables. What's your week-one playbook to bootstrap a registry from nothing — and what do you deliberately leave out?"**
→ *Tests whether the Walmart build was a method or a one-off. The leave-out half is where senior shows.*
> "Mine the existing demand signal — tickets, dashboard usage, the analysts' query history. The top recurring questions define the first archetype, and I'd start with exactly one, narrow. The registry is a demand-ranked backlog where definitions are the features. What I'd leave out: anything two teams disagree about — a contested definition is a governance fight to surface to the client, not something to quietly encode — and the long tail, because every definition carries maintenance cost. Week one buys the boring, high-traffic 60%."

**P3. "Determinism-for-trust is nice, but my clients ask 'why did sales dip in the northeast?' Your system rejects that. You've built a trustworthy calculator when the client wants an analyst."**
→ *Don't defend the calculator as sufficient. Position it as the bottom of the stack.*
> "Right — and it's the bottom of the stack, not the whole stack. An exploratory agent on top decomposes the 'why' into hypotheses, and every quantitative claim it makes routes through the governed layer — that's the same shape as my analytics agent at Walmart. The trust rule is: anything that becomes a decision number is deterministic and traceable; the narrative around it can be probabilistic and labeled as such. What you can't do is let the analyst layer free-hand the numbers — that's how you get a confident story built on an invented figure."

**P4. "You call MCP the control boundary and the semantic layer governance. Which is it? Where does enforcement actually live — and what's enforced versus just logged?"**
→ *His own MCP-governance thesis, pointed at you. The 3.6 distinction (authorization vs observability), now two-layered. Be surgical.*
> "Two layers, different jobs. MCP constrains what the agent can *touch* — the tool and data surface is allowlisted; capabilities not exposed don't exist. The semantic layer constrains what it can *mean* — only governed definitions compile to SQL, so an illegal intent dies before SQL exists. Both of those are enforcement: can't, not shouldn't. What's logged rather than enforced: which questions get asked, what gets flagged as gaps. I think keeping that line crisp — can't-do versus can-see-later — is most of what 'governance' should mean for agent systems."

**P5. "You've rebuilt this twice in six weeks. Sounds like you shipped the wrong thing twice. Why is v3 right — and what signal triggers v4?"**
→ *His own build-break-rebuild filter, weaponized. Naming your next rebuild trigger is the whole answer.*
> "Each rebuild answered a signal, not a whim. V1 to v2: the trust signal — same question, different numbers, business users noticed. V2 to v3: the cost signal — 2x compute in the hot path for value that was really offline. And I can tell you the v4 trigger now: when the gap-flag rate stops falling, registry coverage has plateaued and the bottleneck moves to definition authoring — at which point the investment shifts to tooling that lets business owners write and approve definitions themselves. Knowing your next rebuild trigger before you hit it is the difference between iterating and thrashing."

**P6. "Your prompt ships registry vocabulary to the model — allowed values, income brackets, metric names. At a client, the vocabulary itself can be sensitive: deal terms, client metric names. What reaches the model?"**
→ *Bridge to his AiAssist redaction product — he built exactly this concern into an app. Land the 'zero rows' line.*
> "The model sees the question and registry *metadata* — field names and allowed values — never row data. No query results flow through the LLM; it touches zero rows by construction. Where the vocabulary itself is sensitive, the UPC pattern generalizes: keep it out of the prompt entirely, have the model extract the reference verbatim, resolve it deterministically behind the boundary. The same move that handles high cardinality handles confidentiality — and it's the same instinct as redacting before the model call rather than trusting it after."

---

## The five questions to be unshakeable on (highest probability × highest damage)

1. **Devil's Advocate correlated-failure** (1.3) — your flagship architecture; if the critic can't catch model-induced errors, know exactly what it does and doesn't buy.
2. **Sole-reviewer / silent-wrong at 400+ tickets** (3.4) — the integrity question; have the real review rate and the honest risk.
3. **Probabilistic system mutating the semantic source of truth** (2.3) — name the human gate precisely, or concede it's not automated.
4. **Registry-as-injection-surface in KPI v2** (5.3) — validation + blast radius.
5. **Live demo query safety** (9.1) — you may be asked to run it; don't oversell safety.

**Two additions now that the semantic layer has moved (6/10):**

6. **Silent narrowing** (2b.3) — a number for a quietly narrower question is the system's worst failure mode; own that the user-facing flag is display work still to do.
7. **Gate-when-you're-gone** (P1) — the forward-deployed question; the artifacts-not-person answer must be cold.

For each: write your real answer, find the weak link, study it, re-answer. That loop is the prep.

---

*Questions are probes, not claims about what you built. Facts referenced come from `Kanu Madhok Resume - BCG X Senior AI Factory.md`. Pair with `Honest Framing` for how to answer when a probe lands on something untested.*
