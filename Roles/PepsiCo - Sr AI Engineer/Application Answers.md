# Application Answers — PepsiCo · Sr AI Engineer (posting title: Sr Agentic AI Engineer)

**Apply here:** https://www.pepsicojobs.com/main/jobs/391357?lang=en-us

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why PepsiCo
This role is about designing domain-specific agents that can talk to each other, execute tasks, and run in production with end-to-end observability — which is the portfolio I've built at Walmart over the last year. The JD names Langchain, MCP, and A2A, and lists cloud deployment and observability as first-class, not afterthoughts, and that lines up with how I actually work: I persist agent state to a database so there's no LLM-memory reliance, and I treat the decision log as the eval substrate. I also like that this is explicitly a build-and-deploy IC seat partnered with transformation teams and business stakeholders — the translation from a fuzzy business ask into an agent-ready spec is the part I'm strongest at and the part that decides whether an agent gets adopted or shelved. Chicago hybrid is home base for me, which makes this an easy one to commit to fully.

One honest note: the posting asks for 8+ years. I'm shorter on raw calendar years than that, but the scope is principal-level — production agents approved by Sr. Director and product leadership, in active use, replacing real workflows. Happy to walk through that tradeoff directly.

## Relevant project
Autonomous Jira ticket-resolution agent: a production 6-gate agent (triage, context, plan, execute, validate, report) over an MCP server I built on BigQuery, with a FAISS + BM25 retrieval layer over 11,000 historical queries and a 10-retry self-healing execution budget. It took 400+ tickets from 30-60 minutes to under 10. The MCP-over-direct-credentials choice is deliberate — that's where I enforce and audit what the agent can touch.

Headless KPI monitor: a production agent on a 6-hour cron that detects threshold breaches, runs root-cause analysis, and posts Slack alerts with the diagnosis attached. Every decision persists to BigQuery, so if an LLM call fails mid-cycle the next run picks up exactly where it stopped — no LLM-memory reliance. The v2 is a 3-tier event-driven platform that self-configures through a BigQuery event registry, so a PM can add a new event type without a code deploy. That's the observability-and-reliability story this role is asking for. Underneath both sits a sub-agent analytics flow with context-isolated validation, which is my answer for inter-agent design done safely.
