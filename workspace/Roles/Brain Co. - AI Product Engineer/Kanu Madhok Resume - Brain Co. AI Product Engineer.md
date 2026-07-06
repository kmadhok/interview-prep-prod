# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .docx / .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Partnered directly with Product, Data Science, and business stakeholders to translate ambiguous business questions into specs, then designed and shipped a self-service analytics agent over 67 BigQuery tables from zero — sub-agent orchestration with context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate), 8 deterministic SQL rules, 23-case golden-query eval suite. Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures.
- Built and shipped an autonomous ticket-resolution agent end-to-end that closed 400+ requests across 8 categories over 15 months — 6-gate triage, MCP-driven context gathering, RAG with FAISS + BM25 retrieval over 11,000 historical queries, self-healing execution with a 10-retry budget. Cut turnaround from 30–60 minutes per request (up to a full day for complex ones) to under 10 minutes.
- Built a headless KPI monitor on a 6-hour cron (threshold breaches → root-cause analysis → Slack alerts) with decision logging and BigQuery state persistence for production observability; designed a 3-tier event-driven v2 self-configuring through a BigQuery event registry — new event types ship without code deploys.
- Replaced ~20 recurring workflows run by hand 1–2× weekly with end-to-end automation on a 68-table BigQuery platform; stratified-sampling data pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Worked directly with the client to scope and build a RAG-to-proposal generator from zero, deployed on AWS EC2; cut proposal time ~30%; adopted into their workflow. Best in Show — UChicago MSADS Capstone.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot, built end-to-end (Streamlit front-end + Gemini 2.5 + RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Build & deploy (end-to-end): agent + RAG systems from zero, MCP server design, sub-agent orchestration, context engineering, prompt engineering, golden-set evaluation, headless cron agents, event-driven architectures

APIs / backend / cloud: FastAPI, Cloud Run, AWS EC2, REST endpoints, microservice-style services, BigQuery scheduled queries, Slack webhooks, JSONL state stores, CI/CD (pytest, version control)

Front-end / viz: Streamlit, React Recharts, Power BI (DAX, XMLA TMSL), Tableau, LookML, Matplotlib

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
