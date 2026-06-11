---
name: write-outreach
description: Draft cold outreach (email / LinkedIn / InMail) for a recruiter, hiring manager, or referral about a specific role. Use when Kanu wants to cold-message someone, or when jd-to-ready needs the Cold Outreach.md drip drafted. Single message standalone, or the full 4-email drip in pipeline use.
---

# Write Outreach

Draft targeted, voice-locked cold outreach. This is the one *executor* for outreach — `jd-to-ready` calls this skill instead of reimplementing the spec.

**Source of truth — don't restate it here.** The voice, the 5-beat body, the 50–125 word range, the subject-line formula, the 4-email drip cadence, the banned-phrase lists, and the Hail Mary all live in **`Outreach Templates.md`** (sections 1/1a = cold recruiter + drip; sections 4/4a = cold HM/peer-IC + drip). The research rationale lives in `Cold Outreach Emails Best Practices.md`. This skill executes: it picks the right template section, finds the hook, fills the beats from canonical facts, and writes the output. **`Outreach Templates.md` wins on any conflict** — there is no competing inline spec.

## Contract

**Modes:** `single` (default) | `drip`

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `contacts` | yes | `single`: one `{name, title, company, channel_confidence}`. `drip`: the two `top_picks` (#1 recruiter + #1 HM/peer-IC) from `find-contacts(full)`. |
| `role_title` | yes | Exact target role. |
| `company` | yes | Target company. |
| `archetype` | no | From jd-to-ready step 2; helps pick the lead achievement. |
| `lead_theme` | no | The JD's top theme; selects which canonical achievement anchors beat 2. |
| `urgency` | no | Competing-processes list, or the literal `none`. Drives beat 3. **Never fabricated** — if absent, omit beat 3. |
| `hooks` | no | Per-recruiter activity hooks from `enrich-contacts` — `{recruiter, hook_text, source, date, url}`. When present for a contact, it's a **real scraped post/repost** and takes top precedence as the beat-1 trigger (see hook-finding step). |
| `channel_confidence` | per contact | Email confidence from find-contacts; drives email-vs-InMail choice. |
| `mode` | yes | `single` (one message) or `drip` (4-email sequence per top pick). Default `single`. |
| `role_folder` | `drip` mode | `drip` writes `Cold Outreach.md` here. Also used in `single` mode to locate `<role_folder>/Verified Emails.md` for the Gmail draft — NOT hard-required for `single`: if unknown, the message still returns to chat and Gmail-draft creation is skipped with a `no-folder` gap. |

**Outputs**
| What | When | Where |
|------|------|-------|
| One drafted message (subject + body + signature, channel flagged) | `single` | returned to chat |
| `Cold Outreach.md` | `drip` | `<role_folder>/Cold Outreach.md` — role summary, urgency context, the two contact tables (passed through from find-contacts), a 4-email drip for each top pick (intro + FU1 + FU2 + Hail Mary = 8 drafts), and a Notes block (send timing, send order, reserves) |
| Gmail draft (Drafts folder, never sent) | `single` always; `drip` intro only | Gmail via `mcp__claude_ai_Gmail__create_draft`; To: from `<role_folder>/Verified Emails.md` |
| `gaps[]` | always | cross-skill schema `{source: "outreach", kind, detail}` — e.g. `{source:"outreach", kind:"no-hook", detail:"no specific hook found for <name>; asked Kanu"}`. Empty `[]` if none. |

**Standalone:** `write-outreach(contacts: {one person}, role_title, company, mode: single)`
**Pipeline (from jd-to-ready):** `write-outreach(contacts: top_picks, role_title, company, archetype, lead_theme, urgency, mode: drip, role_folder)`

## Process

1. **Pick the template section** from `Outreach Templates.md`: recruiter → sections 1/1a; HM or peer-IC → sections 4/4a. Follow that section's voice, beats, length, subject formula, and (in `drip`) the FU1/FU2/Hail-Mary cadence exactly.

2. **Find the hook** — it's the single biggest reply-rate driver. Precedence:
   0. **An `enrich-contacts` activity hook for this contact** → the strongest beat-1 opener you can get, because it's real and specific to *them*: "I saw you recently reposted the SFL Scientific AI Specialist Leader opening…". Use it verbatim as the trigger line when present. It cites a real scraped post, so never paraphrase it into something the recruiter didn't actually post.
   1. `lead_theme` → the matching canonical achievement from `Resume Achievements Master.md` (A1/A3/A4/A5/F1/U1) becomes beat 2, with its verified number.
   2. A JD-specific detail (practice area, stack item, customer segment) → beat 4 "why-this-company."
   3. The trigger line (beat 1) from context: applied → "I just applied for…"; job-board → "Found your post on…"; cold → "Saw [Company]'s [specific thing]…".

   If you can't find a real, specific hook, **ask Kanu for one detail** before drafting — never fabricate one. Record `{source:"outreach", kind:"no-hook", ...}` in `gaps[]` if you had to ask.

3. **Fill the beats from canonical facts only.** Numbers come from the canonical "verified proof points" (same discipline as `tailor-resume`). Beat 3 (urgency) appears ONLY if `urgency` is real — never invent competing processes.

4. **Choose the channel** per `channel_confidence`: High/Medium inferred email → email; Low / no email → LinkedIn InMail (drop the "Resume attached." line).

5. **`drip` mode:** write the full 4-email sequence per top pick (intro + FU1 + FU2 + Hail Mary) per `Outreach Templates.md` 1a/4a, then assemble `Cold Outreach.md` (role summary, urgency context, the two find-contacts tables, the two drips, Notes). `single` mode: write one message for the one contact.

6. **Save to Gmail draft** — runs only AFTER the Format check gate passes for the message in question; never draft from an unchecked message. Use `mcp__claude_ai_Gmail__create_draft` — it saves to the Drafts folder and sends nothing. This skill DRAFTS ONLY; never call any send tool.
   - **When:** `single` → always draft the one message (in addition to returning it to chat). `drip` → draft the INTRO email only; FU1/FU2/Hail Mary stay in `Cold Outreach.md` and are NOT drafted (they're conditional, silence-triggered sends).
   - **Subject / body / signature:** copy verbatim from the format-check-passed draft. Email channel only (InMail messages aren't Gmail).
   - **To: resolution** — read `<role_folder>/Verified Emails.md`, a `| Name | Email | Confidence |` table **written by `find-contacts(full)` step 4.5** (Apollo-verified top-pick emails; this skill only READS it). Match the contact's name against the `Name` column case-insensitively, tolerating minor whitespace; if a cell has a nickname in parens like "Allison (Allie) Brown", match on the full cell. Use that row's `Email` as To:. Prefer a `High`-confidence row; if the matched row is `Low`/inferred, still draft but record `{source:"outreach", kind:"low-confidence-recipient", detail:"<name>: To: is an inferred address; verify before send"}`.
   - **Fallback** — if `Verified Emails.md` doesn't exist, or the name isn't found, set To: = `madhok.kanu@gmail.com` and record `{source:"outreach", kind:"unverified-recipient", detail:"no verified email in Verified Emails.md for <contact name> — To: set to madhok.kanu@gmail.com; swap before send"}`. (Gmail's API needs at least one recipient — that's why the fallback uses Kanu's own address rather than an empty To:.)
   - **No `role_folder` in `single` mode** — skip Gmail-draft creation, still return the message to chat, and record `{source:"outreach", kind:"no-folder", detail:"no role_folder given — skipped Gmail draft; returned message to chat only"}`.
   - **Attachments** — `create_draft` can't attach files. If the body says "Resume attached." (cold/intro recruiter + HM templates do), record `{source:"outreach", kind:"manual-attachment", detail:"create_draft can't attach files — attach resume in Gmail before sending"}`.

## Format check (run before returning ANY draft)

Check every draft against `Outreach Templates.md` before returning it. This is a gate, not a suggestion — if any item fails, rewrite and re-check first.

- [ ] **Section match** — the right template section is used (recruiter → 1/1a; HM/peer-IC → 4/4a) and its beats/voice are followed.
- [ ] **Subject** — < 70 chars, leads with the credential (recruiter) or something specific to *them* (HM/peer-IC); `Re: [same as intro]` on every follow-up.
- [ ] **5-beat body** — beats 1, 2, 4, 5 present; beat 3 (urgency) present ONLY if `urgency` is real, omitted otherwise. Follow-ups carry only their designated beat (FU1 restates lead, FU2 nudges, Hail Mary adds urgency).
- [ ] **Length** — intro 50–125 words (target ~100); FU1 ≤ 60; FU2 ≤ 40; Hail Mary ~80. Count the words.
- [ ] **No banned phrases** — none of the banned openers ("I hope this email finds you well", "Just wanted to reach out", "I came across your profile", etc.) or hype words ("leverage", "spearhead", "synergy", "drove", "passionate", "rockstar", "ninja"). ("circle back" is allowed in FU2 only.)
- [ ] **Signature block EXACT** — cold/intro uses the full block (name · email · linkedin · github, + Live demo line where the template has it); warm/follow-up uses just `Best,` / `Kanu`. Match the template literally — don't paraphrase or reorder.
- [ ] **One CTA** — exactly one clear, low-friction ask per message.
- [ ] **Channel correct** — email vs. InMail chosen per `channel_confidence`; "Resume attached." line dropped on InMail.
- [ ] **No fabrication** — every hook, number, and competing-process is real and canonical; nothing invented.

## Hard rules
- `Outreach Templates.md` is the spec; this skill executes it and never overrides it.
- Length, banned-phrase, and subject rules come from that file — don't relax them.
- **No fabricated personalization or urgency.** If a hook or a competing process isn't real, omit it or ask.
- One clear ask / CTA per message.
- **Draft, never send — universal across channels.** This skill may create Gmail DRAFTS only (`mcp__claude_ai_Gmail__create_draft`, which saves to Drafts and sends nothing) and must never call any send tool. Same invariant as LinkedIn: confirm with Kanu before any `mcp__linkedin__send_message`. Across both channels this skill drafts; it doesn't send.
