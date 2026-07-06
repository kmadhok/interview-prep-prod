# Application Answers — Snowflake · Forward Deployed Analytics Engineer & AI Specialist

**Apply here:** https://jobs.ashbyhq.com/snowflake/44ca2f15-1af0-49e3-92f1-1f96a9f6a616

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Snowflake
This role is the exact work I already do, just pointed at customer data instead of Walmart's. The JD frames it as owning the full stack from source ingestion to the semantic layer that exposes business meaning to natural language — building semantic models a non-technical analyst can query in plain English through Cortex Analyst. I've built that layer: a self-service analytics agent over 67 BigQuery tables that business teams query themselves, and a semantic layer feeding it. I also live in the client-facing translation seat the JD describes — my job at Walmart is turning ambiguous business questions from Product and stakeholders into agent-ready specs, then staying until the thing runs in production and the team can maintain it. And the daily-AI-coding-assistant baseline isn't a stretch for me; I build these systems in Claude Code every day, so "AI as a high-trust collaborator" is just how I work. The part I'm most drawn to is that this role doesn't stop at the recommendation — you write the code, build the semantic foundation, and hand back something the customer can run.

## Relevant project
Self-service analytics agent over 67 BigQuery tables (semantic layer for business users). I designed and shipped a four-sub-agent flow — Context Researcher, SQL Drafter, Validator, and a Devil's Advocate that challenges the output before it ships — so business teams can ask a question in plain English and get a validated answer without waiting on the one analyst who knows the schema. Underneath the LLM I put 8 deterministic SQL rules (no SELECT *, every join needs a key, no cross-table aggregation without a date filter) that catch structural mistakes cheaply before any model call, plus a 23-case golden-query suite the agent has to pass to ship. It's the only AI skill in active use by business teams on Data Ventures, approved by Sr. Director and product leadership. That's the same shape as the Cortex Analyst work: define the metrics, dimensions, and relationships an agent needs to reason correctly, then guard the edge cases so it doesn't fail on a real question.

Live text-to-SQL copilot (public demo). I built and deployed a natural-language-to-SQL copilot anyone can hit — Streamlit front end, RAG over historical queries so the model anchors on real column names instead of inventing them, live BigQuery execution, and an auto-visualization layer that picks the chart type from the result shape. It runs against a real schema, not a sandbox, because a demo on synthetic data doesn't survive the first question about actual join semantics. It's the standalone proof of the exact pattern this role productionizes — clean data plus a grounded model equals reliable natural-language querying — and it's live if the team wants to try it mid-conversation.
