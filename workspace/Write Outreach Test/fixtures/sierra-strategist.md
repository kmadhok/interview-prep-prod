# Fixture — sierra-strategist

The inputs the `write-outreach` skill needs to produce ONE cold-recruiter email. Real role from
`Roles/Sierra - Strategist Agent Development/`.

## Skill inputs (mode: drip, recruiter contact only)
- **role_title:** Strategist, Agent Development
- **company:** Sierra
- **archetype:** agent development / product (FDE blend)
- **lead_theme:** agent design + customer outcomes
- **role_folder:** `Roles/Sierra - Strategist Agent Development`

## Beat-3 mode for this fixture: **OMIT** (tests clean live-sourcing → no live process)
No today-or-future competing process survives the freshness filter. The skill MUST source beat 3 live
from `Pipeline.md`, find nothing eligible, and **omit beat 3 cleanly**. Judge `urgency_social_proof`
on a clean omission (see RUBRIC).

## Recruiter contact (the one top-pick)
| Name | Title | Email | Confidence | Channel |
|------|-------|-------|-----------|---------|
| Greg Marsh | Head of Recruiting, Sierra | greg@sierra.ai | High (EmailFinder-verified) | Email |

## JD details available for beat 4 (why-this-company)
- Agent Strategist function: turn fuzzy business problems into agent specs + outcomes.
- Sierra crossed **$200M ARR** — build-at-scale angle.
- On-site SF Bay Area · $150K–$300K.

## Canonical achievements in play (from Resume Achievements Master.md)
- Self-service analytics agent over 67 BigQuery tables; sub-agent orchestration; HITL; 23-case eval suite; only AI skill in active use by business teams.
- Partner with Product + Data Science to turn fuzzy asks into agent specs (maps almost word-for-word to the Agent Strategist job).

## Hook case
Product/strategy angle, not pure-eng — this fixture tests whether the skill picks the
strategist-flavored achievement (the analytics agent + the "partner with Product/DS to spec agents"
line) over the default Jira-agent hook. Beat 1 = applied/role-interest trigger.
