# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Architected and owned it end-to-end. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Built an autonomous Jira ticket-resolution agent as a production service: 6-gate triage, MCP-driven context gathering, FAISS+BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget that handles API failures and rate limits gracefully. Closed 400+ data requests across 8 categories over 15 months and cut turnaround from 30–60 minutes per request to under 10 minutes each.
- Built a hybrid orchestrator that routes business questions through two backends in parallel — a semantic-layer skill and a context-engineered agent — compares outputs, reasons about disagreements, and feeds discrepancies back to refine definitions over time. Turned work that used to be analyst tickets into product-led self-service.
- Built a headless KPI monitor on a 6-hour cron with workflow orchestration: detects threshold breaches, runs root-cause analysis, posts Slack alerts via webhooks; state and decision logs persist to BigQuery for end-to-end observability, with no LLM-memory reliance. Designed a 3-tier event-driven v2 self-configuring via a BigQuery registry so new event types ship without code deploys.
- Replaced ~20 recurring workflows I ran by hand with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists with zero duplicates, cutting a 3-hour task to ~3 minutes of setup.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

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

Agent stack: MCP server design, sub-agent orchestration, context engineering, prompt engineering (production use cases), workflow orchestration, RAG (FAISS + BM25 + RRF), evaluation suites (golden sets, human-in-the-loop validation), headless cron agents, event-driven architectures, decision logging / observability

APIs / integration: FastAPI, Cloud Run, REST APIs, Slack webhooks, Playwright SSO, cron triggers, self-healing/retry on rate limits and failures, JSONL state stores, CI/CD (pytest, version control)

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), OpenAI, Gemini (2.5 Pro / Flash via Vertex AI); multi-model routing across providers

Data: Python, BigQuery, dbt, SQL, data modeling, PySpark, Airflow, Databricks, MySQL

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
