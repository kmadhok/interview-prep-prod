# Application Answers — Bain & Company · Expert Consultant, Coro, AI Engineer

**Apply here:** https://www.linkedin.com/jobs/view/4430124948 (JD source; also on careers.bain.com — search "Coro AI Engineer", Austin)

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number field: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship required: No.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Bain (Coro)
This role is a near-exact match to how I already work — building agentic GenAI products end-to-end, from rapid POC to production, with hybrid retrieval, MCP-based skills, context engineering, and real evaluation and observability underneath. My Walmart agents use exactly this toolkit: an MCP server as the audited interface to data, hybrid FAISS + BM25 retrieval, and layered eval gates, and I built them by translating ambiguous business questions into agent-ready specs — the client-facing translation Coro emphasizes. The Coro framing of packaging proprietary tools into scaled products, rather than one-off analyses, is the build-once-serve-many work I gravitate to. I'd lead with my shipped agentic and retrieval systems and be upfront that the deep-learning-model-training and Kubernetes-ops parts of the JD are areas I'd ramp into rather than claim.

## Relevant project
At Walmart I built a production agent that took our data-readiness ticket queue from 30–60 minutes per request — sometimes a full day — to under 10 minutes across 400+ tickets in 8 categories, and stakeholders never knew an agent was answering them. It's a 6-gate pipeline (triage → context → plan → execute → validate → report) on an MCP server over BigQuery plus a hybrid FAISS + BM25 retrieval layer over 11,000 historical SQL queries — the context engineering, MCP skills, memory-via-artifacts, and orchestration this JD names, in one shipped system. I chose MCP over direct database credentials to keep an audit boundary, every gate writes a permanent work log, and a 10-retry self-healing budget handles failure before escalation.

For the evaluation and observability half, my self-service analytics agent over 67 BigQuery tables — four sub-agents (Context Researcher → SQL Drafter → Validator → Devil's Advocate) — runs a three-layer gate: 8 deterministic SQL rules, a 23-case golden-query regression suite, then isolated Validator and Devil's-Advocate sub-agents challenging the output in separate context windows. It's the only AI skill currently in active use by business teams on Data Ventures, which is the POC-to-adopted-production arc Coro is hiring for.
