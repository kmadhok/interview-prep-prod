# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Built and shipped to production an autonomous Jira ticket-resolution agent: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Closed 400+ requests across 8 categories over 15 months — cut routine turnaround from 30–60 minutes to under 10 minutes each. Stakeholders never knew an agent was answering them.
- Built a hybrid orchestrator that routes business questions through two backends in parallel — a CubeJS semantic-layer skill co-built with the DS and product team, and a context-engineered agent — then compares outputs, reasons about disagreements (a verifier/critic pattern), and feeds discrepancies back to refine the semantic layer over time. Let Product self-serve analytics requests they previously filed as tickets.
- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence. Designed a v2 as a 3-tier event-driven platform self-configuring via a BigQuery event registry — new event types ship without code deploys.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Built a client-facing RAG-to-proposal generator deployed on AWS EC2 that cut proposal time ~30%; translated the consulting team's requirements into the system and delivered it hands-on. Best in Show — UChicago MSADS Capstone.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Agent & evaluation stack: MCP (Model Context Protocol) server design, sub-agent orchestration, multi-agent patterns (planner / executor / validator / critic), context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), evaluation suites (golden sets, human-in-the-loop validation), multi-model routing across providers, event-driven architectures, decision logging / observability

AI-assisted development: Claude Code, Cursor

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

APIs / triggers / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
