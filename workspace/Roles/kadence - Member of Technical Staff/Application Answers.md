# Application Answers — kadence · Member of Technical Staff

**Apply here:** https://www.linkedin.com/jobs/view/4423056620/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why this role
This role is described almost exactly as the work I already do: production AI systems built on LLMs, agent frameworks, retrieval, and tool orchestration, where the bar is actionable insight and not another chatbot. Everything I've shipped at Walmart is agent work that people actually use to make decisions, and the part of the JD I care most about is the line about knowing where AI creates real value versus unnecessary complexity — that judgment call is the whole job, and it's the discipline I've built by shipping agents into a business team's daily workflow and watching what they trust versus ignore. I also like that it's high-ownership in an ambiguous, fast-moving environment; my strongest work has come from owning a problem end to end, from the retrieval layer up to the customer-facing surface, rather than getting handed a spec. Voice AI is outside what I've built, but it's the kind of adjacent surface I'd want to grow into, and the rest of the stack — Python, LLM APIs, agent frameworks, retrieval and memory optimization — is the center of what I do.

## Relevant project
The build closest to this role is a production Jira ticket-resolution agent I shipped at Walmart. It's a 6-gate pipeline (triage, context, plan, execute, validate, report) sitting on an MCP server I built over our BigQuery platform, with a FAISS + BM25 retrieval layer over 11,000 historical SQL queries I'd written — so the agent gets a curated context interface, not raw schema, and I enforce at the MCP boundary exactly what it's allowed to touch. It writes a permanent artifact at every gate because long-running agents lose coherence as the context window fills, and it self-heals with a 10-retry execution budget before escalating. It took 400+ data-readiness tickets from 30-60 minutes each (a full day for the complex ones) down to under 10 minutes, it's approved by Sr. Director and product leadership, and the stakeholders on the receiving end never knew an agent was answering them. Alongside it I run a self-service analytics agent over 67 BigQuery tables built as a sub-agent flow — Context Researcher, SQL Drafter, Validator, Devil's Advocate — with 8 deterministic SQL rules and a 23-case golden-query suite as the eval gate; it's the only AI skill currently in active use by business teams on Data Ventures. That mix — retrieval, tool orchestration, memory externalized to artifacts, and an eval gate — is the same set of problems this role is about.

<!-- No custom application questions visible on the posting. -->
