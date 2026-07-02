# Application Answers — Okta · Senior Analytics Engineer

**Apply here:** https://www.okta.com/company/careers/business-technology/senior-analytics-engineer-7818510/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why Okta
This role is the exact seam I've been working at for the last year at Walmart: building a governed semantic foundation that serves both human analytics and AI. The JD asks for someone to standardize core Finance and Enterprise metrics with clear, governed logic in dbt and Snowflake, and to prepare well-modeled data for LLM use cases like Snowflake Cortex. On the Customer Perception team I built the semantic layer and the analytics agent that sits on top of it, so I've lived the thing Okta is trying to get right — that AI accuracy is downstream of how well-modeled and well-documented your data actually is. I like that this team owns the data products, not just the pipelines, and partners directly with Finance and People stakeholders, because the translation from a vague executive question into a consistent, reusable definition is the part I'm strongest at. The AI-first framing here is real work, not a slide, and that's what pulls me.

## Relevant project
Self-service analytics agent over 67 BigQuery tables: I designed and shipped a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) that lets business teams ask a question and get back a validated answer instead of waiting in an analyst's queue. It's the only AI skill in active use by business teams on Data Ventures. The part relevant to Okta is the eval and governance layer: 8 deterministic SQL rules (no SELECT *, every join needs a key, no cross-table aggregation without a date filter) fire before any model call, then a 23-case golden-query suite checks results against known-good output. That's the same discipline as dbt tests and shared definitions — structural correctness enforced before anything ships.

Hybrid orchestrator over a semantic layer: I built an orchestrator that routes a business question through both a CubeJS semantic-layer skill and the analytics agent in parallel, then treats their disagreement as signal — when they diverge, it reasons about whether the semantic-layer definition is stale or the agent is wrong, and feeds discrepancies back to refine the definitions over time. That's directly Okta's "shared semantic layer that supports both analytics and AI," with a mechanism for the layer to get smarter without someone hand-authoring every metric.
