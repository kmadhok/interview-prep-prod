# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures. Eliminated the analyst as the bottleneck for routine asks.
- Built an autonomous Jira ticket-resolution agent that resolves issues without human intervention: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months — cut routine turnaround from 30–60 minutes to under 10 minutes and removed ~130–330+ hours of request-cycle time. Stakeholders never knew an agent was answering them.
- Built a registry-governed semantic layer that boxes the LLM into semantic parsing — one call, strict JSON intent, never SQL — with deterministic validation, value canonicalization, UPC normalization with live BigQuery existence checks, and a deterministic SQL compiler, making answers reproducible and the only probabilistic step regression-testable. New or changed definitions pass a human review gate before entering the registry.
- Built a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, so the agent has no LLM-memory reliance. Designed a v2 architecture as a 3-tier event-driven platform self-configuring via a BigQuery event registry. New event types ship without code deploys.
- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Agent stack: MCP (Model Context Protocol) server design, sub-agent orchestration, context engineering, prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), LangChain, ChromaDB semantic memory, evaluation suites (golden sets, human-in-the-loop validation), multi-model routing across providers, headless cron agents, event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

APIs / triggers / glue: FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
