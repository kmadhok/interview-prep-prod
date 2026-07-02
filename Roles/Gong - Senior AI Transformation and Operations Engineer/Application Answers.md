# Application Answers — Gong · Senior AI Transformation and Operations Engineer

**Apply here:** https://job-boards.greenhouse.io/gongio/jobs/4676378006

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000.)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Gong
Both halves of this role line up with what I already do. The innovation half — take a stakeholder's idea and turn it into a working agentic workflow without external engineering, then prove ROI with a POC before scaling — is basically my week at Walmart; I've shipped agents solo that removed real hours from a workflow and got approved by leadership on the strength of the outcome, not a deck. The operations/guardrails half is the part most builders skip and I lean into: I've built decision-logging and observability straight into the data model of a production monitor, and I've shipped cost/latency/accuracy-style tracking and dashboards (top ~1.4% of Walmart's). I'm Chicago-based and a UChicago MS ADS grad, which the posting flagged, and I like that this is an IC, hands-on-keyboard role — scrappy builder who thinks in business value is how I'd describe my own work.

## Relevant project
On the innovation/ROI side: a production agent I built took 400+ data-readiness tickets from 30–60 minutes each (a full day for the hard ones) to under 10 minutes — conservatively about a month of work-days a year recovered. It's an MCP server over BigQuery plus retrieval over 11,000 historical queries, with eval as a real gate (a validator sub-agent re-runs the SQL and checks it against a work log). That's the "build a POC that proves efficacy, then it becomes the thing people depend on" loop this role describes.

On the operations/guardrails side: I run a headless KPI monitor on a 6-hour cron that detects threshold breaches, does root-cause analysis, and posts Slack alerts with the diagnosis attached. Every decision it makes — which threshold breached, which hypothesis it explored, what it posted — is logged to BigQuery, so I can query "how often does the diagnosis match a human's" over any window. I treat alert precision as a first-class metric because a noisy agent gets muted. That's exactly the SLA/accuracy/cost monitoring and standardization the guardrails half of this role asks for.
