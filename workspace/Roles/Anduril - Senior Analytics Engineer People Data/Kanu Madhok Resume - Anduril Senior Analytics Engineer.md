# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Replaced ~20 distinct recruitment workflows I'd been running by hand 1–2× weekly with end-to-end ETL automation on a 68-table BigQuery platform — owning the full lifecycle from ingestion to analytics-ready datasets. Stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.
- Built a registry-governed semantic layer over BigQuery: YAML definitions plus SQLite vocabulary snapshots define legal dimensions, values, and table wiring; a deterministic gate validates and canonicalizes intent into typed dataclasses before a deterministic compiler emits the SQL — governed, documented, reproducible datasets, with data-quality checks and a human review gate on every definition change.
- Designed and shipped to production a self-service analytics system over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation; 8 deterministic SQL rules and a 23-case golden-query evaluation suite enforcing correctness. Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures.
- Built and deployed a headless monitor on a 6-hour cron that continuously checks data/KPI thresholds, runs root-cause analysis on discrepancies, and posts Slack alerts; decision logs and state persist to BigQuery for full observability. Designed a 3-tier event-driven v2 platform self-configuring via a BigQuery registry — new checks ship without code deploys.
- Built an autonomous Jira ticket-resolution agent in modern, refactorable Python with engineering best practices (testing, version control): 6-gate triage, MCP context gathering, FAISS + BM25 retrieval over 11,000 historical SQL queries, self-healing execution. Closed 400+ data requests across 8 categories over 15 months, cutting routine turnaround from 30–60 minutes to under 10 minutes each.
- Partnered with Product, Data Science, and business stakeholders to translate ambiguous analytical needs into well-structured, documented data solutions; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users), cutting data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- RAG-to-proposal generator deployed on AWS EC2; cut proposal time ~30%; Best in Show — UChicago MSADS Capstone.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Data engineering: SQL (expert), Python, BigQuery, dbt, Apache Airflow, Databricks, PySpark, MySQL; ETL/ELT pipelines, registry-governed semantic layers / data models, stratified-sampling, BigQuery scheduled queries, JSONL state stores

Data quality & rigor: typed-dataclass validation, deterministic compilers, golden-set / human-in-the-loop evaluation, data-quality checks, pipeline monitoring & root-cause analysis, decision logging / observability, CI/CD (pytest, version control)

BI & stakeholder delivery: Power BI (DAX, XMLA TMSL), Tableau, LookML / Looker, Streamlit, business-translation for non-technical stakeholders

AI / agent stack: sub-agent orchestration, MCP server design, RAG (FAISS + BM25 + RRF), prompt engineering, event-driven architectures, headless cron agents

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
