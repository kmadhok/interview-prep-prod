# Claude run — what I changed in the skill and why

I diagnosed the gap between the current `write-outreach` output and the gold email as one missing
trait carrying the most rubric weight: the gold email's paragraph two always ends on a **"[Company]'s
[specific JD detail] is the closer match for what I do" relevance pivot** (relevance_match 0.20 +
urgency_social_proof 0.22 = 0.42 of the score). The old §1 template only showed that pivot *inside the
optional beat-3 bracket*, so on the two OMIT fixtures (Distyl, Sierra) — where no live process exists —
the template would drop the urgency clause and leave paragraph two ending on the accomplishment alone,
losing the single trait Kanu named as why the gold email is gold. My edits make the relevance pivot
**mandatory in both beat-3 modes**: fused with urgency when a live process exists (Cohere), standalone
when omitted (Distyl, Sierra). I added explicit three-paragraph shaping (trigger / accomplishment +
optional-urgency + pivot / ask) to `Outreach Templates.md` §1 and reinforced it as a checked gate in
`SKILL.md`'s process step 4 and format check. I touched **no hard invariant** — draft-only,
no-fabrication, the banned-phrase list, the body em-dash gate, the exact signature block, and "one CTA"
are all unchanged; beat 3 is still sourced live from `Pipeline.md` and omitted when nothing survives
the freshness filter (verified: today is 2026-06-28 and every interview process in `Pipeline.md` is
dated 2026-06-26 or earlier, so Distyl/Sierra correctly omit). Every number is canonical (A3 Jira agent,
A1 analytics agent) and Cohere's beat 3 uses only the fixture-declared live processes. The result is
three emails that each reproduce the gold email's structure and its load-bearing pivot, which is what
moves them closer to the standard.
