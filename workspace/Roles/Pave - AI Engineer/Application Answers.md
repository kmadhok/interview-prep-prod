# Application Answers — Pave · AI Engineer

**Apply here:** https://job-boards.greenhouse.io/paveakatroveinformationtechnologies/jobs/4660955005

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why Pave
Pave's AI compensation analyst — autonomous agents that reason over a structured dataset and execute multi-step workflows like market pricing and cycle planning — is almost exactly the system I've been building at Walmart, just pointed at compensation instead of customer data. I've shipped agents that sit on top of a 67-table structured platform and run multi-step reasoning end-to-end, and the thing I learned is that the hard part isn't the LLM call, it's making the agent trustworthy enough that a business user acts on the answer without checking it. The JD emphasizes product instinct and a founder mentality, and that's the half I actually enjoy — my agents got adopted because I obsessed over the customer's real question, not because the architecture was clever. Building a new AI product and taking it to market, end-to-end, in a fast-moving environment is the work I want more of, and doing it on the largest real-time comp dataset is a genuinely interesting substrate.

## Relevant project
Self-service analytics agent over 67 structured tables: I designed a sub-agent flow — Context Researcher gathers schema and historical patterns, SQL Drafter writes the query, a Validator runs deterministic rules, and a Devil's Advocate sub-agent challenges the output before it ships. The Validator and Devil's Advocate deliberately don't share the Drafter's context window, because if the context that wrote the query also validates it you get confirmation bias. It's the only AI skill in active use by business teams on Data Ventures — reasoning over structured data and executing multi-step workflows autonomously, which is the exact shape of Pave's agentic analyst.

Autonomous Jira agent: a production agent that took 400+ tickets from 30-60 minutes to under 10, running a 6-gate multi-step pipeline over an MCP server with a self-healing execution budget. It's my strongest evidence that I can ship an agent that people actually trust and use in production. I also keep a live text-to-SQL copilot (Streamlit + RAG over historical queries + live BigQuery execution) deployed publicly, so I can show the pattern running against a real schema on the call if that's useful.
