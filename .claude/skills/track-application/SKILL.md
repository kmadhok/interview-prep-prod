---
name: track-application
description: Update Pipeline.md with a new application status, add notes from recruiter conversations, or log key dates. Use when the user wants to log that they applied, got a screen, moved to next round, or closed a role.
---

# Track Application

`<repo root>` = the interview-prep repository root; workspace files live under `<repo root>/workspace/`.

Keep `workspace/Pipeline.md` accurate and up to date. Single-behavior primitive — no modes.

## Contract

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `company` | yes | Company name (matches the Pipeline row). |
| `role` | yes | Role title. |
| `status` | yes | One of the status values below. |
| `notes` | no | Date, recruiter name, format intel, next steps. |

**Outputs**
| What | When | Where |
|------|------|-------|
| Updated/added row | always | `workspace/Pipeline.md` (in place) |
| Format intel | when provided | project memory (survives sessions) |

**Standalone:** `track-application(company, role, status, notes?)`
Callable by other skills the same way (e.g. after an application is submitted).

## Inputs needed
- Company and role name
- New status (Applied, Phone Screen, Technical, Offer, Closed, etc.)
- Any notes (date, recruiter name, format intel, next steps)

## Process
1. Read current `workspace/Pipeline.md`.
2. **Applied transition:** use the deterministic tool — it moves the row Considering → Active and composes the stage cell (do not hand-edit for this case):
   ```bash
   python3 "<repo root>/scripts/pipeline_row.py" mark-applied --pipeline "<repo root>/workspace/Pipeline.md" --company "<Company>" --role "<Role>" --date <YYYY-MM-DD> --via "<ATS/referral/etc>"
   ```
   Exit 3 = no Considering row (add one first or hand-place directly in Active); exit 4 = already Applied (report, don't force).
3. **All other status changes** (Recruiter Screen, Technical, Offer, Closed…): find the matching row and update status + notes in place by hand — these carry free-form notes the tool doesn't model.
4. If the role doesn't exist yet, add a new row (trigger `interview-prep-intake` if a full folder setup is needed).
5. Save format intel to project memory so it survives across sessions.

## Status values
- `Considering` — identified but not yet applied
- `Applied` — submitted application
- `Recruiter Screen` — call scheduled or completed
- `Technical / Case` — technical or case round
- `Final Round` — onsite or final panel
- `Offer` — offer received
- `Closed` — withdrew, rejected, or ghosted
