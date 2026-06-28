# Fixture — cohere-fde

The inputs the `write-outreach` skill needs to produce ONE cold-recruiter email. Real role from
`Roles/Cohere - Forward Deployed Engineer Agentic Platform/`.

## Skill inputs (mode: drip, recruiter contact only)
- **role_title:** Forward Deployed Engineer, Agentic Platform
- **company:** Cohere
- **archetype:** FDE / client-facing
- **lead_theme:** agents / RAG / end-to-end agent delivery
- **role_folder:** `Roles/Cohere - Forward Deployed Engineer Agentic Platform`

## Beat-3 mode for this fixture: **LIVE PROCESS PROVIDED** (tests the gold email's signature move)
This fixture hands the skill a real, declared competing-process list so the harness can test whether
the skill reproduces the gold email's paragraph-two move (real process + timeline + "closer match"
pivot, target never the backup). The skill should USE it, not omit beat 3.

> **urgency (declared live processes — use verbatim as the canonical input; do NOT invent beyond this):**
> Active processes at Walmart for two internal AI engineering roles (Principal SWE on Agent Builder +
> Principal Data Analyst) and at BCG X for a Senior AI role. Pivot target = Cohere's FDE/North work.
>
> *(This is a seeded TEST input, clearly labeled. It mirrors the gold email's own live-process list.
> In production the skill sources this live from `Pipeline.md` and omits it when nothing survives the
> freshness filter — see the other two fixtures for the omission case.)*

## Recruiter contact (the one top-pick)
| Name | Title | Email | Confidence | Channel |
|------|-------|-------|-----------|---------|
| Michael Pagano | GTM & Executive Recruiter, Cohere (NYC) | michael.pagano@cohere.com | High (EmailFinder-verified) | Email |

## JD details available for beat 4 (why-this-company)
- Building on **North**, Cohere's secure enterprise platform.
- Translating enterprise problems into production agents in customer environments.
- Enterprise-high reliability bar: eval suites + human-in-the-loop.

## Canonical achievements in play (from Resume Achievements Master.md — pick the best for beat 2)
- Jira agent: agentic RAG over 11,000 historical queries, closed 400+ requests, 30–60 min → under 10.
- Self-service analytics agent over 67 BigQuery tables; only AI skill in active use by business teams; 23-case golden-query eval suite + HITL.

## Hook case
JD-detail hook (the North platform / enterprise-agent angle). No enrich-scraped post for this recruiter — beat 1 = applied/role-interest trigger.
