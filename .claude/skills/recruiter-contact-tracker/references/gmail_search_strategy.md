# Gmail Search Strategy

This is the query bank that consistently surfaces the right people without drowning you in newsletter noise. Run the queries that make sense in parallel (the Gmail connector accepts ~50 threads per call) and merge results.

Replace `<floor>` with your search floor date in `YYYY/MM/DD` format. For a fresh build that's typically `today - 2 years`. For a refresh, it's `(latest_existing_date - 7 days)` to catch anything near the boundary.

## Core queries (always run)

### 1. LinkedIn InMail forwards
```
(from:linkedin.com subject:"InMail") after:<floor>
```
LinkedIn forwards InMails to email. Senders appear as `inmail-hit-reply@linkedin.com` — the actual recruiter's name is in the subject or snippet. Email addresses are *not* exposed, so record these as `(LinkedIn InMail only)`.

### 2. ATS auto-emails (captures company + role even when recruiter is hidden)
```
from:(greenhouse.io OR lever.co OR ashbyhq.com OR myworkday.com OR icims.com OR smartrecruiters.com OR jobvite.com OR rippling.com OR ats.rippling.com OR talent.icims.com OR us.greenhouse-mail.io OR hire.lever.co OR nurture.icims.com) after:<floor>
```
Most of these are pure noise (auto-rejections, application confirmations), but two things make them worth scanning:
1. Some include the recruiter's name in the body or signature.
2. Pattern of applications shows Kanu which companies are in his pipeline — useful context when triaging.

### 3. Interview / scheduling subjects
```
subject:(interview OR "phone screen" OR "next steps" OR "scheduling" OR "onsite" OR "loop" OR "panel") after:<floor> -category:promotions
```
This catches the high-signal threads: actual interview invites, coordinator scheduling, panel logistics. Recruiter and coordinator names are usually in the From or signature.

### 4. Recruiter language (broad sweep)
```
subject:(recruiter OR recruiting OR "talent acquisition" OR "opportunity" OR "reaching out" OR "exciting role" OR "interested in chatting") after:<floor> -category:promotions
```

### 5. Referral threads
```
("referred you" OR "referral" OR "got your name" OR "Googler" OR "recommended you for") after:<floor> -from:linkedin -from:no-reply -from:noreply
```
Surfaces internal-referrer threads. Microsoft uses `donotreply@email.careers.microsoft.com` for referral notifications — those reveal the referrer's name in the body.

## Company-domain sweep

Once you have a rough company list (from the queries above + Kanu's known pipeline), pull every human email exchange with those domains:

```
from:(@walmart.com OR @bcg.com OR @mckinsey.com OR @google.com OR @stripe.com OR @anthropic.com OR @openai.com OR @apple.com OR @cvshealth.com OR @deloitte.com OR @grainger.com OR @upside.com OR @amazon.com OR @microsoft.com OR @meta.com OR @uber.com OR @linkedin.com OR @snowflake.com OR @figma.com OR @hubinternational.com OR @pppllc.com) after:<floor> -from:no-reply -from:noreply
```

Add/remove domains based on Kanu's actual pipeline. New active companies should be added — old ones with zero activity in the window can be dropped to save query budget.

## Kanu's own outbound

Don't forget threads Kanu started. He often cold-emails internal contacts asking to be routed to the right recruiter — those people are valuable contacts even when they never replied.

```
in:sent after:<floor> -to:noreply -to:no-reply -to:jobs-noreply
```

Sift this manually — too broad to use directly, but rich for finding cold-outbound contacts.

## Hard skip list

These senders are pure noise — skip on sight:

- `jobalerts-noreply@linkedin.com` — daily job alert digests
- `newsletters-noreply@linkedin.com` — "AI Engineer Interview Prep Q&A" type content
- `updates-noreply@linkedin.com` — generic engagement nags
- `jobs-noreply@linkedin.com` — saved job reminders
- `noreply@glassdoor.com` — Glassdoor "real talk" threads
- `info@mail.joinleland.com` — Leland event promos
- `info@marketing.mlbemail.com` / `TheAthletic@…` / `team@info.classpass.com` — totally unrelated
- `noreply@luma-mail.com` / `LelandFreeEvents…@calendar.luma-mail.com` — event RSVPs
- Generic ATS confirmations (`expedia@myworkday.com`, `statefarm@nurture.icims.com` Spring/Summer/Fall newsletters, `no-reply@ashbyhq.com` for application-received emails) — UNLESS a real name appears in the body

## Tricky cases

- **HackerRank assessment emails** (`support@hackerrankforwork.com`) — these often hide a coordinator's name in the body ("Marina has scheduled an interview between you and Jun"). When you see one, `get_thread` and pull the coordinator email.
- **`yello.co`** is McKinsey's interview scheduling tool — same pattern as HackerRank.
- **Out-of-office replies** — sometimes reveal a coverage contact (e.g., Stripe's Mack Santos OOO directing to Addy Roberts). Capture both.
- **Bounce notifications** (`mailer-daemon@googlemail.com`) — useful for noting which guessed email patterns *don't* work. Record the working address only.
- **Same person, multiple aliases** — Google recruiters often appear from both `@google.com` and `@xwf.google.com`. Treat as one contact; use the `@google.com` form as canonical.

## Pacing

Don't run all 7 queries serially — that wastes tokens and time. The Gmail connector accepts parallel calls; fire 4-5 at once and merge. A typical 2-year sweep returns 100-200 threads, of which maybe 30-50 contain useful contacts after triage.
