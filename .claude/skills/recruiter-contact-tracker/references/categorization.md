# Categorization Rubric

Every contact gets exactly one of these five `type` values. The point of the categories is to make the tracker scan-able: when the user is about to apply somewhere new, they want to instantly see who's worth pinging vs. who's a dead lead.

## active

**Signal:** Live pipeline. There are reciprocal messages within roughly the last 30 days. Something is in motion right now.

**Examples:**
- Recruiter screen just completed, recruiter said "I'll have an update next week."
- Interview loop scheduled, awaiting feedback.
- Recruiter routed the user to another team and the intro is still pending.

**How to display:** Top of the page, blue tag. These are the people the user should not lose track of.

## warm

**Signal:** A real human relationship exists, even if not currently active. They replied to the user, or they got past the application stage with them, or they sourced them and engaged in actual back-and-forth.

**Examples:**
- McKinsey recruiter who ran a full loop 3 months ago — even though that role didn't land, she now knows the user.
- Recruiter who phone-screened the user for a role that ultimately didn't progress.
- Sourcer who explicitly offered to route the user to a different team.
- Hiring manager who sent a personal follow-up after a rejection.

**Why it matters:** These are re-engagement candidates. When a new role opens at their company, the user can warm-restart the conversation with "Hi [name], we spoke about [previous role]…"

## referrer

**Signal:** Internal employee at a target company who has referred (or could refer) the user, *not* their recruiter.

**Examples:**
- Family/friend at Microsoft submitting referrals on the user's behalf.
- A Googler who pushed the user's resume through internal channels.
- A former colleague at Walmart who's now at Anthropic.

**Why a separate category:** Referrers are usually higher-leverage than external recruiters — they can vouch for the user's actual work. They also need to be approached differently (a casual ping, not a formal recruiter message).

## cold

**Signal:** the user sent outbound, no human reply yet (or only an automated rejection followed).

**Examples:**
- the user emailed a recruiter directly after applying; no reply.
- the user reached out to an internal contact at a target company; no reply.
- Multi-recipient outreach where some bounced and one delivered but never responded.

**Why keep these:** They're not dead — they're just unconverted. Same human is still on LinkedIn, still hiring, often just buried. Worth a follow-up if a relevant role opens.

## stale

**Signal:** One of these is true:
1. No activity in 12+ months and the original conversation never went anywhere.
2. Skill-mismatched outreach the user would never realistically pursue (e.g., body-shop staffing recruiters pitching Oracle EPM contract roles when the user does senior AI/DS work).
3. Auto-rejection email with no prior human contact — the "person" was never really there.
4. Known to be unavailable (e.g., on extended leave) AND the coverage contact is captured separately.

**Why keep them at all:** Sometimes useful to know who you've already been ruled out by, so you don't re-pitch them. But these should be at the bottom of the page and visually de-emphasized.

## Edge cases

- **You can't tell name + company from the thread.** If the sender's display name is "Hiring Team" and the body is templated, skip the contact entirely. Don't pollute the tracker with anonymous entries.
- **Same person, different email format over time.** Treat as one contact. Use the most recent working address. Note format changes in `notes` if relevant ("emails as @xwf.google.com sometimes").
- **Recruiter moved companies.** Keep the most recent role/company in the row. If you can tell from a sig line they're now elsewhere, note it: "Now at [new company] per Apr 2026 signature."
- **External staffing agency vs. in-house recruiter.** External agencies (ISGF, Diverse Lynx, VDart, Quantum World) are almost always low-value for senior AI/DS roles — default them to `stale` unless they're pitching something the user would actually take.
- **LinkedIn-only InMail with no email exposed.** Set `email` to `(LinkedIn InMail only)` and keep the row — the contact is still reachable via LinkedIn.

## Promotion / demotion when refreshing

When refreshing an existing tracker, contacts can move categories naturally:

- `active` → `warm`: pipeline ended (offer not extended, candidacy paused) but the human relationship remains.
- `warm` → `stale`: >12 months silent and no realistic re-engagement angle.
- `cold` → `warm`: they finally replied. Promote!
- `cold` → `stale`: no reply after 12+ months.

If the user manually moved someone to a different category in a previous edit, respect that. Don't auto-revert.
