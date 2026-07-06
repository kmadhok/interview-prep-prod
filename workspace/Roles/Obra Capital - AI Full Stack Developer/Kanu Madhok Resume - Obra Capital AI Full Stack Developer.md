# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Built an autonomous Jira ticket-resolution agent with agentic RAG: 6-gate triage, MCP-driven context gathering, FAISS+BM25 retrieval over 11,000 historical SQL queries, self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months and cut turnaround from 30–60 minutes per request to under 10 minutes each. Shipped a real LLM product people depended on daily.
- Built a registry-governed semantic layer over BigQuery with deterministic validation, value canonicalization, complex SQL compilation, and a human review gate; designed to handle sensitive, governed data so the same question returns the same answer every time.
- Built a hybrid orchestrator on top of the agent that lets Product self-serve requests they previously filed as tickets; routes questions through a semantic-layer skill and the context-engineered agent, reasons about disagreements, and feeds discrepancies back to refine definitions over time.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; state and decision logs persist to BigQuery for end-to-end observability.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

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

- Live deployed text-to-SQL copilot (Streamlit front-end + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI / LLM products: RAG (embeddings + FAISS + BM25 + RRF), retrieval systems, ChromaDB semantic memory, LangChain, MCP server design, sub-agent orchestration, context engineering, evaluation suites (golden sets, human-in-the-loop validation), multi-model routing across providers

Backend / full-stack: Python, FastAPI, Cloud Run, REST APIs, CI/CD (pytest, version control), Streamlit, React Recharts, JSONL state stores, Playwright SSO

Data / SQL: BigQuery, dbt, SQL (complex query design + optimization), PySpark, Airflow, Databricks, MySQL

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
