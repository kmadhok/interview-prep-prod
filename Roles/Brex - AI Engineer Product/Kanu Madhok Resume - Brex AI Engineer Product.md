# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Product-minded AI engineer who ships the harness around agents — reviewer surfaces, data contracts, eval and feedback loops — that makes non-deterministic reasoning trustworthy and operable for real users._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables and the **product harness around it** that makes the agent's output trustworthy: sub-agent orchestration (Context Researcher → SQL Drafter → Validator → Devil's Advocate), 8 deterministic SQL rules, human-in-the-loop review, and a 23-case golden-query evaluation suite. Approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures.
- Built and shipped an autonomous Jira ticket-resolution agent and the operability layer that lets a non-deterministic system be relied on: 6-gate triage, MCP-driven context gathering, agentic RAG (FAISS + BM25 over 11,000 historical SQL queries), self-healing execution with a retry budget, and tracing/decision-logging for observability and clear failure modes. Closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10. Stakeholders never knew an agent was answering them.
- Built a registry-governed semantic layer that defines the **data contracts** between an LLM and the system of record: strict-JSON intent with Pydantic-style schema validation (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — the product compensating for a non-deterministic core so outputs stay reproducible and trustworthy on governed data.
- Designed and deployed a headless KPI monitor that detects threshold breaches, runs root-cause analysis, and posts Slack alerts, persisting decision logs to BigQuery for end-to-end observability and feedback signals; designed a 3-tier event-driven v2 that self-configures through a registry so new behaviors ship without code deploys.
- Translated ambiguous product requirements into shipped features for technical and non-technical stakeholders, led working sessions, and drove adoption; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; **ran controlled A/B experiments** on prompt-driven behavior and made calls based on what the data said — 15% persuaded to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator deployed on AWS EC2; scoped the use case with the client, talked to users directly, and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- On a small team, owned a product surface end-to-end: logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit front-end + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): built the backend and the customer-facing UI myself. Live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI / agents: agentic systems & the product harness around them (evaluation, tracing, feedback loops, human-in-the-loop workflows), agent orchestration/routing, LLM-orchestration, context engineering, MCP server design, guardrails & schema validation, productizing non-deterministic systems

Evaluation & experimentation: evals & testing (golden sets, regression suites, HITL), controlled A/B experiments, tracing / observability / decision logging, product feedback loops

Backend: Python, FastAPI, REST APIs, system design, data modeling, API shape, data contracts / schema validation, Cloud Run, GCP / AWS, event-driven architectures, headless cron services, CI/CD (pytest), Git

Frontend (working level): Streamlit, React Recharts, customer-facing UI flows _(production React/TS is a growth area, not a core strength)_

Data: BigQuery, dbt, SQL, PySpark, Airflow, Databricks

LLMs / dev: Claude (Opus / Sonnet / Haiku), Gemini (2.5 via Vertex AI), OpenAI; Claude Code, Cursor, LangChain

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
