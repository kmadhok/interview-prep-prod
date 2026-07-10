# write-outreach — Behavior Contract

The write-outreach step drafts `Cold Outreach.md` with two intro sections
(one per recipient), addresses drawn from `Verified Emails.md`, and no
placeholder leaks. This contract pins the observable end-state of a
completed write-outreach run. (The never-sent Gmail invariant is live-tier
only — Decision 6 — and is out of per-skill scope.)

## Clauses

### write-outreach-C1: Cold Outreach.md exists with two intro sections

`workspace/Roles/Acme - Senior Agent Builder/Cold Outreach.md` exists and
contains at least two intro/recipient sections. A section is a heading at
`#` or `##` level that introduces a distinct outreach target (e.g.
"## Intro — Recruiter", "## Intro — Hiring Manager").

**How checked:** Read the file; find headings matching `^#{1,2}\s+.*intro`
(case-insensitive); assert at least two such headings.

### write-outreach-C2: Every To: address appears in Verified Emails.md

Every `To:` line in `Cold Outreach.md` carries an address that appears in
`Verified Emails.md`. Outreach never sends to an address that was not
verified/inferred.

**How checked:** Collect every email after `To:` lines in Cold Outreach.md;
collect every email in Verified Emails.md; assert each To: address is in the
verified set.

### write-outreach-C3: Zero placeholder leaks

`Cold Outreach.md` contains none of the placeholder markers that indicate
unfinished drafting: `[NUMBER?]`, `<user_`, `{name}`, `[slot`, `TBD`.

**How checked:** Read the file; assert none of those five strings appear.
