# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures. Partnered cross-functionally with Product, Data Science, and business stakeholders end to end.
- Built and shipped an autonomous Jira ticket-resolution agent with agentic RAG and similarity search: 6-gate triage, MCP-driven context gathering, FAISS + BM25 retrieval over 11,000 historical SQL queries, self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months — cut routine turnaround from 30–60 minutes to under 10 minutes each.
- Built a registry-governed semantic layer with a governance/guardrails framework: a single LLM call maps the question to strict JSON intent (the model never writes SQL), a deterministic gate validates and canonicalizes it into a typed dataclass, and a deterministic compiler emits the SQL — reproducible answers, with the one probabilistic step isolated and regression-tested. New definitions pass a human review gate.
- Built and deployed a headless KPI monitor on a 6-hour cron with end-to-end observability — threshold detection, root-cause analysis, Slack alerts, decision logging, and BigQuery state persistence (no LLM-memory reliance). Designed a 3-tier event-driven v2 platform self-configuring via a BigQuery event registry; new event types ship without code deploys.
- Replaced ~20 recurring recruitment workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests across models persuaded 15% to donate to an opposing cause.

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

Agent / LLM stack: sub-agent orchestration, multi-model routing across providers, MCP server design, context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), ChromaDB semantic memory / vector search, governance & guardrails (typed validation, human-in-the-loop), evaluation suites (golden sets), headless cron agents, event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

APIs / cloud / glue: FastAPI, Cloud Run, AWS (EC2), BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
