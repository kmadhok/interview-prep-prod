# Outreach Templates

**Purpose.** Reusable, voice-locked openers for every outreach situation I hit on the job hunt — cold recruiters, post-screen thank-yous, nudge-after-silence, cold hiring-manager DMs, post-interview thank-yous, application follow-ups, networking asks. Saves me 20 minutes per email and keeps the tone consistent.

**The voice rules (these are non-negotiable):**

- First person, conversational. Read it out loud — if it doesn't sound like me talking to someone over coffee, rewrite it.
- No corporate filler. **Banned openers:** "I hope this email finds you well" / "I hope you are doing well" / "I hope this message finds you well", "Just wanted to reach out", "I wanted to reach out to express my interest", "I came across your profile", "I wanted to take a moment to". **Banned hype words:** "leverage/leveraged", "spearhead/spearheaded", "synergize/synergy", "drove", "passionate", "rockstar", "ninja". (Note: "circle back" is NOT banned — it's used intentionally in the FU2 follow-up template as a light, established nudge; don't flag it.)
- One specific hook per message — a project, a person, a JD detail. Generic = ignored.
- Short. If a paragraph isn't earning its place, cut it.
- End with one clear, low-friction ask. "Could we chat for 15 min next week?" is better than "I'd love to learn more."
- **Every generated draft must pass the installed `human-writing` skill** before it's considered done. That skill strips hedging, buzzwords, passive voice, and vague claims — run it on every email body.
- **Body em-dash gate (separate hard rule).** `human-writing` does NOT catch em dashes, so there is a SEPARATE, non-negotiable gate: ZERO em dashes (` — `, U+2014) anywhere in the email **body prose** — em dashes are a top AI tell. Rewrite with a comma, period, or colon instead. **Exception:** subject lines MAY keep the prescribed em-dash forms shown in the subject formulas in this file (e.g. `Built a 400-ticket Jira agent — Interested in [Role]`). So: body prose = no em dashes; subjects = em dash allowed only where a template here prescribes it.

**Signature block (use on every message unless context dictates otherwise):**

```
Best,
Kanu Madhok
madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok
```

For warmer / follow-up messages drop the contact lines and use just:

```
Best,
Kanu
```

---

# 1. Cold recruiter — initial outreach

**When to use.** I haven't applied yet, or I've applied and want to fast-track. Recruiter is on LinkedIn / company careers page / a previous req I saw.

**Channel.** LinkedIn InMail or email. LinkedIn first if I can find them; email if I have it.

### Subject line

Lead with the credential, not the role — recruiters open subject lines that signal who's emailing them, not which req it's about. Pick the form that fits:

- **Has competing process / known company:** `Ex-Walmart Agent Builder Interested in [Role] @ [Company]`
- **Has strong recent demo:** `Built a 400-ticket autonomous Jira agent — Interested in [Role] @ [Company]`
- **School connection to recruiter:** `Fellow UVA grad — Interested in [Role] @ [Company]`
- **Replying to a public posting:** `Re: your [HN/X/LinkedIn] post — Walmart agent builder interested`

Under 70 chars. Prefix with the recruiter's first name only when there's real personal context, e.g., `Dan | Ex-Walmart Agent Builder Interested in [Role] @ [Company]`.

### Body — 5-beat structure (~100 words, 50–125 hard range)

**Shape it like the gold email: three tight paragraphs.** P1 = beat 1 alone (one line). P2 = beats 2+3+4 fused into one flowing block that LANDS on the relevance pivot. P3 = beat 5 (the ask). Don't bolt the beats on as separate sentences-by-numbers; they should read as one person talking.

1. **Trigger line.** "I just applied for [exact role title] in your [practice/team]" (if applied), or "Found your post on [source]" / "Saw [Company]'s [specific thing]" (if cold). One sentence, its own paragraph.
2. **One accomplishment with a number.** From canonical achievements — the autonomous Jira agent (400+ tickets, 30–60 min → under 10), the autonomous data analyst, the hybrid orchestrator. ONE accomplishment, not a resume dump. Pick the one closest to this role's lead theme. Hyperlink the live demo when natural.
3. **Urgency / social proof (only if real, sourced from `Pipeline.md` at draft time).** Name real, CURRENTLY-LIVE competing processes from `Pipeline.md` by company + role + a concrete timeline ("interview Friday"), woven into the SAME sentence as the relevance pivot (beat 4), never as a standalone brag. **Freshness rule:** a process qualifies ONLY if its date is today-or-in-the-future relative to the draft date. DROP any item dated before today, and DROP anything flagged in `Pipeline.md` as STALE / PASSED / CLOSED / REJECTED. Never carry a "TODAY <past-date>" line forward. If zero live processes remain after filtering, OMIT beat 3 entirely. Never hardcode a date and never fabricate a process (`Pipeline.md` itself flags stale-date drafts as a failure).
4. **Relevance pivot — the load-bearing beat (always present, both modes).** This is the single trait that makes the gold email gold: end paragraph two on a line that ties THIS role to *what Kanu actually does*, phrased as a "[Company]'s [specific JD detail] is the closer match for what I do" pivot. It must be specific to the req (a named practice, stack item, platform, or customer segment from the JD), not generic flattery, and it must read as relevance, not interest. **When beat 3 is live**, fuse it: "...however [Company]'s [JD detail] is the closer match for what I do." **When beat 3 is omitted**, the pivot still closes paragraph two on its own: "[Company]'s [JD detail] is the closest match I've seen to the work I'm already doing." Either way, paragraph two ends on relevance to the target.
5. **Specific ask.** "I'd like to start the interview process. Are you the right person, or can you point me to the recruiter who owns this req? Resume attached." One ask, its own paragraph.

### Template

> **Subject:** Ex-Walmart Agent Builder Interested in [Role] @ [Company]
>
> Hi [First name],
>
> I just applied for the [exact role title] role in your [practice/team].
>
> At Walmart Data Ventures my autonomous Jira-resolution agent closed 400+ data requests and cut turnaround from 30–60 minutes to under 10 for each ticket. [Beat 3, ONLY if a real live process exists: I'm in active processes at [Company A] for [Role] (interview [day]) and at [Company B] for [Role], however] [Company]'s [specific JD detail] is the closer match for what I do.
>
> I'd like to start the interview process. Are you the right person, or can you point me to the recruiter who owns this req? Resume attached.

**Two ways paragraph two ends (pick by beat-3 mode):**

- **Beat 3 LIVE** — fuse urgency + pivot into one sentence: *"…cut turnaround from 30–60 minutes to under 10 for each ticket. I'm in active processes at [Company A] for [Role] (interview [day]) and at [Company B] for [Role], however [Company]'s [JD detail] is the closer match for what I do."*
- **Beat 3 OMITTED** (no live process) — drop the urgency clause but KEEP the relevance pivot so paragraph two still closes on the target: *"…cut turnaround from 30–60 minutes to under 10 for each ticket. [Company]'s [JD detail] is the closest match I've seen to the work I'm already doing."*

Never leave paragraph two ending on the accomplishment alone — it must land on why THIS role fits what Kanu does.
>
> Best,
>
> Kanu
>
> ---
> Kanu Madhok
> madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok
> Live demo: [URL from Demo Portfolio.md]

### Hook bank (swap into beat 2 if the Jira agent isn't the best fit for the role)

- **Agent-builder / platform roles:** *"I've spent the last year building and shipping production agents inside Walmart Data Ventures — Jira intake automation, an autonomous data analyst, and a hybrid semantic-layer orchestrator. The role reads like the version of that work I'd want to be doing at a bigger scope."*
- **FDE / client-facing roles:** *"I've shipped AI work end-to-end with both internal stakeholders at Walmart and external clients at FTI Consulting (RAG proposal generator, adopted into their workflow, won Best in Show at UChicago). FDE is the version of that work across a portfolio of customers, which is exactly where I want to be."*
- **Consulting / AI Factory / product-builder roles:** *"I've shipped two productized AI skills inside Walmart's Claude Code fork — first-of-kind across Walmart Data Ventures, cleared through formal Product + DS partnership review. The AI Factory role reads like the same work at firm scale."*
- **Eval / data-quality / measurement-heavy roles:** *"I've spent the last year designing the eval and HITL infrastructure under a portfolio of LLM agents — golden-set harness reusable across every agent I've shipped, deliberate HITL placement based on cost-of-error analysis. The role lines up unusually well with that work."*

### Length target

50–125 words (target ~100). Recruiters open and skim — every line has to earn its place.

---

# 1a. Cold recruiter — follow-up drip

> **Standalone follow-up cadence — NOT used by the jd-to-ready pipeline.** The pipeline ships ONE intro email per top pick (no follow-ups). The FU1 / FU2 / Hail-Mary templates below are for MANUAL, silence-triggered sends only.

**When to use.** Manual use only. Pair a Section 1 intro with the three follow-ups below, drafted at the same time. Send sequentially if silent. Data backs up the 3-touch cadence — responses often come on the 3rd, not the 1st.

**Channel.** Reply to the original thread (`Re: [original subject]`). Never start a new one.

### Follow-up 1 — send 3–4 business days after intro if silent

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Following up on the [role title] role at [Company]. The Jira agent I mentioned (400+ tickets, 30–60 min → under 10) is the closest analogue to what I read in the JD around [specific JD detail].
>
> Happy to send anything else helpful — what's the best next step?
>
> Best,
>
> Kanu

≤ 60 words.

### Follow-up 2 — send 4–5 business days after FU1 if still silent

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Wanted to circle back on this. What do next steps look like?
>
> Best,
>
> Kanu

≤ 40 words.

### Hail Mary — send only when fresh urgency arises

**Trigger.** New onsite scheduled, new offer with a clock, or travel to their city — something real and time-bound. Never invent.

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Quick update — I'm doing onsites with [Company A] and [Company B] [date / "this week" / "next week"] and wanted to give [Company] a chance to weigh in before timelines harden. If there's interest, I'd be happy to do a phone screen this week and slot a technical loop while I'm already in [city] / available.
>
> Best,
>
> Kanu

~80 words. Leads with the urgency, restates the ask with a built-in time window.

### Don't

- Don't open follow-ups with "Sorry to bother you" or "I know you're busy" — undermines the 3-touch logic.
- Don't pad with new content. FU1 restates the lead, FU2 is the nudge, Hail Mary adds urgency. That's it.
- Don't wait two weeks between touches "to be polite." 3–4 / 4–5 day cadence is the spec.

---

# 2. Post-recruiter-screen thank-you (same day)

**When to use.** Immediately after a recruiter screen (within 2–4 hours). Don't sleep on it.

**Channel.** Email — usually a reply to whatever thread the recruiter set up.

### Template

> Hi [First name],
>
> Thank you for the opportunity to interview for the [role title] role. I had a great time learning about the role and your experiences at [Company]!
>
> Best,
> Kanu

**That's it.** Don't write more. The job of this email is to be warm, fast, and short. Recruiters get hundreds of these — a clean one-liner outperforms a 3-paragraph thank-you every time.

**Real-world reference:** This is the exact pattern that worked with Ganna Volkova at BCG X on 2026-05-07. She replied within 23 minutes with a "next week" update commitment.

### Variants

- **If they mentioned a specific next step:** Add one line — *"Looking forward to [next step she named — e.g., the team interview, the take-home, the update next week]."*
- **If you discussed a specific role detail you want to flag interest on:** Add one line — *"Especially excited about [specific JD element they emphasized] — that's [one-sentence why it lines up]."* Don't oversell.

---

# 3. Recruiter nudge — after "I'll get back to you next week"

**When to use.** Recruiter said "I'll have an update next week" and the week + a buffer day have passed without a follow-up. Default buffer = 3 business days after their stated date.

**Channel.** Reply to the original thread. Don't start a new one.

### Template

> Hi [First name],
>
> Just floating this back up — wanted to check whether there's an update on the [role title] role on your end. No rush, just want to make sure I'm not missing a reply in my inbox.
>
> Best,
> Kanu

### Variants

- **If you have a competing offer or timeline pressure:** Add one line — *"I'm in conversations with a couple of other teams as well and want to keep you in the loop on timing if there's anything you can share."* Use this *only* if it's true. Bluffing reads as bluffing.
- **If the silence is longer (10+ business days past their stated date):** Add a soft re-state of interest — *"Still very interested in the role — happy to share an updated resume or jump on a call if it'd help move things forward."*

### Don't

- Don't apologize for nudging. ("Sorry to bother you" undercuts you.)
- Don't ask "any update?" without naming the role. They're juggling 20 roles.
- Don't send before 3 business days past their stated date. Earlier reads as anxious.

**Real-world reference:** Ganna at BCG X said "next week" on 2026-05-07. "Next week" = week of 2026-05-11. Buffer to 2026-05-15 (Friday). If no update by EOD 5/15, send this nudge.

---

# 4. Cold hiring manager / engineering lead / peer IC

**When to use.** I've identified the actual hiring manager, a senior engineer on the team, or a peer IC already in the role and want to skip the recruiter funnel (or supplement it). Best ROI when paired with an active application.

**Channel.** LinkedIn InMail. Skip email — cold-emailing someone you've never met from a non-corporate domain is iffy.

### Subject line

Lead with something specific to *them*, not just the role — HMs and peer ICs are protective of their time and respond to evidence you looked at their work, not a templated header. Pick one:

- **Their specific work:** `Your [project / talk / post] — interested in [Role] @ [Company]`
- **Shared background:** `Fellow [school / former employer] — interested in [Role] @ [Company]`
- **Direct role interest (fallback):** `Ex-Walmart Agent Builder Interested in [Role] @ [Company]`

Under 70 chars.

### Body — 5-beat structure (~100 words, 50–125 hard range)

Same 5 beats as Section 1, with two tweaks:

- **Beat 1** anchors to *them* (their work) instead of "I just applied". e.g., "Saw your post on [topic] — that's what made me look at the [role] req."
- **Beat 5 ask** builds in an escape valve so they can route you to the right owner instead of feeling cornered: "Are you the right person to talk to, or can you point me to the recruiter who owns this req?"
- **Beat 3 (urgency)** follows the SAME rule as Section 1: source it from `Pipeline.md` at draft time, name only CURRENTLY-LIVE processes (date today-or-in-the-future), DROP anything dated before today or flagged STALE / PASSED / CLOSED / REJECTED, never carry a "TODAY <past-date>" line forward, and OMIT beat 3 entirely if zero live processes remain. Never hardcode a date, never fabricate a process. Tie the pivot to their work where possible.

### Template

> **Subject:** Your [project / talk / post] — interested in [Role] @ [Company]
>
> Hi [First name],
>
> Saw [specific thing about them: a project, a post, a talk, a paper, a product] — that's what made me look closer at the [exact role title] req at [Company].
>
> At Walmart Data Ventures my autonomous Jira-resolution agent closed 400+ data requests and cut turnaround from 30–60 minutes to under 10 for each ticket. [Optional beat 3 if real: I'm in active processes at [Company A] for [Role] and at [Company B] for [Role], however [Company]'s [specific JD detail tied to their work] is the closer match.]
>
> I'd like to start the interview process. Are you the right person to talk to, or can you point me to the recruiter who owns this req?
>
> Best,
>
> Kanu
>
> ---
> Kanu Madhok
> madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok
> Live demo: [URL]

### Hook research — what to put in "[specific thing about them]"

Before sending, look at their LinkedIn for: a post they wrote, a talk they gave, a project they led, a paper they published, a company milestone they were named in. Even one specific reference makes the difference between "form letter" and "this person actually looked at me."

### Length target

50–125 words (target ~100). HMs and peer ICs skim harder than recruiters — be tight.

---

# 4a. Cold HM / peer IC — follow-up drip

> **Standalone follow-up cadence — NOT used by the jd-to-ready pipeline.** The pipeline ships ONE intro email per top pick (no follow-ups). The FU1 / FU2 / Hail-Mary templates below are for MANUAL, silence-triggered sends only.

Same cadence as Section 1a. Manual use only. Reply to the original thread.

### Follow-up 1 — send 3–4 business days after intro if silent

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Following up on the [role title] req. The Jira agent (400+ tickets, 30–60 min → under 10) is the closest analogue to what your team is doing on [specific thing — their project / the JD's main capability].
>
> Worth a 15-min chat, or should I route to the recruiter?
>
> Best,
>
> Kanu

≤ 60 words.

### Follow-up 2 — send 4–5 business days after FU1 if still silent

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Wanted to circle back. Open to a quick chat, or should I take this to the recruiter?
>
> Best,
>
> Kanu

≤ 40 words.

### Hail Mary — send only when fresh urgency arises

> **Subject:** Re: [same as intro]
>
> Hi [First name],
>
> Quick update — I have onsites with [Company A] and [Company B] [timing] and wanted to give [Company] a shot before timelines harden. If there's interest on your end, happy to do a phone screen this week and a technical loop while I'm already in [city] / available.
>
> Best,
>
> Kanu

~80 words.

---

# 5. Post-interview thank-you (per panelist)

**When to use.** After every panel interview. **One per panelist**, sent within 24 hours of the interview ending — same-day if possible.

**Channel.** Email if I have it (recruiter usually shares); LinkedIn if not.

### Template

> Hi [First name],
>
> Thank you for the time today — I enjoyed our conversation about [specific topic they raised that I want to plant again].
>
> [One-sentence callback to something they said + one-sentence follow-up that adds value or shows I kept thinking about it. Not generic.]
>
> Looking forward to next steps. Happy to share anything else that'd help.
>
> Best,
> Kanu

### Examples of good middle-paragraph callbacks (from the Walmart panel pre-built bench)

- *"You asked how the orchestrator handles disagreement at scale — I kept thinking about it after the call, and the part I didn't say clearly is that the review queue is partitioned by domain ownership, so the governance burden doesn't centralize on one product team."*
- *"Your point about quiet automation being more interesting than visible automation stuck with me — that's how I'd been undersignaling the Jira agent internally, and it's something I'll change in how I describe the work."*
- *"Appreciated you pushing on the 'why move from Walmart' question. The cleanest answer I gave you was 'scoped to one team vs. Walmart scale,' but the deeper one is that I want to build the framework that other people ship agents on top of, not just ship the agents — and that's the Agent Builder role specifically."*

### Don't

- Don't send identical messages to multiple panelists. They compare notes.
- Don't add 4 paragraphs of new content. The thank-you is warm and short — not a second interview.
- Don't ask "do you have any updates?" in the thank-you. Wrong forum.

---

# 6. Application follow-up — no response after N days

**When to use.** Submitted an application, no recruiter reach-out, ≥ 10 business days have passed. (Less than 10 = too early.)

**Channel.** LinkedIn to a recruiter if I can identify one for that req. Email to a generic careers inbox is mostly a void — only do it if there's no LinkedIn path.

### Template (to a specific recruiter)

> Hi [First name],
>
> I applied for the [role title] role at [Company] on [date]. Wanted to surface the application in case it's helpful — happy to share more on background, send a resume directly, or chat for 15 min if it makes sense.
>
> Short version: I'm a Senior Data Analyst at Walmart Data Ventures doing principal-level AI engineering — production agents (Jira automation, autonomous data analyst, hybrid orchestrator), and two productized AI skills inside Walmart's Claude Code fork.
>
> Best,
> Kanu Madhok
> madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok

### Length target

≤ 100 words. They didn't reply the first time; the second touch has to be even shorter.

---

# 7. Networking / mutual-connection ask

**When to use.** Someone in my network is at a company I'm targeting, or knows someone there. I want a warm intro.

**Channel.** LinkedIn DM or text if I know them well. Email if it's a more formal acquaintance.

### Template

> Hey [First name],
>
> Hope you're doing well! I'm looking at the [role title] role at [Company] — saw you're connected to [target person, if specific] / saw you spent some time there, and wanted to ask: would you be open to making a quick intro / sharing how you found the team?
>
> Happy to send a resume and a 2-line pitch you could forward if you'd rather pass it along than do the intro yourself.
>
> Either way — no pressure, appreciate you thinking about it.
>
> Best,
> Kanu

### The 2-line pitch (when forwarded)

> Kanu Madhok, Sr Data Analyst at Walmart Data Ventures doing principal-level AI engineering — production agents (Jira automation, autonomous data analyst, hybrid text-to-data orchestrator), two productized AI skills in Walmart's Claude Code fork. Resume + a live NL-to-SQL Copilot demo on request.

Keep the pitch ready to paste — friends doing intros don't want to write the pitch themselves.

### Don't

- Don't ask for an intro without offering to make it easy on them. The 2-line pitch is the courtesy.
- Don't follow up to a networking ask more than once. If they don't reply, they don't reply.

---

# 8. Decline / pause an outreach gracefully

**When to use.** A recruiter reaches out for a role I'm not pursuing right now, but I want to keep the relationship warm.

### Template

> Hi [First name],
>
> Thanks for reaching out about the [role title] role — I'm flattered you thought of me. I'm not actively looking right now / I'm in the late stages of another process / the timing isn't right, so I'm going to pass on this one.
>
> Would love to stay in touch — if anything else opens up at [Company] that you think I'd be a fit for, please keep me in mind. Easiest way to reach me is here or at madhok.kanu@gmail.com.
>
> Best,
> Kanu

### Why this matters

Recruiters move companies. The one I politely decline today is at a different company in 18 months. A warm "not now" outperforms a cold "no" or a ghost.

---

# Outreach tracker — quick log

Keep this updated as I send messages. Helps me remember who I've talked to and when to nudge.

| Date | To | Company / role | Channel | Type | Response? | Next action |
|---|---|---|---|---|---|---|
| 2026-05-07 | Ganna Volkova | BCG X / Sr AI Product Builder | Email | Post-screen thank-you | Yes, 23 min — "update next week" | Nudge by 2026-05-15 if silent |
| | | | | | | |

---

# Notes

- **Subject lines matter.** Keep them specific: "[Role title] at [Company] — quick note from Kanu Madhok" outperforms "Interested in opportunity." Names and roles in the subject line dramatically improve open rates from recruiters who get 200 InMails a week.
- **LinkedIn vs. email.** LinkedIn for first-touch cold outreach to people who don't know me; email for anyone I've already interacted with (recruiter screens, referrals from my network).
- **Timing.** Send Tue–Thu, late morning (~11 AM) or early afternoon (~2 PM) in the recipient's timezone — the most reliable open-rate window for cold recruiter/HM outreach. Avoid Mondays (inbox-triage day) and Friday afternoons (dead). Same-day thank-yous beat next-day ones. _[Reconciled 2026-05-31: prior version of this file said "Mondays 9–11 AM"; the inline jd-to-ready step-5 spec said avoid Mondays / Tue–Thu. Standardized on Tue–Thu. Kanu — confirm this is the rule you want, since it's now the single source for both the standalone `write-outreach` skill and the jd-to-ready pipeline.]_
- **The bench of hooks is the real moat.** The templates here change ~10% per send. The Walmart project list + the FTI capstone are what makes any hook specific. Update the project list in this file when I ship something new.
