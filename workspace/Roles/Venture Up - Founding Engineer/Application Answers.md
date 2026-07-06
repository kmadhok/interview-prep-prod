# Application Answers — Venture Up (undisclosed seed-stage AI agent-platform startup) · Founding Engineer

**Apply here:** https://www.linkedin.com/jobs/view/4430984248/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why this role
The product you're building — the permissions, guardrails, and activity logging that make enterprises trust AI agents in production — is the exact problem I've been solving on the inside at Walmart. When I put an agent into production, the first thing I build is the control layer: what it's allowed to touch, how every action is logged, and how a human can audit what it did. So the "agent workforce" thesis isn't abstract to me; it's the part of agent work I care most about. I want a founding seat where I own product areas end to end and work directly with early enterprise customers, which is how I already operate — I find the real problem, ship the thing, and stay until it runs. To be straight about fit: I come at this from the AI/data-engineering and agentic-systems side rather than classic full-stack web SWE, so the K8s/Docker/AWS scaling layer would be a ramp for me — but the guardrails, observability, and control-plane axis is where I'm strongest.

## Relevant project
Autonomous agent with a built-in control plane. My production ticket-resolution agent at Walmart runs on an MCP server over BigQuery rather than direct database credentials — the MCP layer is deliberately where I enforce what the agent is allowed to look at, which is the permissions-and-guardrails problem your platform generalizes. Every step writes to a permanent work log: the query it considered, the table it picked, the join it made — an audit trail and activity log for every agent action, plus a 10-retry self-healing budget before it escalates. That's the trust layer your early customers need to put agents into production safely, built from experience rather than theory.

Headless KPI monitor (durable state, no LLM-memory reliance). I built a production agent on cron where every decision persists to BigQuery instead of LLM memory, so it survives failed model calls and picks up exactly where it stopped. Building observability and durable activity logging into the data model — not bolting it on — is the reliability discipline a founding engineer on an agent-control-plane needs from day one.
