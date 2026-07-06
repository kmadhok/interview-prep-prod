# Application Answers — Chan Zuckerberg Initiative · Applied AI Engineer, Investments

**Apply here:** https://job-boards.greenhouse.io/chanzuckerberginitiative/jobs/7958444

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship not required.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why Chan Zuckerberg Initiative
The core of this role — build AI-enabled applications and workflows that take manual research and operational work off people's plates, and make information more accessible — is exactly what I do day to day at Walmart, just pointed at investment data instead of customer data. I've spent the last year turning slow, manual analyst workflows into agents and pipelines, and a big part of that was the unglamorous half the JD calls out: data validation, monitoring, and quality checks so the outputs are actually trustworthy. The LLM and retrieval side is where I'm strongest — I've shipped RAG systems and workflow automation in production, not just prototypes. I don't have an investing background, but the JD asks for interest there, and I'm genuinely drawn to the "manager of managers" problem of making a lot of unstructured information legible and actionable. And the mission — technology aimed at disease and learning — is the kind of thing I'd want the automation work to be funding.

## Relevant project
I built an autonomous agent at Walmart that took 400+ data-readiness and stewardship requests from 30–60 minutes each (a full day for the complex ones) down to under 10 minutes. It runs a six-gate pipeline over an MCP server I put in front of BigQuery, plus a retrieval layer over 11,000 historical queries, so the agent gets a curated, audited view of the data instead of raw credentials — that boundary is where I enforce what it's allowed to touch. Every step writes to a work log, which gives me an audit trail and keeps the agent stable on long runs, and it self-heals failed queries before escalating. It's approved by senior leadership and the stakeholders on the receiving end never knew an agent was answering them.

I also built and deployed a live text-to-SQL copilot outside my day job — Streamlit front end, Gemini grounded on RAG over historical queries, live BigQuery execution, and auto-generated charts. You type a natural-language question and get SQL, results, and a visualization back. It's the standalone version of the "make information accessible, automate the manual pull" pattern this role is about, and it's live if the team wants to try it: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/
