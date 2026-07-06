# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_AI engineer who builds on the Claude platform daily — MCP servers, agentic workflows, and prompt pipelines that connect LLMs to enterprise systems (Jira, Slack, BigQuery) and ship to production._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built and shipped to production an autonomous Jira ticket-resolution agent that connects an LLM to enterprise systems via **MCP-driven context gathering**: 6-gate triage, agentic RAG (hybrid FAISS + BM25 over 11,000 historical SQL queries), and self-healing execution with a retry budget. Closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10. Built tracing/decision-logging to troubleshoot API behavior and MCP tool execution across the stack.
- Designed and shipped a self-service analytics agent over 67 BigQuery tables: sub-agent orchestration, prompt pipelines, 8 deterministic rules, and a 23-case golden-query evaluation suite I iterate on to improve reliability and output quality. Approved by Sr. Director and product leadership; currently the only AI skill in active use by business teams on Data Ventures.
- Built a registry-governed semantic layer that boxes the LLM into strict-JSON intent with schema validation (the model never writes SQL), deterministic validation/canonicalization, and a human review gate — enterprise governance and reliable output quality on sensitive, governed data.
- Deployed a headless KPI monitor that detects threshold breaches, runs root-cause analysis, and posts **Slack** alerts, persisting decision logs to BigQuery for observability; designed a 3-tier event-driven v2 self-configuring through a registry so new integrations ship without code deploys.
- Daily builder on **Claude** (Opus / Sonnet / Haiku via Wibey, a Claude Code fork) and **Claude Code / Cursor**; translated ambiguous business problems into AI workflows for non-technical stakeholders, led working sessions, and drove adoption. Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards; Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator for an enterprise consulting client, deployed on AWS EC2; scoped the use case with the client and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests on prompt-driven behavior persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Claude / LLM platform: Anthropic Claude (Opus / Sonnet / Haiku), Claude Code, Claude Chat; daily LLM-app development; prompt engineering & prompt pipelines; LLMs in production

Agent stack: MCP server design & configuration, agentic workflows, sub-agent orchestration, context engineering, RAG & hybrid retrieval (FAISS + BM25 + RRF), evals & testing (golden sets, regression suites, human-in-the-loop), tracing / observability / decision logging, self-healing/retry execution

Integrations & APIs: Python, JavaScript (working), FastAPI, REST APIs (building & consuming), Slack webhooks, Jira, BigQuery, Cloud Run, event-driven architectures, enterprise AI governance / schema validation / guardrails

Data: BigQuery, dbt, SQL, PySpark, Airflow, Databricks; CI/CD (pytest), Git

Other LLMs / dev: Gemini (2.5 via Vertex AI), OpenAI; Cursor, LangChain

Viz: Power BI (DAX, XMLA TMSL), Tableau, Streamlit

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
