# Resume Achievements Master - Kanu Madhok

**Purpose.** This is the conservative source of truth for resume-worthy achievements. Everything in this file is intended to be safe to use in tailored resumes, outreach notes, and interview prep.

**Rule for future tailoring.** Pull from this file by default. If a role seems to need a stronger or more specific claim than what appears here, check `Resume Claims To Verify.md` and leave a `[VERIFY: ...]` note for Kanu rather than importing the claim.

**Important source rule.** Tailored resumes in role folders are outputs, not sources. Do not use an older tailored resume to justify a stronger claim. If a fact is not in the canonical achievement entry's **Verified proof points** or explicitly confirmed by Kanu, it is not resume-safe.

**Separate verification queue.** Unverified BCG/legacy claims live in `Resume Claims To Verify.md`. Do not use that file as resume source material until a claim has been confirmed and promoted here.

**Current verified sources checked.**

- `Deloitte - Anthropic Forward Deployed Engineer GPS/Kanu Madhok Resume - Deloitte FDE GPS.md`
- `Walmart - Principal SWE Agent Builder/Agent Builder Resume.png`

---

## Resume Tailoring Contract - Read Before Writing Any Resume

Use this contract for `tailor-resume`, `jd-to-ready`, or any manual resume draft.

### Claim statuses

- **Resume-safe:** Facts inside this file, especially each entry's **Verified proof points**.
- **Private drafting only:** Anything in `Resume Claims To Verify.md`. These can guide questions for Kanu, but cannot appear in outward-facing material.
- **Legacy draft only:** Anything that appears only in an older role-specific resume. Treat it as untrusted until it is promoted into this file with proof.

### Allowed transformations

- Reorder bullets to match the JD.
- Shorten or lengthen a canonical bullet without changing the facts.
- Swap vocabulary to match the role, as long as the claim stays equivalent.
- Use a subset of verified proof points.
- Combine two canonical achievements only when both IDs are named in private drafting notes and the combined sentence does not create a new causal claim.

### Forbidden transformations

- Do not upgrade status language: "demo" -> "production", "active use" -> "org-wide rollout", "co-built" -> "owned", "designed v2" -> "shipped v2".
- Do not add metrics that are not in **Verified proof points**: accuracy, latency, adoption, user count, LOC, test count, dataset size, time window, or dollar impact.
- Do not borrow a number from one achievement and attach it to another.
- Do not use "first", "only", "official", "productized", "org-wide", or "deployed" unless that exact status is verified in the achievement entry.
- Do not list skills just because the JD asks for them. Skills must come from the canonical skills block or a verified project entry.
- Do not turn a project narrative from `Master Story Bank.md` into resume facts if those facts conflict with this file. This file wins for numbers and proof points.

### Pre-send checklist

Before saving a tailored resume, compare any unusually strong metric, adoption claim, or platform claim against this file. If the fact is not here, remove it or add a `[VERIFY: ...]` note for Kanu. The known blocked phrases and legacy-risk resumes are tracked in `Resume Claims To Verify.md`.

---

## Header - Contact Block

```text
Kanu Madhok
952-303-1045 - madhok.kanu@gmail.com - github.com/kmadhok - linkedin.com/in/kanu-madhok
```

**Positioning line (cross-role, FDE-friendly):**

> End-to-end AI engineer who embeds with stakeholders, rapidly prototypes, and ships production-grade agentic systems with measurable business impact.

Optional selected-project line, supported by the Deloitte/SWE resume:

```text
Live deployed text-to-SQL copilot: Streamlit + Gemini 2.5 + RAG over historical queries, BigQuery execution, auto-visualization
Demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/
```

---

# Canonical Achievements - Supported By Deloitte/SWE Resume

## Walmart Data Ventures - Senior Data Analyst

*Sep 2024 - Present - Chicago, IL*

### A1. Self-Service Analytics Agent Over BigQuery

**Tags:** `agents` - `BigQuery` - `sub-agent orchestration` - `context engineering` - `validation` - `business-translation`

**Resume bullet, conservative:**

> Designed and shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration and human-in-the-loop validation (Context Researcher -> SQL Drafter -> Validator -> Devil's Advocate); 8 deterministic SQL rules and a 23-case golden-query evaluation suite. Partnered with Product, Data Science, and business stakeholders to translate ambiguous business questions into agent-ready specs. Approved by Sr. Director and product leadership and currently the only AI skill in active use by business teams on Data Ventures. Eliminated the analyst as the bottleneck for routine asks.

**Compact variant:**

> Shipped to production a self-service analytics agent over 67 BigQuery tables with sub-agent orchestration, human-in-the-loop validation, 8 deterministic SQL rules, and a 23-case golden-query evaluation suite; approved by Sr. Director/product leadership and used cross-functionally by business teams on Data Ventures.

**Verified proof points:** 67 BigQuery tables - 4-agent flow - 8 deterministic SQL rules - 23 golden-query test cases - Sr. Director and product leadership approval - active use by business teams.

---

### A2. Hybrid Orchestrator / Semantic-Layer Comparison Flow

**Tags:** `agents` - `semantic layer` - `orchestration` - `cross-functional` - `business-translation`

**Resume bullet, conservative:**

> Built a hybrid orchestrator on top of the analytics agent. Routes business questions through two backends in parallel: a CubeJS semantic-layer skill co-built with the DS and product team, and the context-engineered agent itself. Compares outputs, reasons about disagreements, and feeds discrepancies back to refine the semantic layer's definitions over time.

**Compact variant:**

> Built a hybrid text-to-data orchestrator that compares a CubeJS semantic-layer skill with a context-engineered agent, reasons through disagreements, and feeds discrepancies back into semantic-layer definition refinement.

**Verified proof points:** CubeJS semantic-layer skill - co-built with DS and product team - context-engineered agent - parallel routing - disagreement review/refinement loop.

---

### A3. Autonomous Jira Ticket-Resolution Agent

**Tags:** `agents` - `MCP` - `RAG` - `FAISS` - `BM25` - `workflow automation` - `stakeholder support`

**Resume bullet, conservative:**

> Built and shipped to production an autonomous Jira ticket-resolution agent: 6-gate triage, MCP-driven context gathering, agentic RAG with embeddings-based FAISS + BM25 retrieval over 11,000 historical SQL queries, self-healing execution with a 10-retry budget. Closed 400+ data requests across 8 categories over 15 months; cut turnaround from 30-60 minutes per request, and up to a full day for complex ones, to under 10 minutes each. Stakeholders never knew an agent was answering them.

**Compact variant:**

> Built a production Jira ticket-resolution agent with 6-gate triage, MCP-driven context gathering, agentic RAG (embeddings + FAISS + BM25) over 11,000 historical SQL queries, and self-healing execution; closed 400+ requests across 8 categories and cut turnaround from 30-60 minutes to under 10 minutes.

**Verified proof points:** 6-gate triage - MCP-driven context gathering - FAISS+BM25 - 11,000 historical SQL queries - 10-retry budget - 400+ data requests - 8 categories - 15 months - 30-60 minutes to under 10 minutes - complex requests up to a full day before.

---

### A4. Recruitment Workflow Automation

**Tags:** `automation` - `BigQuery` - `sampling` - `data operations` - `end-to-end`

**Resume bullet, conservative:**

> Replaced ~20 distinct recruitment workflows I had been running by hand 1-2x weekly with end-to-end automation on a 68-table BigQuery platform. Stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates. A recurring 3-hour task now takes ~3 minutes of setup.

**Compact variant:**

> Automated ~20 recurring recruitment workflows on a 68-table BigQuery platform; stratified-sampling pipelines recruited 280,000+ panelists across 29 categories with zero duplicates and reduced a recurring 3-hour task to ~3 minutes of setup.

**Verified proof points:** ~20 workflows - 1-2x weekly manual cadence - 68-table BigQuery platform - 280,000+ panelists - 29 categories - zero duplicates - 3 hours to ~3 minutes.

---

### A5. Headless KPI Monitor And Event-Driven V2 Design

**Tags:** `agents` - `monitoring` - `Slack` - `BigQuery` - `event-driven architecture` - `root-cause analysis`

**Resume bullet, conservative:**

> Built and deployed to production a headless KPI monitor on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts; end-to-end observability via decision logging and BigQuery state persistence, so the agent has no LLM-memory reliance. Designed a v2 architecture as a 3-tier event-driven platform (reactive events, threshold KPIs, PM-owned themes) self-configuring via a BigQuery event registry. New event types ship without code deploys.

**Compact variant:**

> Built a production headless KPI monitor that runs every 6 hours, detects threshold breaches, performs root-cause analysis, posts Slack alerts, and persists decision logs to BigQuery for end-to-end observability; designed a 3-tier event-driven v2 architecture self-configuring through a BigQuery event registry.

**Verified proof points:** 6-hour cron - threshold breaches - root-cause analysis - Slack alerts - BigQuery state - no LLM-memory reliance - 3-tier event-driven v2 - BigQuery event registry - new event types without code deploys.

---

### A6. Power BI Dashboards And Making A Difference Award

**Tags:** `dashboards` - `Power BI` - `self-service analytics` - `recognition`

**Resume bullet, conservative:**

> Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards (1,064 views, 22 users); cut data-request turnaround from 1-24 hours to 5-10 minutes; Making a Difference Award.

**Compact variant:**

> Delivered 5 Power BI dashboards ranked top 1.4% of Walmart's 207,000 dashboards; reached 1,064 views across 22 users and cut data-request turnaround from 1-24 hours to 5-10 minutes.

**Verified proof points:** 5 dashboards - top 1.4% of 207,000 Walmart dashboards - 1,064 views - 22 users - 1-24 hours to 5-10 minutes - Making a Difference Award.

---

### A7. Live Text-To-SQL Copilot Demo

**Tags:** `RAG` - `NL-to-SQL` - `BigQuery` - `Streamlit` - `Gemini` - `demo`

**Resume bullet, conservative:**

> Live deployed text-to-SQL copilot using Streamlit, Gemini 2.5, LangChain-orchestrated RAG (embeddings over historical queries), BigQuery execution, and auto-visualization.

**Demo URL:** `https://sql-rag-frontend-simple-481433773942.us-central1.run.app/`

**Verified proof points:** live demo URL - Streamlit - Gemini 2.5 - LangChain - embeddings-based RAG over historical queries - BigQuery execution - auto-visualization.

---

## University of Chicago - Data Science Institute

*Jan - Sep 2024 - Chicago, IL*

### U1. Persona-Driven Multi-LLM Donation Experiment

**Tags:** `experimentation` - `LLM` - `A/B testing` - `research`

**Resume bullet, conservative:**

> Persona-driven multi-LLM (OpenAI + Gemini) chatbot for a 500+ participant donation experiment; controlled A/B tests persuaded 15% to donate to an opposing cause.

**Verified proof points:** OpenAI + Gemini - 500+ participants - controlled A/B tests - 15% persuaded to donate to an opposing cause.

---

## FTI Consulting - UChicago MSADS Capstone

*Jan - Aug 2024 - Chicago, IL*

### F1. RAG-To-Proposal Generator

**Tags:** `RAG` - `consulting` - `AWS EC2` - `capstone` - `award`

**Resume bullet, conservative:**

> RAG-to-proposal generator deployed on AWS EC2; cut proposal time ~30%; Best in Show - UChicago MSADS Capstone.

**Verified proof points:** RAG-to-proposal generator - AWS EC2 - ~30% proposal-time reduction - Best in Show, UChicago MSADS Capstone.

---

## Innovare (EdTech Startup) - Data Scientist

*Oct 2022 - Mar 2023 - Chicago, IL*

### I1. Logistic-Regression Risk Model And Looker Dashboards

**Tags:** `ML` - `dashboards` - `Looker` - `education analytics`

**Resume bullet, conservative:**

> Logistic-regression risk model + Looker dashboards for 10+ districts (5,000+ students); retention +7%, failures -15%.

**Verified proof points:** logistic-regression risk model - Looker dashboards - 10+ districts - 5,000+ students - +7% retention - -15% failures.

---

# Canonical Skills - Supported By Deloitte/SWE Resume

Use this as the default skills menu. Add new skills only after they are supported by a canonical achievement or Kanu confirms them.

```text
Agent stack: MCP server design, sub-agent orchestration, context engineering,
prompt engineering, RAG (embeddings + FAISS + BM25 + RRF), LangChain,
ChromaDB semantic memory, evaluation suites (golden sets, human-in-the-loop validation),
multi-model routing across providers, headless cron agents, event-driven architectures,
decision logging / observability

LLMs: Claude (Opus / Sonnet / Haiku via Wibey), Gemini (2.5 Pro / Flash via Vertex AI), OpenAI

AI-assisted development: Claude Code, Cursor

APIs / triggers / glue: FastAPI, Cloud Run, BigQuery scheduled queries,
Slack webhooks, cron, Playwright SSO, JSONL state stores, CI/CD (pytest, version control)

Data: BigQuery, dbt, SQL, Python, PySpark, Airflow, Databricks, MySQL

Viz: Power BI (DAX, XMLA TMSL), Tableau, LookML, Streamlit, Matplotlib, React Recharts
```

---

# Quick-Reference Theme Index

- **Agent / agent-platform building:** A1, A2, A3, A5
- **RAG / retrieval systems:** A3, A7, F1
- **NL-to-SQL / text-to-data:** A1, A2, A7
- **MCP / tool-use infrastructure:** A3
- **Business translation:** A1, A2, A3, A4, A5
- **Automation / simplification:** A3, A4, A5
- **Dashboards / BI:** A6, I1
- **Experimentation / causal:** U1
- **Consulting / capstone:** F1
- **Recognition / awards:** A6, F1

---

# Notes For Future Tailoring Sessions

- Use A1, A2, A3, A4, A5, and A6 as the Walmart canonical set.
- Use A7 only as a selected project/demo.
- If a JD wants principal/staff-level platform evidence, lead with A1/A2/A3/A5.
- If a JD wants hard engineering rigor beyond the canonical achievements, leave a `[VERIFY: ...]` note for Kanu.
- If a JD wants consulting/client-facing experience, use F1 conservatively.
