# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_AI engineer who ships production LLM/agent systems end-to-end — RAG, orchestration, and evaluation — and partners cross-functionally to deliver measurable impact._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built and shipped to production an autonomous Jira ticket-resolution agent with agentic RAG: 6-gate triage, MCP-driven context gathering, FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10 minutes per request. Shipped a real LLM product people depended on daily.
- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); built an 8-rule deterministic SQL guardrail set and a 23-case golden-query evaluation suite to measure accuracy. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Built a registry-governed semantic layer over BigQuery that boxes the LLM into semantic parsing — one call, strict JSON intent, never SQL — with deterministic validation, value canonicalization, and a deterministic SQL compiler, making the only probabilistic step regression-testable. Designed for sensitive, governed data with a human review gate on definition changes.
- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; decision logs and state persist to BigQuery for end-to-end observability and telemetry.
- Partnered cross-functionally with Product, Data Science, and business stakeholders to translate ambiguous user needs into agent-ready specs and reliable shipped features.
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

AI / LLM products: LLM-powered workflows, agents that plan and act (ReAct-style multi-step), sub-agent orchestration, context engineering, prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), retrieval systems, ChromaDB semantic memory, LangChain, MCP server design, LLM evaluation suites (golden sets, human-in-the-loop, accuracy/latency), multi-model routing across providers

Backend / production: Python, FastAPI, Cloud Run, REST APIs, CI/CD (pytest, version control), headless cron agents, event-driven architectures, decision logging / observability / telemetry, JSONL state stores, Playwright SSO

Cloud AI/ML: Google Vertex AI (Gemini 2.5 Pro / Flash), Cloud Run; LLM integration across providers

Data / SQL: BigQuery, dbt, SQL (complex query design + optimization), PySpark, Airflow, Databricks, MySQL

LLMs: Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit, React Recharts, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
