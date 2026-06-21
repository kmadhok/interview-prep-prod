# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables, owning it end to end: sub-agent orchestration with context-isolated validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate), 8 deterministic SQL rules, and a 23-case golden-query evaluation suite. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.
- Evolved that agent into a registry-governed semantic-layer platform: YAML definitions plus SQLite vocabulary snapshots define the domain; a deterministic prompt builder generates the LLM contract; a single LLM call maps each question to strict JSON intent (the model never writes SQL); a deterministic gate validates and canonicalizes it before a deterministic compiler emits the SQL — same question, same answer, every time, with the one probabilistic step regression-testable. New or changed definitions pass a human review gate before entering the registry.
- Built an autonomous Jira ticket-resolution service: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months — cut turnaround from 30–60 minutes per request (and up to a full day for complex ones) to under 10 minutes each. Stakeholders never knew an agent was answering them.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; state persists to BigQuery so the agent has no LLM-memory reliance. Designed its v2 as a 3-tier event-driven platform (reactive events, threshold KPIs, PM-owned themes) self-configuring via a BigQuery event registry — new event types ship without code deploys.
- Replaced ~20 distinct recruitment workflows I'd been running by hand 1–2× weekly with end-to-end automation on a 68-table BigQuery platform. Stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- RAG-to-proposal generator (knowledge-assistant over a document corpus) deployed on AWS EC2; cut proposal time ~30%; Best in Show — UChicago MSADS Capstone.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Platform & engineering: event-driven architectures, registry-governed semantic layers, deterministic compilers, headless cron agents, evaluation suites (golden sets, human-in-the-loop validation), decision logging / observability, CI/CD (pytest, version control)

APIs / services / cloud: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores

Agent & AI stack: MCP (Model Context Protocol) server design, sub-agent orchestration, context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), ChromaDB semantic memory, multi-model routing across providers

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

Front-end / viz: Streamlit, React Recharts, Power BI (DAX, XMLA TMSL), Tableau, LookML, Matplotlib

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
