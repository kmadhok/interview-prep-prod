# Fixture — distyl-fde

The inputs the `write-outreach` skill needs to produce ONE cold-recruiter email. Real role from
`Roles/Distyl - Forward Deployed AI Engineer/`.

## Skill inputs (mode: drip, recruiter contact only)
- **role_title:** Forward Deployed AI Engineer
- **company:** Distyl (Distyl AI)
- **archetype:** FDE / client-facing
- **lead_theme:** end-to-end / agents
- **role_folder:** `Roles/Distyl - Forward Deployed AI Engineer`

## Beat-3 mode for this fixture: **OMIT** (tests clean live-sourcing → no live process)
No today-or-future competing process survives the freshness filter. The skill MUST source beat 3 live
from `Pipeline.md`, find nothing eligible, and **omit beat 3 cleanly** — not fabricate, not stretch a
stale process. Judge `urgency_social_proof` on a clean omission (see RUBRIC).

## Recruiter contact (the one top-pick)
Use the **EmailFinder-verified** recruiter, not the pattern-inferred one, so the fixture is clean.
| Name | Title | Email | Confidence | Channel |
|------|-------|-------|-----------|---------|
| Austin Amberg | Technical Sourcer, Distyl (SF) | austin.amberg@distyl.ai | High (EmailFinder-verified) | Email |

## JD details available for beat 4 (why-this-company)
- Production systems in **customer environments**, not demos.
- $150K–$250K base + equity · SF hybrid (Tue–Thu in-office).
- FDE = the same end-to-end build work across a portfolio of customers.

## Canonical achievements in play (from Resume Achievements Master.md)
- Jira agent: MCP context-gathering + RAG over 11,000 historical queries, closed 400+ requests, 30–60 min → under 10.
- Self-service analytics agent over 67 BigQuery tables; sub-agent orchestration; 23-case eval suite + HITL.

## Hook case
Richest contact data of the three; enrich-hook candidate (a recruiter post about growing Distyl's
eng team exists in the role folder). If a real scraped post is available it takes beat-1 precedence;
otherwise beat 1 = applied/role-interest trigger. Do NOT fabricate the post if it isn't supplied.
