# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_AI engineer who designs and ships production agent systems — orchestration, prompt frameworks, safety controls, and LLM evaluation pipelines that automate complex workflows end-to-end._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a multi-agent orchestrator that reasons about a task, plans, and executes: a self-service analytics agent over 67 BigQuery tables with a Context Researcher → SQL Drafter → Validator → Devil's Advocate sub-agent flow, 8 deterministic SQL rules, and human-in-the-loop oversight. Approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures — a production agent system, not a prototype.
- Built and shipped an autonomous Jira agent that automates a complex multi-step workflow end-to-end: 6-gate triage, MCP-driven context gathering, agentic RAG (FAISS + BM25) over 11,000 historical SQL queries, and self-healing execution with a retry budget; closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10 — reducing manual intervention on routine operations.
- Built LLM evaluation and agent-behavior testing infrastructure: a 23-case golden-query evaluation suite plus regression tests and human-in-the-loop validation, and a registry-governed semantic layer that boxes the LLM into strict-JSON intent with deterministic validation and a human review gate — safety/oversight mechanisms that make agent behavior reliable and reproducible.
- Built a hybrid orchestrator that routes a request through two backends, reasons about disagreements, and refines definitions over time; built a headless KPI monitor (6-hour cron) with root-cause analysis, Slack alerts, and decision-logging observability — low-touch autonomous services with end-to-end traceability.
- Worked across GPT/Claude/Gemini (multi-model routing) and shipped LLM-powered services on FastAPI + Cloud Run; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Built a RAG-to-proposal generator deployed on AWS EC2; owned design and evaluation end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

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

Agent systems: agent orchestrator design, multi-step workflow automation, sub-agent orchestration, reasoning/planning/execution loops, agent-behavior testing, safety mechanisms & human-in-the-loop oversight, context engineering, MCP server design

LLM evaluation: golden-set / regression evaluation suites, evaluation metrics & pipelines, output validation / guardrails, decision logging / tracing / observability

LLM products: prompt-engineering frameworks, RAG & vector search (embeddings + FAISS + BM25 + RRF), multi-model routing (GPT-4 / Claude / Gemini), LangChain

Backend / cloud: Python, FastAPI, microservices, REST APIs, Cloud Run, GCP / AWS, CI/CD (pytest)

Data: BigQuery, dbt, SQL, PySpark, Airflow, Databricks, MySQL

LLMs / dev: Claude (Opus / Sonnet / Haiku), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI GPT-4; Claude Code, Cursor

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
