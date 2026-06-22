# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built a registry-governed semantic layer over BigQuery that standardizes business definitions in one place: YAML definitions plus SQLite vocabulary snapshots define legal dimensions, values, and table wiring; a deterministic gate validates and canonicalizes intent into a typed dataclass before a deterministic compiler emits the SQL — same question, same answer, every time. New or changed definitions pass a human review gate before entering the registry. 16 governed demographic dimensions; reproducible by construction and regression-testable.
- Designed and shipped a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules, 23 golden-query test cases. Partnered with Product, Data Science, and business stakeholders to translate ambiguous, competing business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.
- Replaced ~20 distinct recruitment workflows I'd been running by hand 1–2× weekly with end-to-end automation on a 68-table BigQuery platform. Stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.
- Built an autonomous Jira ticket-resolution agent: 6-gate triage, MCP-driven context gathering, FAISS+BM25 retrieval over 11,000 historical SQL queries, self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months — cut turnaround from 30–60 minutes per request (and up to a full day for complex ones) to under 10 minutes each.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; state and decision logs persist to BigQuery for end-to-end observability, so the agent has no LLM-memory reliance. Designed a v2 architecture as a 3-tier event-driven platform self-configuring via a BigQuery event registry — new event types ship without code deploys.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Data & modeling: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL; registry-governed semantic-layer design (YAML + SQLite vocabulary snapshots), deterministic SQL compilation, value canonicalization

BI & self-service analytics: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

Engineering rigor: CI/CD (pytest, version control), evaluation suites (golden sets, human-in-the-loop validation), decision logging / observability, JSONL state stores

AI / LLM for analytics: NL-to-SQL, RAG (embeddings + FAISS + BM25 + RRF), LangChain, multi-model routing; Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
