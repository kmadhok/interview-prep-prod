# Application Answers — CVS Health · Manager, AI Engineer (Claude)

**Apply here:** https://www.linkedin.com/jobs/view/4423018076/ (responses managed off LinkedIn; canonical CVS Workday posting not confirmed)

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000.)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why CVS Health
This role is close to exactly what I already do — build on the Claude platform and wire it into the systems a team actually runs on. At Walmart I stood up an MCP server over our BigQuery platform so a Claude-based agent gets a curated, audited interface instead of raw database credentials, and I've shipped agentic workflows into a Jira queue and Slack. The MCP-plus-enterprise-integration core here maps one-to-one to what I've built. Healthcare is a regulated environment, and I design with audit boundaries and human gates as first-class concerns, not afterthoughts — that's the part of the JD (governance, security considerations around AI) I care about most. What pulls me is doing this at CVS's scale, and being the hands-on engineer setting the standards for how the enterprise builds on Claude.

## Relevant project
I built a production agent that took 400+ Walmart data-readiness tickets from 30–60 minutes each (a full day for the complex ones) down to under 10 minutes. Architecturally it's an MCP server over BigQuery plus a retrieval layer over 11,000 historical queries — I went MCP over direct DB credentials because the MCP layer is where I enforce what the agent is allowed to touch; direct creds would have been faster but I'd have lost the audit boundary. Every gate writes a permanent work-log artifact and there's a 10-retry self-healing execution budget, so it stays stable and auditable. It's approved by Sr. Director and product leadership, and the stakeholders on the receiving end never knew an agent was answering them.

I also run a headless KPI monitor on a 6-hour cron that detects threshold breaches, does root-cause analysis, and posts Slack alerts with the diagnosis attached. The design choice that matters for production reliability: state persists to BigQuery, not LLM memory — if a model call fails mid-cycle, the next run picks up exactly where the last stopped. That "no LLM-memory reliance" pattern is how I make agents dependable enough to run unattended, which is the bar for anything wired into enterprise systems.
