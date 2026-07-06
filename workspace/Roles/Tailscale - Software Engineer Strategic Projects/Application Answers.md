# Application Answers — Tailscale · Software Engineer, Strategic Projects

**Apply here:** https://job-boards.greenhouse.io/tailscale/jobs/4700280005

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Tailscale
The part of this role I want most is the exact thing I've been doing: taking agent-generated prototypes and making them dependable in production, with the review, testing, and security practices wrapped around them so they actually hold. Your team treats coding agents as a force multiplier and expects every engineer to be a power user — I build my systems in Claude Code daily and I have a real point of view on where agents accelerate work, where they fail, and how to gate them. Aperture and the MCP-gateway / LLM-proxy workloads are the kind of emerging surface I've been building against, and the "works in a demo → stable in production" journey — hardening, error handling, observability, closing the long tail of edge cases — is the work I find satisfying rather than a chore. To be straight about fit: my production systems are in Python on GCP, not Go, so Go would be a ramp for me — but the agentic-application and production-rigor half of this role is squarely where I already operate.

## Relevant project
Headless KPI monitor (production agent, no LLM-memory reliance). I built an agent that runs every 6 hours on cron, detects KPI threshold breaches, runs root-cause analysis, and posts a Slack alert with the diagnosis attached. The architectural decision that matters for a role about hardening agent code: every decision it makes — which threshold breached, which hypothesis it explored, what it posted — persists to BigQuery, not to LLM memory. If a model call fails mid-cycle, the next run picks up exactly where the last stopped because state is durable. That's the difference between a demo agent and one you can leave running unattended, which is the production bar this team owns.

Autonomous Jira agent with an enforced audit boundary. My production ticket-resolution agent runs on an MCP server over BigQuery rather than direct database credentials — deliberately, because the MCP layer is where I enforce what the agent is allowed to look at. Direct creds would have shipped faster but I'd have lost the audit boundary. It also has a 10-retry self-healing execution budget: a failed query gets diagnosed and retried before it escalates. That's the same instinct as wrapping agent-generated code in review and security practices so it's safe to run against real load.
