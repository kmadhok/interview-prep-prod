# Application Answers — Accenture Federal Services · Generative AI Applications Engineer (Agents & RAG)

**Apply here:** https://job-boards.greenhouse.io/accenturefederalservices/jobs/4669272006

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number field: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship required: No.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Accenture Federal Services
AFS is shipping GenAI where reliability, latency, and safety are the actual product, not a nice-to-have, and that's the constraint I build under too. My strongest work is agentic + RAG systems in production — hybrid retrieval, deterministic guardrails, and layered evaluation gates — with no model training required, which is exactly this role's scope. I'm a U.S. citizen and have cleared federal-context gates before, so the citizenship and secure-environment requirements aren't a blocker. The parts of the JD I'm most drawn to are RAG-done-right and LLM-evaluation — IR-style retrieval quality, prompt and policy testing, safe rollback and fallback — because that's where most GenAI apps quietly fail, and it's where I've spent the most time.

## Relevant project
At Walmart I built a production agent that took our data-readiness ticket queue from 30–60 minutes per request — sometimes a full day — to under 10 minutes across 400+ tickets in 8 categories. The retrieval core is the part most relevant here: a hybrid FAISS + BM25 layer over 11,000 historical SQL queries, fronted by an MCP server over BigQuery that acts as the audited interface so the agent only sees what it's allowed to. Every one of its 6 gates writes to a permanent work log, and it has a 10-retry self-healing budget with recovery and escalation before it gives up — the fallback discipline this JD asks for. Today I'm the human gate; the next version moves the gate to a golden-set regression that scores the agent's process and abstains when it doesn't match.

For evaluation specifically, my self-service analytics agent over 67 BigQuery tables runs a three-layer eval gate ordered cheapest-to-most-expensive: 8 deterministic SQL rules that fire before any LLM call, a 23-case golden-query suite, then isolated Validator and Devil's-Advocate sub-agents that challenge the output in context windows separate from the drafter. The answer ships only when every layer clears; otherwise it escalates rather than guesses — the low-hallucination, safe-rollback posture the mission-grade framing needs.
