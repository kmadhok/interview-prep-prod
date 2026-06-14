---
name: write-outreach
description: Draft cold outreach (email / LinkedIn / InMail) for a recruiter, hiring manager, or referral about a specific role. Use when Kanu wants to cold-message someone, or when jd-to-ready needs the Cold Outreach.md drip drafted. Single message standalone, or two intro emails (recruiter #1 + HM/peer-IC #1) in pipeline use.
---

# Write Outreach

Draft targeted, voice-locked cold outreach. This is the one *executor* for outreach — `jd-to-ready` calls this skill instead of reimplementing the spec.

**Source of truth — don't restate it here.** The voice, the 5-beat body, the 50–125 word range, the subject-line formula, the body-prose em-dash gate, and the banned-phrase lists all live in **`Outreach Templates.md`** (sections 1 = cold recruiter intro; section 4 = cold HM/peer-IC intro). The follow-up cadence (sections 1a/4a — FU1/FU2/Hail Mary) is **archived/manual-only**: pipeline mode does NOT emit it. The research rationale lives in `Cold Outreach Emails Best Practices.md`. This skill executes: it picks the right template section, finds the hook, fills the beats from canonical facts, and writes the output. **`Outreach Templates.md` wins on any conflict** — there is no competing inline spec.

## Contract

**Modes:** `single` (default) | `drip` (pipeline)

> The mode name `drip` is **retained for caller compatibility** (jd-to-ready still passes `mode: drip`), but it no longer emits a multi-touch sequence. `drip` now means **pipeline mode — one intro email per top pick (2 total: recruiter #1 + HM/peer-IC #1), no follow-ups.**

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `contacts` | yes | `single`: one `{name, title, company, channel_confidence}`. `drip`: the two `top_picks` (#1 recruiter + #1 HM/peer-IC) from `find-contacts(full)`. |
| `role_title` | yes | Exact target role. |
| `company` | yes | Target company. |
| `archetype` | no | From jd-to-ready step 2; helps pick the lead achievement. |
| `lead_theme` | no | The JD's top theme; selects which canonical achievement anchors beat 2. |
| `urgency` | no | Competing-processes list, or the literal `none`. Drives beat 3. Default when not passed: **derive from `Pipeline.md` (live only)** via the freshness filter in Process step 3 — read live processes, never fabricate. If none survive the filter, omit beat 3. |
| `hooks` | no | Per-recruiter activity hooks from `enrich-contacts` — `{recruiter, hook_text, source, date, url}`. When present for a contact, it's a **real scraped post/repost** and takes top precedence as the beat-1 trigger (see hook-finding step). |
| `channel_confidence` | per contact | Email confidence from find-contacts; drives email-vs-InMail choice. |
| `mode` | yes | `single` (one message for one contact) or `drip` (pipeline: one intro email per top pick — 2 total, no follow-ups). Default `single`. Name `drip` kept for caller compatibility; it no longer emits a sequence. |
| `role_folder` | `drip` mode | `drip` writes `Cold Outreach.md` here. Also used in `single` mode to locate `<role_folder>/Verified Emails.md` for the Gmail draft — NOT hard-required for `single`: if unknown, the message still returns to chat and Gmail-draft creation is skipped with a `no-folder` gap. |

**Outputs**
| What | When | Where |
|------|------|-------|
| One drafted message (subject + body + signature, channel flagged) | `single` | returned to chat |
| `Cold Outreach.md` | `drip` | `<role_folder>/Cold Outreach.md` — role summary, urgency context, the two contact tables (passed through from find-contacts), **two intro emails (one per top pick: recruiter #1 + HM/peer-IC #1)**, and a Notes block (send timing, send order, **same-company double-send guard**, reserves) |
| Gmail draft (Drafts folder, never sent) | `single` (the one message); `drip` (**both intros — one per top pick**) | Gmail via `mcp__claude_ai_Gmail__create_draft`; To: from `<role_folder>/Verified Emails.md` |
| `gaps[]` | always | cross-skill schema `{source: "outreach", kind, detail}` — e.g. `{source:"outreach", kind:"no-hook", detail:"no specific hook found for <name>; asked Kanu"}`. Empty `[]` if none. |

**Standalone:** `write-outreach(contacts: {one person}, role_title, company, mode: single)`
**Pipeline (from jd-to-ready):** `write-outreach(contacts: top_picks, role_title, company, archetype, lead_theme, urgency, mode: drip, role_folder)`

## Process

1. **Pick the template section** from `Outreach Templates.md`: recruiter → section 1 (cold recruiter intro); HM or peer-IC → section 4 (cold HM/peer-IC intro). Follow that section's voice, beats, length, and subject formula exactly. In `drip` you write the **intro only** — the follow-up cadence (sections 1a/4a) is archived/manual-only and is NOT emitted by the pipeline.

2. **Find the hook** — it's the single biggest reply-rate driver. Precedence:
   0. **An `enrich-contacts` activity hook for this contact** → the strongest beat-1 opener you can get, because it's real and specific to *them*: "I saw you recently reposted the SFL Scientific AI Specialist Leader opening…". Use it verbatim as the trigger line when present. It cites a real scraped post, so never paraphrase it into something the recruiter didn't actually post.
   1. `lead_theme` → the matching canonical achievement from `Resume Achievements Master.md` (A1/A3/A4/A5/F1/U1) becomes beat 2, with its verified number.
   2. A JD-specific detail (practice area, stack item, customer segment) → beat 4 "why-this-company."
   3. The trigger line (beat 1) from context: applied → "I just applied for…"; job-board → "Found your post on…"; cold → "Saw [Company]'s [specific thing]…".

   If you can't find a real, specific hook, **ask Kanu for one detail** before drafting — never fabricate one. Record `{source:"outreach", kind:"no-hook", ...}` in `gaps[]` if you had to ask.

3. **Source beat-3 urgency LIVE from `Pipeline.md` (freshness-filtered).** Before drafting, if `urgency` wasn't passed (or to validate what was), read `Pipeline.md` and extract currently-live competing processes, applying this **freshness filter**:
   - Keep ONLY processes dated **today or in the future** (today = the current date).
   - Drop anything dated **before today**, and drop anything flagged `STALE`, `PASSED`, `CLOSED`, or `REJECTED`.
   - If **nothing survives** the filter, **omit beat 3 entirely** — do not stretch a stale process to fill it.
   - **Never fabricate or hardcode** a competing process; beat 3 is only ever populated from real, live Pipeline.md rows (or a real `urgency` input).

4. **Fill the beats from canonical facts only.** Numbers come from the canonical "verified proof points" (same discipline as `tailor-resume`). Beat 3 (urgency) appears ONLY if a real, freshness-passing process exists (per step 3) — never invent competing processes.

5. **Choose the channel** per `channel_confidence`: High/Medium inferred email → email; Low / no email → LinkedIn InMail (drop the "Resume attached." line).

6. **Write the drafts.** `drip` mode: write **ONE intro email per top pick (2 total: recruiter #1 + HM/peer-IC #1)** per `Outreach Templates.md` sections 1/4 — no follow-ups. Then assemble `Cold Outreach.md` (role summary, urgency context, the two find-contacts tables, the two intro emails, and a Notes block incl. send timing, send order, the **same-company double-send guard**, and reserves). `single` mode: write one message for the one contact.

7. **Human-writing pass (every draft).** Before the Format check, run each draft through the `human-writing` skill to strip hedging, buzzwords, and passive voice and make it read like Kanu actually talking. THEN run the Format-check gate below. Only a draft that has passed both the human-writing pass and the Format check is eligible for Gmail drafting.

8. **Save to Gmail draft** — runs only AFTER the human-writing pass AND the Format check gate pass for the message in question; never draft from an unchecked message. Use `mcp__claude_ai_Gmail__create_draft` — it saves to the Drafts folder and sends nothing. This skill DRAFTS ONLY; never call any send tool.
   - **When:** `single` → always draft the one message (in addition to returning it to chat). `drip` → draft **BOTH intros** (one per top pick: recruiter #1 + HM/peer-IC #1). There are no follow-ups to draft.
   - **Same-company double-send guard:** because both `drip` intros go to the same company, record `{source:"outreach", kind:"same-company-double-send", detail:"two cold drafts to <Company> (<recruiter> + <HM>); send at most one cold, or space them out"}` in `gaps[]`.
   - **Subject / body / signature:** copy verbatim from the format-check-passed draft. Email channel only (InMail messages aren't Gmail).
   - **To: resolution** — read `<role_folder>/Verified Emails.md`, a `| Name | Email | Confidence |` table **written by jd-to-ready step 4c** (the `verify-emails` script — EmailFinder.dev SMTP-verified top-pick emails; this skill only READS it). Match the contact's name against the `Name` column case-insensitively, tolerating minor whitespace; if a cell has a nickname in parens like "Allison (Allie) Brown", match on the full cell. Use that row's `Email` as To:. Prefer a `High`-confidence row; if the matched row is `Low`/inferred, still draft but record `{source:"outreach", kind:"low-confidence-recipient", detail:"<name>: To: is an inferred address; verify before send"}`.
   - **Fallback** — if `Verified Emails.md` doesn't exist, or the name isn't found, set To: = `madhok.kanu@gmail.com` and record `{source:"outreach", kind:"unverified-recipient", detail:"no verified email in Verified Emails.md for <contact name> — To: set to madhok.kanu@gmail.com; swap before send"}`. (Gmail's API needs at least one recipient — that's why the fallback uses Kanu's own address rather than an empty To:.)
   - **No `role_folder` in `single` mode** — skip Gmail-draft creation, still return the message to chat, and record `{source:"outreach", kind:"no-folder", detail:"no role_folder given — skipped Gmail draft; returned message to chat only"}`.
   - **Attachments** — `create_draft` can't attach files. If the body says "Resume attached." (cold/intro recruiter + HM templates do), record `{source:"outreach", kind:"manual-attachment", detail:"create_draft can't attach files — attach resume in Gmail before sending"}`.

## Format check (run before returning ANY draft)

Check every draft against `Outreach Templates.md` before returning it. This is a gate, not a suggestion — if any item fails, rewrite and re-check first.

- [ ] **Section match** — the right template section is used (recruiter → 1; HM/peer-IC → 4) and its beats/voice are followed.
- [ ] **Subject** — < 70 chars, leads with the credential (recruiter) or something specific to *them* (HM/peer-IC).
- [ ] **5-beat body** — beats 1, 2, 4, 5 present; beat 3 (urgency) present ONLY if a real, freshness-passing live process exists (Process step 3), omitted otherwise.
- [ ] **Length** — intro 50–125 words (target ~100). Count the words.
- [ ] **Body em-dash gate** — zero em dashes (` — `, U+2014) in the email BODY; subject lines may use the template's prescribed dash form.
- [ ] **No banned phrases** — none of the banned openers ("I hope this email finds you well", "Just wanted to reach out", "I came across your profile", etc.) or hype words ("leverage", "spearhead", "synergy", "drove", "passionate", "rockstar", "ninja").
- [ ] **Signature block EXACT** — cold/intro uses the full block (name · email · linkedin · github, + Live demo line where the template has it). Match the template literally — don't paraphrase or reorder.
- [ ] **One CTA** — exactly one clear, low-friction ask per message.
- [ ] **Channel correct** — email vs. InMail chosen per `channel_confidence`; "Resume attached." line dropped on InMail.
- [ ] **No fabrication** — every hook, number, and competing-process is real and canonical; nothing invented.

## Hard rules
- `Outreach Templates.md` is the spec; this skill executes it and never overrides it.
- Length, banned-phrase, and subject rules come from that file — don't relax them.
- **No fabricated personalization or urgency.** If a hook or a competing process isn't real, omit it or ask.
- One clear ask / CTA per message.
- **Draft, never send — universal across channels.** This skill may create Gmail DRAFTS only (`mcp__claude_ai_Gmail__create_draft`, which saves to Drafts and sends nothing) and must never call any send tool. Same invariant as LinkedIn: confirm with Kanu before any `mcp__linkedin__send_message`. Across both channels this skill drafts; it doesn't send.
