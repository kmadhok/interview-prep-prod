# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Forward-deployed analytics engineer who embeds with stakeholders, builds governed semantic layers that make data agent-ready, and turns ambiguous business questions into natural-language answers — Claude/Cursor as the daily dev environment._

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Built a registry-governed semantic layer over BigQuery that exposes governed business meaning to natural-language queries: YAML/SQLite definitions of dimensions, values, and table wiring; a single LLM call maps the question to strict-JSON intent (the model never writes SQL); deterministic validation, value canonicalization, and a deterministic SQL compiler make answers reproducible; definition changes pass a human review gate. Exactly the metric/dimension/relationship modeling an AI agent needs to reason correctly over customer data.
- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables that lets business stakeholders ask questions in plain English: sub-agent orchestration, 8 deterministic SQL rules, and a 23-case golden-query evaluation suite for QA; approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures. Identified and resolved upstream data-structure and naming gaps that would otherwise make the agent return wrong answers.
- Built and shipped an autonomous Jira ticket-resolution agent with agentic RAG: 6-gate triage, MCP-driven context gathering, hybrid FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution; closed 400+ requests across 8 categories over 15 months and cut routine turnaround from 30–60 minutes to under 10. Built tracing/decision-logging for observability and clear failure modes.
- Replaced ~20 recurring manual workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, reducing a recurring 3-hour task to ~3 minutes of setup — pipeline design, data QA, and automated testing across the full stack.
- Translated ambiguous business problems into technical specs for technical and non-technical stakeholders, led working sessions, and drove adoption; delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes; Making a Difference Award. Daily driver of Claude (Opus/Sonnet) and Cursor/Claude Code as primary build environment.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Delivered a RAG-to-proposal generator for an enterprise consulting client, deployed on AWS EC2; scoped the use case with the client, communicated tradeoffs, and owned delivery end-to-end; cut proposal time ~30%; **Best in Show — UChicago MSADS Capstone**.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; designed controlled A/B tests (rigorous validation methodology) that persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); feature engineering on real-world data; retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit front-end + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): turns plain-English questions into governed SQL answers. Live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

Analytics engineering: data modeling, semantic layer / semantic views, single-source-of-truth modeling, metrics & dimension definitions, data QA & automated testing, data governance (permissions, lineage, definitions), dbt

Data / SQL: Advanced SQL (CTEs, window functions, incremental pipelines), BigQuery, Python (type-hinted), PySpark, Airflow, Databricks, Git (PRs/branches/code review), CI/CD (pytest)

AI / LLM: NL-to-SQL over governed data, AI agents & agentic workflows, agent orchestration, RAG & hybrid retrieval (FAISS + BM25 + RRF), MCP server design, evals (golden sets, regression suites, human-in-the-loop), schema validation / data contracts

AI-assisted dev (daily): Claude (Opus/Sonnet), Cursor, Claude Code, LangChain; Gemini (2.5 via Vertex AI), OpenAI

Client-facing: business-requirements-to-spec translation, stakeholder workshops, reusable playbooks/templates; Viz: Power BI (DAX), Tableau, Streamlit

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
