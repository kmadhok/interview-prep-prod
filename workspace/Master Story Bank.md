# Master Story Bank — Kanu Madhok

**Purpose.** Every STAR story I reuse across interviews lives here once, with its beats, proof points, and the questions it best answers. When prepping a new role, I pick 6–10 stories from this file and tailor them — I don't rewrite from scratch. The role-folder `Interview Answers.md` becomes a *selection + tailoring* of these stories, not a parallel library.

**How to use.**

1. Open the role's `My Interpretation of Job Description.md`. List the 5–7 themes the panel will probe (failure, ambiguity, end-to-end ownership, platform thinking, cross-functional, business translation, technical depth, simplification, etc.).
2. For each theme, pick the story below tagged with it. Don't use the same story for more than two themes on the same panel — it reads as thin.
3. Copy the relevant story block into the role's `Interview Answers.md`, then tailor:
   - swap the closing "why this role" line for the role at hand
   - tune vocabulary to the JD (e.g., "consulting delivery" for BCG X, "client engagement" for Snorkel)
   - cut any beat the panel won't care about (BCG X doesn't need MCP depth; Walmart Agent Builder does)
4. Drill out loud. If a story takes more than 90 seconds spoken, cut a beat.

**Conventions.**

- Each story has: ID, one-line hook, theme tags, the 5 beats, canonical lines I want pulled, anticipated follow-ups, proof points (real numbers only).
- `[NUMBER?]` = unverified — leave the placeholder until confirmed; never invent.
- Story IDs match the Resume Achievements Master where applicable (S-A4 = Story for resume A4 Jira agent).

---

## Theme → Story map

Use this to scan fast when building a new `Interview Answers.md`.

- **Failure / change-of-mind / what would you do differently:** S-A8 (V1→V2 platform pivot)
- **Biggest impact / proudest build / leverage:** S-A4 (Jira agent flywheel) · S-A8 (V1→V2)
- **End-to-end ownership (problem spotted → shipped → measured):** S-A4 · S-A3 · S-F1 (FTI capstone) · S-I1 (Innovare)
- **Built before anyone asked / bias to action:** S-A4 · S-A8 · S-A5 (MCP servers)
- **Discovered a problem no one else had noticed:** S-A4 (intake bottleneck) · S-A7 (semantic-layer/agent reconciliation gap)
- **Ambiguity / weakly-defined problem:** S-A8 · S-A7
- **Cross-functional (DS + Product + Eng):** S-A7 · S-A3
- **Technical depth / system design walkthrough:** S-A7 (hybrid orchestrator) · S-A5 (MCP) · S-A8 (context layer)
- **Simplification / removed steps / killed scope:** S-A8 (killed the V1 frontend) · S-A6 (652K→50 in 45s)
- **Engineering rigor (typing, testing, CI):** S-A6
- **Business translation (vague stakeholder → scoped automation):** S-A3 · S-A4 · S-B1 (Baker Tilly)
- **Consulting / client-facing delivery:** S-F1 · S-B1
- **Experimentation / causal / measurement:** S-U1 (donation experiment) · S-I1
- **Leadership without authority / influence:** S-A2 (productized Wibey skills) · S-A7
- **Career narrative (Sr DA → Principal SWE positioning):** S-CAREER

---

# Stories

---

## S-A8 — Killed V1, built a platform (V2)

**One-line hook.** "I shipped a text-to-SQL app that nobody used, so I tore it down and rebuilt it as the platform every analytics agent in our org now runs on."

**Theme tags.** failure · change-of-mind · platform · leverage · simplification · ambiguity · technical-depth · bias-to-action

**Best for.** "Time you failed" · "Time you had to rip something out and redo it" · "What would you do differently" · "Time you simplified something complex" · "Time you built before alignment" · platform/system-design walkthroughs

### Beats

- **The miss.** V1 was a text-to-SQL RAG app — frontend, English in, SQL against BigQuery out, demoed it to senior leadership and product teams. Technically it worked. Adoption stalled. I'd asked users to leave their existing workflow for a new frontend.
- **The reflection.** The blocker wasn't the model. It was the surface. The valuable piece was the *context*, not the UI.
- **The rebuild.** Stopped building an app, started building a platform. Decomposed V1 into a reusable context layer + MCP, delivered as a skill inside Wibey (Walmart's Claude Code fork). The original RAG became one tool exposed through the MCP.
- **The compounding outcome.** Same context layer now powers the autonomous data analyst, KPI monitor, geo-readiness agent, and the hybrid semantic-layer orchestrator. One failed app → N downstream agents.
- **The lesson.** Adoption is a product problem, not a technology problem. The reusable asset was the substrate, not the app on top of it.

### Canonical lines I want pulled

- *"Stopped building an app, started building a platform."*
- *"One failed app turned into N agents because the second time I got the abstraction right."*
- *"Adoption is a product problem, not a technology problem."*

### Anticipated follow-ups

- **"What's the context layer?"** — A structured markdown knowledge base wrapped in an MCP that decides what to inject per task: docs, EDA results against BigQuery, or data samples. Static piece = the markdown. Dynamic piece = the MCP picking what's relevant per question, so the agent gets grounded context instead of guessing from schema names.
- **"How is V2 different from V1 at the architecture level?"** — V1 was a vertical app. V2 is a horizontal substrate. V1 made users switch tools; V2 sits inside the tool they already use.
- **"What was the moment you knew V1 wasn't going to land?"** — [TO FILL IN — a specific meeting, piece of feedback, or adoption metric.]
- **"How do you know V2 isn't going to fail the same way?"** — V2 doesn't have its own surface. It rides whatever surface the user already lives in. The failure mode of V1 was the surface; removing the surface removes the failure mode.

### Proof points

- ≥4 downstream agents on the same context layer: text-to-SQL copilot, autonomous analyst, KPI monitor, geo-readiness, hybrid semantic-layer orchestrator
- V1 → V2 cycle: ~[NUMBER?] months from V1 demo to V2 deployment
- V2 surface = Wibey skill (delivered through Walmart's Claude Code fork)

### Cut-down version (60 seconds)

V1 was a text-to-SQL app. Demoed it, technically worked, adoption stalled — I'd asked users to leave their workflow. The blocker wasn't the model, it was the surface. So I stopped building an app and built a platform: the context layer plus MCP under the original RAG, delivered as a skill inside our internal Claude Code fork. The same context layer now powers four other agents. Lesson: adoption is a product problem, not a tech problem. One failed app turned into N agents because the second time I got the abstraction right.

---

## S-A4 — Jira agent / leverage flywheel

**One-line hook.** "I was the bottleneck on my own team's stakeholder intake, so I built the agent that quietly replaced me on that work — and the time it freed up funded the rest of the agent portfolio."

**Theme tags.** biggest-impact · leverage · end-to-end · built-without-asking · business-translation · technical-depth · HITL · bias-to-action

**Best for.** "Walk me through a problem you owned end-to-end" · "Tell me about something you built before anyone asked" · "Time you discovered a problem nobody noticed" · "Biggest impact you've had" · agent-design walkthroughs · "When do you keep a human in the loop?"

### Beats

- **The cost.** Customer Perception runs on Jira intake — data readiness, hierarchy lookups, panelist questions, survey response rates. I was the only one answering. Typical ticket 30–60 min; complex ones, full day. 400+ tickets handled since Jan 2025.
- **The realization.** The intake bottleneck was what was keeping me from building anything else. Same shapes of questions kept recurring.
- **The architecture.** 6-gate pipeline: triage → context (MCP, FAISS + BM25 over 11K-ticket archive) → plan → draft → execute (BigQuery) → validate. 13 tools across querying, docs, lookups. 4-phase workflow, 10-retry self-healing, 80%+ SQL reuse via similarity search.
- **The deliberate HITL.** Agent drafts; I review and post. Made that call because the cost of a wrong answer to a stakeholder is much higher than the cost of my two-minute review. Stakeholders never see the agent — they see a normal Jira reply from me.
- **The real win = leverage.** Complex tickets went from a full day to 10–15 min. But the bigger outcome: once intake was off my plate, I built the autonomous analyst, KPI monitor, and self-growing semantic layer on top of the same context infrastructure. The Jira agent became the platform that funded the rest of the portfolio.

### Canonical lines I want pulled

- *"I deliberately kept myself as the human in the loop."*
- *"Stakeholders never see the agent — they see a normal Jira reply from me."*
- *"The Jira agent ended up being the platform that funded the rest of the portfolio."*
- *"400+ tickets handled without anyone realizing the answers weren't all coming from me."*

### Anticipated follow-ups

- **"Why didn't you let it auto-post?"** — Cost of a wrong response to a stakeholder is much higher than two minutes of my review. Trust ramp matters; these are people I work with every week. At platform scale I'd add confidence thresholds and auto-post on high-confidence cases.
- **"How do you know the drafts are good?"** — Two validations. Structural SQL correctness against the context layer's knowledge graph (join paths, semantic definitions). Intent matching against how similar questions were answered in the 11K-ticket archive — wildly different shapes flag.
- **"What's the moment stakeholders couldn't tell?"** — There wasn't one. Nobody asked. They just kept submitting tickets and getting faster, well-supported responses. I'd underestimated what the panel might find load-bearing — quiet automation can be more interesting than visible automation, because it shows up as capacity.
- **"Why retrieval over 11K tickets?"** — Most stakeholder questions aren't novel; they're variants of questions asked 3 months ago. The archive lets the agent ground its draft in *how this team has answered this kind of question before*, not just what the schema says.

### Proof points

- 400+ Jira tickets handled since Jan 2025
- Turnaround: 60–90 min → ~5 min review-and-approve; complex tickets full day → 10–15 min
- 6 gates · 4-phase workflow · 10-retry self-healing · 80%+ SQL reuse
- 11K-ticket historical archive · FAISS + BM25 retrieval · 13 tools

### Cut-down version (60 seconds)

I was the only one handling Customer Perception's Jira intake — data readiness, panelist lookups, response rates. Typical ticket 30–60 min, complex ones full day, 400+ since January. It was the bottleneck on everything else. So I built a 6-gate agent: triage, context retrieval over our 11K-ticket archive, plan, draft, BigQuery execute, validate. Deliberate HITL — agent drafts, I review and post, stakeholders never see the agent. Complex tickets went from a full day to 10–15 minutes. But the real win was leverage: once intake was off my plate, I built the autonomous analyst, the KPI monitor, and the semantic-layer orchestrator on top of the same context infrastructure. The Jira agent became the platform that funded the rest of the portfolio.

---

## S-A7 — Hybrid orchestrator / self-growing semantic layer

**One-line hook.** "Two text-to-data approaches each fail in different directions. I ran both in parallel and turned the disagreements into a flywheel that grows the semantic layer on its own."

**Theme tags.** technical-depth · cross-functional · platform · first-principles · system-design · business-translation

**Best for.** Design-walkthrough questions · "Walk me through your agent architecture" · "Cross-functional collaboration" · "Time you reasoned from first principles" · Principal-level platform-thinking signal

### Beats

- **Two approaches, each broken.** Semantic layer (Cube.js, dbt MetricFlow): deterministic, auditable, brittle — every metric hand-defined. Context-engineered agent: flexible, handles novel questions, can hallucinate joins.
- **What's in production.** Both, separately. Cube.js semantic-layer agent (joint with DS + Product — they own definitions, I own the agent). Context-engineered agent on the V2 context layer. Both deployed.
- **The insight.** They're not competing — they're complementary. Each fails where the other succeeds. Run both in parallel; disagreement is signal.
- **The orchestrator.** Same question fans to both. Reconciling agent receives both outputs. Agree → ship. Disagree → semantic layer wins as the live answer (auditable path, source of truth), *but* the disagreement gets flagged for product-team review. If real, product ratifies and DS adds it as a new semantic-layer entry. Next time, both paths agree on the first pass.
- **Why self-growing.** Captured + ratified disagreements = labeled training data for new semantic-layer entries. Agreement rate is the headline metric — trending up means the flywheel works.

### Canonical lines I want pulled

- *"Disagreements aren't bugs — they're labeled training data for the semantic layer."*
- *"Semantic layer wins ties, but the disagreement still gets flagged for product-team review."*
- *"Three-way contract: DS owns the semantic layer, I own the agent layer and the orchestrator, product owns scope and disagreement review."*
- *"Surfaced 20 candidate definitions the semantic layer was missing, just from one run against the golden set."*

### Anticipated follow-ups

- **"Why product team for review instead of DS or you?"** — Product owns *what the metrics mean to the business* — exactly what's being decided. DS owns *how* the metric is defined (the modeling) once product ratifies. I built the pipe; I shouldn't be the one deciding which business metrics exist.
- **"What stops bad definitions from being persisted?"** — The product-team review gate. The agent path never ratifies itself. Without that gate, a confidently-wrong answer would drift the semantic layer over time. With it, the semantic layer only grows from earned consensus.
- **"What's the golden set?"** — A curated set of question/answer pairs grounded in the context layer — the same eval harness reusable across every agent on that layer (Jira agent, autonomous analyst, KPI monitor, orchestrator). Add a new Q/A pair → regression coverage for all of them at once.
- **"Could this scale Walmart-wide?"** — Yes — architecture doesn't change. What changes is the governance (who ratifies in which domain) and partitioning by ownership boundary. The bigger the scope, the more valuable the loop, because manually maintaining a semantic layer at enterprise scale is exactly what doesn't scale.

### Proof points

- 2 production backends (semantic-layer agent + context-engineered agent)
- 20 candidate definitions surfaced from one golden-set run, pre-production
- Orchestrator built end-to-end, validated, production rollout in flight
- Reusable golden-set eval harness across ≥4 agents

### Cut-down version (90 seconds)

Two standard approaches to text-to-data each fail in different directions. Semantic layer is deterministic and auditable but brittle — every metric hand-defined. Context-engineered agent is flexible but can hallucinate joins. I shipped both, separately, with Data Science and Product. Then I built a reconciling orchestrator: same question fans to both, agreement ships, disagreement flags for product review. Semantic layer always wins as the live answer — it's the auditable path. But ratified disagreements become new semantic-layer entries. Validated end-to-end on a golden set that's reusable across every agent on the same context layer; one run surfaced 20 candidate definitions the semantic layer was missing. The reason I call it self-growing: disagreements aren't bugs, they're labeled training data. Agreement rate is the headline metric — trending up means the flywheel's working.

---

## S-A3 — Autonomous data analyst

**One-line hook.** "I built the self-service analytics agent that publishes its own analyses on a 740K-panelist dataset — analyst time concentrated at the publish gate, not the work."

**Theme tags.** end-to-end · business-translation · platform · agent-design · HITL

**Best for.** "Tell me about an end-to-end build" · agent-design walkthroughs · "How do you decide HITL placement?" · "Time you built something the business actually adopted"

### Beats

- **The cost.** Stakeholder questions on Customer Perception data — 740K-panelist BigQuery dataset, 6 core tables. Each ad-hoc analysis = a Jira ticket = my time. Analyst-bound throughput.
- **The pipeline.** 9 gated stages: SELECT → PLAN → EXECUTE → INTERPRET → PACKAGE → CHART → NARRATE → VALIDATE → COMMIT. Sub-agent orchestration with context isolation per stage.
- **The HITL choice.** Analyst review concentrated at *publish* time, not at every stage. The agent runs the whole pipeline; I gate it before it commits.
- **Adoption.** 146 published analyses in 6 weeks. Approved by Director + product leadership. Currently the only AI skill in active use by business teams in Data Ventures.
- **What it changed.** Throughput went from "as many analyses as I have hours" to "as many analyses as I can review at publish time."

### Canonical lines I want pulled

- *"Analyst time concentrated at the publish gate, not at the work."*
- *"146 published analyses in 6 weeks on a 740K-panelist dataset."*
- *"The only AI skill in active use by business teams in Data Ventures."*

### Proof points

- 9 gated stages
- 146 published analyses in 6 weeks
- 740K-panelist BigQuery dataset
- 6 core tables · sub-agent orchestration with context isolation
- Director + product leadership approval

---

## S-A5 — MCP servers / latency win

**One-line hook.** "Three MCP servers gave our agents zero-hardcoded-knowledge access to a 43-table BigQuery dataset and cut latency 4–6×."

**Theme tags.** platform · technical-depth · simplification · leverage

**Best for.** Technical-depth probes · "How do you decouple agent logic from data?" · "What's an example of a platform decision that paid off?"

### Beats

- **The drag.** Agents had hardcoded schema assumptions per use case. Every new agent re-encoded the same domain knowledge, and latency was painful — 90–120s for non-trivial queries.
- **The design.** 3 MCP servers, 24+ tools across querying, schema introspection, and lookups. Stdio transport. Agents reason over the 43-table dataset by calling tools, not by carrying schema in their prompt.
- **The result.** Latency 90–120s → 20–25s. Same MCP surface now powers the text-to-SQL copilot, autonomous analyst, Jira agent, and downstream KPI/geo agents.
- **The platform argument.** Tools are the agent contract. Centralize them and you only have to fix a schema change once, not in every agent.

### Proof points

- 3 MCP servers · 24+ tools · stdio
- 43-table BigQuery dataset, zero hardcoded knowledge
- Latency 90–120s → 20–25s (4–6× reduction)

---

## S-A6 — ML pipeline / engineering rigor

**One-line hook.** "Replaced multi-week manual schema mapping with a 4-layer ML pipeline that takes 45 seconds — typed, tested, and runnable on demand."

**Theme tags.** engineering-rigor · ML-pipeline · simplification · end-to-end

**Best for.** "Tell me about something you engineered to production standards" · "Time you replaced manual work with a system" · "How do you think about testing/typing in ML code?"

### Beats

- **The manual cost.** Analysts spent weeks mapping which columns related across tables. Pure pattern-matching by hand on hundreds of tables.
- **The build.** 4-layer pipeline (candidate generation → feature extraction → classification → confidence filtering). 7,327 LOC, `mypy --strict`, 131 pytest tests.
- **The collapse.** 652K candidate column pairs → 50 classified relationships in 45 seconds.
- **Why the rigor.** This is the kind of code that gets reused without me in the room. Strict typing + tests mean future-me (or someone else) can extend it without fear.

### Proof points

- 7,327 LOC · `mypy --strict` · 131 pytest tests
- 652K candidate pairs → 50 relationships · 45 seconds
- Replaced weeks of manual analyst effort

### Canonical line

*"Strict typing and 131 tests because this is the kind of code that gets reused without me in the room."*

---

## S-F1 — FTI RAG capstone (Best in Show)

**One-line hook.** "Shipped a RAG proposal generator into a consulting firm's real workflow — adopted on production work, 30% faster proposals, won Best in Show."

**Theme tags.** consulting · client-facing · end-to-end · RAG · award · shipped-not-prototyped

**Best for.** Consulting / FDE / client-facing roles · "Time you shipped something a real org adopted" · "Tell me about a project end-to-end" · "Time you worked with non-technical stakeholders"

### Beats

- **The setup.** UChicago MSADS capstone, partnered with FTI Consulting. Brief: their proposal-writing process was slow and inconsistent across consultants.
- **The build.** RAG application — query rewriting (+34% generation quality), adaptive chunking (+42% retrieval). Dockerized Streamlit on AWS EC2.
- **The adoption.** Got pulled into FTI's actual workflow, not just demo-and-leave. Proposal time down ~30%.
- **The recognition.** Won Best in Show at UChicago MSADS Capstone.
- **The takeaway.** Adoption is what made the project real. Same lesson I'd later relearn the hard way on V1 (S-A8).

### Proof points

- −30% proposal time
- +34% generation quality (query rewriting)
- +42% retrieval (adaptive chunking)
- Dockerized Streamlit · AWS EC2
- Adopted into FTI workflow
- Best in Show, UChicago MSADS Capstone

---

## S-I1 — Innovare student-risk model

**One-line hook.** "Built and shipped a student-risk model across 10+ school districts that lifted retention 7% and cut course failures 15%."

**Theme tags.** classical-ML · end-to-end · business-translation · dashboards · early-career

**Best for.** "Time you shipped classical ML" · "Time you worked with non-technical end users" · roles that want pre-LLM ML maturity (Snorkel, BCG X analytics-heavy engagements)

### Beats

- **The brief.** EdTech startup. Districts wanted early warning on at-risk students.
- **The model.** Logistic regression with feature engineering on attendance, grades, behavioral incidents. Deployed across 10+ districts, 5K+ students.
- **The pipeline.** Automated ELT into BigQuery so the model and downstream dashboards stayed fresh without manual pulls.
- **The outcome.** +7% retention. −15% course failures. +23% reporting accuracy after the ELT swap.
- **Why this story still matters.** It's the proof I can do classical ML end-to-end (not just LLMs), and I've worked with non-technical educators as end users.

### Proof points

- 10+ districts · 5K+ students
- +7% retention · −15% course failures · +23% reporting accuracy
- BigQuery ELT pipeline · logistic regression

---

## S-B1 — Baker Tilly / Oracle + RPA + computer vision

**One-line hook.** "Owned Oracle enterprise implementations end-to-end with client business and IT stakeholders — built the supporting RPA and AWS computer-vision automations alongside the platform work."

**Theme tags.** consulting · client-facing · end-to-end · RPA · pre-agent · cross-functional

**Best for.** Consulting / FDE roles (BCG X, Snorkel, Deloitte) · "Time you worked with clients" · "Pre-LLM automation experience" · "Time you bridged business + technical"

### Beats

- **The role.** Enterprise Platform Management consultant at Baker Tilly. Oracle implementations across mid-market clients.
- **The end-to-end shape.** Problem definition with client business + IT → solution scoping → build (Oracle config, RPA workflows, AWS computer vision for document automation) → deployment → handoff.
- **The breadth.** Pre-agent automation muscle. RPA was the classical predecessor; the agent work today is the same problem (high-volume manual workflow) with better tools.
- **Why this story matters.** Two things consulting/FDE panels want: client-facing comfort and end-to-end ownership *before* I had AI as a hammer. It shows the muscle is real, not LLM-shaped.

### Proof points

- Oracle enterprise platform implementations
- Client business + IT stakeholder ownership
- RPA workflows + AWS computer-vision solutions
- Problem definition → deployment

---

## S-U1 — Multi-LLM donation experiment

**One-line hook.** "Ran a 500+ participant A/B experiment using a persona-tuned multi-LLM chatbot — 15% of participants shifted donations to an opposing cause."

**Theme tags.** experimentation · causal-design · LLM-orchestration · agents · research

**Best for.** Snorkel-style data/eval roles · BCG X experimentation work · "Time you designed something to measure causal impact" · "Time you tuned an LLM system for a specific outcome"

### Beats

- **The setup.** UChicago Data Science Institute research project. Designing a study on LLM persuasion across personas.
- **The system.** Multi-LLM chatbot (OpenAI + Gemini) with controlled persona and temperature conditions.
- **The experiment.** 500+ participants, staged A/B with controlled persona conditions.
- **The result.** 15% of participants shifted their stated donation to an opposing cause under the experimental conditions.
- **Why this story matters.** Proof I can design *causal* experiments on LLM systems, not just ship and hope. That muscle is what Snorkel's evaluation/synthetic-data work is built on.

### Proof points

- 500+ participants
- OpenAI + Gemini multi-LLM
- Controlled persona + temperature conditions
- 15% persuasion shift in opposing direction

---

## S-A2 — Productized Wibey skills (influence)

**One-line hook.** "First analyst at Walmart Data Ventures to productize official Wibey skills — cleared formal Product + DS partnership review and distributed org-wide."

**Theme tags.** leadership-without-authority · cross-functional · platform · leverage · influence

**Best for.** "Time you got something into production others used" · "Time you influenced without authority" · "Time you cleared a high bar of organizational scrutiny"

### Beats

- **The build.** Two AI skills inside Wibey (Walmart's Claude Code fork): cp-analytics and Simple CP Interaction.
- **The bar.** Skills had to clear formal Product + Data Science partnership review — same review path any official internal tool goes through.
- **The first-of-kind.** First analyst across Data Ventures to ship official Wibey skills.
- **Why it matters.** Productized ≠ local script. These went through the same review and distribution path as any official tool, and the path itself is what makes the work reusable.

### Proof points

- 2 productized Wibey skills
- First-of-kind across Walmart Data Ventures
- Cleared formal Product + DS partnership review
- Distributed org-wide

---

## S-CAREER — Sr Data Analyst → Principal SWE positioning

**One-line hook.** "My title is Senior Data Analyst; the work is principal-level engineering — and I have the artifact list to prove it."

**Theme tags.** career-narrative · framing · pre-empt

**Best for.** Any role where the title gap will be obvious from my resume · "Why are you ready for a Principal title?" · "What's the gap between your title and your work?"

### Beats

- **The honest framing.** The title is what the role was scoped as when I joined Customer Perception. The actual work outgrew the title.
- **The signal.** What I've shipped in this seat: text-to-SQL copilot, Jira agent, 9-stage autonomous analyst, MCP layer, hybrid orchestrator, ML classification pipeline. That's principal-level system design, end-to-end ownership, and platform thinking.
- **Why the title hasn't moved.** Org constraint — Customer Perception is an analytics-titled function. The work I do isn't bounded by that, but the title rubric is.
- **The pre-empt.** Don't apologize for it. Lead with "title is Senior Data Analyst; the work is principal-level AI engineering" and let the artifacts make the case.

### Canonical lines

- *"Title on paper is Senior Data Analyst; the work is principal-level AI engineering."*
- *"Recognized with a Making a Difference Award for 2025 work."*

---

# Stories I still need to draft

These are slots in the bank where I don't yet have a polished story but the question shows up often enough that I should write one:

- **Feedback that genuinely changed how you work** — [TO DRAFT — need a real piece of feedback, who gave it, what I tried first that didn't fix it, what eventually did.]
- **Killed your own proposal / said "we don't need to build this"** — [TO DRAFT — V1→V2 is partial fit but the question wants a *don't-build* decision, not a *rebuild* decision.]
- **Conflict with a peer or stakeholder** — [TO DRAFT — disagreement, how I handled it, outcome.]
- **A time you stopped working on something partway through** — [TO DRAFT — the inverse of bias-to-action. Could lean on V1 abandonment if I frame it as a kill rather than a rebuild.]
- **Mentorship / pulling someone else up** — [TO DRAFT — anyone I onboarded, taught, or unblocked at Walmart, FTI, or Baker Tilly.]

When one of these shows up on a role's question list, draft it here first, then pull into the role folder.

---

# Notes for tailoring

- **Walmart Agent Builder panel** wants: end-to-end ownership, business translation, HITL judgment, agent system-design. Lead with S-A4 + S-A7 + S-A8 (failure). Keep S-A5 in reserve for technical-depth probes.
- **BCG X AI Factory Product Builder** wants: consulting-flavored product thinking, Claude Code experience, building things consultants adopt. Lead with S-F1 + S-A2 (productized) + S-A8. S-B1 reinforces consulting muscle. Don't over-index on MCP internals.
- **Snorkel FDE DaaS** wants: data + eval + HITL + API integration + client-facing. Lead with S-A4 (HITL eval pipeline shape) + S-U1 (eval/causal design) + S-A6 (engineering rigor) + S-F1 (client-facing). De-emphasize Walmart-internal naming.
- **Deloitte GPS Anthropic FDE** wants: Anthropic stack, Claude Code, government-context comfort. Lead with S-A8 (Wibey is Claude Code) + S-A2 (productized skills inside Claude Code fork) + S-A4. S-B1 reinforces client-facing maturity.
