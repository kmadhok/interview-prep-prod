---
name: verify-postings
description: Verify whether the not-yet-applied job postings in the user's `Pipeline.md` are still live, and grade each LIVE / DEAD / UNVERIFIED. Trigger whenever the user asks to check if their postings/jobs are still active, still open, still accepting applications, or "did these close" / "are these still live" / "verify my pipeline postings" / "which of these are dead". Runs a deterministic script for company ATS pages, then a sequential LinkedIn MCP worklist for LinkedIn-sourced roles. Do NOT trigger for filing a JD (interview-prep-intake), the apply-ready pipeline (jd-to-ready), or finding NEW jobs (find-fresh-jobs).
---

# Verify Postings

A repeatable workflow to check whether the user's not-yet-applied pipeline roles are still worth spending time on. The core insight: live roles are verified by finding them in a reliable source; dead roles are often verified by failing to find them against a live backdrop where the company is clearly still posting other roles.

The bundled script handles the deterministic part: company ATS and job pages that can be fetched over HTTP. LinkedIn-sourced roles need authenticated LinkedIn MCP calls, so the script emits a stable, ordered worklist for those.

## When this fires

Use this skill when the user asks whether roles in `Pipeline.md` are still live, still open, still accepting applications, closed, dead, stale, or worth applying to.

Good trigger examples:

- "verify my pipeline postings"
- "which of these are dead"
- "are my saved jobs still live"
- "did these close"
- "check if the not-yet-applied jobs are still active"

## Do NOT use when

- the user shares a fresh JD and wants it filed into the workspace -> use `interview-prep-intake`.
- the user wants the full apply-ready package for a role -> use `jd-to-ready`.
- the user wants to find NEW jobs that match their target profile -> use `find-fresh-jobs`.
- the user asks for prep material for an interview already in motion -> use the normal role-folder prep workflow.

## Workflow

1. Run the script:

   ```bash
   python3 <SKILL_DIR>/scripts/verify_postings.py
   ```

   `<SKILL_DIR>` resolves to the `verify-postings` skill folder. The script prints Tier 1 verdicts that are already resolved, plus Tier 2 and Tier 3 MCP worklists.

2. Execute the Tier 2 worklist: run each `mcp__linkedin__get_job_details(...)` call ONE AT A TIME. Never parallelize LinkedIn MCP calls; this is the `linkedin-mcp-operations` invariant. A result showing "Reposted", "Actively reviewing", or "Apply" means LIVE. An error, empty result, removed page, or unavailable posting means DEAD.

3. Execute the Tier 3 worklist: run each `mcp__linkedin__search_jobs(...)` call ONE AT A TIME. If the company's own posting for that title appears, mark it LIVE, capture the job id, and backfill it into the role's `Job Description.md` so the next run routes it into Tier 2. If it does not appear but the company is clearly posting OTHER roles, mark it probable DEAD. Absence against a live backdrop is the dead signal.

4. Grade confidence. HTTP 404, HTTP 410, or page text like "no longer accepting" is CERTAIN dead. Absence-from-search is PROBABLE dead. Keep that distinction in the report.

5. Fold results back into `Pipeline.md`: move CERTAIN-dead roles to "Closed / On hold" and move their folders to `_Archived/`; flag PROBABLE-dead roles in place with a note like "LinkedIn shows no live posting — verify on company site". Always confirm with the user before archiving.

6. Report a tight summary table to the user: LIVE / DEAD / UNVERIFIED, with the highest-fit live roles called out first.

## Why a pure script can't do all of it

LinkedIn job pages need authenticated browser scraping, and only the LinkedIn MCP reaches them. The MCP also cannot be driven from a standalone Python process. More importantly, "closed" is often inferred from absence, not a clean HTTP status. So the script owns the deterministic ATS tier and generates a stable, ordered worklist for the LinkedIn tier.

## Key files

- `.claude/skills/verify-postings/scripts/verify_postings.py` — stdlib-only Python 3.11+ verifier; no external dependencies.
- `Pipeline.md` — source of truth for role rows and sections.
- `Roles/<Company - Role>/Job Description.md` — source for captured LinkedIn, ATS, or company job URLs.
