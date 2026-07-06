# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Drove end-to-end development of a self-service analytics agent over 67 BigQuery tables from proof-of-concept to production: sub-agent orchestration with context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate), 8 deterministic SQL rules, and a 23-case golden-query evaluation suite. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Built a registry-governed semantic layer that boxes the LLM into semantic parsing — one call, strict JSON intent, never SQL — with deterministic validation, value canonicalization, and a deterministic SQL compiler, making answers reproducible and the only probabilistic step regression-testable. New or changed definitions pass a human review gate before entering the registry, enabling scalable, reproducible research over the data.
- Built and shipped to production an autonomous Jira ticket-resolution agent: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months — cut routine turnaround from 30–60 minutes to under 10 minutes and removed ~130–330+ hours of request-cycle time.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, so the agent has no LLM-memory reliance. Designed a 3-tier event-driven v2 platform self-configuring through a BigQuery event registry — new event types ship without code deploys.
- Replaced ~20 recurring recruitment workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, reducing a recurring 3-hour task to ~3 minutes of setup.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher_

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

ML / AI engineering: production ML/AI model build → validate → deploy → monitor, evaluation suites (golden sets, human-in-the-loop validation), sub-agent orchestration, context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), LangChain, ChromaDB semantic memory, multi-model routing across providers, headless cron agents, event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

MLOps / pipelines / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
