# Application Profile

Canonical **apply-side** answers for ATS application forms — the source of truth for the answers doc in every apply packet (see `Automation Design - Two-Orchestrator/Spec - Apply Packet.md`). Search-side filters (comp floor, seniority, skip lists) live in `Job Search Target Profile.md`; this file holds only what gets typed into application forms.

**Never-invent rule:** generators copy from here or leave a `[?]` placeholder — they do not compose new claims. Maintained via the `interview-prep-reusables` skill.

## Facts

- **Salary expectation:** $130,000+ base. Form phrasing: _"Targeting $130k+ base; flexible depending on total compensation and scope."_ For forms that force a single number, enter `130000`.
- **Work authorization:** U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship question: **No**, sponsorship not required.)
- **Notice period / availability:** 2 weeks from offer acceptance.
- **Current employer / title:** Walmart Data Ventures — Senior Data Analyst, Customer Perception team.
- **Email:** madhok.kanu@gmail.com
- **Phone:** `[NUMBER?]`
- **LinkedIn URL:** `[URL?]`
- **Location / relocation / remote preference:** `[PREFERENCE?]`

## Standard short answers

- **Why this company / this role:** generated per role from the JD + `.classification.json` themes — deliberately no canned block here; a reusable paragraph would read as one.
- **Describe a relevant project:** select from `AI Build Walkthrough - Master.md` by the role's archetype; link the matching demo from `Demo Portfolio.md` when the form allows URLs.
- **How did you hear about this role:** "LinkedIn" unless the role folder records another source.

## Custom-question policy

Questions **visible on the posting** get drafted into the role's answers doc at prep time. Questions that only appear inside the apply flow are answered live, aided by the blocks above — do not guess at them in the packet.
