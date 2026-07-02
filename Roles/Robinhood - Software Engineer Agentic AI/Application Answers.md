# Application Answers — Robinhood · Software Engineer, Agentic AI

**Apply here:** https://boards.greenhouse.io/robinhood/jobs/7975477

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Robinhood
This role is about taking GenAI and ML work the rest of the way into production-grade systems that people actually depend on, and that transition — prototype to something reliable enough to trust in a financial product — is the part of agent work I care most about. The JD leans on model serving, observability, fault tolerance, and CI/CD, which is exactly where I've spent my time: my production agents at Walmart aren't demos, they run on cron, persist state durably, and have to be right on a number that a business decision rides on. I also like that Robinhood is putting agentic AI against real backend surfaces — market data, trading, auth — instead of a chat sidebar, because that's where reliability engineering actually matters. To be straight about fit: my depth is Python, LLMs, agent architecture, and data systems on GCP/BigQuery — the heavy distributed-systems stack here (Kubernetes, Spark, Go/gRPC at scale) is where I'd be ramping rather than leading on day one, and I'd rather say that than oversell it.

## Relevant project
The closest match is a headless KPI monitor I run in production at Walmart — an agent on a 6-hour cron that detects threshold breaches against a KPI registry, runs root-cause analysis against the underlying tables, and posts a Slack alert with the diagnosis already attached. The design decision that's relevant here: state persists to BigQuery, not to LLM memory. Every decision the agent makes — which threshold breached, which hypothesis it explored, what it posted — is written durably, so if an LLM call fails mid-cycle the next run picks up exactly where the last one stopped. That's the same fault-tolerance and observability discipline the JD asks for, built into the data model instead of bolted on. The v2 is a 3-tier event-driven platform that self-configures through a BigQuery event registry, so new event types ship without a code deploy.

I also run a production Jira-resolution agent built on an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical queries. I went MCP over handing the agent direct DB credentials because the MCP layer is where I enforce what the agent is allowed to touch — direct creds would have been faster but I'd have lost the audit boundary. It also has a 10-retry self-healing execution budget: a failed query gets diagnosed and retried before it escalates. That agent took 400+ recurring tickets from 30–60 minutes each to under 10 minutes.
