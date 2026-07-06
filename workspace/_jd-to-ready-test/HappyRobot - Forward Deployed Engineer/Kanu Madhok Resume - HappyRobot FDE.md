# Kanu Madhok

952-303-1045 · madhok.kanu@gmail.com · github.com/kmadhok · linkedin.com/in/kanu-madhok

End-to-end AI engineer who embeds with stakeholders, rapidly prototypes, and ships production-grade agentic systems with measurable business impact.

Live Demo: NL-to-SQL Copilot — Dockerized Streamlit on GCP Cloud Run · https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## Experience

### Walmart Data Ventures — Senior Data Analyst
*Sep 2024 – Present · Chicago, IL*

- Built and shipped to production an autonomous Jira ticket-resolution agent that closed 400+ data requests across 8 categories over 15 months, cutting routine turnaround from 30–60 minutes to under 10 minutes per request. Removed ~130–330+ hours of request-cycle time on routine tickets alone. Under the hood: 6-gate triage, MCP-driven context gathering, agentic RAG with FAISS + BM25 retrieval over 11,000 historical SQL queries, and self-healing execution with a 10-retry budget. Stakeholders never knew an agent was answering them.

- Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher → SQL Drafter → Validator → Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures.

- Built a hybrid orchestrator on top of the analytics agent that lets Product self-serve analytics requests they previously submitted as tickets. Routes questions through two backends in parallel — a CubeJS semantic-layer skill co-built with the DS and product team, and the context-engineered agent itself — compares outputs, reasons about disagreements, and feeds discrepancies back to refine semantic-layer definitions over time. Converted 30–60 minutes of analyst execution per covered request into product-led self-service.

- Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence. Designed a 3-tier event-driven v2 architecture self-configuring through a BigQuery event registry so new event types ship without code deploys.

- Replaced ~20 recurring recruitment workflows run by hand 1–2x weekly with end-to-end automation on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates, reducing a recurring 3-hour task to ~3 minutes of setup.

- Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1–24 hours to 5–10 minutes. Making a Difference Award.

### FTI Consulting — UChicago MSADS Capstone
*Jan – Aug 2024 · Chicago, IL*

- Built a RAG-to-proposal generator deployed on AWS EC2 and adopted into FTI Consulting's workflow; cut proposal time ~30%. Best in Show — UChicago MSADS Capstone.

### University of Chicago, Data Science Institute
*Jan – Sep 2024 · Chicago, IL*

- Built a persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

### Innovare (EdTech Startup) — Data Scientist
*Oct 2022 – Mar 2023 · Chicago, IL*

- Built a logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures -15%.

---

## Selected Project

- **Live NL-to-SQL Copilot** — Streamlit + Gemini 2.5 + LangChain-orchestrated RAG (embeddings over historical queries), BigQuery execution, auto-visualization. Public-facing version of the agent-on-data architecture deployed inside Walmart Data Ventures. Demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

---

## Skills

**Agent stack:** MCP server design, sub-agent orchestration, context engineering, prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), LangChain, ChromaDB semantic memory, evaluation suites (golden sets, human-in-the-loop validation), multi-model routing across providers, headless cron agents, event-driven architectures, decision logging / observability

**LLMs:** Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

**AI-assisted development:** Claude Code, Cursor

**APIs / triggers / glue:** FastAPI, Cloud Run, BigQuery scheduled queries, Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

**Data:** BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

**Viz / front-end:** Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts

---

<!--
TAILORING NOTES (not part of the resume — strip before export):

Archetype: FDE / client-facing. Themes: end-to-end, agents, LLM-orchestration, platform, business-translation, cross-functional.

Lead ordering rationale:
- Jira agent (A3) leads: production agent + integration-heavy (MCP, third-party systems) + "stakeholders never knew an agent was answering" maps to HappyRobot's autonomous-AI-worker + customer-facing thesis.
- Analytics agent (A1) + hybrid orchestrator (A2): production agents + business-translation + cross-functional partnership (Product/DS) = the "blends customer engineering with technical development" ask.
- FTI RAG generator (F1) kept high as the cleanest "shipped into a real customer's workflow and they adopted it" FDE proof.
- NL-to-SQL demo (A7): clickable proof of LLM-orchestration + RAG.

CANONICAL-ONLY: every bullet pulled verbatim/condensed from Resume Achievements Master.md (A1, A2, A3, A4, A5, A6, F1, U1, I1, A7). No metric invented, no status upgraded.

KNOWN GAP vs JD (surface in report, do NOT fabricate to fill):
- JD wants "Comfortable Full-Stack: React, TypeScript, Node.js." Kanu's canonical skills block has Python, FastAPI, Streamlit, React Recharts (viz) — but NOT confirmed React/TypeScript/Node.js app-development depth. Left React Recharts in the viz line honestly; did NOT add TypeScript or Node.js. [VERIFY: does Kanu have production React/TS/Node experience to claim full-stack? If yes, promote to Resume Achievements Master first, then add here. If no, this is a real gap to address in the cover note / interview, not on the resume.]
- JD wants "LLM prompting and tuning of voices and transcribers." Kanu has heavy LLM prompting/orchestration; no voice/speech (TTS/STT) experience in canonical material. Not claimed.
-->
