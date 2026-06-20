# Kanu Madhok

952-303-1045 - madhok.kanu@gmail.com - github.com/kmadhok - linkedin.com/in/kanu-madhok

End-to-end AI engineer who embeds with stakeholders, rapidly prototypes, and ships production-grade agentic systems with measurable business impact.

Live deployed text-to-SQL copilot: Streamlit + Gemini 2.5 + RAG over historical queries, BigQuery execution, auto-visualization. Demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Senior Data Analyst
*Sep 2024 – Present — Chicago, IL*

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures. Eliminated the analyst as the bottleneck for routine asks.
- Built and shipped to production an autonomous Jira ticket-resolution agent that closed 400+ data requests across 8 categories over 15 months, cutting routine turnaround from 30-60 minutes to under 10 minutes per request. Removed ~130-330+ hours of request-cycle time on routine tickets alone. Under the hood: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Stakeholders never knew an agent was answering them.
- Built a hybrid orchestrator on top of the analytics agent that lets Product self-serve analytics requests they previously submitted as tickets. Routes business questions through two backends in parallel — a CubeJS semantic-layer skill co-built with the DS and product team, and the context-engineered agent — compares outputs, reasons about disagreements, and feeds discrepancies back to refine semantic-layer definitions over time. Converted 30-60 minutes of analyst execution per covered request into product-led self-service.
- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, with no LLM-memory reliance. Designed a v2 architecture as a 3-tier event-driven platform self-configuring via a BigQuery event registry, so new event types ship without code deploys.
- Replaced ~20 distinct recruitment workflows run by hand 1-2x weekly with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, reducing a recurring 3-hour task to ~3 minutes of setup.

### Innovare (EdTech Startup) — Data Scientist
*Oct 2022 – Mar 2023 — Chicago, IL*

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures -15%.

## SELECTED PROJECTS

- **Live text-to-SQL copilot** — Streamlit, Gemini 2.5, LangChain-orchestrated RAG (embeddings over historical queries), BigQuery execution, and auto-visualization. Demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/
- **RAG-to-proposal generator** — deployed on AWS EC2; cut proposal time ~30%; Best in Show, UChicago MSADS Capstone.
- **Persona-driven multi-LLM donation experiment** — OpenAI + Gemini chatbot for a 500+ participant study; controlled A/B tests persuaded 15% to donate to an opposing cause.

## SKILLS

**Agent stack:** MCP server design, sub-agent orchestration, context engineering, prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), LangChain, ChromaDB semantic memory, evaluation suites (golden sets, human-in-the-loop validation), multi-model routing across providers, headless cron agents, event-driven architectures, decision logging / observability

**LLMs:** Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

**AI-assisted development:** Claude Code, Cursor

**APIs / triggers / glue:** FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

**Data:** BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

**Viz:** Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
