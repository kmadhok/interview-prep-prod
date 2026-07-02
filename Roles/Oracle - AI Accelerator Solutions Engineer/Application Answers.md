# Application Answers — Oracle · AI Accelerator Solutions Engineer

**Apply here:** https://www.linkedin.com/jobs/view/4409218395/ (OCI role; responses managed off LinkedIn — capture the careers.oracle.com posting before applying)

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why Oracle
The job description reads like a summary of what I already do: take a manual, file-based business process and turn it into a trusted, repeatable AI-assisted workflow, with human-in-the-loop controls so people actually believe the output. At Walmart I've built exactly this shape of thing on the Business Operations side of an analytics org — agents, skills, and MCP integrations that connect to real systems and ship answers stakeholders trust. The must-haves name Claude Code and Anthropic APIs specifically, which is my daily toolset, not a line I'm padding. What makes this role interesting to me is the adoption half of it — the JD calls out training, documentation, and scaling successful solutions across teams, and that's the part most AI projects skip and then die. I care about the workflow surviving after I hand it off, which is why validation and HITL gates show up in everything I build.

## Relevant project
Autonomous Jira ticket-resolution agent: I built a production agent that took 400+ data-readiness tickets from 30-60 minutes each (a full day for the complex ones) down to under 10 minutes, and the stakeholders on the receiving end never knew an agent was answering them. It's a 6-gate pipeline over an MCP server I built on top of BigQuery, plus a FAISS + BM25 retrieval layer over 11,000 historical queries. I went MCP over handing the agent direct DB credentials because the MCP layer is where I enforce what the agent is allowed to touch — that's the audit boundary, and it's the same integration-and-trust problem Oracle is describing. Every gate writes a permanent artifact, and there's a 10-retry self-healing budget before it escalates. Today I'm the human in the loop reviewing the work-log artifacts; the next version moves that gate to a golden-set regression that abstains and kicks back a "need clarification" instead of guessing.

Self-service analytics agent over 67 tables: the same pattern pointed at a different workflow — a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) that lets business teams self-serve validated answers. It's the only AI skill in active use by business teams on Data Ventures, which is the "drive efficiency and adoption" outcome this role is measured on.
