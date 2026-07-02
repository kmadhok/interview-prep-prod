# Application Answers — Salesforce · AI Builder, Emerging Talent (Agentforce)

**Apply here:** https://careers.salesforce.com/en/jobs/jr341276/ai-builder-emerging-talent/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Salesforce
The AI Builder role is the exact shape of work I already do — embed with a team, turn an ambiguous business problem into an agent that takes real actions, and own it from design through deploy. What stands out is that Agentforce is live in production for real companies, so this is agent engineering with actual consequences, not a sandbox, and the JD's framing around designing agent intelligence — prompts, reasoning, tool calls, the architecture — is precisely how I think about a build. I also notice Cursor and Claude are the named dev tools, which is my daily stack, so there's no ramp on how the pod actually works. And the consultative side — holding your own in a room with customers, translating their problem into an agentic solution — is what I've been doing at Walmart, partnering with product and data-science stakeholders to turn ambiguous questions into agent-ready specs. On stack: my strengths are Python, LLMs/prompt engineering, agent orchestration, and eval rigor, which map directly; React/TypeScript/GraphQL and Apex are real gaps I'd be ramping on, and I'd rather name that than pretend otherwise.

## Relevant project
The build that maps most directly is a production Jira-resolution agent I own at Walmart — it's the design-agent-intelligence work the JD describes. It's a 6-gate pipeline (triage, context, plan, execute, validate, report) running on an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical queries, with a 10-retry self-healing execution budget that diagnoses and retries a failed action before escalating. It took 400+ recurring tickets from 30–60 minutes each to under 10 minutes, and the stakeholders on the receiving end never knew an agent was answering them — which is the product instinct I'd bring to shipping agents for customers.

For the eval-with-engineering-rigor part, I also built a self-service analytics agent over 67 BigQuery tables — four sub-agents in a flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate), where the Validator and Devil's Advocate deliberately don't share the drafter's context window so they catch hallucinated columns the drafter would defend. The gate to ship is: passes 8 deterministic rules, passes the relevant golden case out of a 23-case suite, and both reviewers clear it — otherwise it escalates instead of guessing. It's currently the only AI skill in active use by business teams on Data Ventures.
