---
name: recruiter-contact-tracker
description: Mine Kanu Madhok's Gmail for recruiter, hiring manager, and internal referrer contacts and build or refresh a sortable, filterable HTML tracker at `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html`. Trigger whenever Kanu asks to build, refresh, update, expand, or audit his recruiter contact list/tracker/spreadsheet; asks "who has reached out to me about a role"; wants to surface recruiters, hiring managers, sourcers, or referrers from his inbox; or wants a list of people he can ping when applying to new roles. Also trigger on bare requests like "find my recruiters", "who can I reach out to", "make me a contact list", "build out a list of recruiters", or "search my email for hiring people" inside Interview Prep. Do NOT trigger when the user wants to draft an outreach email for a specific role (that's `job-outreach`), file a single JD into the pipeline (that's `interview-prep-intake`), or look up one specific person.
---

# Recruiter Contact Tracker

A repeatable workflow to mine Kanu's Gmail for everyone who could matter in a job search — recruiters, hiring managers, talent partners, internal referrers, and warm threads he's started himself — and assemble it into a single sortable HTML page he can keep updated.

The whole point: when Kanu's about to apply somewhere, he wants to be able to ctrl-F a real person to ping rather than firing applications into ATS black holes. This skill produces (and keeps fresh) that ctrl-F list.

## When this fires

Use this skill any time Kanu wants the *contact list* itself produced or refreshed. If he's preparing for a specific role or drafting a single email, that's a different skill — see "Do NOT use when" below.

## Workflow

Follow these steps in order. Each step assumes Gmail tools are connected (the connector name typically includes "Gmail" — look for `search_threads` and `get_thread`).

### 1. Confirm scope (only if ambiguous)

The defaults below work well; only ask if the request is contradictory or you don't have Gmail access yet.

- Look-back window: **2 years** by default. Ask only if the user implies "all time", "this year only", or similar.
- Output location: **`/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html`**. Don't relocate it.
- Categories to include: **recruiters + hiring managers + referrers + warm cold-outbound threads Kanu started himself**. Skip if the user says "only external recruiters" or similar.

### 2. Detect whether the tracker already exists

```bash
ls "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html"
```

- **If it exists**, this is a *refresh*. Extract existing rows so you can merge new findings without clobbering Kanu's hand-edited notes or categories:
  ```bash
  python3 <SKILL_DIR>/scripts/render_tracker.py extract \
      "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html"
  ```
  This prints the rows as JSON. Keep this — you will merge into it later.

  Then find the most recent `date` in those rows. That's your incremental search floor (use `after:<that_date - 7 days>` to catch anything that landed near the boundary).

- **If it does not exist**, this is a *fresh build*. Search the full 2-year window.

### 3. Search Gmail

Run several targeted queries in parallel — the Gmail tool returns ~50 threads per call and you want broad coverage. See `references/gmail_search_strategy.md` for the full query bank. The essentials:

1. **LinkedIn InMail forwards** — `(from:linkedin.com subject:"InMail") after:<floor>`
2. **ATS auto-emails** (catch the role + company, not the recruiter) — `from:(greenhouse.io OR lever.co OR ashbyhq.com OR myworkday.com OR icims.com OR smartrecruiters.com OR jobvite.com OR rippling.com) after:<floor>`
3. **Interview/scheduling subjects** — `subject:(interview OR "phone screen" OR "next steps" OR "scheduling" OR "onsite" OR "loop" OR "panel") after:<floor> -category:promotions`
4. **Recruiter language** — `subject:(recruiter OR recruiting OR "talent acquisition" OR "opportunity" OR "reaching out") after:<floor>`
5. **Referral threads** — `("referred you" OR "referral" OR "got your name" OR "Googler") after:<floor>`
6. **Company-domain sweep** for known target companies — `from:(@walmart.com OR @bcg.com OR @mckinsey.com OR @google.com OR @stripe.com OR @anthropic.com OR @openai.com OR @apple.com ...) after:<floor>`
7. **Kanu's own outbound** to recruiter-like addresses — search Sent mail for `to:(@<company>.com) -to:noreply -to:no-reply` for each target company, OR a broad scan of Sent with subjects mentioning "recruiter" or job IDs.

Don't fetch full thread bodies for every result — the search snippets + headers (sender, to, subject, date) contain almost everything you need. Only `get_thread` for threads where the snippet hides crucial info (e.g., a HackerRank invite where the actual interviewer/coordinator name is in the body).

### 4. Triage and categorize

For every thread, classify the sender(s) using the rubric in `references/categorization.md`. The short version:

| Category | Signal |
|---|---|
| **active** | Live pipeline in the last ~30 days, reciprocal messages, interview scheduled |
| **warm** | Real human reply, you got past the application stage, relationship exists |
| **referrer** | Internal employee referring Kanu (not an external recruiter) |
| **cold** | Outbound Kanu sent, no human reply yet |
| **stale** | >12 months silent, skill-mismatched (Oracle EPM body shops, etc.), or auto-rejection with no prior human contact |

**Always skip** the noise: `jobalerts-noreply`, `hit-reply@linkedin.com` newsletter digests, `newsletters-noreply@linkedin.com`, `noreply@glassdoor.com`, `info@mail.joinleland.com`, `TheAthletic@…`, generic ATS confirmations (`no-reply@ashbyhq.com`, `expedia@myworkday.com`, etc.) UNLESS they expose a real recruiter's name in body text you care about.

For each contact you keep, capture:
- **name** (best guess from sender display name or signature; "(unknown)" if truly hidden, e.g. LinkedIn InMail)
- **company**
- **role / title** (recruiter, hiring manager, sourcer, talent acquisition, internal referrer — be specific when known)
- **email** (the actual address; if it's LinkedIn-InMail-only, write `(LinkedIn InMail only)`)
- **date** (ISO `YYYY-MM-DD` of the most recent message in the thread that involves them)
- **type** (one of: `active`, `warm`, `referrer`, `cold`, `stale`)
- **notes** (one or two crisp sentences: what role, what happened, why this person matters or doesn't)

### 5. Merge with existing data (refresh case only)

When merging with existing rows:

- **Match by email** (case-insensitive) as the primary key. Fall back to `name + company` for entries without a real email.
- **Preserve user-edited fields.** If the existing row's `notes` differs from your generated guess, keep the user's notes. Same for `type` — if a user moved someone from `cold` to `warm`, respect that.
- **Update `date`** when you found a newer thread for that contact.
- **Append** new contacts that weren't in the existing file.
- **Don't delete** anyone unless the user explicitly asked you to prune.

When in doubt about whether something was hand-edited vs. machine-generated, keep both possibilities open and surface the conflict in your final summary rather than overwriting.

### 6. Render the HTML

Pass the merged rows to the bundled renderer:

```bash
echo '<rows_json_here>' | python3 <SKILL_DIR>/scripts/render_tracker.py render \
    "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html"
```

The renderer uses `assets/tracker_template.html`, which produces a single self-contained HTML page (no external deps): search box, category filter, click-to-sort columns, color-coded category tags, mailto links. The "generated on" date in the header is auto-filled with today's date.

### 7. Summarize what changed

After the file is written, give Kanu a short summary in chat:

- Total contacts in the tracker (before vs. after, or just "N contacts" on a fresh build).
- Notable adds — the 3-5 most strategically interesting new contacts (warm > active > referrer > cold).
- Anything weird worth flagging: bounced addresses, OOO replies, recruiters who moved companies, contacts who haven't been touched in >12 months and could use a re-engagement ping.
- A clickable `[View your recruiter contact list](computer:///Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Recruiter Contacts.html)` link.

Keep the summary tight — Kanu wants the file, not a wall of text about the file.

## Do NOT use when

- The user asks to **draft a cold outreach email** for a specific role → use `job-outreach`.
- The user shares a **single fresh JD** and wants it filed → use `interview-prep-intake`.
- The user wants to **look up one specific person** (e.g., "find the email for the BCG X recruiter") → just search Gmail directly, no tracker needed.
- The user wants **interview prep material** for a role they have lined up → that's a normal Interview Prep folder workflow, no tracker needed.

If both this and another skill plausibly apply (e.g., "build me a recruiter list AND draft outreach to the top 3"), do the tracker first, then hand off to `job-outreach` for the drafting.

## Key references

- `references/gmail_search_strategy.md` — the full query bank, including company-domain sweeps and edge cases.
- `references/categorization.md` — detailed rubric with examples for each category.
- `scripts/render_tracker.py` — extracts existing rows, renders new HTML. Always invoke via python3.
- `assets/tracker_template.html` — the HTML template. Don't edit unless changing the page's look.
