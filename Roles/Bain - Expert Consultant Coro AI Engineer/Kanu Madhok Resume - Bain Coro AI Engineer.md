# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_End-to-end AI engineer who embeds with stakeholders, ships agentic GenAI products from POC to production, and turns ambiguous business problems into measurable outcomes._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration, context engineering, human-in-the-loop controls, 8 deterministic SQL rules, and a 23-case golden-query evaluation suite — turning raw, heterogeneous data into structured analytics business teams rely on. Approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures.
- Built and shipped an autonomous Jira ticket-resolution agent with agentic RAG and advanced retrieval: 6-gate triage, MCP-driven context gathering, hybrid FAISS + BM25 retrieval with reranking over 11,000 historical SQL queries, memory/state management, and self-healing execution with a retry budget; closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10. Built tracing/decision-logging for observability and clear failure modes.
- Built a registry-governed semantic layer over BigQuery — YAML/SQLite definitions, deterministic prompt builder, strict-JSON intent with Pydantic-style schema validation (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — enforcing reliable data contracts and reproducible outputs on sensitive, governed data with access controls and PII awareness.
- Built a hybrid orchestrator with routing across two backends (a semantic-layer skill and a context-engineered agent) that reasons about disagreements and refines definitions over time; let Product self-serve requests previously filed as tickets — designed reusable components and orchestration patterns, not one-offs.
- Translated ambiguous business problems into AI use cases for technical and non-technical stakeholders, led working sessions, and drove adoption; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator for an enterprise consulting client, deployed on AWS EC2; scoped the use case with the client, communicated tradeoffs, and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; designed controlled A/B tests (rigorous validation methodology) that persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); feature engineering on real-world data; retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit front-end + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI / LLM products: GenAI applications (copilots, workflow automation, decision support), AI agents with reasoning/planning, agentic workflows & tool use, agent orchestration/routing, context engineering, memory/state management, MCP server design & reusable skills/tools, schema validation (Pydantic-style data contracts)

Retrieval / search: RAG & hybrid retrieval (embeddings + FAISS + BM25 + RRF reranking), vector databases, indexing/metadata/relevance tuning, source attribution

Evaluation & delivery: evals & testing (golden sets, regression suites, human-in-the-loop), tracing / observability / decision logging, guardrails & output validation, responsible-AI & PII handling, CI/CD (pytest), prompt/agent versioning

Backend / cloud: Python, FastAPI, REST APIs, Cloud Run, GCP / AWS deployment, headless cron services, LLM API integration

Data / ML: BigQuery, dbt, SQL, feature engineering, model validation/testing, PySpark, Airflow, Databricks, MySQL

LLMs / dev: Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI; Claude Code, Cursor, LangChain

Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
