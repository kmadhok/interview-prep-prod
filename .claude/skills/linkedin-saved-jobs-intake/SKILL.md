---
name: linkedin-saved-jobs-intake
description: Use this skill when the user pastes a block of jobs copied from their LinkedIn "Saved Jobs" page (linkedin.com/my-items/saved-jobs/) into their Interview Prep workspace and wants them filed in bulk. Each pasted entry is typically `Title \n Company · Location \n Posted Xh/d ago`. This skill (1) searches each job via the LinkedIn MCP to recover the canonical LinkedIn job URL + ID, (2) appends a row per job to root `Saved Jobs Export.md`, (3) creates a `Company - Role` folder for each new job, (4) fetches the full JD via WebFetch on the LinkedIn URL and writes it to `Job Description.md`, and (5) adds a row per new job to the `Considering / not yet applied` section of `Pipeline.md` under a dated subsection. Trigger on language like "here are my saved jobs", "intake my saved jobs", "file all of these", "bulk import these jobs", "pulled my saved jobs list", or when the user pastes 3+ LinkedIn-formatted job entries at once. Do NOT trigger for a single JD share (use `interview-prep-intake`) or when intent is apply-ready prep for one role (use `jd-to-ready`). Defaults: APPEND to `Saved Jobs Export.md` (cumulative across runs), SKIP jobs whose folder already exists (do not overwrite prior prep work).
---

# LinkedIn Saved Jobs — Bulk Intake

`<repo root>` = the directory containing `profile.yaml`; the workspace files live under `<repo root>/workspace/`.

This skill is the "I just exported my saved jobs from LinkedIn, file all of them" workflow. It composes three lower-level operations — LinkedIn MCP search, WebFetch on the canonical URL, and the existing intake-row pattern from `interview-prep-intake` / `jd-to-ready` — into one sequential batch.

Read the root `AGENTS.md` (or `CLAUDE.md`) in the Interview Prep workspace before starting. Workspace conventions live there and may have evolved since this skill was written. Folder naming, Pipeline.md row format, and the JD reading-copy structure all come from `interview-prep-intake` — reuse them, do not reinvent.

## Where things live

- Workspace root: `<repo root>/workspace/`
- Bulk export tracker: `workspace/Saved Jobs Export.md` (created on first run, appended thereafter)
- Role folders: `workspace/Roles/<Company - Role Title>/` (active/considering roles live under `workspace/Roles/`; closed roles in `workspace/_Archived/`)
- Per-role JD: `<role folder>/Job Description.md`
- Pipeline tracker: `workspace/Pipeline.md`

## What "saved jobs paste" looks like

A copy from `linkedin.com/my-items/saved-jobs/` typically renders one job as 3–5 lines:

```
Senior AI Engineer
Morgan Stanley · New York, NY
Reposted 12h ago

+3
Add note
Apply
```

Or for some listings:

```
Forward Deployed Engineer
HappyRobot · Chicago, IL (Hybrid)
Reposted 1d ago

Add note
Apply
```

Ignore the `+N`, `Add note`, `Apply` chrome lines. The data you need is **line 1 (title)**, **line 2 (company · location)**, and **line 3 (posted-ago string)**. Locations sometimes include a `(Hybrid)` / `(Remote)` / `(On-site)` suffix — preserve it. If the paste includes header chrome from the page itself (`Jobs / Connections / Notes`, `Saved · 34`, `In Progress · 18`, etc.), strip it before parsing.

## Workflow

Do these steps in order. Do not parallelize the LinkedIn MCP calls (see Rate-limit safety below). File writes and WebFetch calls CAN be parallelized after the MCP search phase is complete.

### 1. Parse the paste

Walk the pasted text and extract a list of `{title, company, location_raw, work_mode, posted_ago}` for each job:

- `title` = line 1, trimmed
- Split line 2 on ` · ` (middle-dot with spaces). Left = `company`. Right = `location_raw`.
- If `location_raw` ends with `(Hybrid)`, `(Remote)`, or `(On-site)`, peel it into `work_mode` and strip from `location_raw`.
- `posted_ago` = line 3 (e.g., "Reposted 12h ago", "Posted 6d ago"). Keep verbatim.
- If parsing yields fewer than 3 jobs or any line is ambiguous, surface the parse table to the user before continuing — better to confirm than guess.

Tell the user the count up front: "Parsed N jobs. Starting sequential LinkedIn MCP search."

### 2. Sequential LinkedIn MCP search per job

**Rate-limit safety — non-negotiable.** The `linkedin-mcp` maintainer (GitHub issue stickerdaniel/linkedin-mcp-server#351) confirmed: sequential is fine, parallel/loops trigger LinkedIn's automation detection and can warn or soft-ban the account. Do not parallelize `mcp__linkedin__search_jobs` calls across jobs. One job, one call at a time. Don't run the same query in a tight loop.

For each parsed job, call `mcp__linkedin__search_jobs` with:

- `keywords`: `"<title> <company>"` (concatenate, don't quote — LinkedIn search treats this as an OR-ish fuzzy match)
- `location`: extract a city from `location_raw` (e.g., "New York", "Chicago", "Seattle", "Remote"). For multi-city or `United States (Remote)`, use `"Remote"`. If the result set looks wrong, retry once with the city alone (drop the state).
- `max_pages`: `1` (more is wasteful — the right match is almost always in the first 10 results if it exists at all)

**Picking the right result:** From the returned `job_ids` / `references.search_results`, find the entry whose `text` ≈ the saved title AND whose company section matches the saved company (search the surrounding `search_results` text for the company name). Capture the numeric `job_id` and build the URL as `https://www.linkedin.com/jobs/view/<job_id>/`.

**If no clean match:** Try one fallback query with narrower keywords (e.g., just `"<company> <one-distinctive-word-from-title>"`). If that also fails, mark the job `[NOT FOUND]` and move on. Do not burn 3+ MCP calls per job — small employers, expired reqs, and reposts often genuinely won't surface, and the unmatched-URL path (paste from LinkedIn UI later) is fine.

### 3. Append rows to `Saved Jobs Export.md`

**Append mode.** If `Saved Jobs Export.md` exists, append a new dated subsection at the bottom. If it doesn't exist, create it with the header below.

File header (only on first creation):

```markdown
# LinkedIn Saved Jobs Export

**Source:** LinkedIn "Saved Jobs" — pulled via LinkedIn MCP (sequential, jittered)
**Method:** Each job searched by `title + company + location`; matched against company name in results.

Cumulative log — each `## Batch YYYY-MM-DD` subsection below is one bulk-intake run.

---
```

Per-run subsection:

```markdown
## Batch YYYY-MM-DD (N jobs)

| # | Title | Company | Location | Posted | LinkedIn URL | Folder | Status |
|---|-------|---------|----------|--------|--------------|--------|--------|
| 1 | <title> | <company> | <location_raw + work_mode> | <posted_ago> | <url or `[NOT FOUND]`> | <folder name> | New / **Skipped (folder exists)** |
| ... |
```

Use `YYYY-MM-DD` from the current date. Per-batch coverage summary (matched / not-found / skipped) at the bottom of the subsection.

### 4. Create role folders (skip if exists)

For each parsed job:

- Determine the folder name using the same rules as `interview-prep-intake` (Company - Role Title, drop punctuation that fights filesystems, shorten only when needed). Existing folders to match in style: `Walmart - Principal SWE Agent Builder`, `BCG X - Senior AI Factory Product Builder`, `Snorkel AI - Forward Deployed Engineer DaaS`, `Notion - Software Engineer AI Workflows`.
- If the folder already exists: **skip**. Do not overwrite `Job Description.md` (the user may have prep work in there). Mark the row Status = `Skipped (folder exists)` in the export file. Do not add a Pipeline row.
- If the folder is new: create it. Write a `Job Description.md` stub (header only) immediately so the folder isn't empty if WebFetch fails in step 5.

### 5. WebFetch the full JD per new folder

For each NEW folder (skipped ones don't get this step):

- If LinkedIn URL was captured in step 2: `WebFetch` the URL with a prompt like *"Extract full job description for <Company - Title>. Include role title, company, location, work model, salary, responsibilities, qualifications, tech stack, team context. Keep bullets verbatim."*
- If URL is `[NOT FOUND]`: write the stub JD with a `## URL — PASTE FROM LINKEDIN UI` placeholder and a `## Full JD (paste below)` block. Don't burn a WebFetch call on a known-bad URL.

**Parallel here is fine** — WebFetch calls are independent reads against LinkedIn's public job pages, not the gated Voyager API the MCP uses. Batch all WebFetches in a single tool-call message after step 2's sequential phase is done.

Use the JD body structure from `interview-prep-intake` (verbatim sections, drop ATS chrome, keep responsibilities/quals/comp). Header should include:

```markdown
# <Company> — <Role Title>

**Filed:** YYYY-MM-DD (via batch saved-jobs export)
**Source:** LinkedIn saved jobs
**LinkedIn URL:** <url or `[NOT FOUND — paste from LinkedIn UI]`>
**Location:** <location_raw> · <work_mode if any>
**Comp range:** <if WebFetch surfaced it, else "Not listed in posting">
**Posted:** <posted_ago>
```

### 6. Append rows to `Pipeline.md`

Open `Pipeline.md`. Find the `Considering / not yet applied` section. Just before the next `---` separator (the one that precedes `## Closed / On hold`), insert a new subsection:

```markdown
### Bulk-imported YYYY-MM-DD from LinkedIn saved jobs (JD bodies <captured | partial>)

_All rows below are bare intake stubs <or full JDs captured>. Before applying to any of them, review the folder's `Job Description.md`, then run `jd-to-ready`. Rows marked `[NOT FOUND]` need a manual URL pull from the LinkedIn UI._

| Role | Stage | Next action | Date | Contacts | Folder |
|------|-------|-------------|------|----------|--------|
| ... one row per NEW folder ... |
```

For each NEW folder (not skipped), add a row with:

- **Role**: `**<Company> — <Role Title> (<city or geo>)**`
- **Stage**: `Filed only — bulk import`
- **Next action**: Tactical note based on what WebFetch surfaced. Always include a geography flag if the role is on-site somewhere other than the user's home location (the user's timezone/region is in profile.yaml). For `[NOT FOUND]` rows, lead with **"URL not surfaced by MCP — paste from LinkedIn UI."**
- **Date**: `Filed YYYY-MM-DD; <posted_ago>`
- **Contacts**: `_TBD_`
- **Folder**: `[[<folder name>]]`

### 7. Report back

End-of-run summary, one short paragraph + a one-line tally:

- Tally: `Parsed N. Matched M. Skipped S (folder exists). Not found F.`
- Where the export file is (root `Saved Jobs Export.md`).
- Which folders are new and have full JDs vs. which need manual URL pulls.
- If any rows surfaced gates worth flagging at intake time (heavy travel, on-site-only geography, citizenship requirement), call them out — don't bury in the table.

Do not auto-run `jd-to-ready` or any per-role tailoring. Bulk intake stops at "everything filed, ready for the user to pick which ones to deepen."

## Rate-limit safety (read this)

LinkedIn's Voyager API (which the `linkedin-mcp` wraps) does not publish hard rate limits — the threshold is per-account and private. The MCP maintainer's stance:

> "Avoid repetitive patterns (loops, mass scraping) and normal use is fine. LinkedIn keeps the threshold private and it varies per account. They almost always show a warning prompt first if you trigger their automation detection, so you'll have a chance to back off before anything actually breaks."
> — stickerdaniel, linkedin-mcp-server#351

The mitigations baked into this skill:

1. **Sequential MCP calls only.** No parallel `search_jobs` across jobs in the same paste. The MCP's internal queue jitters them; let it.
2. **One search per job, one fallback at most.** Two queries × 20 jobs = 40 calls, spread over ~10–15 min. That's well within "normal use."
3. **No `get_job_details` calls.** WebFetch on the canonical URL gets the same JD without burning Voyager API budget.
4. **WebFetch is parallel-safe.** It hits LinkedIn's public HTML job pages, which has different (and looser) rate-limit behavior than the Voyager API.

If you ever see a LinkedIn warning prompt surface through the MCP, stop immediately, report it to the user, and don't retry for at least an hour.

## Edge cases and what to do

- **Paste includes non-job header chrome** (`Saved · 34`, `Jobs / Connections / Notes`, pagination "Previous / 1 / 2 / 3 / Next", `Not seeing some jobs?`): strip during parse.
- **Two jobs in the paste have the same `Company - Role Title`**: rare, but possible if a company has two reqs with identical titles in different cities. Disambiguate folder names with `(City)` suffix only when this collision happens. Don't add city suffixes preemptively.
- **A LinkedIn search returns multiple plausible matches** (e.g., "Sr AI Engineer" and "Senior AI Engineer" at the same company): prefer the one whose listing text shows the exact saved-line title.
- **WebFetch returns generic LinkedIn search results instead of a JD** (happens for expired/inactive req IDs — LinkedIn redirects stale URLs to a search page): treat that URL as `[NOT FOUND]`, downgrade the row, and write the stub JD with the URL placeholder. Do not retry. This usually means the req was closed between when the user saved it and when this skill ran.
- **The folder exists but is empty** (no `Job Description.md` inside): treat as new — write the JD, don't skip. Empty folder is leftover from an aborted run, not real prep work.
- **A "company" name is actually a recruiting agency** (Singular Recruitment, Riviera Partners, etc.): keep the agency as `Company` in the folder name. If the underlying client is disclosed in the JD body, capture both in the JD header (`Company: <agency>` + `Client: <client name>`). Otherwise note "Client not disclosed."
- **A pasted job is a duplicate of one already in the Pipeline's `Active` / `Applied` section** (the user re-saved a role they're already pursuing): treat as `Skipped (folder exists)`; do not add a Pipeline row; flag it in the report-back so the user knows they double-saved.

## What this skill does NOT do

- Does not run `jd-to-ready` on any role automatically. Bulk intake is filing, not prep.
- Does not write `Cold Outreach.md`, tailored resumes, or contact research. Those are per-role decisions the user makes after triage.
- Does not update `active_interview_pipeline.md` auto-memory unless a role moves out of `Filed only — bulk import` (and at that point the per-role intake / `jd-to-ready` skills handle it).
- Does not regenerate `Pipeline.html`. The user regenerates that manually or via the `.claude/render_pipeline.py` script.
