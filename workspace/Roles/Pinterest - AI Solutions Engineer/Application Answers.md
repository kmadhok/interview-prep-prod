# Application Answers — Pinterest · AI Solutions Engineer

**Apply here:** https://www.pinterestcareers.com/jobs/?gh_jid=7714127

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why Pinterest
Embedding AI-native engineering directly inside business functions is the exact job I've been doing at Walmart, just without the formal title. The JD describes someone equally comfortable reading a business process flowchart and writing production Python — discover the automation opportunity with a corporate-function team, scope it, ship the tool, and drive adoption. That end-to-end loop, especially the adoption half, is where I've spent the last year: my agents got used because I sat with the stakeholders, mapped the real bottleneck, and built something they trusted enough to stop double-checking. I also like that the bar here is genuine engineering — clean code, tests, CI/CD, guardrails, and responsible-AI judgment on sensitive data — not prototype-and-hand-off. The agentic-literacy checklist (MCP, Agent Skills, Hooks, A2A, eval sets, HITL review queues) is my daily working vocabulary, so I could be useful on day one and credible with both a Finance manager and an engineer in the same afternoon.

## Relevant project
Autonomous Jira ticket-resolution agent: I embedded a production agent into a real business workflow — 400+ data-readiness tickets taken from 30-60 minutes each to under 10, and the stakeholders never knew an agent was answering them. It's a 6-gate pipeline over an MCP server I built on BigQuery, with a FAISS + BM25 retrieval layer and a self-healing retry budget, and permanent work-log artifacts at every gate for auditability. That's the full Pinterest arc — discovery, production build, guardrails, adoption — in one project.

Self-service analytics agent over 67 tables: a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) with context-isolated validation, 8 deterministic pre-LLM rules, and a 23-case golden-query eval suite — the only AI skill in active use by business teams on Data Ventures. This is my evidence for the "design and evaluate AI outputs at scale" preferred bar: eval sets, HITL review at rollout, and structural guardrails that fire before any model call. I also run a headless KPI monitor on cron with state persisted to BigQuery (no LLM-memory reliance) as my reliability-and-design-for-failure story — retries, escalation, durable state.
