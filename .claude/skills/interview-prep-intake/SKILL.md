---
name: interview-prep-intake
description: Use this skill whenever Kanu Madhok pastes, links, attaches, or shares a job description (JD) he wants filed into his Interview Prep workspace at `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/`. The skill creates the `Company - Role` subfolder, writes `Job Description.md`, adds a row to root `Pipeline.md`, and updates the auto-memory `active_interview_pipeline.md`. Trigger on explicit intake language ("add this to my pipeline", "intake this JD", "track this role", "create a folder for this job", "save this JD", "file this role") AND on bare JD shares inside Interview Prep when intent looks like saving/tracking. Do NOT trigger when the user wants cold outreach drafting, recruiter lookup, or cold-email writing — that is the `job-outreach` skill. If both could apply and the user is ambiguous, ask whether they want to file, draft outreach, or both before invoking either skill.
---

# Interview Prep — JD Intake

This skill takes a job description Kanu has shared and files it into his Interview Prep workspace using the conventions documented in that workspace's `CLAUDE.md` / `AGENTS.md`. It is the boring-but-load-bearing first step before any deeper prep happens.

Read the root `AGENTS.md` (or `CLAUDE.md`) in the Interview Prep folder before you start — the workspace conventions there are the source of truth and may have evolved since this skill was written. The steps below are the workflow as of when this skill shipped.

## Where things live

- Workspace root: `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/`
- Role folders: `<workspace root>/<Company - Role Title>/`
- Pipeline tracker: `<workspace root>/Pipeline.md` (rendered copy at `Pipeline.html`)
- Auto-memory file for the active pipeline: `active_interview_pipeline.md`, in the memory directory listed in your system prompt (it lives under `Library/Application Support/Claude/.../spaces/<space-id>/memory/`). Don't hardcode the full path — read it from the system prompt for the current session, since the session-scoped part of the path can vary.

If the user is in a different workspace and you can't find this structure, ask before assuming. Don't create the workspace from scratch.

## Workflow

Do these steps in order. Most JDs go through all of them in under a minute. Don't pepper the user with questions — make sensible defaults and offer fixes at the end.

### 1. Parse the JD

Pull these fields from the JD (paste, file, or URL — fetch URLs, read PDFs):

- **Company name** — the actual employer. **Check who is actually hiring**, not just the words in the role title. Postings often have a misleading title (e.g., "Anthropic Forward Deployed Engineer" was a *Deloitte* role using the Anthropic stack, not an Anthropic-the-company role). The apply URL's domain (`apply.deloitte.com` → Deloitte), the "About / The Team" section, and any legal-entity footer ("As used in this posting, 'X' means…") are the giveaways. When the title names a vendor/tool but the employer is someone else, capture it as `<Employer>` and note the tech-stack framing separately.
- **Role title** — exactly as the company writes it (e.g., "Forward Deployed Engineer - Data as a Service")
- **Location(s)** — cities + remote/hybrid/onsite + any travel % requirement (travel % is easy to miss and matters a lot for some of these roles)
- **Compensation** — base, OTE, equity, bonuses if listed
- **Key requirements** — years required, must-have tools (Python, SQL, ML, LLMs, cloud, etc.), level signals
- **Team / org context** — what team the role sits on, why the team exists if mentioned
- **Hard gates** — surface anything that could be an outright disqualifier *before* prep starts: US citizenship requirement, security clearance requirement ("ability to obtain"), no-sponsorship clauses, mandatory in-office cadence, heavy travel %, hard-required certifications. These belong in their own "Notes for Kanu" callout (see step 3) and in the report-back (step 6) so Kanu notices them before investing time.
- **Source** — URL if given, otherwise note "Pasted by user on YYYY-MM-DD". If a requisition / job-ID number is in the posting, capture it — it makes the application step easier later.

If something isn't in the JD, mark it `_Not listed_` rather than invent it.

#### Trim boilerplate

Job postings — especially on ATS platforms like Workday, Greenhouse, Deloitte's careers site, etc. — come wrapped in a lot of chrome that isn't part of the job description proper. Drop it. Examples of what to drop:

- Social share buttons / "Share this job with…" blocks
- "Caution against fraudulent job offers" / scam-alert warnings
- "Recruiting tips" or "Benefits" or "Life at <Company>" generic marketing paragraphs that link out
- "Our people and culture", "Our purpose", "Professional development" boilerplate at the bottom — unless the JD substantively customizes them for the role
- Legal entity footers and "Deloitte means Deloitte Consulting LLP, a subsidiary of…" notes — capture the legal entity once in the header, then drop
- Generic EEO / accommodation paragraphs at the very end

Keep the substantive sections verbatim: position summary, "Work you'll do" / role overview, responsibilities, qualifications (required + preferred), compensation, "Why join" if it has actual role-specific content. The goal is a clean reading copy that Kanu can scan in 60 seconds — not a regurgitation of the ATS page.

### 2. Decide the folder name

Pattern: `Company - Role Title`. Keep it readable; shorten the role only if it would otherwise become an unwieldy folder name. Existing folders are the reference style:

- `Walmart - Principal SWE Agent Builder` (shortened from "Principal Software Engineer, Agent Builder")
- `BCG X - Senior AI Factory Product Builder` (kept as-is)
- `Snorkel AI - Forward Deployed Engineer DaaS` (shortened from "Forward Deployed Engineer - Data as a Service")

Rules:
- Drop punctuation that fights filesystems (commas, slashes, parens).
- Use clean abbreviations only where they're obvious in context ("SWE" for Software Engineer, "DaaS" for Data as a Service). When in doubt, keep the long form.
- Don't include location, salary, or req IDs in the folder name.
- If a folder with that name already exists, do NOT overwrite — see edge cases below.

### 3. Write `Job Description.md` inside the new folder

Use this structure. Omit sections that don't apply. Keep the content faithful to the JD — this file is a clean reading copy, not a summary, and not editorialized.

```markdown
# <Role Title>

**Company:** <Company>
**Locations:** <Locations>
**Compensation:** <Comp range, OTE, equity>
**Source:** <URL, or "Pasted by user on YYYY-MM-DD">

---

## About <Company>

<Verbatim "About the company" section if the JD provides one>

## About the Role

<Verbatim role overview / "About the Role" section>

## Main Responsibilities

<Sub-headings if the JD uses them, bullets otherwise>

## What We're Looking For

<Verbatim requirements list>

## Compensation

<Verbatim comp paragraph, including equity note>

## Why Join

<The company's pitch / "Why join" section, if provided>
```

Markdown niceties (headers, bullets, **bold** on key phrases) are fine. Don't paraphrase whole sections — keep the JD's language so Kanu can pattern-match to it later.

#### Optional: Notes for Kanu

If the JD contains anything Kanu should notice before deciding to apply — hard gates (citizenship, clearance, no sponsorship, mandatory travel %, RTO/in-office cadence), title-vs-employer mismatches, unusual compensation structures, atypical interview process hints, or anything else that materially shapes the apply/no-apply decision — append a `## Notes for Kanu` section at the bottom of `Job Description.md`. This is the only section where editorializing is fine; everything above it stays faithful to the source.

Keep it tight: 3–6 bullets, each a single sentence. Don't pad with "this is exciting!" filler — Kanu is reading this to make a decision, not to be sold to. If there's nothing flag-worthy beyond the JD itself, skip this section entirely.

### 4. Update `Pipeline.md`

Read the current `Pipeline.md`. The sections are:

- **Upcoming this week** — bulleted callouts for imminent interviews. Only touch if a date is already locked.
- **Active** — table of roles currently in process (applied / recruiter screen / interviewing).
- **Considering / not yet applied** — table for roles Kanu is evaluating but hasn't applied to yet.
- **Closed / On hold** — terminal states.

**Default placement: `Considering / not yet applied`.** Only put a new row directly into **Active** if Kanu has clearly said he's already applied, is in a recruiter screen, or has an interview booked.

Row format (match the existing rows — column order matters because `Pipeline.html` is rendered from this):

```
| **<Company> — <Role>** | <Stage> | <Next action> | <Date> | <Contacts> | [[<Folder name>]] |
```

Sensible defaults for a new `Considering` row:

- **Stage:** `Considering — JD reviewed, not yet applied`
- **Next action:** `Decide whether to apply; if yes, tailor resume + draft cold outreach (try job-outreach skill)`
- **Date:** `Posted role; no deadline captured` — unless a deadline is in the JD
- **Contacts:** `_TBD — recruiter/HM lookup pending_`
- **Folder:** `[[<Company - Role Title>]]` (Obsidian wiki-link; must match the folder name exactly)

Also update the `_Last updated: YYYY-MM-DD_` line near the top of `Pipeline.md` to today's date.

If `Pipeline.html` exists, it is now stale. **Do not regenerate it silently** — mention this in your final report so Kanu can ask for a regeneration if he wants one.

### 5. Update the auto-memory

Open `active_interview_pipeline.md` in the auto-memory directory (path is in your system prompt). It is a project-type memory listing the roles Kanu is currently prepping for.

Append a new numbered bullet under the existing list (or update an existing one if this role is already in there). Match the existing style:

- Lead with role name and company in bold.
- State the current status clearly ("Considering, not yet applied" / "Recruiter screen scheduled" / etc.).
- One line on what's distinctive about this role — tech stack, level, comp band, framing ("founding member of X team", etc.). This is the hook future-you uses to recognize the role at a glance.
- Note the date it was added if it's new.

Don't bloat the file. Each entry should fit comfortably on a screen.

Also update the description/header timestamp ("as of YYYY-MM-DD") if it's stale.

### 6. Report back

Keep the recap short. Kanu just pasted the JD — he knows what's in it. He wants to see that it landed correctly and what comes next.

Include:

- A `computer://` link to the new `Job Description.md`.
- A `computer://` link to the updated `Pipeline.md`.
- One line noting the memory was updated.
- A line about `Pipeline.html` being stale (ask if he wants it regenerated).
- **Surface any hard gates from step 1 right here, by name.** Don't bury them in the JD file and assume Kanu will scroll. If the role requires citizenship, clearance, no-sponsorship, heavy travel, or a hard cert, name it explicitly in the report and ask the disambiguating question (e.g., "this requires US citizenship + clearance eligibility — is that a blocker for you?"). Better to ask one direct question than to spin up tailored-resume work for a role he can't take.
- If there was a **title-vs-employer mismatch** worth flagging (the role title names a vendor/tool but the employer is someone else), say so in one line — "Note: posted as 'Anthropic FDE' but the employer is Deloitte" — so Kanu doesn't carry a wrong mental model into prep.
- A short suggestion for the natural next step — usually: tailor resume for this role, run the `job-outreach` skill if he wants to apply, or build out the full prep artifact set if an interview gets scheduled.

Don't restate the full JD or write a 12-section summary. Don't pad with motivational fluff.

## Edge cases

- **Folder already exists.** Don't overwrite. Tell Kanu the folder is there, ask whether he wants to refresh the JD in place, save as a variant (e.g., `Job Description - v2.md`), or skip.
- **Ambiguous role title or multi-role JD.** Ask which role he means before creating the folder. Renaming a folder later is messy because the wiki-link in `Pipeline.md` has to change too.
- **No company name / generic recruiter listing.** Ask for the company. Don't file under "Confidential" or a placeholder — it'll lose context.
- **Internal mobility (role at Walmart Data Ventures).** Flag it as internal in the memory entry. The prep approach differs (he can talk to people internally, has insider context, may face different format).
- **JD already applied / interview already booked.** Put the row in **Active** instead of **Considering**, and update the memory entry to reflect the current stage. If an interview date is set, also add a bullet under **Upcoming this week** if it falls within the next 7 days.
- **JD is for a role outside Kanu's current focus areas** (data, AI, AI engineering, product engineering, AI strategy/ops). Still file it — judgment about fit is his, not yours — but don't editorialize.

## Voice for memory and tracker entries

These files are for future-you and future-Kanu to scan in seconds. Be specific and concrete:

- Bad: "Senior engineering role at a startup."
- Good: "FDE role at Snorkel AI's DaaS org; Python/SQL + LLM eval + synthetic data + HITL pipelines; $172–300K OTE; positioned as founding member of technical DaaS team."

Quantified comp, distinctive tech-stack hooks, and the "why this role is special" framing carry the load.
