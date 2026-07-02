# Application Answers — Accenture · AI Native Engineer, Reinvention Center

**Apply here:** https://www.accenture.com/us-en/careers/jobdetails?id=R00325558_en

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number field: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship required: No.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Accenture
This role is the work I already do, just pointed at clients — designing enterprise-ready agents with retrieval, orchestration, tool invocation, and real evaluation harnesses, then getting them adopted inside a complex org. At Walmart I've shipped agent systems end-to-end and earned adoption from stakeholders who didn't know or care what was under the hood, which is the harder half of the job. The ATC framing of technologist-and-trusted-advisor — running workshops and POCs to shape use cases — matches how I actually work; I spend as much time translating an ambiguous business ask into an agent-ready spec as I do building. I've also worked across multiple providers (Claude and Gemini), so the multi-provider abstraction piece reads as familiar. And I like that you measure agents on accuracy, latency, safety, and cost rather than on demos, because that's the gate I hold my own builds to.

## Relevant project
At Walmart I built a production agent that took our data-readiness ticket queue from 30–60 minutes per request — sometimes a full day — to under 10 minutes, across 400+ tickets in 8 categories, and the stakeholders on the receiving end never knew an agent was answering them. It's a 6-gate pipeline (triage → context → plan → execute → validate → report) built on an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical SQL queries; I went MCP over direct database credentials because that's where I enforce what the agent is allowed to touch, so I keep an audit boundary. Every gate writes to a permanent work log so the agent doesn't lose coherence as its context fills, and it has a 10-retry self-healing budget before it escalates. Today I'm the human gate reviewing those logs; the next version moves the gate to a golden-set regression that scores the agent's process, not just its SQL, and abstains when the process doesn't match.

I also shipped a self-service analytics agent over 67 BigQuery tables — four sub-agents in a flow (Context Researcher → SQL Drafter → Validator → Devil's Advocate) — that's the only AI skill currently in active use by business teams on Walmart Data Ventures. The Validator and Devil's Advocate run in context windows isolated from the Drafter on purpose, so the context that wrote the SQL isn't the one that approves it, and underneath the LLM I layered 8 deterministic SQL rules plus a 23-case golden-query suite so an answer only ships when every layer clears.
