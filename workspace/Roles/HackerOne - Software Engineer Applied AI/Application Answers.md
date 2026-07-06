# Application Answers — HackerOne · Software Engineer, Applied AI

**Apply here:** https://jobs.ashbyhq.com/hackerone/9721a4c7-ff1e-47ca-a89e-97688ebff96c

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000.)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why HackerOne
The core of this role — LLM-powered workflows, RAG pipelines, orchestration components, and the reasoning and evaluation around an in-platform agent like Hai — is my day-to-day. I've built RAG over historical queries, sub-agent orchestration with context-isolated validation so the model that produced an answer isn't the one that approves it, and evaluation gates that decide whether an answer ships or the agent abstains. The security domain is new to me, but the AI-engineering core transfers directly, and Hai is exactly where I'd want to work, because a security agent is where the confident-wrong failure mode matters most — clean output on a stale or wrong premise — and that's the failure mode I design against. Anthropic being a HackerOne customer is a nice bonus given how much of my recent work is on the Claude platform. I'd lead with LLM integration, RAG, orchestration, and eval, and ramp on the classical-ML-framework side as needed.

## Relevant project
The build I'd lead with is a self-service analytics agent over 67 BigQuery tables — a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) with layered evaluation: 8 deterministic rules fire before any LLM call, then a 23-case golden-query suite, then context-isolated validation. That cheapest-to-most-expensive eval ordering, plus the deliberate separation between the context that generates and the context that checks, is the applied-AI engineering pattern this role is built on. It's the only AI skill in active use by business teams on Data Ventures.

I also shipped a production agent that took 400+ tickets from 30–60 minutes each to under 10, on an MCP server over BigQuery with a 10-retry self-healing execution budget. Eval there is a gate, not a philosophy — a validator re-executes the work and checks it against a persistent log, and the failure mode I explicitly build against is confident-wrong, which is the one that matters most in a security context. That "measure model behavior, analyze telemetry, iterate on measurable impact" loop is exactly how the JD frames the work.
