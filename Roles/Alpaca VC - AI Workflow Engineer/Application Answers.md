# Application Answers — Alpaca VC · AI Workflow Engineer

**Apply here:** https://apply.workable.com/alpaca-vc/j/89D682FC4C

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number field: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship required: No.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Alpaca VC
This is a greenfield version of what I've been doing at Walmart — taking work that eats hours across a team and turning it into production agentic systems, with real architectural ownership rather than implementing someone else's spec. The JD's emphasis on APIs, webhooks, auth flows, rate limits, and failure modes is the unglamorous core of every agent I've shipped; my Jira agent has self-healing retries and rate-limit handling because production forced it. I've built directly against Anthropic and other LLM APIs and orchestrated multi-step workflows end-to-end, so the technical bar reads as familiar. The VC domain is new to me, but the JD is clear this is an engineering hire first, and the first-engineer, shape-the-platform framing is exactly the kind of ownership I want.

## Relevant project
At Walmart I built a production agent that took our data-readiness ticket queue from 30–60 minutes per request — sometimes a full day — to under 10 minutes across 400+ tickets. It's the kind of "this used to take hours across the team" automation this role is about: a 6-gate pipeline on an MCP server over BigQuery, with hybrid FAISS + BM25 retrieval, and — the part that matters for production — a 10-retry self-healing execution budget, rate-limit handling, and permanent work-log artifacts at every gate so the agent stays coherent and auditable instead of drifting as its context fills. I chose MCP over direct database credentials because that's where I enforce what the agent is allowed to touch.

I also built a headless KPI monitor that runs every 6 hours on cron, detects threshold breaches, runs root-cause analysis, and posts a Slack alert with the diagnosis attached. Its design principle is directly relevant to workflow orchestration: no LLM-memory reliance — every decision persists to BigQuery, so if a call fails mid-cycle the next run resumes exactly where the last one stopped. The v2 is a 3-tier event-driven platform that self-configures through a registry, so a new workflow ships by adding a row, not a code deploy.
