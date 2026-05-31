# Interview Answers — Walmart Agent Builder (v2, corrected)

> **Version note (2026-05-16).** Corrections rolled in from the Work Artifacts review:
> - **Q2 Jira agent** — agent is fully autonomous (skill-level, zero internal HITL); my review sits *outside* the agent loop. Tool count 14, not 13. Retrieval substrate is 313 historical BQ SQL queries with Gemini + BM25 + RRF — not 11k Jira tickets with FAISS. Pipeline is 5 phases, not 6 gates.
> - **Q3 Self-growing semantic layer** — the full auto-update loop is *built and ready* but currently *gated off* (`CP_AUTO_IMPROVE_ENABLED=true`, default off). Today the disagreement review with product team runs manually. Real growth-loop mechanics (clustering, cube-gap-filler, equivalence test, draft PR, safety rails) added. Real scale numbers added.
> - **Q4 Autonomous data analyst** — operates across the full 68-table cp-platform surface via the MCP, not 6 tables. REFLECT scoring + composable cp-audit / cp-fix / cp-context-validate ecosystem added.
> - **Q5/Q6/Q8** — downstream consumers updated (7+, including Slack `/cp` bot). 18-experiment evaluation framework + drift detection added as Principal-level signals.
> - **Q15** — tool count, drift detection, scale numbers, three-tier LLM fallback, flagship `cp_generate_validated_sql` tool added.

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
- *What grew out of it.* Power BI dashboards → Python pipelines → **Jira agent (400+ tickets resolved end-to-end by an autonomous skill)** → autonomous data analyst → self-growing semantic layer.
- *Recognition.* Making a Difference Award earlier this year for 2025 work.
- *Why Agent Builder.* Scoped to one team today. Role = same work at Walmart scale. *"That's the version of this work I want to be doing."*

**Draft**

> Today I'm a Senior Data Analyst at Walmart Data Ventures supporting Customer Perception — I'm the point of contact for about 30 people across business and technical teams who come to me with analytics, stewardship, and readiness questions. Pretty quickly I realized the volume of that intake wasn't something one person could keep up with, so I started building — both probabilistic and deterministic systems — to absorb it. That's grown into Power BI dashboards, Python pipelines, a Jira resolution agent that autonomously handles tickets end-to-end, an autonomous data analyst, and a self-growing semantic layer that refines its own definitions over time. Earlier this year that work earned me a Making a Difference Award for what I shipped in 2025. What pulls me toward Agent Builder is that I've been doing this scoped to one team — the role makes it possible to do it at the scale Walmart actually operates at, and that's the version of this work I want to be doing.

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
- *The architecture (the skill itself).* 5-phase pipeline: **TRIAGE → UNDERSTAND → PLAN → EXECUTE → DELIVER.** Validation lives *inside* EXECUTE as a per-query self-healing loop with a 10-retry budget — 3 retries for SQL syntax, 2 for timeouts, 3 for unexpected-zero-row results that open an Investigation Branch with a hypothesis.
- *The MCP layer.* All schema, joins, and domain context come from cp-analytics-mcp — **14 tools + 4 read-only resources**. Retrieval over the **313 historical BigQuery queries** indexed from 180 days of `JOBS_BY_USER` — hybrid Gemini embeddings + BM25 + RRF fusion.
- *Autonomy posture.* The agent itself is **fully autonomous, zero internal human checkpoints** — triage to CSV delivery is all on the agent. My review sits *outside* the agent loop: when the agent finishes, I look at the synthesized response and post it back into Jira myself. The agent has no concept of my review step — that's a deliberate workflow choice for stakeholder trust, not an agent-design constraint.
- *Outcome.* Complex tickets went from a full day to 10–15 minutes. **400+ tickets handled since January 2025.**
- *The real win = leverage.* The intake bottleneck was what had been keeping me from building anything else. Once it was off my plate, I built the autonomous data analyst, the KPI monitor, and the self-growing semantic layer on top of the same context infrastructure the Jira agent already used. *"The Jira agent ended up being the platform that funded the rest of the portfolio."*

**Draft**

> Customer Perception runs on Jira intake — stakeholders submit tickets when they need data readiness or analysis work. The questions are pretty varied: what's the product hierarchy for a specific supplier, what UPCs map to which products, which panel studies bought a given UPC in a given timeframe, which of those panelists took a specific survey, what was the response rate. I was the only one answering them, and before the agent, a typical ticket took me 30 minutes to an hour, with complex ones eating most of a day. I've handled over 400 of these since January 2025, so it was the single biggest drain on my time and the bottleneck on everything else I wanted to build.
>
> The agent is a 5-phase pipeline — triage, understand, plan, execute, deliver. Triage is six gates that decide whether a ticket is solvable end-to-end. Understand pulls the schema, the join paths, and the domain context for the tables involved through our MCP server — fourteen tools and four read-only resources — and pulls two or three similar past queries from a knowledge base of 313 historical BigQuery queries we indexed off 180 days of job history, scored with hybrid Gemini embeddings plus BM25 plus reciprocal rank fusion. Plan decomposes the work into a numbered SQL plan. Execute runs each query with a 10-retry self-healing budget — three retries for syntax, two for timeouts, three for unexpected zero-row returns, where the agent opens what we call an Investigation Branch and forms a hypothesis before adjusting the filter. Deliver writes the CSVs, updates the manifest, and synthesizes the response.
>
> The autonomy detail that matters: the *agent itself is fully autonomous*. There are zero internal human checkpoints in the pipeline — triage to CSV delivery is all on the skill. The human-in-the-loop in this workflow is *outside* the agent: when it finishes, I review the synthesized response and post it back into Jira myself. The agent has no concept that I review it — that's a deliberate workflow choice on my side, because the cost of a wrong stakeholder message is much higher than the cost of a failed BigQuery retry. I separated those two failure budgets. The agent's autonomy is sized for execution; my review is sized for communication.
>
> The outcome that matters wasn't the time per ticket, though complex ones did go from a full day to 10–15 minutes. The bigger win was leverage. The intake bottleneck was what had been keeping me from building anything else. Once it was off my plate, I built the autonomous data analyst, the KPI monitor, and the self-growing semantic layer on top of the same context infrastructure the Jira agent already used. So the Jira agent ended up being the platform that funded the rest of the portfolio.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"The agent itself is fully autonomous; the HITL sits outside the agent"* — strongest line, opens the reliability / scaling-trust follow-up. Reframes HITL as a *workflow* decision, not an *agent-design* limitation. Principal-level signal.
2. *"The Jira agent ended up being the platform that funded the rest of the portfolio"* — opens the leverage / platform-thinking question, which maps directly to the Agent Builder role.
3. *"Investigation Branches when a query returns zero rows"* — opens the reasoning-under-uncertainty follow-up; uncommon depth.
4. *"The same context infrastructure"* — opens the technical depth question that ties back to Q15's context layer + MCP story.

### Anticipated follow-ups

**"Why didn't you let it auto-post?"**
Cost of a wrong response to a stakeholder is much higher than the cost of two minutes of my review. The trust ramp matters — these are people I work with every week. I deliberately wired the agent so the post step is in my hands, not the agent's. If I were operating at platform scale where I couldn't review every reply, I'd add explicit confidence thresholds, auto-post on high-confidence cases, and route low-confidence cases through a queue. The architecture supports that; the choice not to do it yet is about trust, not capability.

**"How does the agent know it's done well?"**
Two complementary validation paths, both running inside the agent. First, structural SQL correctness — the agent verifies its generated SQL against the cp-analytics-mcp context layer, which exposes a 52-node, 63-edge join knowledge graph, 36+ verified join paths, and 89 indexed domain sections. Joins, columns, and query shape all get checked against what the schema and the graph say is valid. Second, intent matching — the agent compares the proposed answer against how similar questions have been answered in the historical archive of 313 past BQ queries. If the shape of the answer is wildly different from precedent, that's a flag. The triage gate at the front is the first filter — six checks that decide whether the ticket is solvable end-to-end before any drafting happens.

**"What were the 14 tools?"**
Five categories. Schema and context — `cp_get_schema`, `cp_get_join_path`, `cp_get_domain_context`, `cp_get_gcc_context`, `cp_get_backlog` — all in-memory JSON, zero-latency. Execution — `cp_query` against BigQuery, and the flagship `cp_generate_validated_sql` which is a complete NL→SQL→validate→execute pipeline in one call. Discovery and RAG — `cp_ask_docs` over the ChromaDB index, `cp_search_sql` over the 313-query SQL knowledge base. Reporting workflow — `cp_init_report`, `cp_build_execution`, `cp_create_chart`, `cp_validate`. And maintenance — `cp_refresh_knowledge` to trigger pipeline scopes. Plus four read-only resources — `cp://domain`, `cp://tables`, `cp://backlog`, `cp://index` — that expose the raw context files by URI.

**"What's an Investigation Branch?"**
When a query returns zero rows or unexpected results, the agent opens a hypothesis block in the worklog — "I expected N rows, got 0; hypothesis is X; running a 5-min exploratory query to test." It runs the exploration, documents the finding, then applies the learning to the next query. The branches are preserved through rolling compression as encoded debugging knowledge. The cleanest real example I have is BDV-6665, where the agent initially returned 523 qualified completes, the stakeholder said 9 should be excluded for video opt-out, and the investigation surfaced that the Q12 column was 100% NaN because opt-in is a panelist-level preference, not a survey answer. The agent self-corrected with a join into `market_research_panelist_preference.video_activity_opt_in_flag = TRUE`, landed on 514, kept Q1 as `superseded` for the audit trail.

**"Why retrieval over 313 historical queries — what's that for?"**
Most stakeholder questions aren't novel — they're variants of questions someone else asked 3 months ago. The historical archive grounds the agent's plan in *how this team has answered this kind of question before*, not just what the schema says. The 313 number is queries deduplicated from 180 days of BigQuery `JOBS_BY_USER`, filtered to SELECT-only on CP datasets, with Gemini-generated natural-language descriptions attached so the agent can match by intent, not just by table name.

**"Was there a moment you knew stakeholders couldn't tell?"**
Honest answer: there was no single aha moment. Nobody ever asked. They just kept submitting tickets and getting faster, well-supported responses. I'd treated the Jira agent as plumbing — I thought the visible-impact projects would land harder, the ones stakeholders could touch directly, like the CLI for the semantic layer or the Slack alerts from the KPI monitor. So I wasn't promoting it. The "more interest than I expected" signal came later, when people noticed I'd been quietly absorbing 400+ tickets while shipping three other systems in parallel. The lesson for me: I'd underestimated what the panel might find load-bearing. Quiet automation can be more interesting than visible automation, because it shows up as capacity, not as a product.

### Short version (if cut for time, ~60 seconds)

Hit only: business cost (400+ tickets, 30 min–1 hr each) → 5-phase autonomous pipeline (one sentence) → HITL is outside the agent, not inside (workflow decision, not agent-design limit) → leverage win (funded the rest of the portfolio).

## 3. What's the self-growing semantic layer?

> Note: this is what the resume calls the **hybrid orchestrator** — same system, two names. "Self-growing semantic layer" describes what it does over time; "hybrid orchestrator" is the architectural shape. Drop the bridge in the first sentence so the panelist doesn't think these are two separate projects.

**Beats**
- *The problem.* Two standard approaches to text-to-data, each broken in a different way. **Semantic layer** (Cube.js, dbt MetricFlow): deterministic and auditable, but brittle — every metric has to be hand-defined upfront. **Context-engineered agent**: flexible, handles novel questions, but can hallucinate joins or pick the wrong metric. Pick one and you live with its failure mode.
- *Scale of what's modelled.* Customer Voice / Customer Spark — **1.1M panelists (~773K active), 158M task rows, 32K surveys**. The Cube layer has **23 cube definitions across 5 domains** (panelist lifecycle, task/survey pipeline, rewards & billing, recruitment & audience, operational & data quality).
- *What's in production.* Both paths. The **Cube.js semantic-layer skill** on port :4000 — I built end-to-end (definitions, modeling, the skill itself); product team scoped the first stakeholder questions to onboard. The **context-engineered agent** (`cp-discovery-bq` on the bq-proxy port :5050) sitting on the cp-platform context layer + MCP. Both deployed and actively used.
- *The insight.* They're not competing — they're complementary. Each fails where the other succeeds. Run both in parallel and you can use the disagreement as signal.
- *The hybrid orchestrator.* Same user question fans out to both backends as parallel sub-agent dispatches. A reconciliation classifier compares results with a **0.5% numeric tolerance** and tags every answer with one of 5 verdicts: `SAME_INTENT_SAME_RESULT`, `COVERAGE_GAP`, `AMBIGUOUS_QUESTION`, `SAME_INTENT_DIFFERENT_RESULT`, `LLM_FAILURE`.
- *Why hybrid (not pick one).* Cube-only and you don't know what questions you *can't* answer. Raw-SQL-only and users need their own GCP credentials and the LLM-generated queries are unaudited. Hybrid is best of both — **no user permissions required**, governed where definitions exist, exploratory where they don't.
- *Disagreement handling — today.* Coverage gaps and disagreements are logged automatically. The ratify-and-add step is currently a manual workflow with the product team — they review flagged disagreements, decide if it's a real new measure or noise, and I add the new Cube definition. That's deliberate; we're building trust on the loop before we let it run on its own.
- *Disagreement handling — the auto-update loop that's built.* The full auto-improve pipeline is engineered and ready, gated behind `CP_AUTO_IMPROVE_ENABLED=true` (default off). When enabled: a weekly driver reads the gap log, **clusters by SHA256 `cluster_id`** over `(missing_from_cube, raw_table, columns_used)`, triggers when the same concept appears **≥3 times from ≥2 distinct users in 7 days**, dispatches a `cube-gap-filler` skill to synthesize a candidate YAML measure, runs an **equivalence test** (loads YAML into local Cube, compiles to SQL, executes against BQ, must match the reference raw SQL within 0.5%), and **opens a draft PR** with full provenance — cluster ID, redacted user questions, equivalence proof table.
- *Safety rails (built into the auto-update).* Draft PRs only — human marks Ready for Review. Max 2 PRs/day. No PR without equivalence proof. Only ADD measures (never modify or delete). Only `model/*.yml` files touched. CI guard workflow asserts PR is draft and body has an equivalence table. Privacy redaction on user questions before logging.
- *Ownership shape.* I built the whole stack end-to-end — semantic layer, context-engineered agent, hybrid orchestrator, reconciliation classifier, the cube-gap-filler skill, the equivalence test harness, the CI guards. **Product** owns scope + manual disagreement review today. **DS** owns the production service account the orchestrator queries through (deliberate UX choice — end users skip BigQuery auth).

**Draft**

> So this is what the resume calls the hybrid orchestrator — same system. "Self-growing semantic layer" is the way I describe what it does over time; "hybrid orchestrator" is the architectural shape.
>
> The data this sits on is Customer Voice — 1.1 million panelists, about 773K active, 158 million task rows, 32 thousand surveys. The Cube layer I built has 23 cube definitions across five domains: panelist lifecycle, the task and survey pipeline, rewards and billing, recruitment and audience, and operational and data-quality cubes.
>
> Most enterprise text-to-data setups pick one of two approaches and live with the tradeoffs. The semantic-layer approach — Cube.js, dbt's semantic layer, similar tools — is deterministic and auditable, but it's brittle: every metric has to be hand-defined upfront, and it can only answer questions that map to existing definitions. The context-engineered approach is the opposite — an agent sitting on the context layer plus MCP I described earlier — flexible, handles novel questions, but it can hallucinate joins or pick the wrong metric for what the user actually meant. Each fails in a different direction.
>
> I built both — separately — and they're both deployed and serving real traffic today. The Cube.js semantic-layer skill I built end-to-end on port :4000: the definitions, the modeling decisions, the YAML, the skill itself. The context-engineered agent is `cp-discovery-bq` sitting on the cp-platform MCP and bq-proxy. The hybrid orchestrator was the next step — every user question dispatches both paths as parallel sub-agents, a reconciliation classifier compares the results with a 0.5% numerical tolerance, and the answer comes back tagged with one of five verdicts — same intent same result, coverage gap, ambiguous question, same intent different result, or LLM failure. Same-intent-same-result is verified by both paths; coverage-gap means the Cube layer didn't model this, so the raw path answered; the disagreement verdicts are the interesting cases.
>
> The reason I went hybrid instead of picking one — a Cube-only system means users don't know what questions they *can't* ask, and a raw-SQL-only system needs the user's own GCP credentials and ships unaudited LLM SQL. Hybrid is best of both: governed where definitions exist, exploratory where they don't, and no user permissions required because everything routes through a DS-owned service account.
>
> The growth loop — and this is the part where I want to be precise about what's running today versus what's built and ready. The capability we have built and ready: every coverage gap and disagreement gets logged to a structured trace file. A weekly driver clusters gaps by a deterministic SHA-256 cluster ID over the combination of which Cube measure was missing, which raw table the gap-filling query used, and which columns it touched. When the same concept hits the log three or more times from at least two distinct users in seven days, the driver dispatches a `cube-gap-filler` skill that synthesizes a candidate YAML measure seeded with the raw SQL, the expected value, and the table FQN. We run an equivalence test — load the proposed YAML into a local Cube, compile it to SQL, execute it against BigQuery, and compare to the reference raw SQL. If the value matches within 0.5 percent, the driver opens a *draft* pull request on the semantic-layer repo with full provenance — cluster ID, redacted user questions, the equivalence proof table, failure logs. That pipeline is engineered and tested end-to-end.
>
> The piece that's gated: the whole auto-improve loop runs behind an environment flag, `CP_AUTO_IMPROVE_ENABLED`, default off. Today, what's actually running is the disagreement *detection* — every gap and conflict is logged automatically — but the ratify-and-add step is a manual workflow with the product team. They look at the flagged disagreements, decide if it's a real missing measure or noise, and I add the new Cube definition. We're being deliberate about turning the autonomous loop on. The safety rails are built into it — drafts only, max two PRs per day, no PR without an equivalence proof, only adds (never modifies or deletes), only the model YAML files, a CI guard that asserts the PR is draft and the body has the equivalence table, privacy redaction on user questions before they get logged. But shipping a self-modifying semantic layer is a trust problem more than an engineering problem. Right now the manual path is the one running, and that's the right call until the org is ready for the flag to flip.
>
> Last piece on ownership: I built the whole stack end-to-end — both backends, the orchestrator, the reconciliation classifier, the cube-gap-filler skill, the equivalence test harness, the CI guards. Product team scopes which questions get onboarded and runs the manual disagreement review today. The DS team owns the production service account the orchestrator queries through — that's why they handle the actual deploy step — but the architecture and the build are mine end-to-end.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"The capability is engineered and ready; the deployment is deliberately gated until the org is ready for the flag to flip"* — strongest line. Opens the trust / risk-management follow-up. Principal-level signal: knowing when to ship capability ≠ when to ship the *use* of capability.
2. *"Disagreements aren't bugs — they're labeled training data for the semantic layer"* — opens the architecture / flywheel question.
3. *"No user permissions required"* — opens the UX / cross-functional follow-up. Frames the architecture choice as a UX call, not an infra call.
4. *"I built the whole stack end-to-end — both backends, the orchestrator, the cube-gap-filler skill, the CI guards"* — opens the ownership / scope question. **The cleanest end-to-end signal you can land.** Maps directly to Agent Builder.
5. *"Clustering by deterministic SHA-256 cluster ID, triggered when ≥3 occurrences from ≥2 users in 7 days"* — opens the reliability / why-not-trigger-immediately follow-up. Specific enough that the panel knows the design isn't hand-wavy.

### Anticipated follow-ups

**"Why isn't the auto-update loop turned on?"**
Two reasons, in order of importance. First, trust — letting an agent open PRs against the semantic layer that defines what every business metric means is a step you only take after the org has lived with the manual version long enough to know what the failure modes look like. The Cube layer is the source of truth between calls; a confidently-wrong autonomous addition could drift it. Second, governance — the question of who's authorized to ratify a new business definition is a product-org question, not an engineering one. Until that's been formalized, the manual review with product *is* the governance. The flag flips when both of those are ready.

**"What's the difference between what's running and what's built?"**
What's running: the two backends, the orchestrator, the reconciliation classifier, the verdict tagging, the gap logging. So users get answers with a confidence verdict on every call, and every disagreement gets captured. What's built but gated: the weekly clustering driver, the cube-gap-filler skill, the equivalence test harness, the draft-PR generation, the CI guard workflow. All of that is tested and ready — the env flag toggles it. Today the path from "disagreement logged" to "new Cube measure added" goes through me and product manually; with the flag on, it goes through the autonomous loop and surfaces as a draft PR for product to mark Ready.

**"How does the reconciliation classifier decide?"**
Same intent, same result within 0.5% numeric tolerance — verified, ship the Cube answer. Coverage gap — Cube returned nothing or errored, raw path answered, log the gap. Ambiguous question — both paths ran but the user's intent was unclear; surface the diagnostic. Same intent, different result — both paths ran, both claim to answer the same question, but the numbers disagree outside the 0.5% tolerance; this is the highest-signal case for the growth loop. LLM failure — one path errored; ship the other.

**"Why product team for review instead of you?"**
Product owns *what the metrics mean to the business*, which is exactly what's being decided when a disagreement comes up — "is this a real new metric the team needs, or noise?" I built the semantic layer and the orchestrator, so technically I could just add new entries on my own — but that would put me in the position of unilaterally deciding which business metrics exist, which isn't my call. Product is the right gate for that judgment. Once they ratify, I add the entry and the orchestrator picks it up on the next run.

**"What stops bad definitions from being persisted back if the loop is enabled?"**
Five gates in order. First, the cluster threshold — has to be ≥3 occurrences from ≥2 distinct users in 7 days, so one weird question doesn't drive a PR. Second, the equivalence test — the proposed YAML has to compile, run against BQ, and match the reference raw SQL within 0.5%. Third, the PR is *draft only* — human marks Ready. Fourth, the CI guard workflow asserts the PR is draft and the body contains the equivalence proof table. Fifth, hard constraints — only ADD measures, never modify or delete, only `model/*.yml` files touched. The agent path never gets to ratify itself; it only proposes through a path with five filters in front of it.

**"Why not just use the context-engineered agent everywhere? It's more flexible."**
Fair question. Two reasons to keep the Cube layer in the mix anyway. First, auditability and consistency: stakeholders need to trust that "active panelist" means the same thing on Monday as it does Friday — the semantic layer is the source of truth that survives between calls; a per-call agent judgment doesn't give you that. Second, the Cube layer is row-capped at 5K and PII-protected as a governance property; the raw path is unrestricted, which is the right tool for exploration but not for routine answers. The deterministic path is the rail; the agent path is the explorer. Hybrid lets us have both, and the set of "where definitions exist" grows on its own once the auto-improve flag flips.

**"How do you measure whether the growth loop is working?"**
Headline metric: the rate of `SAME_INTENT_SAME_RESULT` verdicts. As ratified candidates land in the Cube layer, that number trends up — the flywheel is working. Secondary: coverage-gap rate, net-new measures ratified per week, time-to-resolution on flagged disagreements, downstream accuracy on recurring questions.

**"Is the orchestrator in production?"**
The two backends and the orchestrator with reconciliation are in production today, serving real traffic. The auto-update loop is gated off behind `CP_AUTO_IMPROVE_ENABLED=true`, which is currently false. The manual disagreement review with product is the workflow running today.

**"Could this approach scale to Walmart-wide?"**
That's the version of this I want to be building. At my current scope, the Cube layer is one team's metrics. The architecture doesn't change at enterprise scale — what changes is the governance around the review gate (who's authorized to ratify new measures in which domain) and the partitioning of the semantic layer by ownership boundary. The growth loop holds. Honestly, the bigger the scope, the more valuable the loop becomes, because manually maintaining a semantic layer across the enterprise surface is exactly what doesn't scale.

### Numbers — what you have, what's still TBD
- ✅ **Customer Voice scale:** 1.1M panelists (~773K active), 158M task rows, 32K surveys, 23 cubes across 5 domains.
- ✅ **Reconciliation:** 0.5% numeric tolerance, 5 verdict types, parallel sub-agent dispatch.
- ✅ **Auto-update loop (built, gated):** SHA-256 cluster_id, ≥3 occurrences from ≥2 users in 7 days, cube-gap-filler skill, equivalence test (0.5%), draft PR with provenance, 6 safety rails, env flag default-off.
- 📌 **Cube agreement rate today** — what % of user questions land `SAME_INTENT_SAME_RESULT` vs `COVERAGE_GAP`. Strongest single thing you can add if you have it.
- 📌 **Disagreements logged so far** — if you've been collecting them, a count strengthens the "the data is there for the loop to fire on" framing.

## 4. What's the autonomous data analyst?

> Note: this is a TMAY-planted hook — your opener names it explicitly, so the panel may grab it directly. The strongest framing is *sibling to the Jira agent on the same substrate, opposite HITL posture*. That contrast lets you teach the panel something about when each pattern applies — a Principal-level signal — instead of just describing another system.

**Beats**
- *Where it sits in the stack.* Sibling to the Jira agent on the same cp-platform context layer + MCP substrate. Different surface: instead of routing through me on a Jira ticket, business users dispatch it directly inside Wibey (our internal Claude Code equivalent) as the `cp-analytics` skill.
- *The business problem.* Even after the Jira agent absorbed the response work, I was still the rate-limiter on novel exploration — users had to come to me to get started. This was the next leverage step: take me out of the loop on the read path entirely.
- *Scope.* Operates across the **full 68-table cp-platform surface (1,350+ columns)** via the MCP. The MCP injects schema, joins, and domain context per dispatch — no hardcoded schemas.
- *The architecture.* Pure orchestrator pattern — the skill itself **never runs Bash directly**, only Read/Write/Glob/Grep/Task. Each analytical idea is dispatched to a Task sub-agent with its own isolated context. Three wins from that: context isolation (large SQL results from one idea don't pollute another's reasoning), autonomy (sub-agents execute BQ commands without triggering CLI safety prompts), crash recovery (`session.json` + `backlog.json` survive any failure; `/cp-analytics resume` detects mid-flight crashes).
- *REFLECT scoring (the depth engine).* After each idea completes, findings get scored: **Score = Impact × Surprise × Gaps.** Impact 1-3 by panelist count (<1K / 1K-50K / 50K+), Surprise 1-3 (expected / somewhat unexpected / contradicts assumptions), Gaps 0-1 (actionable / unanswered "why?"). **Score ≥4 triggers an immediate depth idea** (IDEA-002 → IDEA-002-D1 → IDEA-002-D1-D2). Stops at max_depth or when findings are directly actionable.
- *SQL traceability as a contract.* Every analysis produces `execution.json` with **complete, copy-paste executable SQL** for every query. Post-Dispatch Validation enforces it — fully-qualified tables, no ellipses, no pseudo-code, > 50 chars. Violations are blocking errors. Every number traceable to runnable SQL.
- *Composable ecosystem.* `cp-analytics` produces. **`cp-audit`** validates across 6 layers (SQL schema, SQL logic, interpretation, prose arithmetic, cross-analysis, evidence chain, reproducibility) → PASS / WARN / FAIL. **`cp-fix`** remediates in dependency order (sql_rewrite, recalculation, artifact_repair, limit_expansion, narrative_rewrite, chart_regeneration), snapshots originals before modifying, re-dispatches cp-audit after. **`cp-context-validate`** regenerates schema ground truth daily from BigQuery `INFORMATION_SCHEMA.COLUMNS`.
- *Idea generation.* When the backlog is exhausted, the orchestrator collects existing questions, identifies gaps (tables never analyzed, under-explored categories, recommendations to validate), generates 15 candidates, deduplicates, keeps the best 10. New ideas are queued for next invocation, not run in the same session.
- *Why "autonomous."* No human in the loop on the read path. Validation happens inside the agent — schema correctness against the context layer, intent matching against historical query patterns, and the post-dispatch validation contract on the SQL itself. Answer ships directly to the user.
- *Adoption proof.* **57 cp-analytics analyses powered by the platform.** The only AI skill currently in active use by business teams across Data Ventures. Approved by Director + product leadership.

**Draft**

> The autonomous data analyst is the sibling to the Jira agent, sitting on the same cp-platform context layer and MCP I described earlier. Different surface, though — instead of business users filing a Jira ticket that I'd answer, they dispatch the `cp-analytics` skill directly inside Wibey, our internal Claude Code equivalent, and get the answer back themselves.
>
> The business problem was that even after the Jira agent absorbed the response work, I was still the rate-limiter on anyone doing novel exploration. So this was the next leverage step: take me out of the loop on the read path entirely.
>
> Scope-wise it operates across the full 68-table cp-platform surface — about 1,350 columns — via the MCP. The MCP injects schema, joins, and domain context per dispatch, so nothing is hardcoded. New tables get added once they're documented in the context layer with the same validation guarantees the rest of the catalog has.
>
> Architecturally it's a pure orchestrator. The skill itself never runs Bash directly — only Read, Write, Glob, Grep, and Task. Every analytical idea is dispatched to a Task sub-agent with its own isolated context. Three reasons that matters. Context isolation — large SQL results from one idea don't pollute another's reasoning. Autonomy — sub-agents execute BigQuery commands without triggering CLI safety prompts every time. Crash recovery — `session.json` and `backlog.json` survive any failure; `/cp-analytics resume` detects mid-flight crashes and picks up where the session left off.
>
> The depth-first engine inside it is what I call REFLECT scoring. After each idea completes, findings get scored on three dimensions — impact, by panelist count; surprise, on a three-point scale where 1 is expected and 3 contradicts assumptions; and gaps, which is a binary on whether the finding leaves an unanswered "why?". Score equals impact times surprise times gaps. If the score is four or higher, the orchestrator immediately generates a depth idea — IDEA-002 spawns IDEA-002-D1, which can spawn D2 — and executes it before moving to the next top-level idea. Stops at max-depth or when findings are directly actionable. That's the heuristic that turns multi-hypothesis exploration into something deterministic instead of letting the agent wander.
>
> The validation contract on every analysis is something I built explicitly. Every analysis produces an `execution.json` file with the complete, copy-paste executable SQL for every query — fully qualified table references, no ellipses, no pseudo-code, longer than fifty characters. The post-dispatch validation step enforces it as a blocking error — if the SQL isn't traceable, the idea doesn't proceed. That means every number in every report is auditable back to its source query, which is the foundation for the audit-fix loop on top.
>
> That ecosystem is composable by design. `cp-analytics` produces analyses. `cp-audit` validates them across six layers — SQL schema, SQL logic, interpretation, prose arithmetic, cross-analysis consistency, and evidence chain — and returns PASS, WARN, or FAIL. `cp-fix` consumes audit findings and remediates them in dependency order — SQL rewrites, recalculations from CSVs, narrative fixes for causation overreach, chart regenerations — snapshots originals before modifying, and re-dispatches `cp-audit` after to verify the fix landed. `cp-context-validate` is the substrate beneath all of them, regenerating the schema ground truth daily from BigQuery's INFORMATION_SCHEMA. Each skill does one thing. The whole loop runs without me.
>
> The autonomy point matters because of the contrast with the Jira agent. On the Jira agent, my review sits outside the loop because the cost of a wrong stakeholder message is high. The autonomous data analyst is different — it ships answers directly to users with validation happening inside the loop, and the audit-and-fix cycle running on top catches anything that slips through. Same substrate, different posture, sized for a different cost profile.
>
> On adoption: 57 analyses powered by the platform, approved by my Director and product leadership, and it's the only AI skill currently in active use by business teams across Data Ventures.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Sibling to the Jira agent on the same substrate, different HITL posture"* — opens the platform-thinking question. **Strongest line.**
2. *"REFLECT scoring — Impact × Surprise × Gaps, score ≥4 triggers a depth dive"* — opens the architecture deep-dive. Engineering panelists will pull this; the formula is name-able.
3. *"SQL traceability is enforced as a contract, not optional documentation"* — opens the reliability / how-do-you-trust-an-agent question.
4. *"cp-analytics produces, cp-audit validates, cp-fix remediates, cp-context-validate maintains ground truth — each skill does one thing"* — opens the composable-ecosystem question. **Principal-level signal — Unix-philosophy platform design.**
5. *"The only AI skill currently in active use by business teams in Data Ventures"* — opens the adoption / why-this-and-not-others question.

### Anticipated follow-ups

**"How is this different from the Jira agent?"**
Different surface, different HITL posture, different user. Jira agent serves stakeholder requests that route through me; my review sits outside the agent loop because the cost of a wrong stakeholder reply is high. The autonomous data analyst serves direct user exploration; the user runs the query, the blast radius of a wrong answer is small — their own next decision — so the HITL stays inside the loop (validation contract, cp-audit, cp-fix). Same substrate underneath. Different agent for a different cost profile.

**"What does the sub-agent orchestration actually look like?"**
A pure orchestrator that never runs Bash. It dispatches each analytical idea as a Task with isolated context. The sub-agent gets the user question plus the relevant slice of the cp-platform MCP (schema, joins, domain context). It writes SQL, executes via the MCP's `cp_query`, validates against the schema, writes the CSV, generates the chart, returns findings. The orchestrator scores the findings with REFLECT and decides whether to spawn a depth idea or move on. Crash recovery is a primary feature — `session.json` plus `backlog.json` are the source of truth, and `/cp-analytics resume` is a real command.

**"Why context isolation? What does that buy you?"**
Two things. Token cost — nobody's holding 68 tables' worth of schema in context if they only need 2 for this question, which keeps per-query cost low. And isolation in the reasoning sense — if the SQL-generation sub-agent makes a wrong assumption about a column, the next sub-agent doesn't inherit it. The validator reads the query and the source independently. Same logic as code review: the reviewer should be checking the code against the requirement, not co-anchoring with the author.

**"How do you validate the answers without a human in the loop?"**
Three layers. First, structural — the SQL is checked against the cp-platform context layer (52-node, 63-edge join graph, 36+ verified join paths, 89 indexed domain sections). Second, the SQL traceability contract — every query has to be fully-qualified, runnable, complete; violations are blocking. Third, the audit-fix loop running on top — `cp-audit` re-validates the whole analysis across 6 layers and `cp-fix` remediates in dependency order, with `cp-audit` re-dispatched after every fix. So the validation runs three times across three different layers before an analysis is considered done.

**"What kinds of questions can it handle?"**
Multi-hypothesis exploration — "what's driving the drop in completion rate for new panelists" — where the agent spawns hypotheses, scores each finding with REFLECT, and spawns depth ideas off any score ≥4. Simple aggregations and join-heavy questions work obviously. Things it appropriately declines: questions that need tables outside the cp-platform catalog, or questions where the answer requires business context only a human has — those get flagged and routed back.

**"Why 'pure orchestrator'? Why not just let the orchestrator run Bash?"**
Two reasons. First, the CLI safety prompts — every Bash call requires permission in Wibey; you can't ship a fully autonomous skill if half its actions need approval. Pushing Bash into sub-agents avoids that. Second, separation of concerns — the orchestrator's job is *coordination* (dispatch, scoring, depth decisions, session management), not *execution*. Sub-agents are the execution layer. Keeps the orchestrator's reasoning clean and the failure modes localized.

**"What's the approval story?"**
Approved by my Director and product leadership before it shipped as the only AI skill in active use by business teams in Data Ventures. *[TO FILL IN — what they needed to see, the gate, what pushback you handled, what trade-offs you made to get to yes.]*

**"What about adoption numbers — queries per week, who's using it?"**
57 analyses powered by the platform, plus the broader cp-platform substrate powering the Jira agent, KPI monitor, hybrid orchestrator, and the Slack `/cp` bot. *[TO FILL IN — pin down active-user count and per-week analysis volume.]*

**"How would this work at Walmart scale?"**
The architecture is the part that scales — sub-agent orchestration with isolated context plus a per-domain MCP plus a composable audit-fix ecosystem is the right shape for an enterprise data surface, because the alternative (one monolithic agent holding the whole schema) doesn't scale at all. What changes at scale is the substrate — context layers per domain, governance for who owns each domain's MCP, partitioning of the audit rules by ownership boundary. The pattern transfers; the governance is the new work.

### Short version (if cut for time, ~60 sec)

Sibling to the Jira agent on the same cp-platform substrate (68 tables, 1,350+ columns via the MCP) → delivered as a Wibey skill, users dispatch directly → pure orchestrator pattern (never runs Bash, only Read/Write/Glob/Grep/Task; sub-agents execute) → REFLECT scoring (Impact × Surprise × Gaps, ≥4 triggers depth) → SQL traceability enforced as a blocking contract → composable cp-audit (6-layer validator) + cp-fix (autonomous remediation) on top → only AI skill in active use by business teams in DV, 57 analyses powered.

### Numbers / proof points to nail before the interview
- ✅ **Scope:** 68 tables, 1,350+ columns via the cp-platform MCP.
- ✅ **REFLECT formula:** Impact × Surprise × Gaps, threshold 4, max-depth-bounded.
- ✅ **Adoption signal:** 57 analyses powered, only AI skill in active business-team use in DV.
- 📌 **Active users / queries per week** — pin down before Monday.
- 📌 **The Director + product leadership approval moment** — what they needed to see, what pushback.
- 📌 **3-4 concrete example questions** — for the "what can it do" follow-up.

## 5. You're already doing agent work at Walmart — why move?

> Note: this is the question your TMAY explicitly tees up ("scoped to one team today"). Land it confidently — if this reads as defensive or evasive, the rest of the interview gets read through that lens. **Lead with the pull, not the push.** Stay positive about Data Ventures — panelists likely know your current team.

**Beats**
- *Lead with the pull.* Agent Builder is the platform shape I've been reaching for inside Data Ventures. Every system I've shipped in the last 18 months has the same architecture — thin agent on a reusable substrate. Pattern works. But the substrate I built serves one team. The leverage version is a framework other people ship on top of, at enterprise scope.
- *Why this role specifically.* The JD reads like the work I've been doing already — biz/tech generalist, owns end-to-end, biased for action, first-principles thinking. Not a stretch — the version of my current work where the surface area matches the solution shape.
- *Why now.* What I shipped in 2025 — V1→V2, the Jira agent, the autonomous data analyst, the hybrid orchestrator — is the proof I can operate at platform shape. Making a Difference Award was the inflection point.
- *Respect piece.* Not running away from DV. DV is where I figured the platform pattern out — they gave me the runway to fail fast on V1, ship V2, and prove the substrate works across **7+ downstream consumers including a Slack `/cp` bot.** The move is to do that work at the scope it was sized for.

**Draft**

> The honest answer is what the role is, not what I'm leaving. Agent Builder is the platform shape I've been reaching for inside Data Ventures already. Every system I've shipped over the last 18 months has the same architecture — a thin agent on a reusable substrate, where the substrate is the asset and each new agent is just the next thin thing built on top. That pattern works. But the substrate I built at Data Ventures serves one team's surface area. The leverage version is a framework that other people ship on top of, at enterprise scope. That's Agent Builder.
>
> When I read the job description, it reads like the work I've been doing already — biz/tech generalist, owns problems end-to-end, biased for action, first-principles thinking. That's how I've been operating, just at smaller scope. So this isn't a stretch role for me — it's the version of my current work where the surface area matches the solution shape.
>
> On timing — what I shipped in 2025 is what gives me confidence to make this move now rather than speculate about it. V1 to V2 was the lesson. The Jira agent, the autonomous data analyst, the KPI monitor, the Slack `/cp` bot, and the cp-business / cp-discovery / cp-hybrid skills were the validation that the platform pattern repeats — seven-plus downstream consumers on one substrate. The hybrid orchestrator was proof I can build the platform itself, not just agents on top of it. The Making a Difference Award earlier this year was a useful signal — what I'd been doing got recognized as worth doing. The next step is to do it where the scope of the problem matches the shape of the solution.
>
> And to be clear about Data Ventures: I'm not running away. DV is where I figured this whole pattern out — they gave me the runway to fail fast on V1, ship V2, and prove the substrate works across seven-plus downstream consumers. I want to take what I learned there and apply it at the scope it was always headed toward.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Thin agent on a reusable substrate, where the substrate is the asset"* — opens the platform-thinking question. Maps directly to Agent Builder's "framework other teams build on" framing. **Strongest line.**
2. *"Seven-plus downstream consumers on one substrate"* — concrete proof of the pattern repeating.
3. *"This isn't a stretch role for me"* — confident, opens the why-are-you-ready / Senior-DA-to-Principal question (Q6 territory). Pre-empts the title objection.
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
Three things. First, Walmart-internal context — the data systems, the stakeholder language, the political shape of how things actually get done across teams. Second, a working model of the substrate pattern that's already proven at Walmart scope (one team, 7+ downstream consumers), so I know what's likely to repeat at enterprise scope and what won't. Third, a working evaluation methodology — the golden set + reusable eval harness + the 18-experiment evaluation framework — that's transferable to whatever the Agent Builder team is building.

**"What concerns you about the move?"**
*[NOTE: this is Q14 territory — full answer there. Quick version if asked here: scope shift means new stakeholders, new domains, longer time-to-first-shipped-thing. Mitigation is the substrate pattern itself — I know how to ramp on a new domain because that's exactly what the context layer is for.]*

**"How is this a Principal-level move from Senior DA?"**
*[NOTE: this is Q6 — full answer there. Quick bridge if asked here: the title hides what I've shipped. The Principal-level signals — system design, end-to-end ownership, multi-month solo builds, leverage thinking — are what I've been doing. Title is the lagging indicator.]*

### Numbers / proof points to nail before the interview
- ✅ **Downstream consumers on the cp-platform substrate: 7+** — cp-analytics, jira-ticket-worker, simple-cp-interaction, kpi-monitor, customer-voice-semantic-layer (cube-gap-filler), Slack `/cp` bot, cp-business / cp-discovery / cp-hybrid skills. Plus three distribution mechanisms: Wibey MCP, Wibey skill registry, Code Puppy agent marketplace, Python library imports.
- 📌 **Stakeholder reach** — how many people across DV use the systems today.
- 📌 **Manager-conversation status** — only number that matters here is "did you have it yet, and if so when" — write the answer for yourself before the interview so you're not improvising.

## 6. Senior Data Analyst → Principal SWE — why are you ready?

> Note: this is the title-objection pre-empt. The panel will be looking for whether you're defensive, hand-wavy, or grounded. Lead with the work, not with apology. The strongest move is to make the title gap feel like *their* observation to verify, not *your* problem to explain away.

**Beats**
- *Honest frame.* Title says Senior DA. The work doesn't. Put 2025 next to the JD and you're looking at Principal-level outputs under a DA title.
- *The five signals.* **System design** (V1→V2, cp-platform context layer + MCP, hybrid orchestrator). **Leverage** (one substrate, 7+ downstream consumers). **End-to-end ownership** (every system shipped solo, design through production). **Multi-month solo builds** (V2, the orchestrator, the autonomous data analyst — each a multi-month effort). **Evaluation rigor** (golden set + reusable eval harness + 18 architecture experiments across 5 phases scored on accuracy / latency / cost / consistency + 5 daily drift validators with auto-doc-regen).
- *Why the title hasn't moved.* DV is structured as a DA team — the role grew into platform work because that's what the team needed, but the org chart didn't follow. Org constraint, not capability gap.
- *Internal recognition.* Making a Difference Award earlier this year for 2025 work — leadership signaling the work is over the title.
- *Confident close.* This isn't a stretch up. It's a calibration to where the work already is. Title is the lagging indicator; shipped systems are the leading one.

**Draft**

> The honest frame on the title question is that the title says Senior Data Analyst and the work doesn't match. If you take what I've shipped over the last 18 months and put it next to the Agent Builder JD, you're looking at Principal-level outputs — they just happened under a DA title.
>
> The signals I'd point to. First, system design. V1 to V2 was a full architectural rethink — I tore down a working text-to-SQL app and rebuilt it as the cp-platform context layer plus MCP. That's not analyst work, that's platform work. The hybrid orchestrator is a multi-backend system design with a self-growing feedback loop — again, not analyst scope.
>
> Second, leverage. Seven-plus downstream consumers on one substrate — cp-analytics, the Jira agent, simple-cp-interaction, the KPI monitor, customer-voice-semantic-layer, a Slack bot, and the cp-business / cp-discovery / cp-hybrid skills. The whole point of the V1 → V2 lesson was figuring out that the asset is the substrate, not the agent on top. That's platform thinking, which is exactly what the role is asking for.
>
> Third, end-to-end ownership. Every system I just named was solo — design, build, deploy, validation, rollout to stakeholders. There's no point where I handed something off and watched someone else finish it.
>
> Fourth, multi-month solo builds. V2 was a [NUMBER? months]-long rebuild, the hybrid orchestrator was a [NUMBER? months]-long build, the autonomous data analyst was a multi-month effort on top of that. Those aren't sprint-scope problems — they're staff-level engineering efforts I owned beginning to end.
>
> Fifth — and this is the one that doesn't usually show up in a Senior DA portfolio — evaluation rigor. The platform doesn't just have a golden set and a reusable eval harness across every agent on the substrate. It has an 18-experiment evaluation framework across five phases — baselines, quick wins, RAG optimization, agent architecture, system design — scoring approaches on accuracy, latency, cost, and consistency. And it has five daily drift validators against live BigQuery — schema, enums, joins, table inventory, DDL cross-reference — with a three-tier LLM fallback (Wibey Opus → Sonnet → Gemini 2.5 Pro) auto-regenerating docs when drift gets detected. None of that is reactive — it's the platform maintaining itself.
>
> The reason the title hasn't moved is structural, not capability-driven. Data Ventures is organized as a DA team — the role grew into platform work because that's what the team needed, but the org chart didn't follow. I haven't pushed hard internally for a title change because it would mean restructuring how DV thinks about its headcount, which isn't my fight to pick. The Making a Difference Award earlier this year was leadership's way of saying *the work is over the title* — but the title itself is sticky for org reasons that have nothing to do with what I'm actually capable of.
>
> So when I look at the Agent Builder role, this isn't a stretch up — it's a calibration to where the work already is. The systems are shipped, the pattern is proven, and the panel can verify the outputs directly. The title is the lagging indicator. The shipped systems are the leading one.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"Title is the lagging indicator; shipped systems are the leading one"* — quotable, opens the calibration / signal question. **Strongest line.**
2. *"Seven-plus downstream consumers on one substrate"* — opens the platform-leverage follow-up. Maps directly to the Agent Builder mandate.
3. *"18-experiment evaluation framework across 5 phases"* — opens the rigor / methodology follow-up. **Strongest Principal-level signal you can plant** — uncommon for a Senior DA portfolio.
4. *"Five daily drift validators with auto-doc-regen via three-tier LLM fallback"* — opens the platform-maturity follow-up. Shows the substrate maintains itself.
5. *"Multi-month solo builds — staff-level engineering efforts I owned beginning to end"* — opens the scope / Principal-signal question.
6. *"The work is over the title"* — opens the org-constraint / why-not-promoted-internally follow-up.

### Anticipated follow-ups

**"What are the 18 experiments?"**
Five phases. Phase 1 baselines — full context stuffing at ~660K tokens, raw RAG, full MCP agent. Phase 2 quick wins — partial stuffing, RAG for historical SQL, prioritized ordering. Phase 3 RAG optimization — chunk-size sweeps (256, 512, 1024, 2048), hybrid search with reranking, query decomposition. Phase 4 agent architecture — structured plan versus RAG-as-tool versus consolidated tools, sqlglot SQL parser, parallel tool execution. Phase 5 system design — RAG-Generate-then-MCP-Validate two-stage, tiered router (simple → RAG, complex → MCP), cached MCP plus enriched RAG. Each scored on accuracy, latency, cost, consistency. Some are shipped (cp-platform itself is the synthesis), some are in evaluation.

**"How does drift detection actually work?"**
Five validators run as a 6 AM daily cron against live BigQuery. `check_schema.py` diffs BQ schema vs the curated `tables.md` to catch new, changed, or dropped columns. `check_enums.py` validates documented enum values against `SELECT DISTINCT` results. `check_joins.py` tests every confirmed join path by executing it. `check_tables.py` is a table-inventory count. `check_ddl.py` cross-references BQ schema against the Azure SQL DDL in the engineering repos. Output is JSON to `context/validation.log`; drift feeds into the next `doc_generator.py` run, which auto-regenerates the affected docs via a three-tier LLM fallback — Wibey Opus first, Sonnet on timeout, Gemini 2.5 Pro on second failure. So docs never go stale silently and the regen path never blocks on a single LLM being unavailable.

**"Why didn't you push for a title change at Walmart first?"**
Two reasons. First, DV's headcount is structured around DA roles — moving my title would mean restructuring how the team thinks about its allocation, which is a much bigger conversation than my career path. Second, I'd rather have the work argue for me than argue for the work. If the systems aren't convincing on their own, a different title wouldn't fix that. The Making a Difference Award was the cleanest internal signal — leadership recognizing the work is over the title without formally adjusting it.

**"What's the gap between Senior DA and Principal SWE you're aware of?"**
The honest gap is breadth. I've built deep on one team's problems — the substrate is proven at one team's surface area, not at enterprise scope. The mitigation is the substrate pattern itself: I built the context layer because I needed to ramp on a new domain quickly, and that's exactly what makes ramping on the next domain faster. Principal scope means more domains, more stakeholders, more partner teams — and the patterns I've already proven transfer. What I haven't done is operate that pattern at enterprise scope, but that's the role, not a prerequisite for it.

**"Have you ever managed engineers?"**
Not formally. I've owned cross-functional dependencies — product team scoping, DS team owning the production service account, business stakeholders on adoption — but I haven't had direct reports. I'd want to be honest about that as I scale into Principal scope. The leverage I've built so far has been through systems, not through people, and stepping into Principal here means making sure I can do both. My read of the JD is that the role is principal *engineer*, not principal *manager* — the leverage expectation is through architecture and platform, which is where my track record is.

**"What's the strongest single piece of evidence you'd point to?"**
The hybrid orchestrator. It's the cleanest end-to-end ownership signal in the portfolio — multi-month solo build, novel architecture, reusable eval harness, validated against a golden set, in production this week, with a complete auto-improve loop engineered and gated behind an env flag. If you want a single artifact that says "this person is operating at platform scope," that's it.

**"Could this be a Senior SWE role instead — why Principal?"**
Fair question, and I'd be open to whatever calibration the panel lands on. My read is that the JD specifically asks for first-principles thinking, end-to-end ownership, and biz/tech generalism — those read as Principal-coded asks. And the substrate-on-which-others-build framing in the JD is platform work, which is also Principal-coded. But I'm not married to the title — I'm reading the work and saying my shipped systems match it. If the panel calibrates differently, I want to hear that read and understand it.

**"What's something Principal-level you haven't done yet?"**
Operating the substrate pattern across multiple team boundaries simultaneously. I've proven it on one team's surface area; the version where the substrate has to serve multiple downstream teams with different ownership boundaries, different governance, different SLAs — that's the next ring out, and that's exactly what Agent Builder is. So the honest answer is: I haven't done it yet, but that's the role, not a gap I'd need to close before I started.

### Numbers / proof points to nail before the interview
- ✅ **Downstream consumer count on the substrate: 7+** (the list above)
- ✅ **18-experiment framework across 5 phases**, scored on accuracy / latency / cost / consistency
- ✅ **5 daily drift validators**, auto-doc-regen via 3-tier LLM fallback (Wibey Opus → Sonnet → Gemini 2.5 Pro)
- ✅ **57 cp-analytics analyses powered by the platform**
- 📌 **Duration of each multi-month build** — V2 rebuild, hybrid orchestrator, autonomous data analyst. Pin down before the interview.
- 📌 **DA team size at DV** — useful color for "I'm the platform person on a team that wasn't built as a platform team."
- 📌 **MAD Award framing** — confirm the citation language if you can pull it.

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
- *The recovery (kept short).* V2 tore the frontend out. Decomposed V1 into a reusable cp-platform context layer + MCP, delivered as a skill inside Wibey — internal Claude Code equivalent — where engineers already worked. Same substrate now powers **7+ downstream consumers including a Slack `/cp` bot.**
- *The lesson.* Adoption is a product problem, not a technology problem. Second-order — the part that actually changed how I work — the reusable asset usually isn't the thing the user touches; it's the substrate underneath. Every system I've shipped since has been a thin agent on a reusable substrate.

**Draft**

> The clearest failure I can point to is something I shipped last summer. V1 of a text-to-SQL RAG app — a frontend where business teams could ask questions in English and get back SQL against BigQuery, with vector retrieval over historical queries grounding the model. Technically it worked. I demoed it to senior leadership and the product teams. It just didn't get used.
>
> The reason it didn't get used was a call I made early and didn't go back and validate. I'd scoped it as a product problem and built a new frontend. But the business teams I was building it for already lived in Slack, Jira, and BigQuery's native UI — and I was asking them to leave those tools and come over to mine. There was no forcing function for that switch, and I hadn't actually tested whether the surface was the part worth building. So I shipped a working system that solved a problem nobody was choosing to bring me. Months of build, with the daily-active number staying near zero.
>
> The reflection took a while to land. My first instinct was to assume the model needed to be better, or that I needed more training data, or that the demos hadn't been compelling enough. The thing I missed for too long was that the blocker wasn't the system — it was the surface I'd put it behind. The valuable piece, the curated context that grounded the LLM's answers, was the part nobody could see, because it was wrapped in a frontend nobody used.
>
> The recovery was V2. I tore the frontend out and rebuilt the system as the cp-platform context layer plus an MCP, delivered as a skill inside Wibey — our internal Claude Code equivalent, which is where the engineers already worked. The same substrate now powers seven-plus downstream consumers — the autonomous data analyst, the Jira agent, the KPI monitor, the hybrid orchestrator, the simple-cp-interaction skill, a Slack `/cp` bot, and the cp-business / cp-discovery / cp-hybrid skills. So the failed app ended up turning into a multi-consumer substrate because the second time around I built the abstraction, not the product.
>
> The lesson I carry is twofold. First-order: adoption is a product problem, not a technology problem — meeting people where they already work matters more than how clever the underlying system is. Second-order, and this is the one that actually changed how I work — the reusable asset usually isn't the thing the user touches, it's the substrate underneath. Every system I've shipped since V1 has been a thin agent on a reusable substrate. That pattern came directly from V1 not landing.

**Hooks planted (ranked by likelihood they get pulled)**
1. *"A call I made early and didn't go back and validate"* — opens the decision-process / how-do-you-test-assumptions follow-up. Principal-level signal — answers "do you learn from your own mistakes" with a specific cognitive failure, not just an outcome.
2. *"The valuable piece was the part nobody could see, because it was wrapped in a frontend nobody used"* — quotable, opens the architecture follow-up. Bridges naturally into Q15 / context-layer territory if not already used there.
3. *"The reusable asset usually isn't the thing the user touches"* — opens the platform-thinking question. Maps directly to Agent Builder.
4. *"My first instinct was to assume the model needed to be better"* — opens the self-correction follow-up. Shows you can name your own bias.

### Anticipated follow-ups

**"When did you actually realize V1 wasn't going to land?"**
*[TO FILL IN — concrete moment makes the reflection feel real. Candidates: a specific 1:1 with a stakeholder saying "yeah it's cool but I'd have to remember to use it," a usage dashboard showing flat DAU for N weeks, a moment where you watched yourself answer a question in Slack instead of opening the tool you'd built.]*

**"How long did you keep trying to fix V1 before deciding to rebuild?"**
*[TO FILL IN — be honest. The right answer is whatever the real number is.]*

**"What kept you from validating the surface earlier?"**
Honest answer: I was excited about the model and the retrieval. I treated the frontend as the obvious wrapper and didn't interrogate whether it was the right wrapper. The mistake wasn't *missing the data* — adoption was visibly flat — it was that I'd anchored on "the system needs to be better" before I'd considered "the system is fine, the placement is wrong." The reason I now ship into existing surfaces by default — Wibey, Jira, Slack — is V1.

**"What would you do differently if you started V1 over?"**
Two things. First, validate the surface before building the system — even a stub deployed into Wibey or Slack would have shown me whether the *placement* mattered before I sunk months into a frontend that didn't. Second, design for the abstraction earlier — V1 was a monolith because I was thinking like a product builder; if I'd designed the context layer as a first-class API from day one, the rebuild would have been weeks not months.

**"Is the failure that V1 didn't get adopted, or that you didn't predict it wouldn't?"**
Fair distinction, and it's the second one. Lots of v1s don't land — that's expected. The failure is that the *reasons* it didn't land were knowable before I started building, and I didn't make space to ask the right questions. That's the part I own.

**"Have you applied this lesson somewhere else since?"**
Yes — explicitly. Every system I've shipped since V1 has gone into a surface someone already uses, and is built as a thin agent on a reusable substrate. The Jira agent goes into Jira. The autonomous data analyst goes into Wibey. The KPI monitor pings Slack. The semantic-layer agent fronts an interface engineers already query. That's the V1 lesson operationalized.

**"Did V1 ever come back in any form?"**
Yes — as a *tool*, not as a product. The original RAG over historical SQL is now one of the tools exposed through the MCP in V2 (`cp_search_sql`, hybrid Gemini + BM25 + RRF over 313 indexed queries). So the technical work wasn't wasted — it just had to be repackaged into something other agents could use, instead of something a user had to come visit.

### Short version (if cut for time, ~60 seconds)

Hit only: shipped V1 of a text-to-SQL RAG app with its own frontend → adoption stalled because I'd asked users to leave the tools they already lived in → mistake was anchoring on "the system needs to be better" instead of "the placement is wrong" → V2 was a context layer + MCP delivered as a skill into Wibey, where engineers already worked → that same substrate now powers 7+ downstream consumers including a Slack bot → the lesson that changed how I work: the reusable asset usually isn't the thing the user touches, it's the substrate underneath.

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

1. **Early Jira agent iteration that miscarried.** Did any early version of the Jira agent produce a wrong answer that went to a stakeholder before you added Investigation Branches? If yes, this is a strong backup — it's about agent reliability, which is on-topic for Agent Builder, and the recovery (Investigation Branches as encoded debugging knowledge) is in your Q2 answer.

2. **Cube.js semantic layer onboarding miss.** When you first onboarded the semantic-layer agent, did you assume adoption would follow naturally and have to course-correct on definition ownership or stakeholder engagement? Strong backup because it's a different failure shape (governance/scoping) from V1→V2's (surface/placement).

3. **An earlier dashboard or analytics deliverable that nobody used.** Any pre-agent work where you shipped something polished and watched it not get adopted? Structurally similar to V1→V2 but with different stakes — if it predates the agent work, it shows the V1 lesson was actually *re-learned*, which is honest and human.

4. **Misjudging the scope of one of the multi-month builds.** Did you underestimate any of V2, the orchestrator, or the autonomous data analyst — committing to a timeline you couldn't hit, or scoping the first version too ambitiously? Different failure shape (estimation / scope discipline) — a Principal-level failure mode the panel will recognize.

**Once you pick one and give me a few details, I'll draft the backup at the same level of polish as the primary.**

### Numbers / proof points to nail before the interview
- 📌 **The "when I realized V1 wasn't landing" moment** — a concrete date / meeting / metric. Strongest single thing you can add to the primary.
- 📌 **V1 build duration** — months from start to demo. Sets the scale of the failure.
- 📌 **V2 build duration vs. V1** — gives the recovery a comparable timeframe.
- 📌 **V1 actual usage numbers** — even rough ("near zero weekly active users" is fine if true).
- ✅ **7+ downstream consumers** on the V2 substrate (confirmed).

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
- *V2.* Stopped building an app, started building a platform. Decomposed V1 into the **cp-platform context layer + MCP (14 tools + 4 read-only resources)**, delivered as a skill inside Wibey (the internal equivalent of Claude Code). Original RAG became `cp_search_sql`, one tool exposed through the MCP. Same substrate now powers **7+ downstream consumers — 68 BigQuery tables, 1,350+ columns, 226 ChromaDB chunks, 313 indexed historical queries, 89 domain sections, 36+ verified join paths, a 52-node, 63-edge knowledge graph, 57 cp-analytics analyses powered.**
- *Self-maintaining substrate.* 5 daily drift validators (schema, enums, joins, tables, DDL) auto-trigger doc regen via a 3-tier LLM fallback (Wibey Opus → Sonnet → Gemini 2.5 Pro). The substrate maintains itself.
- *Flagship tool.* `cp_generate_validated_sql` — full Gemini 2.5 Pro NL→SQL with Gemini 2.5 Flash function-calling validation, dry-run, execute, all in ~60s.
- *The lesson.* Adoption is a product problem, not a technology problem. One failed app turned into a multi-consumer substrate because the second time I got the abstraction right.

**Draft**

> What I want this panel to remember is that I'm passionate about AI, I move fast on new techniques, and I'm willing to learn from my own mistakes in a way that changes the architecture the second time around. The clearest example is something I shipped last year. V1 was a text-to-SQL RAG app — a frontend that let business teams ask questions in English and got back SQL against BigQuery, with vector embeddings of historical queries retrieved into the LLM's context. Technically it worked, and I demoed it to senior leadership and the product teams. But adoption stalled, because I'd asked users to switch into a new frontend instead of meeting them where they already worked. The blocker wasn't the model — it was the surface. So I stopped building an app and started building a platform. V2 was the cp-platform context layer plus an MCP — fourteen tools and four read-only resources — delivered as a skill inside Wibey, our internal equivalent of Claude Code. The original RAG became `cp_search_sql`, one tool exposed through that MCP. The same substrate now powers seven-plus downstream consumers — the autonomous data analyst, the Jira agent, the KPI monitor, the hybrid orchestrator, a Slack bot, and three other CP skills — across 68 BigQuery tables and 1,350-plus columns, with 226 ChromaDB chunks, 313 indexed historical queries, 89 domain sections, 36-plus verified join paths, and a 52-node knowledge graph for multi-hop join pathfinding. Fifty-seven cp-analytics analyses powered by it. And the substrate maintains itself — five daily drift validators against live BigQuery auto-trigger doc regen via a three-tier LLM fallback. The lesson I carry forward is that adoption is a product problem, not a technology problem — and the reusable asset was the *context layer*, not the UI. One failed app turned into a multi-consumer substrate because the second time I got the abstraction right.

**Hooks planted (ranked by likelihood they get pulled)**
1. "Stopped building an app, started building a platform" — opens the architecture / platform follow-up
2. "Context layer + MCP, 14 tools + 4 resources" — opens technical depth (most likely from the engineers on the panel)
3. "The substrate maintains itself" — opens the platform-maturity follow-up. **Principal-level signal.**
4. V1 → V2 — doubles as a failure / change-of-mind story
5. "Seven-plus downstream consumers" — opens platform-leverage / Agent Builder fit angle

### Technical depth (if probed)

**Context layer (one-liner):** A structured markdown knowledge base wrapped in an MCP that decides what context to inject per task — docs, EDA results, or data samples — so the agent gets grounded context instead of guessing from schema names alone.

**Context layer (longer):**
- *Single Source of Truth:* `context/domain.md` (~500 lines, business definitions + SQL patterns + data quirks), `context/tables.md` (~400 lines, 68 schemas + joins + PII classifications), `context/schema.json` (450KB, BigQuery `INFORMATION_SCHEMA.COLUMNS` snapshot, machine-generated daily). These three are the source of truth; everything else is derived.
- *Compiled artifacts:* `context_compiler.py` converts markdown → in-memory JSON for zero-latency MCP lookups (16 tables full columns, 36+ confirmed joins, 89 indexed domain sections, 52-node knowledge graph).
- *RAG layer:* ChromaDB persistent index, 226 chunks across 8 semantic section types, Gemini embeddings at 3072 dims.
- *SQL knowledge base:* 313 historical queries indexed from 180 days of `JOBS_BY_USER`, hybrid Gemini embeddings + BM25 + RRF fusion.
- *Drift detection:* 5 daily validators (schema, enums, joins, tables, DDL cross-ref) run as a 6 AM cron; output JSON to `context/validation.log`; drift feeds into the next `doc_generator.py` run for auto-correction.
- *Doc regen:* 3-tier LLM fallback — Wibey Opus → Sonnet → Gemini 2.5 Pro — so doc generation never blocks on a single model being unavailable.

**MCP (14 tools + 4 resources):**
- *Schema / context (zero-latency, in-memory):* `cp_get_schema`, `cp_get_join_path`, `cp_get_domain_context`, `cp_get_gcc_context`, `cp_get_backlog`.
- *Execution:* `cp_query`, `cp_generate_validated_sql` (the flagship — Gemini 2.5 Pro generates → Gemini 2.5 Flash validates via function calling → dry-run → execute, ~60s).
- *Discovery / RAG:* `cp_ask_docs` (over ChromaDB), `cp_search_sql` (over the 313-query KB).
- *Reporting workflow:* `cp_init_report`, `cp_build_execution`, `cp_create_chart`, `cp_validate`.
- *Maintenance:* `cp_refresh_knowledge`.
- *Resources:* `cp://domain`, `cp://tables`, `cp://backlog`, `cp://index`.

### Anticipated follow-ups

**"Why a context layer instead of just giving the agent SQL tool access and letting it explore?"**
Agents waste tokens and make wrong assumptions when they have to rediscover the schema every time. Front-loading curated domain knowledge gets accuracy and speed; the EDA path is the escape hatch for when the docs aren't enough. The compiled artifacts make schema and join lookups zero-latency — pure in-memory JSON, no DB round-trip.

**"How does the MCP decide what to inject?"**
Different tools, different strategies. `cp_get_schema` is a deterministic table-name resolution chain — exact match, alias lookup, singular/plural variants, partial substring — into the in-memory JSON. `cp_get_domain_context` does keyword + phrase search across 89 indexed sections with a scoring rubric (title phrase match +15, content phrase match +10, keyword overlap +1). `cp_ask_docs` is RAG-driven — top-k chunks from ChromaDB grounding a Wibey Opus → Sonnet → Gemini fallback. `cp_search_sql` is hybrid retrieval — Gemini embeddings + BM25 + RRF fusion. Different question shapes, different lookup paths.

**"How do you keep the markdown in sync with the actual schema?"**
The 5 daily drift validators. `check_schema.py` diffs the live BQ schema against `tables.md`. When it catches new, changed, or dropped columns, the diff feeds into the weekly `doc_generator.py` run (Monday 7 AM cron, `--scope docs,sql_kb,compile`) which auto-regenerates the affected v2 docs via the 3-tier LLM fallback. So drift surfaces inside 24 hours and gets corrected inside 7 days. No manual maintenance.

**"What happens when EDA contradicts the markdown?"**
The validator catches it. `check_enums.py` runs `SELECT DISTINCT` and compares to documented values; `check_joins.py` tests every confirmed join path by executing it; `check_ddl.py` cross-references against the Azure SQL DDL in the engineering repos. Any mismatch goes into `validation.log` and feeds the next doc regen.

**"What's the moment you realized V1 wasn't going to land?"**
*[TO FILL IN — a specific meeting, piece of feedback, or adoption metric. Concrete moments make the reflection feel real rather than rehearsed.]*

**"What does each downstream agent do?"**
*Jira agent:* autonomous BDV ticket resolver, 5-phase pipeline, fully autonomous as a skill. *Autonomous data analyst:* multi-hypothesis exploration with REFLECT scoring, 57 analyses powered. *KPI monitor:* daily checks on `cp_query` + `cp_get_schema`, Slack alerts. *Hybrid orchestrator:* dual-backend Cube + raw SQL with reconciliation + (gated) auto-improve loop. *Slack `/cp` bot:* `cp_generate_validated_sql` + `cp_ask_docs` over Slack. *simple-cp-interaction:* `cp_ask_docs` + `cp_search_sql` + `cp_get_schema` for low-friction Q&A. *cp-business / cp-discovery / cp-hybrid:* three skills with different autonomy postures over the same MCP.

### Numbers to nail down before the interview

- ✅ **Substrate scale:** 68 tables, 1,350+ columns, 226 ChromaDB chunks, 313 indexed SQL queries, 89 domain sections, 36+ verified joins, 52-node / 63-edge knowledge graph, 14 MCP tools + 4 resources, 5 daily drift validators, 3-tier LLM fallback, 57 cp-analytics analyses powered.
- 📌 **Adoption of V2** — queries per week across all 7+ consumers, DAU/WAU on the product team, hours of manual data pulls replaced.
- 📌 **Accuracy improvements** — anything quantifiable vs. V1 or vs. raw LLM-with-SQL-tool.

### Note: this story doubles as your failure answer (Q8)

The V1 → V2 arc is a clean structural fit for "Tell me about a time you failed." When using it there, lead with "I shipped V1 and it didn't get adopted" — emphasize the *cost* and your *role in causing it*, not just the recovery. The "stopped building an app, started building a platform" insight becomes your STAR result. Decide which question you'd rather use it for — using the same story for both is fine if they're not on the same panel.

---

# Drafting queue (suggested order)

1. ✅ **Q1 — Tell me about yourself** (drafted)
2. ✅ **Q15 — What do you want the panel to remember about you?** (drafted, v2 corrected — 14 tools, drift detection, scale numbers, 3-tier LLM fallback, flagship tool added)
3. ✅ **Q2 — Jira agent** (drafted, v2 corrected — autonomous skill with HITL outside the loop, 5 phases not 6 gates, 14 tools, 313 SQL queries with Gemini+BM25+RRF, Investigation Branches added)
4. ✅ **Q3 — Self-growing semantic layer** (drafted, v2 corrected — 23 cubes / 5 domains, 1.1M panelists / 158M rows scale, 5 reconciliation verdicts with 0.5% tolerance, full auto-update loop mechanics added with explicit "built but gated" framing)
5. ✅ **Q5 — Why move from DV** (drafted, v2 corrected — 7+ downstream consumers count)
6. ✅ **Q6 — Senior DA → Principal SWE** (drafted, v2 corrected — added 18-experiment framework, 5-validator drift detection, 3-tier LLM fallback as the fifth signal)
7. ✅ **Q8 — Failure story** (drafted, v2 corrected — 7+ downstream consumers framing, `cp_search_sql` callout)
8. ✅ **Q4 — Autonomous data analyst** (drafted, v2 corrected — full 68-table scope, REFLECT scoring, SQL traceability contract, composable cp-audit/cp-fix/cp-context-validate ecosystem, 57 analyses adoption signal)
9. **Q9 — First 60–90 days** — Walmart loves this one
10. **Q7 — Why this role, why now**
11. **Q10 — End-to-end ownership**
12. Remaining as time allows
