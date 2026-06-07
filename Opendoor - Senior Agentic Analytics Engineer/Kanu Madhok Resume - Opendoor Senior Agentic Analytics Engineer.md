# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .docx / .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Shipped to production a self-service analytics agent over 67 BigQuery tables that lets business teams query data conversationally instead of waiting on an analyst — sub-agent orchestration, human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate), 8 deterministic SQL rules, 23-case golden-query eval suite. Approved by Sr. Director/product leadership and the only AI skill in active use by business teams on Data Ventures.
- Built a hybrid orchestrator on top of it that lets Product self-serve analytics requests previously filed as tickets: routes questions through a CubeJS semantic-layer skill and the context-engineered agent in parallel, reasons through disagreements, and refines semantic-layer definitions over time. Cut response time 67–92% (30–60 min of analyst execution to under 10 min) and dropped analyst touch time to near-zero.
- Built and deployed a headless KPI monitor on a 6-hour cron that surfaces what matters without being asked: detects threshold breaches, runs root-cause analysis, and posts Slack alerts with recommended focus; BigQuery state persistence, no LLM-memory reliance. Designed a 3-tier event-driven v2 self-configuring via a BigQuery event registry — new event types ship without code deploys.
- Built an autonomous Jira ticket-resolution agent (6-gate triage, MCP context gathering, agentic RAG over 11,000 historical SQL queries, self-healing execution) that closed 400+ requests across 8 categories, cut routine turnaround from 30–60 min to under 10 min, and removed ~130–330+ hours of request-cycle time. Stakeholders never knew an agent was answering them.
- Automated ~20 recurring recruitment workflows on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, cutting a recurring 3-hour task to ~3 minutes of setup.
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

Agent stack: MCP server design, sub-agent orchestration, context engineering, prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), LangChain, evaluation suites (golden sets, human-in-the-loop validation), multi-model routing, headless cron agents, event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI; AI-assisted dev: Claude Code, Cursor

Data & semantic layer: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, CubeJS semantic layer

APIs / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, CI/CD (pytest, version control)

Viz: Power BI (DAX), Tableau, LookML, Streamlit, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
