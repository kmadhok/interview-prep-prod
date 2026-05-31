	# Interview Answers — Walmart Agent Builder

Polished drafts and cheat-sheet beats for the questions most likely to come up. Each entry has:
- **Beats** — the sequence you deliver from memory (your cue card)
- **Draft** — the full spoken version, for practice reps
- **Hooks** — the specific lines you want the interviewer to pull on next

**How to use:**
1. Practice the full draft out loud until the beat order is automatic
2. In the interview, glance only at the beats — the draft is for reps, not for reading
3. Hit the hook line clearly, then stop. The silence cues the follow-up you actually want.

---

# Part 1 — The Opener

## 1. Tell me about yourself

**Beats**
- *Present.* Sr Data Analyst, Walmart Data Ventures — Customer Perception. Point of contact for ~30 people, business + technical. Analytics, stewardship, readiness.
- *The shift.* Intake volume was more than one person could keep up with. Started building — probabilistic + deterministic systems.
- *What grew out of it.* Power BI dashboards → Python pipelines → **Jira agent (400+ drafted responses; nobody realized they weren't all mine)** → autonomous data analyst → self-growing semantic layer.
- *Recognition.* Making a Difference Award earlier this year for 2025 work.
- *Why Agent Builder.* Scoped to one team today. Role = same work at Walmart scale. *"That's the version of this work I want to be doing."*

**Draft**

> Today I'm a Senior Data Analyst at Walmart Data Ventures supporting Customer Perception — I'm the point of contact for about 30 people across business and technical teams who come to me with analytics, stewardship, and readiness questions. Pretty quickly I realized the volume of that intake wasn't something one person could keep up with, so I started building — both probabilistic and deterministic systems — to absorb it. That's grown into Power BI dashboards, Python pipelines, a Jira resolution agent that's drafted 400+ stakeholder responses without anyone realizing the answers aren't all coming from me, an autonomous data analyst, and a self-growing semantic layer that refines its own definitions over time. Earlier this year that work earned me a Making a Difference Award for what I shipped in 2025. What pulls me toward Agent Builder is that I've been doing this scoped to one team — the role makes it possible to do it at the scale Walmart actually operates at, and that's the version of this work I want to be doing.

**Hooks planted (ranked by likelihood they get pulled)**
1. The Jira agent — strongest line, most likely follow-up
2. The self-growing semantic layer
3. "Scoped to one team" → "you're already doing this, why move?"
4. The autonomous data analyst

---

# Part 2 — Direct follow-ups from TMAY (to draft)

> These are the questions your opener tees up. Highest priority to draft, because the interviewer will reach for them first.

## 2. Tell me more about the Jira agent — how did it work?

**Beats**
- *Before.* I was the only person handling Customer Perception's Jira intake. Data readiness questions — product hierarchies by supplier, UPC mappings, which panel studies bought a given UPC in a given timeframe, which of those panelists took a specific survey, response rates. 30 min to 1 hour per ticket; complex ones ate a full day.
- *The bottleneck.* I was the limiter on everything else I wanted to build. Same shapes of questions kept recurring.
- *The architecture.* 6-gate pipeline: **triage → context (MCP, FAISS+BM25 over 11k-ticket archive) → plan → draft → execute (BigQuery) → validate.** 13 tools across querying, docs, and lookups.
- *The deliberate HITL.* Agent drafts the response; I review and post. I made that call because the cost of a wrong answer to a stakeholder is much higher than the cost of my two-minute review. Stakeholders never see the agent — they see a normal Jira reply from me.
- *Outcome.* Complex tickets went from a full day to 10–15 minutes. **400+ tickets handled since January 2025.**
- *The real win = leverage.* The intake bottleneck was what had been keeping me from building anything else. Once it was off my plate, I built the autonomous data analyst, the KPI monitor, and the self-growing semantic layer on top of the same context infrastructure the Jira agent already used. *"The Jira agent ended up being the platform that funded the rest of the portfolio."*

**Draft**

> Customer Perception runs on Jira intake — stakeholders submit tickets when they need data readiness or analysis work. The questions are pretty varied: what's the product hierarchy for a specific supplier, what UPCs map to which products, which panel studies bought a given UPC in a given timeframe, which of those panelists took a specific survey, what was the response rate. I was the only one answering them, and before the agent, a typical ticket took me 30 minutes to an hour, with complex ones eating most of a day. I've handled over 400 of these since January 2025, so it was the single biggest drain on my time and the bottleneck on everything else I wanted to build.
>
> The agent works as a 6-gate pipeline: first it triages whether the ticket is solvable end-to-end, then it pulls context through an MCP layer — including retrieval over our 11,000-ticket historical archive with FAISS plus BM25 — then it plans the response, drafts the answer, executes the underlying queries against BigQuery, and validates the output against the source before it gets handed back to me. There are 13 tools in total across querying, docs, and lookups.
>
> The detail that matters most: I deliberately kept myself as the human in the loop. The agent prepares the response, I review and post. I made that call because the cost of a wrong answer going to a stakeholder is much higher than the cost of my two-minute review. Stakeholders never see the agent — they see a normal Jira reply from me. So from their side, nothing changed except that replies started showing up faster.
>
> But the real outcome wasn't the time on any single ticket, though complex ones did go from a full day to 10–15 minutes. The bigger win was leverage. The intake bottleneck was what had been keeping me from building anything else. Once it was off my plate, I built the autonomous data analyst, the KPI monitor, and the self-growing semantic layer on top of the same context infrastructure the Jira agent already used. So the Jira agent ended up being the platform that funded the rest of the portfolio.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"I deliberately kept myself as the human in the loop"* — opens the HITL / reliability follow-up. This is a principal-level signal and you have a strong defense.
2. *"The Jira agent ended up being the platform that funded the rest of the portfolio"* — opens the leverage / platform-thinking question, which maps directly to the Agent Builder role.
3. *"The same context infrastructure"* — opens the technical depth question that ties back to Q15's context layer + MCP story.

### Anticipated follow-ups

**"Why didn't you let it auto-post?"**
Cost of a wrong response to a stakeholder is much higher than the cost of two minutes of my review. The trust ramp matters — these are people I work with every week. I'd rather take the small overhead and keep the trust intact. If I were operating at platform scale where I couldn't review everything, I'd add explicit confidence thresholds and auto-post only on high-confidence cases.

**"How do you know the drafts are good?"**
Two complementary validation paths. First, structural SQL correctness — the agent verifies its generated SQL against the context layer, which includes a knowledge graph of join paths, semantic definitions, and domain definitions. So joins, columns, and the query shape all get checked against what the schema and the graph say is valid. Second, intent matching — the agent compares the proposed answer against how similar questions were answered in the historical archive. If the shape of the answer is wildly different from precedent, that's a flag. The triage gate at the front also serves as the first filter — it identifies whether the intent of the question is something the agent can answer end-to-end before any drafting happens.

**"What were the 13 tools?"**
Rough taxonomy: doc / RAG retrieval (`ask_docs`, `ask_rag`), BigQuery querying (`query_bigquery`, schema lookup), and knowledge-graph navigation (`get_join_path`). Full breakdown of all 13 is *[TO LOOK UP on work laptop before the interview]*.

**"Was there a moment you knew stakeholders couldn't tell?"**
Honest answer: there was no single aha moment. Nobody ever asked. They just kept submitting tickets and getting faster, well-supported responses. I'd treated the Jira agent as plumbing — I thought the visible-impact projects would land harder, the ones stakeholders could touch directly, like the CLI for the semantic layer or the Slack alerts from the KPI monitor. So I wasn't promoting it. The "more interest than I expected" signal came later, when people noticed I'd been quietly absorbing 400+ tickets while shipping three other systems in parallel. The lesson for me: I'd underestimated what the panel might find load-bearing. Quiet automation can be more interesting than visible automation, because it shows up as capacity, not as a product.

**"Why retrieval over 11k tickets — what's that for?"**
Most stakeholder questions aren't novel — they're variants of questions someone else asked 3 months ago. The historical archive lets the agent ground its draft in *how this team has answered this kind of question before*, not just what the schema says.

### Short version (if cut for time, ~60 seconds)

Hit only: business cost (400+ tickets, 30 min–1 hr each) → 6-gate architecture (one sentence) → deliberate HITL → leverage win (funded the rest of the portfolio).

## 3. What's the self-growing semantic layer?

> Note: this is what the resume calls the **hybrid orchestrator** — same system, two names. "Self-growing semantic layer" describes what it does over time; "hybrid orchestrator" is the architectural shape. Drop the bridge in the first sentence so the panelist doesn't think these are two separate projects.

**Beats**
- *The problem.* Two standard approaches to text-to-data, each broken in a different way. **Semantic layer** (Cube.js, dbt MetricFlow): deterministic and auditable, but brittle — every metric has to be hand-defined upfront. **Context-engineered agent**: flexible, handles novel questions, but can hallucinate joins or pick the wrong metric. Pick one and you live with its failure mode.
- *What's already in production.* Both — separately. The **Cube.js semantic-layer agent** I built end-to-end (definitions, modeling, the agent itself); product team scoped the first stakeholder questions to onboard. The **context-engineered agent** sitting on the V2 context layer + MCP. Both deployed and actively used.
- *The insight.* They're not competing — they're complementary. Each fails where the other succeeds. Run both in parallel and you can use the disagreement as signal.
- *The hybrid orchestrator.* Same user question fans out to both backends. A reconciling agent receives both outputs. Agree → ship. Disagree → the interesting case.
- *Disagreement handling.* **Semantic layer wins ties** — it's the source of truth between calls, the auditable path. *But* the disagreement still gets flagged for **product-team review**. If the agent path surfaced a definition that wasn't yet codified, product ratifies it and that becomes a new semantic-layer entry.
- *Why self-growing.* Captured + ratified disagreements = labeled training data for new semantic-layer entries. **Agreement rate** is the headline metric — trending up means the flywheel is working.
- *Status.* Two backends in production. **Orchestrator built end-to-end, validated against a 20-question golden set, production rollout this week** — DS handles the deploy (service account, by design, so users skip BigQuery auth). Result: **context-engineered 20/20, semantic layer 10/20** (only the existing definitions); 10 disagreements → **20 candidate definitions** for the semantic layer. Lead with proof points, not caveats.
- *Ownership shape.* I built the whole stack end-to-end — semantic layer, context-engineered agent, hybrid orchestrator, eval harness. **Product** owns scope + disagreement review. **DS** owns the production service account the orchestrator queries through (deliberate UX choice — end users don't need their own BigQuery auth), which is why DS handles the deploy step. Build is mine end-to-end.

**Draft**

> So this is what the resume calls the hybrid orchestrator — same system. "Self-growing semantic layer" is the way I describe what it does over time; "hybrid orchestrator" is the architectural shape.
>
> Most enterprise text-to-data setups pick one of two approaches and live with the tradeoffs. The semantic-layer approach — Cube.js, dbt's semantic layer, similar tools — is deterministic and auditable, but it's brittle: every metric has to be hand-defined upfront, and it can only answer questions that map to existing definitions. The context-engineered approach is the opposite — an agent sitting on the context layer plus MCP I described earlier — flexible, handles novel questions, but it can hallucinate joins or pick the wrong metric for what the user actually meant. Each fails in a different direction.
>
> I built both — separately — and they're both deployed and serving real traffic today. The Cube.js semantic-layer agent I built end-to-end: the definitions, the modeling decisions, the YAML, and the agent that sits on top of it. Product team scoped which stakeholder questions to onboard first. The context-engineered agent is the one on the V2 context layer I described earlier.
>
> The hybrid orchestrator was the next step — realizing those two backends aren't competing, they're complementary. Each fails where the other succeeds. So I built a reconciling agent that runs both paths in parallel on the same user question. When they agree, that's the answer. When they disagree, the semantic layer wins — it's the source of truth between calls, the auditable path — but the disagreement still gets flagged for product-team review. If the agent path surfaced a real definition that wasn't yet codified, product ratifies it and that becomes a new semantic-layer entry. The next time the same question comes in, both paths agree on the first pass.
>
> The two backends are in production. The hybrid orchestrator on top of them is built end-to-end and validated — production rollout is this week. The way I validated it: I have a golden set of 20 question/answer pairs grounded in the context layer — the same eval harness I use across all the agents on top of that context layer. The result: the context-engineered agent agreed on all 20, the semantic layer agreed on the 10 it already had definitions for, and from those 10 disagreements the orchestrator surfaced 20 candidate definitions to add to the semantic layer. So the growth loop is already proving out before production even ships. The deploy itself goes through the DS team because the orchestrator queries BigQuery via a service account they own — that's a deliberate UX choice so end users don't need their own BigQuery auth.
>
> The reason I call it self-growing is the design of that feedback loop. Disagreements aren't bugs — they're labeled examples of "the agent figured out a definition that wasn't yet codified." Captured and ratified, they become net-new semantic-layer entries. Agreement rate is the headline metric — trending up means the flywheel is working. Over time the semantic layer accumulates definitions the system has earned, without anyone hand-writing more schema.
>
> Last piece on ownership: I built the whole stack end-to-end — semantic layer, context-engineered agent, orchestrator, eval harness. Product team scopes which questions get onboarded and reviews flagged disagreements. The DS team owns the production service account the orchestrator queries through — that's why they handle the actual deploy step — but the architecture and the build are mine end-to-end.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Disagreements aren't bugs — they're labeled training data for the semantic layer"* — strongest line, opens the architecture / flywheel question.
2. *"Surfaced 20 candidate definitions the semantic layer was missing, just from one run against the golden set"* — concrete proof point, opens the eval-methodology / golden-set follow-up. You **want** this one pulled — landing "reusable eval harness across every agent on the context layer" is a top Principal-level platform-thinking signal.
3. *"I built the whole stack end-to-end — semantic layer, context-engineered agent, orchestrator, eval harness"* — opens the ownership / scope question. **The cleanest end-to-end signal you can land.** Maps directly to Agent Builder.
4. *"Semantic layer wins ties, but the disagreement still gets flagged for product-team review"* — opens the reliability-vs-flexibility tradeoff question.
5. *"DS handles the deploy because the service account is theirs — that's a deliberate UX choice"* — opens the deployment / cross-functional follow-up. Frames the DS dependency as a design decision (UX), not a permissions limitation.

### Anticipated follow-ups

**"How does the orchestrator actually resolve a disagreement?"**
Semantic layer always wins as the live answer — it's the auditable path, it's the source of truth between calls, and stakeholders need that consistency. So the user gets the semantic-layer answer immediately. *But* the disagreement isn't dropped. It gets flagged into a queue for product-team review. Product looks at what the agent path proposed, decides whether it's a real missing definition or a hallucination, and if it's real, ratifies it. Ratified disagreements become new semantic-layer entries. The growth loop only fires after that human ratification — never from the agent's self-judgment.

**"Why product team for review instead of you?"**
Product owns *what the metrics mean to the business*, which is exactly what's being decided when a disagreement comes up — "is this a real new metric the team needs, or noise?" I built the semantic layer and the orchestrator, so technically I could just add new entries on my own — but that would put me in the position of unilaterally deciding which business metrics exist, which isn't my call. Product is the right gate for that judgment. Once they ratify, I add the entry and the orchestrator picks it up on the next run.

**"What stops bad definitions from being persisted back?"**
The product-team review gate. The agent path never gets to ratify itself — it only proposes. Without that gate, a confidently-wrong agent answer would drift the semantic layer over time. With the gate, the semantic layer only grows from earned consensus.

**"Why not just use the context-engineered agent everywhere? It's more flexible."**
Fair question — on the golden set the context-engineered agent went 20-for-20, so technically it could carry the load. Two reasons to keep the semantic layer in the mix anyway. First, auditability and consistency: stakeholders need to trust that "revenue" means the same thing on Monday as it does Friday — the semantic layer is the source of truth that survives between calls, a per-call agent judgment doesn't give you that. Second, the 20-question golden set is a known-good benchmark; production traffic will surface edge cases where the agent path is overconfident or wrong, and you want a deterministic rail running alongside as the fallback-to-trust. The deterministic path is the rail; the agent path is the explorer. Hybrid lets us have both: deterministic answers where definitions exist, agent path where they don't, and the set of "where definitions exist" grows on its own through the review loop.

**"How do you measure whether the growth loop is actually working?"**
Agreement rate is the headline. On the golden set, the context-engineered agent went 20-for-20 against the known-correct answers; the semantic layer agreed on 10 — exactly the questions it already had definitions for. So at baseline: agent recall ~100%, semantic-layer recall ~50%, and 10 disagreements generated 20 candidate definitions for the semantic layer to absorb. The metric to watch over time is the *between-backends* agreement rate — as ratified candidates land in the semantic layer, that number trends up, which is the flywheel working. Secondary metrics: net-new definitions ratified per week, time-to-resolution on flagged disagreements, downstream accuracy on recurring questions.

**"Is the orchestrator in production?" / "What's the deployment plan?" / "Why isn't it shipped yet?"**
Honest framing, no apology: the two backends are in production today; the orchestrator is built end-to-end and validated, with production rollout this week. The deploy goes through the DS team because the orchestrator queries BigQuery via a service account they own — that's a deliberate UX choice so end users don't need their own BigQuery auth. So DS handles the deploy step; I built the full stack. Validation methodology: a golden set of question/answer pairs grounded in the context layer, reusable across every agent I've shipped on that layer. From one run, the orchestrator surfaced **20 candidate definitions** the semantic layer was missing — so the growth loop is proving out before production. The remaining ops items are pipeline plumbing on the production surface and standing up the product-team review workflow (queue, SLAs, handoff into me for the actual semantic-layer entry).

**"What's the golden set?"**
A curated set of question/answer pairs grounded in the context layer — questions stakeholders actually ask, paired with the answers I know are right. I built it once against the context layer itself, so the same eval harness is reusable across every agent I've shipped on top of that layer: the Jira agent, the autonomous data analyst, the KPI monitor, and now the hybrid orchestrator. Two practical wins from that: I can regression-test any of those agents with one set of fixtures, and adding a new question/answer pair counts as coverage for all of them at once. It's the same lesson I took from the V1 → V2 arc — the reusable asset is the substrate (context layer + eval harness), not the agent on top.

**"How is this different from just running two agents and taking a vote?"**
Two things. First, the backends aren't both agents — one is a deterministic semantic-layer query, the other is an agent. The asymmetry is the point: when they disagree, you actually know *which one is the more trustworthy default* (the deterministic one). Second, the disagreement *produces an artifact* — a candidate new definition. A vote just picks an answer for one call; the growth loop changes the system so the next call doesn't need the agent path at all.

**"Could this approach scale to Walmart-wide?"**
That's the version of this I want to be building. At my current scope, the semantic layer is one team's metrics. The architecture doesn't change at enterprise scale — what changes is the governance around the review gate (who's authorized to ratify new definitions in which domain) and the partitioning of the semantic layer by ownership boundary. The growth loop holds. Honestly, the bigger the scope, the more valuable the loop becomes, because manually maintaining a semantic layer across the enterprise surface is exactly what doesn't scale.

**"What was the DS team's role specifically?"**
Narrow but specific: DS owns the production service account the orchestrator uses to query BigQuery. That's a deliberate design choice — end users shouldn't need their own BigQuery auth to use the system. So DS handles the actual production deploy (since the service account is theirs) and any infra changes that touch that account. Everything else — the semantic layer itself, the modeling, the context-engineered agent, the orchestrator, the eval harness — I built. Product scopes which questions to onboard and reviews flagged disagreements; once a disagreement gets ratified, I add the new entry to the semantic layer and the orchestrator picks it up on the next run.

### Numbers — what you have, what's still TBD
- ✅ **Golden set: 20 questions.** Context-engineered agent: **20/20** (100%). Semantic layer: **10/20** (50% — exactly the existing definitions). 10 disagreements → **20 candidate definitions** for the semantic layer (~2 per disagreement).
- ✅ **Production rollout: this week**, DS handling the deploy via service account
- ✅ **Golden set as reusable eval harness** across all agents on the context layer — Jira agent, autonomous data analyst, KPI monitor, hybrid orchestrator
- 📌 **Adoption of the two deployed backends** — who uses them, queries per week, what they've replaced. Strengthens the "real systems, not toy projects" framing if pulled.

## 4. What's the autonomous data analyst?

> Note: this is a TMAY-planted hook — your opener names it explicitly, so the panel may grab it directly. The strongest framing is *sibling to the Jira agent on the same substrate, opposite HITL posture*. That contrast lets you teach the panel something about when each pattern applies — a Principal-level signal — instead of just describing another system.

**Beats**
- *Where it sits in the stack.* Sibling to the Jira agent on the same V2 context layer + MCP substrate. Different surface: instead of routing through me on a Jira ticket, business users query the data themselves — delivered as a skill inside YB.
- *The business problem.* Even after the Jira agent absorbed the response work, I was still the rate-limiter on novel exploration — business users had to come to me to get started, even if the agent did the drafting. This was the next leverage step: take me out of the loop on the read path entirely.
- *Scope.* 6 BigQuery tables — the core Customer Perception data surface. Deliberate MVP boundary; the value of a narrow scope is the validation surface stays small enough to actually verify. *[TO CONFIRM — which 6, and the criterion for expanding.]*
- *The architecture.* Sub-agent orchestration with context isolation. Planner agent decomposes the question; sub-agents handle distinct steps (table selection → SQL generation → validation → synthesis); each sub-agent gets only the context it needs.
- *Why "autonomous."* No human in the loop on the read path. Validation happens inside the agent loop — schema correctness against the context layer, intent matching against historical question patterns — then the answer ships directly to the user. *Contrast with Jira agent, where I'm the deliberate HITL.*
- *Approval signal.* Director + product leadership approved it. *[TO FILL IN — what was the gate, what did they need to see, what pushback did you handle?]*
- *Adoption proof.* The only AI skill currently in active use by business teams across Data Ventures. *[TO FILL IN — user count / query volume / what it replaced.]*

**Draft**

> The autonomous data analyst is the sibling to the Jira agent, sitting on the same V2 context layer and MCP I described earlier. Different surface, though — instead of business users filing a Jira ticket that I'd answer, they can ask the agent directly and get the answer back themselves. It's delivered as a skill inside YB, our internal Claude Code equivalent, so it ships into the workflow people already use.
>
> The business problem was that even after the Jira agent absorbed the response work, I was still the rate-limiter on anyone doing novel exploration — business users had to come to me to get started, even if the agent did the drafting. So this was the next leverage step: take me out of the loop on the read path entirely.
>
> Scoped to 6 BigQuery tables — the core Customer Perception data surface. That's a deliberate MVP boundary. The value of keeping the scope narrow is that the validation surface stays small enough to actually verify the agent end-to-end. The criterion for expanding is the same as for everything else on the substrate: a new table gets added once it's documented in the context layer with the same validation guarantees the original 6 have.
>
> Architecturally, it's sub-agent orchestration with context isolation. A planner agent decomposes the user's question; sub-agents handle distinct steps — table selection, SQL generation, query validation, response synthesis. Each sub-agent gets only the context it needs to do its piece, which has two practical wins. First, token cost: nobody's holding 6 tables' worth of schema in context if they only need 2 for this question. Second, isolation in the reasoning sense: if the SQL-generation sub-agent makes a wrong assumption about a column, the validation sub-agent doesn't inherit that assumption — it's reading the query and the source independently. Same logic as code review: the reviewer should be checking against the requirement, not co-anchoring with the author.
>
> The "autonomous" part is the contrast with the Jira agent. On the Jira agent I deliberately kept myself as the human in the loop because the cost of a wrong stakeholder response was high. The autonomous data analyst is different — it ships answers directly to users, with validation happening inside the agent loop: schema correctness checked against the context layer, intent matched against historical question patterns from the same retrieval substrate the Jira agent uses. The HITL came out because the use case is different — users are running exploratory queries on their own data, the blast radius of a wrong answer is their own next decision, not a stakeholder communication.
>
> On the production side: it's been approved by my Director and product leadership and is the only AI skill currently in active use by business teams across Data Ventures. *[TO FILL IN — concrete adoption numbers: user count, queries per week, what kinds of questions they're running, what they would have had to do before.]*

**Hooks planted (ranked by likelihood they get pulled)**
1. *"The autonomous data analyst is the sibling to the Jira agent on the same substrate"* — opens the platform-thinking question. Bridges to Q5/Q6 territory if not already covered. **Strongest line.**
2. *"The HITL came out because the use case is different"* — opens the reliability / when-to-trust-an-agent question. **Principal-level signal** — the panelist is listening for whether you can articulate *when each pattern applies*, not just that you've used both.
3. *"Sub-agent orchestration with context isolation"* — opens the architecture deep-dive. Engineering panelists will pull this.
4. *"The only AI skill currently in active use by business teams in Data Ventures"* — opens the adoption / why-this-and-not-others question. Strong differentiation signal.

### Anticipated follow-ups

**"How is this different from the Jira agent?"**
Different surface, different HITL posture, different user. Jira agent serves stakeholder requests that route through me; I'm the human in the loop because the response is going to a person I work with and the cost of getting it wrong is high. The autonomous data analyst serves direct user exploration; the user is the one running the query, the blast radius of a wrong answer is small — their own next decision — so the HITL comes out and validation moves inside the agent loop. Same substrate underneath — same context layer, same MCP, same eval harness. Different agent for a different cost profile.

**"What does the sub-agent orchestration actually look like?"**
A planner agent reads the user question and decomposes it into a plan. Then a set of sub-agents execute the plan steps with isolated context. Roughly: table selection (which of the 6 tables matter for this question), SQL generation (write the query, only sees the relevant schema), validation (check the query against the context layer's join paths and semantic definitions), synthesis (turn the result into a natural-language answer). Each sub-agent gets only the context it needs. The planner sees the user question and the available sub-agents; the SQL generator sees the schema and the planner's intent; the validator sees the SQL and the source; the synthesizer sees the result. Nobody sees everything.

**"Why context isolation? What does that buy you?"**
Two things. Token cost — nobody's holding 6 tables' worth of schema in context if they only need 2 for this question, which keeps per-query cost low and latency reasonable. And isolation in the reasoning sense — if the SQL-generation sub-agent makes a wrong assumption about a column, the validation sub-agent doesn't inherit it, because it's reading the query and the source independently. Same logic as code review: the reviewer should be checking the code against the requirement, not co-anchoring with the author.

**"How do you validate the answers without a human in the loop?"**
Two layers, both running inside the agent. First, structural SQL correctness — the validation sub-agent checks the generated SQL against the context layer, which includes the join paths, semantic definitions, and domain rules for those 6 tables. Joins, column types, query shape all get checked against what the schema says is valid. Second, intent matching — the agent compares the proposed answer against how similar questions were answered in the historical archive, the same retrieval substrate the Jira agent uses. If the shape of the answer is wildly off-pattern from precedent, that's a flag and the agent surfaces uncertainty back to the user rather than presenting a confident wrong answer.

**"What kinds of questions can it handle?"**
*[TO FILL IN — pin down 3-4 concrete examples. Strongest version shows the range: a simple aggregation, a join-heavy question, an exploratory "what's driving X" question, and something the agent appropriately declines.]*

**"What kinds of questions can it NOT handle?"**
*[TO FILL IN — be honest. Likely: questions that need joining to tables outside the 6, questions requiring stat methodology beyond what's encoded in the context layer, questions where the answer requires business context only a human has. Naming the boundaries is a maturity signal — it shows you've thought about failure modes, not just happy paths.]*

**"Why only 6 tables?"**
Deliberate MVP scope. The validation surface needs to stay small enough to actually verify; 6 tables was the core Customer Perception data surface. The criterion for expanding is the same as for any agent on the substrate — a new table gets added when it's documented in the context layer with the same validation guarantees the original 6 have. The constraint forces the work to be platform-shaped rather than ad-hoc.

**"What was the approval process like?"**
*[TO FILL IN — Director + product leadership approval. What did they need to see (eval results? demo? security review?), what was the gate, what pushback did you handle, what trade-offs did you make to get to yes?]*

**"What's the adoption story?"**
*[TO FILL IN — concrete numbers. "The only AI skill in active use by business teams in DV" is the headline; the proof points are user count, query volume, and what specifically got replaced — Jira tickets, hand-rolled queries, ad-hoc Slack requests, dashboard waits. The contrast with the pre-agent workflow is the impact.]*

**"How would this work at Walmart scale?"**
The architecture is the part that scales — sub-agent orchestration with isolated context is the right shape for an enterprise data surface, because the alternative (one monolithic agent holding the whole schema) doesn't scale at all. What changes at scale is the validation substrate: the context layer needs to be built per domain, and the question of who owns each domain's context becomes a governance question. The pattern transfers; the governance is the new work.

**"How does this relate to the hybrid orchestrator?"**
Different agent, same substrate, complementary purpose. The autonomous data analyst answers questions where the user already knows what they want — "give me Q3 sales by region for category X." The hybrid orchestrator answers questions where there's metric ambiguity — "what's our revenue this quarter" where "revenue" could mean three different things depending on whether you're product, finance, or marketing. Both run on the same context layer. The autonomous data analyst is the read path for exploratory work; the hybrid orchestrator is the read path for metric-defined work.

### Short version (if cut for time, ~60 sec)

Sibling to the Jira agent on the same V2 context layer → different surface (delivered as a YB skill, users query directly instead of through Jira) → sub-agent orchestration with context isolation (planner + table-selection + SQL-gen + validator + synthesizer, each gets only the context it needs) → autonomous because validation happens inside the loop (schema correctness + intent matching against historical precedent) → HITL came out because the use case is different (user's own exploration, small blast radius) → only AI skill in active use by business teams in DV.

### Numbers / proof points to nail before the interview
- 📌 **Active users / queries per week** — the "only AI skill in active use" framing needs a number behind it. Strongest single thing you can add.
- 📌 **3-4 concrete example questions** — for the "what can it do" follow-up.
- 📌 **The 6 tables** — confirm which 6 and the criterion for them.
- 📌 **The Director + product leadership approval moment** — what they needed to see, the date / gate / signal, what pushback.
- 📌 **What it replaced** — Jira tickets, hand-rolled queries, ad-hoc Slack requests, dashboard waits. The contrast is the impact.

## 5. You're already doing agent work at Walmart — why move?

> Note: this is the question your TMAY explicitly tees up ("scoped to one team today"). Land it confidently — if this reads as defensive or evasive, the rest of the interview gets read through that lens. **Lead with the pull, not the push.** Stay positive about Data Ventures — panelists likely know your current team.

**Beats**
- *Lead with the pull.* Agent Builder is the platform shape I've been reaching for inside Data Ventures. Every system I've shipped in the last 18 months has the same architecture — thin agent on a reusable substrate. Pattern works. But the substrate I built serves one team. The leverage version is a framework other people ship on top of, at enterprise scope.
- *Why this role specifically.* The JD reads like the work I've been doing already — biz/tech generalist, owns end-to-end, biased for action, first-principles thinking. Not a stretch — the version of my current work where the surface area matches the solution shape.
- *Why now.* What I shipped in 2025 — V1→V2, the Jira agent, the autonomous data analyst, the hybrid orchestrator — is the proof I can operate at platform shape. Making a Difference Award was the inflection point.
- *Respect piece.* Not running away from DV. DV is where I figured the platform pattern out — they gave me the runway to fail fast on V1, ship V2, and prove the substrate works across multiple agents. The move is to do that work at the scope it was sized for.

**Draft**

> The honest answer is what the role is, not what I'm leaving. Agent Builder is the platform shape I've been reaching for inside Data Ventures already. Every system I've shipped over the last 18 months has the same architecture — a thin agent on a reusable substrate, where the substrate is the asset and each new agent is just the next thin thing built on top. That pattern works. But the substrate I built at Data Ventures serves one team's surface area. The leverage version is a framework that other people ship on top of, at enterprise scope. That's Agent Builder.
>
> When I read the job description, it reads like the work I've been doing already — biz/tech generalist, owns problems end-to-end, biased for action, first-principles thinking. That's how I've been operating, just at smaller scope. So this isn't a stretch role for me — it's the version of my current work where the surface area matches the solution shape.
>
> On timing — what I shipped in 2025 is what gives me confidence to make this move now rather than speculate about it. V1 to V2 was the lesson, the Jira agent and the autonomous data analyst were the validation that the platform pattern repeats, and the hybrid orchestrator was proof I can build the platform itself, not just agents on top of it. The Making a Difference Award earlier this year was a useful signal — what I'd been doing got recognized as worth doing. The next step is to do it where the scope of the problem matches the shape of the solution.
>
> And to be clear about Data Ventures: I'm not running away. DV is where I figured this whole pattern out — they gave me the runway to fail fast on V1, ship V2, and prove the substrate works across multiple agents. I want to take what I learned there and apply it at the scope it was always headed toward.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Thin agent on a reusable substrate, where the substrate is the asset"* — opens the platform-thinking question. Maps directly to Agent Builder's "framework other teams build on" framing. **Strongest line.**
2. *"This isn't a stretch role for me"* — confident, opens the why-are-you-ready / Senior-DA-to-Principal question (Q6 territory). Pre-empts the title objection.
3. *"DV is where I figured this pattern out — they gave me the runway"* — opens the "why not stay and grow DV into the platform team?" question. You **want** this one pulled — clean answer below.
4. *"The scope of the problem matches the shape of the solution"* — quotable closer; opens the Walmart-scale-ambition question.

### Anticipated follow-ups

**"Why not stay and grow Data Ventures into the platform team?"**
Different mandate. DV's mandate is customer perception analytics — the platform work I've done is *in service of* that mandate, not *as* that mandate. Building the framework as the primary product is a different team with a different scope. If I stayed, I'd keep building point solutions on the substrate I already have, but the substrate itself wouldn't grow beyond one team's surface area. That's not a complaint about DV — it's just a function of what the team exists to do.

**"Have you talked to your manager about this?"**
*[TO FIRM UP — the real answer here matters and it's only one you can write. Three honest framings depending on situation:*
- *If yes: "Yes — they're aware I'm exploring this and supportive of me having the conversation."*
- *If no: "Not yet — I wanted to have the conversation grounded in real interest from a real team rather than as a hypothetical. Once this is more concrete, that's the right next conversation."*
- *If complicated: think about what you actually want to land — usually some version of "I'm being thoughtful about how I handle the internal communication."]*

**"What if you don't get this role?"**
Honest: keep building the platform pattern at DV's scope, keep watching for the right next-scope role. The work doesn't disappear, and the lessons from 2025 still apply. But this role is the cleanest match I've seen for what I've been moving toward — so the alternative is choosing to wait for the next match, not walking away from the trajectory.

**"What would you bring on day 1 that an external hire wouldn't?"**
Three things. First, Walmart-internal context — the data systems, the stakeholder language, the political shape of how things actually get done across teams. Second, a working model of the substrate pattern that's already proven at Walmart scope (one team), so I know what's likely to repeat at enterprise scope and what won't. Third, a working evaluation methodology — the golden set + reusable eval harness — that's transferable to whatever the Agent Builder team is building.

**"What concerns you about the move?"**
*[NOTE: this is Q14 territory — full answer there. Quick version if asked here: scope shift means new stakeholders, new domains, longer time-to-first-shipped-thing. Mitigation is the substrate pattern itself — I know how to ramp on a new domain because that's exactly what the context layer is for.]*

**"Why this team / Bentonville specifically — culture fit?"**
*[TO FIRM UP — needs team-specific intel from recruiter. General-purpose framing: the team is biz/tech generalists, that's how I've been operating; biased for action, that's the pattern of my last 18 months; first-principles thinking, that's the V1 → V2 arc itself.]*

**"How is this a Principal-level move from Senior DA?"**
*[NOTE: this is Q6 — full answer there. Quick bridge if asked here: the title hides what I've shipped. The Principal-level signals — system design, end-to-end ownership, multi-month solo builds, leverage thinking — are what I've been doing. Title is the lagging indicator.]*

### Numbers / proof points to nail before the interview
- 📌 **Count of agents currently built on the substrate** — Jira agent, autonomous data analyst, KPI monitor, hybrid orchestrator, geo-readiness agent — concrete N is your strongest single proof of the pattern repeating
- 📌 **Stakeholder reach** — how many people across DV use the systems today
- 📌 **Manager-conversation status** — only number that matters here is "did you have it yet, and if so when" — write the answer for yourself before the interview so you're not improvising

## 6. Senior Data Analyst → Principal SWE — why are you ready?

> Note: this is the title-objection pre-empt. The panel will be looking for whether you're defensive, hand-wavy, or grounded. Lead with the work, not with apology. The strongest move is to make the title gap feel like *their* observation to verify, not *your* problem to explain away.

**Beats**
- *Honest frame.* Title says Senior DA. The work doesn't. Put 2025 next to the JD and you're looking at Principal-level outputs under a DA title.
- *The four signals.* System design (V1→V2, context layer + MCP, hybrid orchestrator). Leverage (one substrate, five agents on it). End-to-end ownership (every system shipped solo, design through production). Multi-month solo builds (V2, the orchestrator, the autonomous data analyst — each a multi-month effort).
- *Why the title hasn't moved.* DV is structured as a DA team — the role grew into platform work because that's what the team needed, but the org chart didn't follow. Org constraint, not capability gap.
- *Internal recognition.* Making a Difference Award earlier this year for 2025 work — leadership signaling the work is over the title.
- *Confident close.* This isn't a stretch up. It's a calibration to where the work already is. Title is the lagging indicator; shipped systems are the leading one.

**Draft**

> The honest frame on the title question is that the title says Senior Data Analyst and the work doesn't match. If you take what I've shipped over the last 18 months and put it next to the Agent Builder JD, you're looking at Principal-level outputs — they just happened under a DA title.
>
> The signals I'd point to: First, system design. V1 to V2 was a full architectural rethink — I tore down a working text-to-SQL app and rebuilt it as a reusable context layer plus MCP. That's not analyst work, that's platform work. The hybrid orchestrator is a multi-backend system design with a self-growing feedback loop — again, not analyst scope. Second, leverage. The agents I've built — the Jira agent, the autonomous data analyst, the KPI monitor, the geo-readiness agent, and the hybrid orchestrator — all run on the same substrate. The whole point of the V1 → V2 lesson was figuring out that the asset is the substrate, not the agent on top. That's platform thinking, which is exactly what the role is asking for. Third, end-to-end ownership. Every system I just named was solo — design, build, deploy, validation, rollout to stakeholders. There's no point where I handed something off and watched someone else finish it. Fourth, multi-month solo builds. V2 was a [NUMBER? months]-long rebuild, the hybrid orchestrator was a [NUMBER? months]-long build, the autonomous data analyst was a multi-month effort on top of that. Those aren't sprint-scope problems — they're staff-level engineering efforts I owned beginning to end.
>
> The reason the title hasn't moved is structural, not capability-driven. Data Ventures is organized as a DA team — the role grew into platform work because that's what the team needed, but the org chart didn't follow. I haven't pushed hard internally for a title change because it would mean restructuring how DV thinks about its headcount, which isn't my fight to pick. The Making a Difference Award earlier this year was leadership's way of saying *the work is over the title* — but the title itself is sticky for org reasons that have nothing to do with what I'm actually capable of.
>
> So when I look at the Agent Builder role, this isn't a stretch up — it's a calibration to where the work already is. The systems are shipped, the pattern is proven, and the panel can verify the outputs directly. The title is the lagging indicator. The shipped systems are the leading one.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Title is the lagging indicator; shipped systems are the leading one"* — quotable, opens the calibration / signal question. **Strongest line.**
2. *"Five agents on one substrate"* — opens the platform-leverage follow-up. Maps directly to the Agent Builder mandate.
3. *"Multi-month solo builds — staff-level engineering efforts I owned beginning to end"* — opens the scope / Principal-signal question.
4. *"The work is over the title"* — opens the org-constraint / why-not-promoted-internally follow-up. You **want** this one pulled — clean answer below.
5. *"V1 to V2 was a full architectural rethink — not analyst work"* — bridges into Q15 territory if the panelist wants the V1→V2 story.

### Anticipated follow-ups

**"Why didn't you push for a title change at Walmart first?"**
Two reasons. First, DV's headcount is structured around DA roles — moving my title would mean restructuring how the team thinks about its allocation, which is a much bigger conversation than my career path. Second, I'd rather have the work argue for me than argue for the work. If the systems aren't convincing on their own, a different title wouldn't fix that. The Making a Difference Award was the cleanest internal signal — leadership recognizing the work is over the title without formally adjusting it.

**"What's the gap between Senior DA and Principal SWE you're aware of?"**
The honest gap is breadth. I've built deep on one team's problems — the substrate is proven at one team's surface area, not at enterprise scope. The mitigation is the substrate pattern itself: I built the context layer because I needed to ramp on a new domain quickly, and that's exactly what makes ramping on the next domain faster. Principal scope means more domains, more stakeholders, more partner teams — and the patterns I've already proven transfer. What I haven't done is operate that pattern at enterprise scope, but that's the role, not a prerequisite for it.

**"Have you ever managed engineers?"**
Not formally. I've owned cross-functional dependencies — product team scoping, DS team owning the production service account, business stakeholders on adoption — but I haven't had direct reports. I'd want to be honest about that as I scale into Principal scope. The leverage I've built so far has been through systems, not through people, and stepping into Principal here means making sure I can do both. My read of the JD is that the role is principal *engineer*, not principal *manager* — the leverage expectation is through architecture and platform, which is where my track record is.

**"What's the strongest single piece of evidence you'd point to?"**
The hybrid orchestrator. It's the cleanest end-to-end ownership signal in the portfolio — multi-month solo build, novel architecture, reusable eval harness, validated against a golden set, in production this week. And the agreement-rate result — 20-for-20 on the agent path, 10-for-20 on the semantic layer, 20 candidate definitions surfaced for the growth loop — gives you a quantified outcome from one run. If you want a single artifact that says "this person is operating at platform scope," that's it.

**"Could this be a Senior SWE role instead — why Principal?"**
Fair question, and I'd be open to whatever calibration the panel lands on. My read is that the JD specifically asks for first-principles thinking, end-to-end ownership, and biz/tech generalism — those read as Principal-coded asks. And the substrate-on-which-others-build framing in the JD is platform work, which is also Principal-coded. But I'm not married to the title — I'm reading the work and saying my shipped systems match it. If the panel calibrates differently, I want to hear that read and understand it.

**"What's something Principal-level you haven't done yet?"**
Operating the substrate pattern across multiple team boundaries simultaneously. I've proven it on one team's surface area; the version where the substrate has to serve multiple downstream teams with different ownership boundaries, different governance, different SLAs — that's the next ring out, and that's exactly what Agent Builder is. So the honest answer is: I haven't done it yet, but that's the role, not a gap I'd need to close before I started.

**"How do you respond to someone on the panel who says 'a Senior DA can't be a Principal engineer'?"**
I'd say: don't take my word for it, take the artifacts. The V1 → V2 rearchitecture, the context layer, the MCP, the hybrid orchestrator with the eval harness — those are inspectable. If after looking at the systems the panel still reads it as a Senior DA's portfolio, that's a real disagreement and worth surfacing. But the question shouldn't be whether the title on my badge says I can do this work — it should be whether the work I've shipped says I can.

### Numbers / proof points to nail before the interview
- 📌 **Exact agent count on the substrate** — Jira agent, autonomous data analyst, KPI monitor, hybrid orchestrator, geo-readiness agent = **5**. Confirm nothing's missing.
- 📌 **Duration of each multi-month build** — V2 rebuild, hybrid orchestrator, autonomous data analyst. Right now drafted as `[NUMBER? months]`; pin down before the interview so the "staff-level engineering effort" framing has concrete weight behind it.
- 📌 **DA team size at DV** — useful color for "I'm the platform person on a team that wasn't built as a platform team."
- 📌 **MAD Award framing** — confirm the citation language if you can pull it; the strongest version of "the work is over the title" is reading the citation back.

---

# Part 3 — Other high-probability questions

> Not directly teed up by TMAY, but on every panel's standard list.

## 7. Why this role, why now?
*Status: TO DRAFT*

## 8. Tell me about a time you failed

> Note: Q15 ("what should we remember about you") and Q8 are the same V1→V2 arc told differently. Q15 leads with the *recovery* and the *platform lesson*. Q8 leads with the *cost* and *your role in causing it*. **Decision rule on interview day:** if you've already used V1→V2 with this panel for Q15 (or any earlier question), switch to the backup option below. Otherwise V1→V2 is your strongest, sharpest, most-shipped failure story.

### Primary option — V1 → V2 (retuned for failure emphasis)

**Beats**
- *The build.* Mid-2025, V1 of a text-to-SQL RAG app for business teams. Frontend, vector retrieval over historical SQL, generation against BigQuery. Demoed to senior leadership + product teams.
- *What I did wrong.* Scoped it as a *product* problem and built a new frontend. Business teams already lived in Slack, Jira, BigQuery's native UI. I asked them to leave those tools to come to mine — and I hadn't actually validated the surface was the part worth building.
- *The cost.* Adoption stalled. Worked technically, didn't replace anything anyone was already doing. Months of build, demoed up the chain, daily-active number stayed near zero.
- *The reflection.* Blocker wasn't the model and wasn't the data. I'd built a *destination* when the right answer was a *capability*. The valuable piece — the curated context grounding the LLM's answers — was the part nobody could see, because it was wrapped in a frontend nobody used.
- *The recovery (kept short).* V2 tore the frontend out. Decomposed V1 into a reusable context layer + MCP, delivered as a skill inside YB — internal Claude Code equivalent — where engineers already worked. Same context layer now powers four other downstream agents.
- *The lesson.* Adoption is a product problem, not a technology problem. Second-order — the part that actually changed how I work — the reusable asset usually isn't the thing the user touches; it's the substrate underneath. Every system I've shipped since has been a thin agent on a reusable substrate.

**Draft**

> The clearest failure I can point to is something I shipped last summer. V1 of a text-to-SQL RAG app — a frontend where business teams could ask questions in English and get back SQL against BigQuery, with vector retrieval over historical queries grounding the model. Technically it worked. I demoed it to senior leadership and the product teams. It just didn't get used.
>
> The reason it didn't get used was a call I made early and didn't go back and validate. I'd scoped it as a product problem and built a new frontend. But the business teams I was building it for already lived in Slack, Jira, and BigQuery's native UI — and I was asking them to leave those tools and come over to mine. There was no forcing function for that switch, and I hadn't actually tested whether the surface was the part worth building. So I shipped a working system that solved a problem nobody was choosing to bring me. Months of build, with the daily-active number staying near zero.
>
> The reflection took a while to land. My first instinct was to assume the model needed to be better, or that I needed more training data, or that the demos hadn't been compelling enough. The thing I missed for too long was that the blocker wasn't the system — it was the surface I'd put it behind. The valuable piece, the curated context that grounded the LLM's answers, was the part nobody could see, because it was wrapped in a frontend nobody used.
>
> The recovery was V2. I tore the frontend out and rebuilt the system as a reusable context layer plus an MCP, delivered as a skill inside YB — our internal Claude Code equivalent, which is where the engineers already worked. The same context layer now powers four other downstream agents, including the autonomous data analyst and the KPI monitor. So the failed app ended up turning into N agents because the second time around I built the abstraction, not the product.
>
> The lesson I carry is twofold. First-order: adoption is a product problem, not a technology problem — meeting people where they already work matters more than how clever the underlying system is. Second-order, and this is the one that actually changed how I work — the reusable asset usually isn't the thing the user touches, it's the substrate underneath. Every system I've shipped since V1 has been a thin agent on a reusable substrate. That pattern came directly from V1 not landing.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"A call I made early and didn't go back and validate"* — opens the decision-process / how-do-you-test-assumptions follow-up. Principal-level signal — answers "do you learn from your own mistakes" with a specific cognitive failure, not just an outcome.
2. *"The valuable piece was the part nobody could see, because it was wrapped in a frontend nobody used"* — quotable, opens the architecture follow-up. Bridges naturally into Q15 / context-layer territory if not already used there.
3. *"The reusable asset usually isn't the thing the user touches"* — opens the platform-thinking question. Maps directly to Agent Builder.
4. *"My first instinct was to assume the model needed to be better"* — opens the self-correction follow-up. Shows you can name your own bias.

### Anticipated follow-ups

**"When did you actually realize V1 wasn't going to land?"**
*[TO FILL IN — concrete moment makes the reflection feel real. Candidates: a specific 1:1 with a stakeholder saying "yeah it's cool but I'd have to remember to use it," a usage dashboard showing flat DAU for N weeks, a moment where you watched yourself answer a question in Slack instead of opening the tool you'd built, a demo where the questions were softball because nobody was using it for real work.]*

**"How long did you keep trying to fix V1 before deciding to rebuild?"**
*[TO FILL IN — be honest. The right answer is whatever the real number is. "Too long" framing is fine if true; "fairly quickly once I saw the adoption data" is fine if true.]*

**"What kept you from validating the surface earlier?"**
Honest answer: I was excited about the model and the retrieval. I treated the frontend as the obvious wrapper and didn't interrogate whether it was the right wrapper. The mistake wasn't *missing the data* — adoption was visibly flat — it was that I'd anchored on "the system needs to be better" before I'd considered "the system is fine, the placement is wrong." The reason I now ship into existing surfaces by default — YB, Jira, Slack — is V1.

**"What would you do differently if you started V1 over?"**
Two things. First, validate the surface before building the system — even a stub deployed into YB or Slack would have shown me whether the *placement* mattered before I sunk months into a frontend that didn't. Second, design for the abstraction earlier — V1 was a monolith because I was thinking like a product builder; if I'd designed the context layer as a first-class API from day one, the rebuild would have been weeks not months.

**"Is the failure that V1 didn't get adopted, or that you didn't predict it wouldn't?"**
Fair distinction, and it's the second one. Lots of v1s don't land — that's expected. The failure is that the *reasons* it didn't land were knowable before I started building, and I didn't make space to ask the right questions. That's the part I own.

**"Have you applied this lesson somewhere else since?"**
Yes — explicitly. Every system I've shipped since V1 has gone into a surface someone already uses, and is built as a thin agent on a reusable substrate. The Jira agent goes into Jira. The autonomous data analyst goes into YB. The KPI monitor pings Slack. The semantic-layer agent fronts an interface engineers already query. That's the V1 lesson operationalized.

**"Did V1 ever come back in any form?"**
Yes — as a *tool*, not as a product. The original RAG over historical SQL is now one of the tools exposed through the MCP in V2. So the technical work wasn't wasted — it just had to be repackaged into something other agents could use, instead of something a user had to come visit.

### Short version (if cut for time, ~60 seconds)

Hit only: shipped V1 of a text-to-SQL RAG app with its own frontend → adoption stalled because I'd asked users to leave the tools they already lived in → mistake was anchoring on "the system needs to be better" instead of "the placement is wrong" → V2 was a context layer + MCP delivered as a skill into YB, where engineers already worked → that same substrate now powers four downstream agents → the lesson that changed how I work: the reusable asset usually isn't the thing the user touches, it's the substrate underneath.

---

### Backup option — alternative story (use only if V1→V2 has been burned earlier in same panel)

> This slot needs a real story from you. Below is the required *shape* the answer must follow, plus four candidate stories from your portfolio I'd consider. Pick one (or supply a different one) and give me a few details — even 60-90 seconds of context is enough for me to draft.

**Required shape (60–90 second answer):**
- *The build / decision.* What you did, briefly. (10–15 sec)
- *What you did wrong.* Own the specific cognitive mistake, not just the outcome. (15–20 sec)
- *The cost.* Time, trust, missed opportunity, dollars, adoption — concrete. (15–20 sec)
- *The reflection.* What you learned that you couldn't have learned without making the mistake. (15–20 sec)
- *The recovery.* Kept short — this is a failure question, not a success question. (10–15 sec)

**Candidate stories to consider (need your kernel):**

1. **Early Jira agent iteration that miscarried.** Did any early version of the Jira agent produce a wrong answer that went to a stakeholder before you added the HITL gate? If yes, this is a strong backup — it's about agent reliability, which is on-topic for Agent Builder, and the recovery (deliberate HITL) is already in your Q2 answer.

2. **Cube.js semantic layer onboarding miss.** When you first onboarded the semantic-layer agent, did you assume adoption would follow naturally and have to course-correct on definition ownership or stakeholder engagement? Strong backup because it's a different failure shape (governance/scoping) from V1→V2's (surface/placement) — gives the panel a fresh signal.

3. **An earlier dashboard or analytics deliverable that nobody used.** Any pre-agent work where you shipped something polished and watched it not get adopted? Structurally similar to V1→V2 but with different stakes — if it predates the agent work, it shows the V1 lesson was actually *re-learned*, which is honest and human.

4. **Misjudging the scope of one of the multi-month builds.** Did you underestimate any of V2, the orchestrator, or the autonomous data analyst — committing to a timeline you couldn't hit, or scoping the first version too ambitiously? Different failure shape (estimation / scope discipline) — a Principal-level failure mode the panel will recognize.

**Once you pick one and give me a few details, I'll draft the backup at the same level of polish as the primary.**

### Numbers / proof points to nail before the interview
- 📌 **The "when I realized V1 wasn't landing" moment** — a concrete date / meeting / metric. Strongest single thing you can add to the primary.
- 📌 **V1 build duration** — months from start to demo. Sets the scale of the failure.
- 📌 **V2 build duration vs. V1** — gives the recovery a comparable timeframe.
- 📌 **V1 actual usage numbers** — even rough ("near zero weekly active users" is fine if true).
- 📌 **N of downstream agents now on the V2 substrate** — currently drafted as "four other" but confirm exact count.

## 9. Your first 60–90 days
*Status: TO DRAFT*

## 10. Walk me through a problem you owned end-to-end
*Status: TO DRAFT*

## 11. When would you NOT use an LLM?
*Status: TO DRAFT*

## 12. Walk me through your Data Ventures agent architecture (design walkthrough)
*Status: TO DRAFT*

## 13. Are you willing to relocate to Bentonville?
*Status: TO DRAFT*

## 14. What concerns you about this role?
*Status: TO DRAFT*

## 15. What do you want the panel to remember about you?

**Beats**
- *Core message.* Passionate about AI, eager to learn and apply new techniques, willing to learn from my own mistakes — and able to translate those lessons into a better architecture the second time around.
- *V1 (mid-2025).* Text-to-SQL RAG app. Frontend let business teams ask questions in English; vector embeddings of historical SQL retrieved into context; new SQL generated against BigQuery. Demoed to senior leadership + product teams.
- *The miss.* Technically worked. Adoption stalled — required users to leave their existing workflow for a new frontend.
- *The reflection.* Blocker was the surface, not the model. The valuable piece was the context, not the UI.
- *V2.* Stopped building an app, started building a platform. Decomposed V1 into a reusable **context layer + MCP**, delivered as a skill inside YB (the internal equivalent of Claude Code). Original RAG became one tool exposed through the MCP. Same context layer now powers the autonomous data analyst, KPI monitoring, the geo-readiness agent, and other downstream agents.
- *The lesson.* Adoption is a product problem, not a technology problem. One failed app turned into N agents because the second time I got the abstraction right.

**Draft**

> What I want this panel to remember is that I'm passionate about AI, I move fast on new techniques, and I'm willing to learn from my own mistakes in a way that changes the architecture the second time around. The clearest example is something I shipped last year. V1 was a text-to-SQL RAG app — a frontend that let business teams ask questions in English and got back SQL against BigQuery, with vector embeddings of historical queries retrieved into the LLM's context. Technically it worked, and I demoed it to senior leadership and the product teams. But adoption stalled, because I'd asked users to switch into a new frontend instead of meeting them where they already worked. The blocker wasn't the model — it was the surface. So I stopped building an app and started building a platform. V2 was a reusable context layer plus an MCP, delivered as a skill inside YB — our internal equivalent of Claude Code. The original RAG became just one tool exposed through that MCP. The same context layer now powers the autonomous data analyst, KPI monitoring, the geo-readiness agent, and several other downstream agents. The lesson I carry forward is that adoption is a product problem, not a technology problem — and the reusable asset was the *context layer*, not the UI. One failed app turned into N agents because the second time I got the abstraction right.

**Hooks planted (ranked by likelihood they get pulled)**
1. "Stopped building an app, started building a platform" — opens the architecture / platform follow-up
2. "Context layer + MCP" — opens technical depth (most likely from the engineers on the panel)
3. V1 → V2 — doubles as a failure / change-of-mind story
4. "N downstream agents now built on it" — opens platform-leverage / Agent Builder fit angle

### Technical depth (if probed)

**Context layer (one-liner):** A structured markdown knowledge base wrapped in an MCP that decides what context to inject per task — docs, EDA results, or data samples — so the agent gets grounded context instead of guessing from schema names alone.

**Context layer (longer):**
- *Static piece:* organized markdown files describing the data domain — table docs, schemas, semantic context, historical query patterns.
- *Dynamic piece:* an MCP layered on top that decides, per question, what to inject into the context window. The MCP can read the markdown, run EDA against BigQuery to verify assumptions, or pull data samples. Context is grounded in what the data *actually* looks like, not just what someone wrote down about it.

**MCP (in this context):** The instruction layer that tells the agent what tools are available and how to use them. The RAG is one tool; EDA is another; direct BigQuery access is another. The agent composes them.

### Anticipated follow-ups

**"Why a context layer instead of just giving the agent SQL tool access and letting it explore?"**
Agents waste tokens and make wrong assumptions when they have to rediscover the schema every time. Front-loading curated domain knowledge gets accuracy and speed; the EDA path is the escape hatch for when the docs aren't enough.

**"How does the MCP decide what to inject?"**
*[TO FILL IN — actual retrieval strategy: semantic search over markdown, keyword matching, agent-driven selection, etc.]*

**"How do you keep the markdown in sync with the actual schema?"**
*[TO FILL IN — any schema-diff automation, or honest description of the manual process and its tradeoffs.]*

**"What happens when EDA contradicts the markdown?"**
*[TO FILL IN — agent flags it / EDA wins as ground truth / actual behavior.]*

**"What's the moment you realized V1 wasn't going to land?"**
*[TO FILL IN — a specific meeting, piece of feedback, or adoption metric. Concrete moments make the reflection feel real rather than rehearsed.]*

**"What does each downstream agent do?"**
For each (autonomous data analyst, KPI monitoring, geo-readiness agent), have a one-sentence answer: what it does + who uses it + what it replaced.

### Numbers to nail down before the interview

- Adoption of V2 — queries per week, DAU/WAU on the product team, hours of manual data pulls replaced
- Number of downstream agents now built on the context layer
- Anything quantifiable about accuracy improvements vs. V1 or vs. raw LLM-with-SQL-tool

### Note: this story doubles as your failure answer (Q8)

The V1 → V2 arc is a clean structural fit for "Tell me about a time you failed." When using it there, lead with "I shipped V1 and it didn't get adopted" — emphasize the *cost* and your *role in causing it*, not just the recovery. The "stopped building an app, started building a platform" insight becomes your STAR result. Decide which question you'd rather use it for — using the same story for both is fine if they're not on the same panel.

---

# Drafting queue (suggested order)

1. ✅ **Q1 — Tell me about yourself** (drafted)
2. ✅ **Q15 — What do you want the panel to remember about you?** (drafted)
3. ✅ **Q2 — Jira agent** (drafted — has [TO FILL IN] gaps in the anticipated follow-ups)
4. ✅ **Q3 — Self-growing semantic layer** (drafted — agreement-rate numbers nailed; adoption metric still TBD)
5. ✅ **Q5 — Why move from DV** (drafted — manager-conversation answer + agent count still TBD)
6. ✅ **Q6 — Senior DA → Principal SWE** (drafted — multi-month-build durations + agent-count confirmation still TBD)
7. ✅ **Q8 — Failure story** (primary V1→V2 drafted with failure-emphasis retuning; backup option needs your story-kernel pick from 4 candidates)
8. ✅ **Q4 — Autonomous data analyst** (drafted — sibling-to-Jira-agent framing; adoption numbers, approval-process story, 6-tables confirmation still TBD)
9. **Q9 — First 60–90 days** — Walmart loves this one
10. **Q7 — Why this role, why now**
11. **Q10 — End-to-end ownership**
12. Remaining as time allows
