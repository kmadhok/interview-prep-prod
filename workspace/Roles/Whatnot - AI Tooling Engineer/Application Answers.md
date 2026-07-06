# Application Answers — Whatnot · AI Tooling Engineer (Senior AI Engineer)

**Apply here:** https://www.linkedin.com/jobs/view/4425564046/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Whatnot
This is the job I'm already doing, described almost word for word. Building internal AI tools that put AI in the hands of every team, embedding with CX and ops to find the real problem, shipping a working prototype fast and then hardening it, and — the part I care about most — setting the reusable patterns and infrastructure the rest of the org builds on: MCP servers, eval harnesses, reference architectures, packaged skills. At Walmart, automating my own role bought me the time to build the rest, and those builds became productized skills other teams adopt. RAG, MCP, agents, and evals aren't a wishlist for me; I have direct, shipped evidence for each. And "not a model-training or research role" is exactly my strength — I'm an orchestration-and-integration builder, not a fine-tuner. The one thing I'd want to clear early is the Seattle on-site expectation, since I'm Chicago-based.

## Relevant project
Self-service analytics agent + eval harness. I designed and shipped a four-sub-agent flow — Context Researcher, SQL Drafter, Validator, and a Devil's Advocate that challenges the output before it ships — over 67 BigQuery tables, so non-technical teams get validated answers themselves instead of waiting on an analyst. Under the LLM sit 8 deterministic SQL rules and a 23-case golden-query eval suite that gates every ship. It's the only AI skill in active use by business teams on Data Ventures. That's the exact combination this role wants: wire AI into real business context, then build the eval harness that makes off-the-shelf AI dependable.

Autonomous Jira agent (MCP + RAG, embedded, adopted). I built a production agent on an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical queries, taking 400+ data-readiness tickets from 30–60 minutes to under 10. It embedded directly into a real workflow — stakeholders never knew an agent was answering them — and the MCP layer is where I enforce access controls, which matters for the PII and access-control constraints your JD calls out. This is the "sit with a team, understand the workflow, put a working tool in their hands" pattern, shipped and approved by leadership.
