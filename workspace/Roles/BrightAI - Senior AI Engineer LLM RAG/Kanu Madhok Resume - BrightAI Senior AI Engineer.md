# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built and shipped to production an autonomous ticket-resolution agent using agentic RAG: 6-gate triage, MCP-driven context gathering, and FAISS + BM25 retrieval (with reciprocal rank fusion) over 11,000 historical SQL queries, plus self-healing execution with a 10-retry budget. Closed 400+ requests across 8 categories over 15 months, cutting routine turnaround from 30–60 minutes to under 10 minutes. Owned the retrieval quality and debugging across embedding, ranking, model output, and system logic once real users were on it.
- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite to measure accuracy and catch regressions in production. Approved by Sr. Director and product leadership and the only AI skill in active use by business teams on Data Ventures.
- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, so the agent has no LLM-memory reliance. Designed a v2 as a 3-tier event-driven platform self-configuring via a BigQuery event registry — new event types ship without code deploys.
- Evolved the analytics skill into a registry-governed semantic layer over BigQuery: a single LLM call maps the question to strict JSON intent (the model never writes SQL); a deterministic gate validates and canonicalizes intent before a deterministic compiler emits the SQL — same question, same answer, every time, with the one probabilistic step regression-testable.
- Built pipelines that ingest, preprocess, and index large data corpora: replaced ~20 recurring recruitment workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, turning a recurring 3-hour task into ~3 minutes of setup.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Production-grade RAG-to-proposal generator deployed on AWS EC2; cut proposal time ~30%; Best in Show — UChicago MSADS Capstone.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG with embeddings over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

RAG & retrieval: embeddings-based semantic search, FAISS + BM25 + RRF, ChromaDB semantic memory, agentic RAG, LangChain, evaluation suites (golden sets, human-in-the-loop validation)

Agent stack: MCP (Model Context Protocol) server design, sub-agent orchestration, context engineering, prompt engineering, multi-model routing across providers, headless cron agents, event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

APIs / triggers / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
