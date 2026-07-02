# Application Answers — Notion · Software Engineer, AI Workflows

**Apply here:** https://jobs.ashbyhq.com/notion/17330e14-83db-49a4-ae31-411690d97dba

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Notion
The Custom Agents mandate — automating recurring workflows like filing tasks, writing reports, and answering knowledge-base questions — is almost exactly the problem I've spent the last year shipping against, so this is the rare JD where the day-one work is the work I already do. I've built agents that take a stream of repetitive requests, do the retrieval and the reasoning, and hand back something a person can trust, and the hard parts Notion is pointing at — productionizing and scaling asynchronous workflows, reliability at scale, keeping the system coherent from UI down to the data model — are the exact parts I've had to get right, not the demo parts. I also like that Notion frames AI as a collaborative tool held to a craft bar rather than a novelty; the thing I care most about in my own agents is that stakeholders actually adopt them and trust them, which only happens when the reliability and the product judgment are real. My front-end depth is lighter than the React/TypeScript nice-to-haves, and I'd be honest about that as a growth axis — but the LLM/embeddings core, the async-workflow engineering, and the from-inception product ownership are squarely where I've been building.

## Relevant project
The build that maps most directly to Custom Agents is a production Jira ticket-resolution agent I shipped at Walmart — it automates exactly the recurring-workflow shape Notion describes: intake a request, plan, execute, and file the result. It's a 6-gate pipeline (triage, context, plan, execute, validate, report) on an MCP server I built over BigQuery, with a FAISS + BM25 retrieval layer over 11,000 historical queries so the agent works from a curated context interface, and it writes a permanent artifact at every gate because long-running agents lose coherence as the context window fills. It took 400+ recurring tickets from 30-60 minutes each down to under 10, it's approved by Sr. Director and product leadership, and the stakeholders on the receiving end never knew an agent was answering them. For the knowledge-base-query half of the feature, I also built a self-service analytics agent over 67 BigQuery tables as a sub-agent flow with a 23-case golden-query eval suite — it lets non-technical teams ask a question and get a validated answer, and it's the only AI skill currently in active use by business teams on Data Ventures. Both are the async, productionized, reliability-gated version of the workflows this role is about, not prototypes.

<!-- No custom application questions visible on the posting. -->
