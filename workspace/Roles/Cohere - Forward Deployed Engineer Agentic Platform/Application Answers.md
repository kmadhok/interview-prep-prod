# Application Answers — Cohere · Forward Deployed Engineer, Agentic Platform

**Apply here:** https://jobs.ashbyhq.com/cohere/b0bcef37-1d20-414f-aade-c54942d63df9

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship not required.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why Cohere
This role reads like a description of what I already do: take an ambiguous, high-value business problem, frame it as an agentic workflow with real success criteria, and own it end-to-end from prototype to a production agent that's reliable, observable, and auditable. That last clause is the part most people skip and the part I care most about — the agents I've shipped were built for enterprise-grade trust from day one, not demoed and abandoned. North is a compelling place to do this because the constraint is exactly right: startup speed against an enterprise bar, in regulated sectors where "the agent was confidently wrong" isn't acceptable. I've built the eval discipline the JD asks for — evaluation frameworks that go beyond trial-and-error to measure whether an agent's output is actually correct, not just whether it ran — and I'm comfortable being the person translating between a customer's stakeholders and the technical spec. The 20–40% travel and Eastern-time preference both work for me from Chicago.

## Relevant project
The agent I built at Walmart is the closest match to North-style delivery. It took 400+ data-readiness requests from 30–60 minutes each (a full day for the hard ones) to under 10 minutes, running a six-gate plan-and-execute pipeline over an MCP server I put in front of BigQuery. I went with MCP over handing the agent direct database credentials specifically because that layer is where I enforce what it's allowed to touch — I traded some build speed for an audit boundary, which is the right call for sensitive data. Every gate writes to a work log for a full audit trail, and it self-heals failed queries on a retry budget before escalating. It's approved by senior leadership and stakeholders never knew an agent was answering them.

On evaluation specifically — the bar the JD sets — my self-service analytics agent over 67 BigQuery tables layers three checks cheapest-to-most-expensive: eight deterministic SQL rules that fire before any LLM call, a 23-case golden-query suite that passes on result-correctness rather than SQL string-match (there's usually more than one right query), and a context-isolated validator plus a devil's-advocate sub-agent that don't share the drafter's context, so they catch hallucinated columns the drafter would defend. Nothing ships unless all three clear; otherwise it escalates instead of guessing. It's the only AI skill in active business use on my team.
