# SANDBOX — Pipeline + Memory deltas (NOT applied to real files)

This is a TEST run. The real `Pipeline.md`, `Roles/`, auto-memory, and `saved_seen.json` were NOT modified. Below is exactly what intake (step 1) WOULD have written.

## Pipeline.md row (would append to "Considering / not yet applied")

```
| **Decagon — Senior Software Engineer, Agents** | Considering — JD reviewed, not yet applied | Resume ready — apply on the ATS; outreach auto-stages once the row is marked Applied. | Posted role; no deadline captured | _TBD — recruiter/HM lookup pending_ | [[Decagon - Senior Software Engineer Agents]] |
```

Also: update `_Last updated: YYYY-MM-DD_` near top of Pipeline.md to 2026-06-27.

## active_interview_pipeline.md memory entry (would append)

- **Senior Software Engineer, Agents — Decagon.** Considering, not yet applied (added 2026-06-27). NYC on-site, in-office company; $200K–$400K + equity. Agent Engineering team: customer-embedded delivery of production AI agents at enterprise scale (Cash App, Chime, Oura, etc.), eval on latest text/voice models. Strong agent-builder + evaluation fit on the work; main gate is the 5+yr industry-SWE bar (Kanu is analyst/agent-builder, not a 5-yr SWE) plus TypeScript depth and NYC on-site RTO.

## Notes
- Folder name that intake WOULD have used under real Roles/: `Decagon - Senior Software Engineer Agents`.
- `Pipeline.html` would be stale after the row append (not regenerated).

---

# stage-outreach (Orchestrator 2) — STAGE decision delta (2026-06-27)

_Run: stage-outreach test mode, trace run jdtr-20260627164845-53b7b674. NOTHING written to real Pipeline.md / Roles/._

## STAGE decision: NOT STAGED

No `STAGED in Gmail <date>` marker written (not to a folder marker, not to a Pipeline row). Reason: jd-to-ready flagged an UNCONFIRMED hard gate that persists:
- **Seniority/SWE bar:** JD requires "5+ years of industry experience in software engineering"; Kanu is Senior Data Analyst + agent-builder, not a 5-yr industry SWE. (Source: Job Description.md "Notes for Kanu"; .classification.json notes.)
- **On-site NYC (RTO gate):** Decagon is explicitly in-office; role is on-site NYC, not remote.

Per stage-outreach SKILL.md step 6 ("if present and unconfirmed, do not stage — leave the row un-STAGED and note it here") and Degradation section ("Unconfirmed hard gate flagged by jd-to-ready -> do not stage; leave the row un-STAGED until Kanu confirms"). Role stays eligible for re-staging after Kanu confirms.

## Artifacts produced (all in the test folder, sandboxed)
- `.contacts-ledger.md` (find-contacts step 4 + enrich-contacts step 4b)
- `Verified Emails.md` (verify-emails step 4c, EmailFinder.dev)
- `Cold Outreach.md` (write-outreach step 5, drip)
- Gmail DRAFTS (real, never sent, left in Drafts for Kanu):
  - Recruiter intro -> Hana Haitsuka · draft id `r-91809198562248941` · To: hana@decagon.ai (inferred — verify)
  - HM intro -> Katherine Xiao · draft id `r-1360240664783205423` · To (fallback): madhok.kanu@gmail.com (InMail recommended)

## Ordering observation (design issue)
LinkedIn scrape (steps 4/4b), EmailFinder credits (2, step 4c), and both Gmail drafts (step 5) were ALL spent BEFORE the hard-gate decision in step 6. Because the unconfirmed gate blocks staging, every outward action + the 2 credits were spent on a role that does not stage. See findings report for the full writeup.
