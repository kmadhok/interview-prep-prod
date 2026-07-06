# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_AI-native engineer and heavy coding-agent power user who takes LLM and agent prototypes to production — hardening, observability, tests, and the review/security practices that hold the bar around agent-generated code._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Took an autonomous agent from prototype to dependable production and owned the long tail that separates a demo from a product: 6-gate triage, MCP-driven context gathering, hybrid FAISS + BM25 retrieval over 11,000 queries, **self-healing execution with a retry budget**, and tracing/decision-logging for observability and clear failure modes. Closed 400+ requests across 8 categories over 15 months; cut routine turnaround from 30–60 minutes to under 10. Stakeholders never knew an agent was answering them.
- Built the **review/testing practices that wrap around agentic systems**: an analytics agent over 67 BigQuery tables with sub-agent orchestration, 8 deterministic rules, human-in-the-loop validation, and a 23-case golden-query evaluation suite (regression tests for a non-deterministic system). Approved by Sr. Director and product leadership; the only AI skill in active use by business teams on Data Ventures.
- Architected a registry-governed layer that boxes the LLM into strict-JSON intent with schema validation (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — the **security/guardrail practices that hold the production bar** on agent output over governed data.
- Designed and deployed a headless KPI monitor with root-cause analysis, Slack alerting, and decision logs persisted to BigQuery for **operational observability**; designed a 3-tier event-driven v2 self-configuring through a registry so new workloads ship without code deploys. Hardened edge cases, failure modes, and flaky behavior into stable operation.
- **Heavy daily coding-agent power user** (Claude Code / Cursor; Claude Opus/Sonnet via Wibey, a Claude Code fork) with a clear point of view on where agents accelerate work and where they fail; integrate third-party APIs (FastAPI/REST) and ship fast without dropping the quality bar.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Took a RAG-to-proposal prototype to a deployed product for an enterprise client on AWS EC2; worked directly with the customer on the integration; owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) application for a 500+ participant experiment; built on top of LLMs (not just as a dev tool); controlled A/B tests persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- On a small startup team, owned a surface end-to-end: logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): an LLM-proxy-style app built on top of LLMs and shipped. Live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI-native engineering: heavy daily coding-agent use (Claude Code, Cursor) with a POV on wrapping agents in review/testing/security; building applications on top of LLMs and agentic systems; MCP server/gateway design; LLM-orchestration & proxies; prompt engineering

Prototype-to-production: hardening, error handling, edge-case/long-tail closure, observability, tracing / decision logging, operational tooling, self-healing/retry, golden-set & regression testing, guardrails & schema validation, CI/CD (pytest)

Backend / APIs: Python, FastAPI, REST APIs, third-party API integration, Cloud Run, GCP / AWS, event-driven architectures, headless cron services, Git _(Go is a growth area — not yet hands-on; primary languages are Python + JavaScript/TypeScript-working)_

Data: BigQuery, dbt, SQL, PySpark, Airflow, Databricks

LLMs / dev: Claude (Opus / Sonnet / Haiku), Gemini (2.5 via Vertex AI), OpenAI; LangChain

Viz: Power BI (DAX), Tableau, Streamlit

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
