# Application Answers — ServiceNow (Moveworks) · Software Engineer, Agentic AI Systems

**Apply here:** https://careers.servicenow.com/jobs/744000126417779/software-engineer-agentic-ai-systems-moveworks/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Moveworks / ServiceNow
The mission line in this JD — advance the frontier of work that can be entrusted to agents to perform reliably at scale — is basically the sentence I'd use to describe what I've been building. Moveworks' product is a natural-language front door that lets employees automate tasks across business systems, and that's the same shape as the agents I run at Walmart: someone asks a question in plain language, an agent reasons over the real systems and comes back with a validated answer. The specific areas the agent-lab team owns — agent orchestration, agent memory, LLM self-reflection, reliability — are the exact problems I've had to solve to get agents stable in production, not research topics for me. I'm drawn to the "reliable in every sense" framing because that's the hard part, and it's where I've done the most work. To be straight on fit: I'm Python-primary and would be ramping on Go and Java, and the role is on-site in Mountain View while I'm in Chicago, so relocation is a real conversation — but the work itself is squarely what I want to be doing.

## Relevant project
The most relevant build is a production Jira-resolution agent I own — agent orchestration end-to-end. It's a 6-gate pipeline (triage, context, plan, execute, validate, report) on an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical queries, with a 10-retry self-healing execution budget that diagnoses and retries a failed step before escalating. It took 400+ recurring tickets from 30–60 minutes each to under 10 minutes.

The one that maps directly to the team's "agent memory" area is a headless KPI monitor I run on a 6-hour cron where state persists to BigQuery, not to LLM memory. Every decision — which threshold breached, which root-cause hypothesis it explored, what it posted — is written durably, so if an LLM call fails mid-cycle the next run resumes exactly where it stopped. I designed it that way because long-running agents lose coherence as the context window fills; externalizing memory to durable artifacts is what keeps them stable. The failure mode I design against most is confident-wrong — clean output over a stale input — which is the case a process-level check catches that observability alone misses.
