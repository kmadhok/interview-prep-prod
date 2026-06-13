# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .docx / .pdf. Tailored for Cohere — Forward Deployed Engineer, Prompt Specialist (Agentic Platform / North). In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst — embedded with Customer Perception (~30 stakeholders), shipping production LLM agents end-to-end_

- Designed and shipped a production text-to-SQL copilot over a 67-table BigQuery dataset — RAG over a 12K-query corpus, multi-agent orchestration (Context Researcher → SQL Drafter → Validator → Devil's Advocate), prompt-tuned per stage against 23 golden-query test cases and 8 deterministic SQL guardrails. 95% SQL accuracy, ~80% faster query creation; first AI skill in active business use on Data Ventures.
- Built an autonomous Jira ticket-resolution agent with a 6-gate workflow and rigorous per-gate evaluation: MCP-driven context retrieval (FAISS+BM25 over an 11K-ticket archive), plan-then-execute with 10-retry self-healing, 80%+ SQL reuse via similarity search. Closed 400+ data requests across 8 categories — cut turnaround from 30–60 minutes (up to a full day for complex tickets) to under 10 minutes each, with stakeholders never knowing an agent was answering.
- Built 3 MCP servers (24+ tools, stdio) that let every downstream agent reason over the 43-table BigQuery surface with zero hardcoded schema. Same MCP layer now backs the copilot, Jira agent, autonomous analyst, and hybrid orchestrator.
- Architected a 9-stage gated autonomous analytics pipeline (SELECT → PLAN → EXECUTE → INTERPRET → PACKAGE → CHART → NARRATE → VALIDATE → COMMIT) on a 740K-panelist dataset; 146 published analyses in 6 weeks with analyst review concentrated at the publish gate. Prompts and gates iterated on a golden-set harness reused across every agent in the portfolio.
- Co-built a hybrid orchestrator with Data Science and Product: routes business questions in parallel to a Cube.js semantic-layer agent and a context-engineered agent, reconciles outputs, and turns disagreements into ratified semantic-layer entries — a self-growing definition library shared across analytics agents.
- Productized two AI skills (cp-analytics, Simple CP Interaction) org-wide as official internal Wibey (Walmart's Claude Code fork) skills after Product + Data Science partnership review — first AI skills productized across Walmart Data Ventures. Recognized with a Walmart Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024
_AI Engineer (Consulting Capstone) — embedded with the client, shipped into their workflow_

- Deployed a RAG application for consulting-proposal generation adopted directly into FTI's workflow — query rewriting (+34% generation quality), adaptive chunking (+42% retrieval), Dockerized Streamlit on AWS EC2; cut proposal time ~30%. Best in Show — UChicago MSADS Capstone.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment with controlled prompt/temperature conditions; A/B tests persuaded 15% of participants to donate to an opposing cause.

### Baker Tilly — Chicago, IL · Sep 2021 – Sep 2022
_Consultant, Enterprise Platform Management (Oracle)_

- Delivered Oracle enterprise implementations end-to-end with client business and IT stakeholders — including RPA workflows automating high-volume client operations and AWS computer-vision deployments from problem framing through production.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression student-risk model across 10+ districts (5,000+ students): +7% retention, −15% course failures; automated the supporting ELT into BigQuery (+23% reporting accuracy).

---

## SELECTED PROJECT

- **NL-to-SQL Copilot (live demo)** — public mirror of the Walmart architecture: Streamlit + LangChain + Gemini 2.5 + RAG over historical queries + BigQuery execution + auto-visualization, Dockerized on GCP Cloud Run. https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

**Agentic / LLM stack:** Production LLM agents (deployed, evaluated, iterated on), multi-agent orchestration, MCP (Model Context Protocol) server design, tool development & evaluation, prompt engineering & optimization, context engineering, RAG (embeddings + FAISS + BM25 + RRF), evaluation harnesses (golden-set, gated pipelines, human-in-the-loop), LangChain, ChromaDB

**Models:** Anthropic Claude (Opus / Sonnet / Haiku), Cohere Command (familiar from public API), Google Gemini (2.5 Pro / Flash, Vertex AI), OpenAI, multi-model routing

**Customer & delivery:** Customer-embedded delivery (FTI client + Walmart stakeholders), metric definition with non-technical partners (quality / efficiency / accuracy), bridging SWE ↔ ML ↔ business, enterprise rollout & governance review

**Engineering / data:** Python, SQL, FastAPI, Docker, asyncio, mypy `--strict`, pytest; BigQuery, Databricks, MySQL, dbt; GCP (Cloud Run, Vertex AI), AWS (EC2); Slack webhooks, cron, Playwright SSO

**AI dev environment:** Claude Code (daily — via Wibey, Walmart's internal Claude Code fork), authored + productized Claude Code skills, agentic coding workflows

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL

---

## HONORS

- Walmart Making a Difference Award — 2026 (for 2025 AI/agent portfolio impact across Customer Perception)
- Best in Show — UChicago MSADS Capstone (FTI RAG proposal generator)

---

## TAILORING NOTES — Cohere FDE Prompt Specialist

The JD has five verbs: optimize prompts, develop+evaluate tools, build core agents for North (OOTB), build customer-tailored agents, partner with customers on metrics. Five resume changes from the Harrison Street base to hit those squarely:

1. **Bullet 1 — make the prompt+eval work explicit.** Same NL-to-SQL copilot, but the line now foregrounds *"prompt-tuned per stage against 23 golden-query test cases and 8 deterministic SQL guardrails"* — exact match for Cohere's "review, refine, iterate prompts" + "rigorous evaluations."
2. **Bullet 2 — name the eval verbs on the Jira agent.** Rewrote to lead with "rigorous per-gate evaluation" and "plan-then-execute." This is the strongest agents-in-production proof and now reads in Cohere's vocabulary.
3. **Bullet 3 — MCP / tool layer surfaced as its own bullet.** Cohere's "Tool Development & Evaluation" is a first-class responsibility; the MCP work (A5) earned its own line instead of being buried in the copilot bullet.
4. **FTI elevated above the UChicago researcher line.** Cohere is an FDE role — embedded delivery + adoption into a client's workflow is the central proof point, so FTI sits second in the experience block.
5. **Baker Tilly added back (single line).** Pre-Walmart consulting + client-IT stakeholder ownership signals the FDE muscle Cohere wants — but kept to one bullet so the resume stays on one page.
6. **Skills — restructured around Cohere's groupings.** Added a "Customer & delivery" group (FDE language), grouped models separately (Cohere Command named explicitly so it doesn't look like an oversight), kept agentic stack as the lead group with "evaluation harnesses" added as a first-class capability.

What's NOT claimed: fine-tuning Command (no experience); active Cohere ecosystem contributions (none yet); finance / healthcare / telco vertical depth (deferred to interview — Walmart retail is a different vertical but the FDE pattern transfers).

Live Demo line is the NL-to-SQL Copilot (default) — strongest matched proof for the prompt+tool+eval workflow Cohere is hiring for.
