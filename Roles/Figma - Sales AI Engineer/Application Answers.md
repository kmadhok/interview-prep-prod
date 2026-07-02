# Application Answers — Figma · Sales AI Engineer

**Apply here:** https://boards.greenhouse.io/figma/jobs/5991176004

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000.)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Figma
The founding-function framing is the draw — building the reusable AI patterns a whole GTM org will scale, not one-off automations that live and die on one team. What the JD asks for is what I do: ship LLM-powered workflows into the systems people already live in (Slack, a CRM, a data stack), pick the lightest safe solution, constrain outputs, and add quality checks and monitoring so they can be trusted in production. The part I care about most is the last one — whether what I build actually gets adopted. At Walmart the self-service analytics agent I built is the only AI skill in active use by business teams, which is the exact adoption bar this role is set to. I'm comfortable across SQL and operational data, and I like that the mandate is to create templates and connectors others can build on rather than becoming the central dependency.

## Relevant project
The closest match is a self-service analytics agent I designed and shipped over 67 BigQuery tables — a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) that lets business teams ask a question and get a validated answer instead of waiting on an analyst. The trust layer is what makes it production-grade: 8 deterministic SQL rules fire before the LLM ever sees the output, then a 23-case golden-query suite, then context-isolated validation so the agent that wrote the query isn't the one that approves it. It's the only AI skill in active use by business teams on Data Ventures, which is really a story about designing for adoption, not just accuracy.

For the GTM-integration side: I built a production agent wired into a Jira queue and Slack that took 400+ requests from 30–60 minutes each to under 10, on an MCP server over BigQuery with self-healing retries. That's the "integrate across the stack via APIs, keep data flow clean, make it reliable enough to trust" pattern this role runs on — the CRM would just be the next system to connect.
