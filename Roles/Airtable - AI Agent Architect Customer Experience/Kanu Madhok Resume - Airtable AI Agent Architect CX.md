# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .docx / .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built and shipped an autonomous ticket-resolution agent that closed 400+ requests across 8 categories over 15 months without human intervention — cutting turnaround from 30–60 minutes per request (up to a full day for complex ones) to under 10 minutes. Architecture: 6-gate triage decision logic, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical queries, self-healing execution with a 10-retry budget. Stakeholders never knew an agent was answering them.
- Designed and shipped a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite holding retrieval accuracy and catching hallucinated answers before they reach a user. Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures.
- Built a registry-governed semantic layer that boxes the LLM into semantic parsing — one call, strict JSON intent, never raw SQL — with deterministic validation, value canonicalization, and a deterministic compiler, making answers auditable and reproducible (same question, same answer) and the single probabilistic step regression-testable. Definition changes pass a human review gate before entering the registry.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, so the agent has no LLM-memory reliance. Designed a v2 3-tier event-driven platform self-configuring through a BigQuery event registry — new event types ship without code deploys.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users), tying request-turnaround metrics to business outcomes; cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

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

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Agent stack: MCP (Model Context Protocol) server design, sub-agent orchestration, context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), ChromaDB semantic memory, multi-model routing across providers, headless cron agents, event-driven architectures

Reliability & evaluation: golden-set evaluation suites, human-in-the-loop validation, deterministic guardrails / validation gates, decision logging / observability, regression-testable LLM contracts, A/B testing

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

APIs / triggers / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
