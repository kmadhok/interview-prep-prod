# KANU MADHOK

952-303-1045 • madhok.kanu@gmail.com • github.com/kmadhok • linkedin.com/in/kanu-madhok
Live Demo: NL-to-SQL Copilot — Dockerized Streamlit on GCP Cloud Run

---

## EXPERIENCE

### Walmart Data Ventures — Senior Data Analyst, AI/ML Engineering
*Sep 2024 – Present · Chicago, IL*

Embedded with the Customer Perception team as point of contact for ~30 cross-functional stakeholders; built and shipped the AI/agent portfolio that automates analytics intake, query authoring, and ongoing analysis across a 740K-panelist BigQuery footprint. Recognized with a Making a Difference Award for 2025 work.

- Built jira-ticket-worker v3.0 — a 6-gate stakeholder reply agent (triage → context retrieval over an 11K-ticket archive with FAISS + BM25 → plan → draft → BigQuery execution → validation, 10-retry self-healing, 80%+ SQL reuse via similarity search); cut Jira ticket turnaround from ~60–90 min to ~5 min review-and-approve across 400+ requests with zero stakeholder-visible change, freeing the bandwidth that funded the rest of the agent portfolio.
- Designed and shipped a GenAI text-to-SQL copilot over Walmart BigQuery (RAG over a 12K-query corpus, multi-agent LLM orchestration) on GCP Cloud Run; 95% SQL accuracy, ~80% faster query creation, rolling out org-wide to 500+ users.
- Built 3 MCP servers (24+ tools) over stdio enabling agents to reason over a 43-table BigQuery dataset with zero hardcoded schema knowledge; cut agent latency from ~90–120s to ~20–25s — same MCP surface powers the text-to-SQL copilot, autonomous analyst, and Jira agent.
- Architected a 9-stage gated autonomous analytics pipeline (SELECT → PLAN → EXECUTE → INTERPRET → PACKAGE → CHART → NARRATE → VALIDATE → COMMIT); 146 published analyses on a 740K-panelist dataset in 6 weeks with analyst review only at the publish gate.
- Productized two AI skills (cp-analytics, Simple CP Interaction) org-wide as official internal Wibey (Walmart Claude Code fork) skills after partnership review with Product and Data Science leadership — first AI skills productized across Walmart Data Ventures.
- Designed evaluation harness reusable across every agent shipped: golden eval sets, LLM-as-judge scoring, deliberate HITL at post-time placed by cost-of-error analysis (stakeholder-visible decisions gated; reversible decisions automated).

### FTI Consulting — AI Engineer (UChicago MSADS Capstone Engagement)
*Jan – Aug 2024 · Chicago, IL*

- Deployed a RAG application for proposal generation adopted into FTI's actual workflow (Dockerized Streamlit on AWS EC2); cut proposal time ~30%, +34% generation quality via query rewriting, +42% retrieval via adaptive chunking. **Won Best in Show — UChicago MSADS Capstone.**

### University of Chicago, Data Science Institute — Graduate Student Researcher
*Jan – Sep 2024 · Chicago, IL*

- Built a persona-driven multi-LLM (OpenAI + Gemini) chatbot with temperature/persona tuning for a staged donation experiment (500+ participants); persuaded 15% to donate to an opposing cause via controlled A/B tests.

### Innovare (EdTech Startup) — Data Scientist
*Oct 2022 – Mar 2023 · Chicago, IL*

- Built a logistic-regression student-risk model across 10+ districts (5K+ students): +7% retention, −15% course failures. Automated ELT pipeline to BigQuery, +23% reporting accuracy.

### Baker Tilly — Consultant, Enterprise Platform Management (Oracle)
*Sep 2021 – Sep 2022 · Chicago, IL*

- Delivered Oracle enterprise platform implementations end-to-end across **multiple client engagements** with client business and IT stakeholders; built RPA workflows automating high-volume client operations and AWS computer-vision solutions from problem definition through production deployment.

---

## TECHNICAL SKILLS

**AI / Agentic platforms:** Claude Code (primary dev environment), authored + published Claude Code skills, Wibey (Walmart Claude Code fork), Codex, Gemini, Cursor; MCP servers, multi-agent orchestration, orchestrator/sub-agent patterns, agentic workflows, RAG, NL→SQL, context & prompt engineering

**Evaluation & governance:** Golden eval sets, LLM-as-judge, human-in-loop review, A/B testing with controls, output validation, cost-of-error-driven HITL placement, silent-degradation monitoring

**AI stack:** Anthropic Claude, Vertex AI Gemini (2.5 Pro / Flash / embeddings), OpenAI API, ChromaDB, FAISS, MinHash/LSH, LangChain, FastAPI, Streamlit, Pydantic

**Languages / ML:** Python, SQL, R, PySpark; TensorFlow, PyTorch, scikit-learn; A/B testing, time series, clustering, Bayesian methods, logistic regression, gradient boosting, classification

**Data & enterprise integration:** BigQuery, Databricks, MySQL, Hive; API + webhook integrations, MCP integrations across enterprise systems; Power BI (DAX), Tableau, Looker Studio; Oracle enterprise platform; RPA; AWS computer vision

**Cloud / deployment:** GCP (Cloud Run, Vertex AI), AWS (EC2); Docker; asyncio; CI/CD

---

## EDUCATION

**University of Chicago** — M.S., Applied Data Science *(STEM)* — GPA: 4.0
**Loyola University Chicago** — B.S., Information Systems & Economics — GPA: 3.5

---

## HONORS

- **Walmart Making a Difference Award** — 2026, for 2025 AI/agent portfolio impact.
- **Best in Show, UChicago MSADS Capstone** — FTI RAG proposal generator.
