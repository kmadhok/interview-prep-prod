# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_End-to-end software engineer who designs, builds, tests, and ships production data and AI systems — deterministic, regression-tested, and observable — and turns ambiguous problems into reliable services._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed, built, and shipped to production a self-service analytics system over 67 BigQuery tables: sub-agent orchestration, 8 deterministic SQL rules, and a 23-case golden-query evaluation suite; owned it end-to-end from design through deploy and maintenance. Led design reviews with Product, Data Science, and business stakeholders; approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures.
- Built and shipped an autonomous Jira ticket-resolution service with agentic RAG and advanced retrieval: 6-gate triage, MCP-driven context gathering, hybrid FAISS + BM25 retrieval with reranking over 11,000 historical SQL queries, state management, and self-healing execution with a retry budget; closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10. Built tracing/decision-logging for observability and well-defined failure modes.
- Built a registry-governed semantic layer over BigQuery — YAML/SQLite definitions, a deterministic prompt builder, strict-JSON intent with Pydantic-style schema validation (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — enforcing reliable data contracts and reproducible, testable outputs on sensitive, governed data.
- Designed and deployed a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts, persisting decision logs to BigQuery for end-to-end observability; triaged and debugged production issues by analyzing sources and downstream impact. Designed a 3-tier event-driven v2 that self-configures through a BigQuery registry so new event types ship without code deploys — reusable components and patterns, not one-offs.
- Replaced ~20 recurring manual workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, reducing a recurring 3-hour task to ~3 minutes of setup. Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator deployed on AWS EC2; scoped the use case, reviewed tradeoffs with the client, and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

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

Software engineering: Python, SQL, data structures & algorithms, system design, design & code reviews, testability, CI/CD (pytest), version control, debugging / triage / root-cause analysis

Backend / cloud: FastAPI, REST APIs, Cloud Run, GCP / AWS deployment, headless cron services, event-driven architectures, tracing / observability / decision logging

Data: BigQuery, dbt, SQL, data analysis, feature engineering, PySpark, Airflow, Databricks, MySQL

AI / LLM: AI agents & agentic workflows, agent orchestration/routing, RAG & hybrid retrieval (embeddings + FAISS + BM25 + RRF), MCP server design, evals & testing (golden sets, regression suites, human-in-the-loop), schema validation / guardrails

LLMs / dev: Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI; Claude Code, Cursor, LangChain

Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
