# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_End-to-end AI engineer who embeds with business teams, turns manual processes into trusted AI-assisted workflows, and ships agents, skills, and MCP integrations into production adoption._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Partnered with Product, Data Science, and business stakeholders to turn ambiguous, manual asks into a trusted, repeatable AI-assisted workflow: designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration, 8 deterministic SQL rules, a 23-case golden-query evaluation suite, and human-in-the-loop validation. Approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures.
- Built and shipped to production an autonomous Jira ticket-resolution agent that connects to enterprise systems via MCP-driven context gathering and agentic RAG (6-gate triage, FAISS + BM25 retrieval over 11,000 historical SQL queries, self-healing execution with a retry budget); closed 400+ data requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10 — with documented operating procedures, not a one-off script.
- Built a registry-governed semantic layer over BigQuery — YAML/SQLite definitions, a deterministic prompt builder, strict-JSON intent (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — so the same business question returns the same answer every time. Validation and human-in-the-loop controls ensure output accuracy and trust on sensitive, governed data.
- Replaced ~20 recurring recruitment workflows I had been running by hand 1–2× weekly with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, turning a recurring 3-hour task into ~3 minutes of setup — and scaled the pattern across teams.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts, with decision logging and BigQuery state for end-to-end observability; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users) and cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator for an enterprise consulting client, deployed on AWS EC2; scoped the use case with the client and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

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

AI workflow delivery: use-case identification, business-process translation, AI-assisted workflow design, end-to-end ownership (scope → adoption), human-in-the-loop validation & output controls, documentation/runbooks, stakeholder training & adoption

AI / LLM products: AI agents with reasoning/planning, agent orchestration, skills & reusable workflows, MCP server design & integrations, RAG & vector search (embeddings + FAISS + BM25 + RRF), prompt engineering, evals & testing (golden sets, human-in-the-loop), guardrails / output validation, multi-model routing

AI-assisted development: Claude Code, Cursor, Anthropic & OpenAI APIs

Integration / backend: Python, FastAPI, Cloud Run, REST APIs, JSON/YAML, GitHub & version control, CI/CD (pytest), headless cron agents, decision logging / observability; deploys on GCP / AWS

Data / SQL: BigQuery, dbt, SQL (complex query design + optimization), vector databases, PySpark, Airflow, Databricks, MySQL

LLMs: Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
