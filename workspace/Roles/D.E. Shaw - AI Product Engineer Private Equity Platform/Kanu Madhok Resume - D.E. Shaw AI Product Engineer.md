# Kanu Madhok

952-303-1045 • madhok.kanu@gmail.com • [github.com/kmadhok](https://github.com/kmadhok) • [linkedin.com/in/kanu-madhok](https://linkedin.com/in/kanu-madhok)

_Text source for the .pdf. In the formatted version, city · date sit right-aligned to the page edge._

---

## PROFESSIONAL EXPERIENCE

### Walmart Data Ventures — Chicago, IL · Sep 2024 – Present
_Senior Data Analyst_

- Designed and shipped to production an AI-native product — a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Owned it end-to-end from how data is structured to the business logic that shapes behavior, working with Product and business stakeholders to translate ambiguous workflow challenges into product direction. Approved by Sr. Director and product leadership and the only AI skill in active use by business teams on Data Ventures.
- Built a workflow product that streamlines business operations: a hybrid orchestrator that lets Product self-serve analytics requests they previously filed as tickets — routing questions through two backends, comparing outputs, reasoning about disagreements, and refining the underlying definitions over time. Converted 30–60 minutes of analyst execution per covered request into product-led self-service.
- Built and shipped to production an autonomous agent that translates AI capabilities — autonomous tool use, multi-step reasoning — into a practical product feature: 6-gate triage, MCP-driven context gathering, agentic RAG (FAISS + BM25) over 11,000 historical queries, and self-healing execution. Drove it from prototype to production; closed 400+ requests across 8 categories over 15 months, cutting turnaround from 30–60 minutes to under 10.
- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence. Designed a v2 as a 3-tier event-driven platform self-configuring via a BigQuery event registry — new event types ship without code deploys.
- Replaced ~20 recurring recruitment workflows with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, turning a recurring 3-hour task into ~3 minutes of setup — AI leverage applied where it removed genuine toil.

### University of Chicago — Data Science Institute — Chicago, IL · Jan – Sep 2024
_Graduate Researcher, Data & Democracy Initiative_

- Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### FTI Consulting — UChicago MSADS Capstone — Chicago, IL · Jan – Aug 2024

- Took a client-facing RAG-to-proposal product from conception to completion, deployed on AWS EC2; cut proposal time ~30%; Best in Show — UChicago MSADS Capstone.

### Innovare (EdTech Startup) — Chicago, IL · Oct 2022 – Mar 2023
_Data Scientist_

- Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures –15%.

---

## SELECTED PROJECT

- Live deployed text-to-SQL copilot (Streamlit UI + Gemini 2.5 + LangChain-orchestrated RAG over historical queries, BigQuery execution, auto-visualization): live demo — https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## SKILLS

AI product & agent stack: LLM-native product design, agentic frameworks (tool/function calling, multi-step reasoning, autonomous agents), MCP (Model Context Protocol) server design, sub-agent orchestration, context engineering, prompt engineering, RAG (FAISS + BM25 + RRF), evaluation suites (golden sets, human-in-the-loop validation), event-driven architectures, decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

APIs / data / UI: FastAPI, Cloud Run, BigQuery (scheduled queries), SQL, MySQL, Streamlit, React Recharts, Slack webhooks, cron, Playwright SSO, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks

---

## EDUCATION

The University of Chicago — M.S., Applied Data Science (GPA 4.0) — Chicago, IL
Loyola University Chicago — B.S., Information Systems & Economics (GPA 3.5) — Chicago, IL
