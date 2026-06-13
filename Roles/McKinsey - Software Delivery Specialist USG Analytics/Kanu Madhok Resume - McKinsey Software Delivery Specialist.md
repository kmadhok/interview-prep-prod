# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .docx / .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration, human-in-the-loop validation, 8 deterministic SQL rules, and a 23-case golden-query evaluation suite; partnered with Product/DS/business stakeholders to translate ambiguous questions into agent-ready specs. Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures.
- Built a production Jira ticket-resolution agent — 6-gate triage, MCP context gathering, agentic RAG (FAISS + BM25 over 11,000 historical SQL queries), self-healing execution — that closed 400+ requests across 8 categories and cut turnaround from 30–60 minutes to under 10 minutes per ticket. Stakeholders never knew an agent was answering them.
- Built a hybrid text-to-data orchestrator that routes questions through two backends in parallel — a CubeJS semantic-layer skill (co-built with DS/product) and the context-engineered agent — compares outputs, reasons through disagreements, and refines the semantic layer over time; let Product self-serve requests they previously filed as tickets.
- Built a production headless KPI monitor (6-hour cron) that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; full observability via decision logging + BigQuery state, no LLM-memory reliance. Designed a 3-tier event-driven v2 self-configuring through a BigQuery event registry — new event types ship without code deploys.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- RAG-to-proposal generator deployed on AWS EC2 for a client engagement; cut proposal time ~30%; Best in Show — UChicago MSADS Capstone.

- **Selected project:** live-deployed text-to-SQL copilot — Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization. Demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Agentic AI: multi-agent / sub-agent orchestration, tool-calling, MCP server design, context engineering, memory management, prompt engineering, multi-model routing, headless cron agents, event-driven architectures; LLMs — Claude (Opus/Sonnet/Haiku via Wibey), Gemini (2.5 Pro/Flash via Vertex AI), OpenAI

RAG & evaluation: RAG (embeddings + FAISS + BM25 + RRF), ChromaDB semantic memory, LangChain, evaluation suites (golden sets, human-in-the-loop validation), decision logging / observability

Backend & deployment: Python, FastAPI, Cloud Run, microservices / API integration, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data & viz: BigQuery, dbt, SQL, PySpark, Airflow, Databricks, MySQL; Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
