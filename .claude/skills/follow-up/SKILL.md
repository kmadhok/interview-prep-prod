---
name: follow-up
description: Draft a follow-up message after an interview, application, or recruiter silence. Use when the user wants to send a thank-you, nudge a ghosted recruiter, or check on application status.
---

# Follow-Up

`<repo root>` = the interview-prep repository root; workspace files live under `<repo root>/workspace/`.

Draft timely, on-brand follow-up messages. Single-behavior primitive — no modes. Kept separate from `write-outreach` (distinct trigger surface + distinct templates: sections 2/3/5/6 of `workspace/Outreach Templates.md`, not 1/1a/4/4a).

## Contract

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `situation` | yes | One of the context types below (post-interview / nudge / post-screen / application follow-up). |
| `timing` | yes | When was last contact — drives the 48h rule and one-nudge-max. |
| `contact` | yes | Name + role for personalization. |
| `topic` | no | Specific thing discussed (for interview thank-yous). |

**Outputs**
| What | When | Where |
|------|------|-------|
| Drafted follow-up message (≤100 words) | always | returned to chat; never auto-sent |

**Source of truth:** `workspace/Outreach Templates.md` sections 2/3/5/6 (the follow-up/thank-you/nudge templates).

**Standalone:** `follow-up(situation, timing, contact, topic?)`

## Context types

| Situation | Template to pull |
|-----------|-----------------|
| Post-interview thank-you | `post-interview thank-you` from `workspace/Outreach Templates.md` |
| Nudge after recruiter silence | `nudge-after-silence` |
| Post-screen thank-you | `post-screen thank-you` |
| Application follow-up | `application follow-up` |

## Process
1. Confirm the situation and timing (when was last contact?).
2. Pull the matching template from `workspace/Outreach Templates.md`.
3. Personalize: interviewer name, specific topic discussed, role title.
4. Keep it under 100 words — follow-ups should be brief.
5. Confirm with the user before sending.

## Rules
- Don't follow up within 48 hours of an interview unless the interviewer asked you to.
- One nudge max before moving on.
- No passive-aggressive language about silence or delays.
