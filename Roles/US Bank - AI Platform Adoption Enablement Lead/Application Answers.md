# Application Answers — U.S. Bank · AI Platform Adoption & Enablement Lead

**Apply here:** https://www.linkedin.com/jobs/view/4432056856/

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why U.S. Bank
This role is about helping an enterprise adopt AI well — observability and monitoring frameworks, production-ready patterns, governance, and translating business problems into scalable AI — and that's the shape of what I've built at Walmart, just at a smaller scale than a bank. The emphasis on observability and operational excellence is where I actually live: I built a headless KPI monitor where every decision the agent makes is logged to BigQuery, so end-to-end observability is built into the data model, not bolted on. I'm also the person who defines the reusable patterns and does the enablement — my Walmart agents are productized skills other teams adopt, and the analytics agent is the only AI skill in active use by business teams there. To be straight about fit: my stack is GCP/Vertex/Claude/Gemini rather than the Azure AI suite, so I'd frame myself as platform-agnostic with a fast ramp on Azure — the design patterns for adoption, observability, and governance carry across the cloud. The trusted-advisor half of this role, guiding teams on feasibility and trade-offs, is the part of my current job I most enjoy.

## Relevant project
Headless KPI monitor + observability substrate. I built a production agent on a 6-hour cron that detects KPI breaches, runs root-cause analysis, and posts Slack alerts with the diagnosis attached — and every breach detection and root-cause output is queryable in BigQuery. That decision-logging is the eval and monitoring substrate: I can ask "how often does the diagnosis match what a human would conclude" over any time window, and I treat alert precision as a first-class metric because a noisy agent gets muted and might as well not exist. That's exactly the performance/drift/reliability monitoring and feedback-loop discipline this role has to establish across the enterprise.

Registry-governed hybrid orchestrator (governance, lineage, human gate). I built an orchestrator that routes a business question through both a CubeJS semantic layer and a context-engineered agent in parallel, reasons about disagreements, and feeds discrepancies back to refine the definitions over time. Governance is structural: definitions are versioned, disagreements are the audit trail, and today I'm the human gate on which answer is right at low volume. That maps to the model governance, lineage, and auditability this role owns — and to the responsible, reviewable adoption a regulated bank needs.
