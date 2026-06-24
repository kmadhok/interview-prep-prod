# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_End-to-end AI engineer who ships AI to production, builds observability and governance into it, and enables business teams to adopt it — from ambiguous use case to measurable, monitored value._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Set the pattern for how AI use cases get built and adopted on Data Ventures: designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration, 8 deterministic SQL rules, a 23-case golden-query evaluation suite, and human-in-the-loop controls. Partnered with Product, Data Science, and business teams to translate ambiguous business problems into a scalable AI solution; approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams — adoption, not a pilot.
- Built a production headless KPI monitor (6-hour cron) that detects threshold breaches, runs root-cause analysis, and posts Slack alerts, with decision logging and BigQuery state for end-to-end observability; designed a 3-tier event-driven v2 self-configuring via a BigQuery event registry so new monitored use cases ship without code deploys — the observability/monitoring/feedback-loop discipline the role centers on.
- Built a registry-governed semantic layer over BigQuery with model-governance-grade controls (deterministic validation, value canonicalization, version-controlled definitions, human review gate) — giving versioning, lineage, explainability, and auditability so the same question returns the same answer on sensitive, governed data.
- Built and shipped an autonomous Jira agent (agentic AI in production): 6-gate triage, MCP-driven context gathering, agentic RAG (FAISS + BM25) over 11,000 historical SQL queries, and self-healing execution; closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10 — with documented procedures and reusable patterns.
- Drove enterprise adoption through enablement and self-service: a hybrid orchestrator let Product self-serve requests previously filed as tickets; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator for an enterprise consulting client, deployed on AWS EC2; advised the client on feasibility and trade-offs and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; designed controlled A/B tests that persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); partnered with district stakeholders; retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit front-end + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI enablement & advisory: use-case feasibility guidance, business→AI translation, AI app-development patterns, best-practice documentation, self-service enablement, stakeholder adoption, cross-functional leadership, mentoring

AI production, observability & governance: observability/monitoring frameworks (performance, drift, reliability, latency, cost, usage), decision logging/tracing, evals & testing (golden sets, regression, HITL), guardrails/output validation, CI/CD (pytest), event-driven architectures; model/definition versioning, data lineage, explainability, auditability, human review gates, responsible-AI & PII handling

AI / LLM products: AI agents (reasoning/planning), agentic workflows & tool use, agent orchestration, MCP server design, RAG & vector search (embeddings + FAISS + BM25 + RRF), prompt engineering, multi-model routing

Backend / cloud / data: Python, FastAPI, Cloud Run, REST APIs, GCP / AWS, Airflow, dbt; BigQuery, SQL, PySpark, Databricks, Elasticsearch-style retrieval

LLMs / dev: Claude (Opus/Sonnet/Haiku), Gemini (2.5 Pro/Flash via Vertex AI), OpenAI; Claude Code, Cursor, LangChain · Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
