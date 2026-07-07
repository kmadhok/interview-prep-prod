---
name: find-fresh-jobs
description: Use this skill when the user wants a fresh batch of LinkedIn job listings to evaluate against their Job Search Target Profile. Surfaces N high-quality, recently-posted roles via the gated LinkedIn MCP, applies every filter in the Target Profile (geo-adjusted comp floor, seniority, hard-skip company list, archetype, leetcode-free preference, industry exclusions, post-read drop signals), dedupes against the current Pipeline so already-filed roles don't re-surface, and returns a compact evaluation-ready report. Defaults to N=10 jobs posted in the last 24 hours. Trigger language includes "find fresh jobs", "find me jobs", "pull jobs", "show me new jobs", "what's new on LinkedIn today", "run the job search", "morning job pulse", or any variant that asks for a batch of new listings to review. Args supported via natural language ("find me 5 jobs from the last 72h", "find me 15 fresh jobs"). Do NOT trigger when the user shares a single JD and wants it filed (use `interview-prep-intake`), wants the full apply-ready pipeline for one JD (use `jd-to-ready`), or wants to bulk-import jobs they already saved from LinkedIn (use `linkedin-saved-jobs-intake`). If ambiguous, assume they want the default (N=10, 24h) and run it.
---

# Find Fresh Jobs — LinkedIn morning pulse

This skill is the repeatable "what's new for me on LinkedIn today" pass. It surfaces a fresh batch of roles that match the user's `Job Search Target Profile.md`, applies every filter in that file, dedupes against `Pipeline.md`, and returns a compact report they can scan in under 60 seconds.

`<repo root>` = the directory containing `profile.yaml`; the workspace files live under `<repo root>/workspace/`. Read `AGENTS.md` / `CLAUDE.md` at `<repo root>/` first. Workspace conventions there override anything here on conflict.

## What this skill produces

A single compact report (under 600 words) in chat with:

- N job entries (default N=10), each with title, company, location, comp, leetcode risk, "why it fits" bullets, and the LinkedIn permalink
- A short "What I skipped and why" paragraph naming 2–3 dropped results so the user can sanity-check the filters
- A note flagging if the search window had to widen beyond 24h

This skill does NOT file roles, modify Pipeline.md, draft outreach, or apply. Those are separate skills (`interview-prep-intake`, `jd-to-ready`, `write-outreach`). The output is decision support only.

## Inputs (parse from the user's message)

- **N** — how many jobs to return. Default **10**. Override if the user says a number ("find me 5", "15 fresh ones", etc.)
- **Window** — how recent. Default **past 24 hours**. Override if the user says a window ("last 48h", "past 3 days", "this week")
- **Optional theme override** — if the user names a focus ("only data-agent stuff", "skip consulting", "FDE only"), apply it as a post-filter on top of the Target Profile

If parsing is ambiguous, run the default (N=10, 24h). Don't ask.

## Workspace paths (resolved once)

- **Workspace root:** `<repo root>/workspace/`
- **Target Profile (source of truth):** `Job Search Target Profile.md` at workspace root
- **Pipeline (dedupe source):** `Pipeline.md` at workspace root
- **LinkedIn MCP discipline skill (required):** `linkedin-mcp-operations` — invoke via Skill tool BEFORE any `mcp__linkedin__*` call. Enforces the http-transport invariant, sequential-call rule, and diagnostic ladder.

## Workflow

Steps 1 → 6 in order. Don't ask clarifying questions mid-flow — make reasonable judgment calls and surface them in the final report.

### Step 1 — Load the source of truth

Read `Job Search Target Profile.md` in full. Capture:

- **Search query bank** — the literal query strings, ordered Tier 1 → Tier 4
- **Seniority** — Senior / Staff / Principal IC; skip Manager/Director/Junior
- **Geo** — SF, NYC, LA, Chicago, Remote-US
- **Geo-adjusted comp floor** — currently NYC/SF/LA ≥ $170k base; Chicago/Remote/lower-COL ≥ $140k base. Read the actual file values — they may have been tuned.
- **Company size bands** — <200 strong pull; 200–2,000 acceptable; 2,000–50,000 only if FDE/Applied/Solutions/Agent Builder; >50,000 skip unless explicit FDE title
- **Hard-skip company list** — current: Google, Meta, Amazon, Apple, Microsoft, Databricks, Snowflake, Stripe, Airbnb, Two Sigma, Citadel, Jane Street. Exception: title contains "Forward Deployed" / "Applied AI" / "Solutions Engineer" explicitly → read JD before skipping.
- **Always-look company list** — for `get_company_jobs` direct passes if title-search is thin
- **Industry exclusions** — defense, crypto-only, adtech, gambling, tobacco
- **Post-read drop signals** — model training, research scientist, manager track, leetcode tells, dbt/Spark pipeline-only, generic SWE

Always re-read the file — don't cache. The user tunes it.

### Step 2 — Load the dedupe set (Pipeline.md only)

Read `Pipeline.md`. Extract every role already filed (company + role title pairs, and any LinkedIn URLs present). These are the dedupe set — do not re-surface them in the final report regardless of how strong the match is.

Dedupe is **against `Pipeline.md` only**. This skill does NOT keep its own memory of past pulses — re-runs on the same day may legitimately surface the same fresh job twice if it's still unfiled. That's intentional; the Pipeline is the single source of truth for "already considered."

### Step 3 — Invoke the LinkedIn MCP discipline skill

Before any `mcp__linkedin__*` call, invoke `linkedin-mcp-operations` via the Skill tool. Honor it for every subsequent call:

- Sequential only — one MCP call at a time, never parallel
- Jitter between calls
- If a call fails, follow the skill's diagnostic ladder (don't kick the daemon by hand)
- If the daemon isn't up, surface that to the user and stop — don't work around it

### Step 4 — Run the search

Run Tier 1 queries first, sequentially. Suggested first pass (in this order):

1. `"Forward Deployed Engineer"`
2. `"Applied AI Engineer"`
3. `"AI Solutions Engineer"`

Use `mcp__linkedin__search_jobs` with `date_posted` mapped to the requested window (default: past 24 hours — check the tool schema for the exact enum, typically `r86400` for 24h, `r259200` for 72h, etc.).

For each query, collect raw results and apply this pre-filter ladder in order:

1. **Posted-in-window** — drop anything older than the requested window (hard)
2. **Geo** — must be SF / NYC / LA / Chicago / Remote-US
3. **Seniority** — Senior / Staff / Principal IC only
4. **Hard-skip company** — drop unless title contains the FDE/Applied/Solutions exception
5. **Industry exclusion** — drop defense / crypto-only / adtech / gambling / tobacco
6. **Pipeline dedupe** — drop anything already in Pipeline.md
7. **Theme override (if the user provided one)** — drop anything that fails it

**Widening logic.** After running all Tier 1 queries with the requested window, count surviving candidates. If fewer than N candidates survive:

- First widen: drop to Tier 2 queries (`"text-to-SQL"`, `"NL to SQL"`, `"agentic BI"`, `"semantic layer" AI`, `"conversational analytics"`). Same window.
- Second widen: drop to Tier 3 (`LangGraph engineer`, `MCP engineer`, `"multi-agent" engineer`, `"LLM evaluation"`)
- Third widen: extend window from 24h → 72h → 7 days
- Fourth widen: run `mcp__linkedin__get_company_jobs` on the top 5–8 names from the always-look list

**Flag any widening in the final report.** The user wants to know if the day was thin.

Stop searching as soon as you have N pre-filtered candidates.

### Step 5 — Read JDs and apply post-read drop signals

For each surviving candidate, call `mcp__linkedin__get_job_details` to pull the full JD. Sequential, jittered. Drop the result if the JD foregrounds any of:

- "model training" / "pre-training" / "post-training" as main verb
- "research scientist" / "research engineer" framing
- "managing a team" / "leading a team of N engineers"
- "Spark / dbt / Airflow pipeline" with no agent layer
- "strong CS fundamentals" / "algorithms & data structures" (leetcode tell)
- Generic SWE role where AI is incidental
- Comp listed and **below the geo-adjusted floor** (NYC/SF/LA <$170k base, Chicago/Remote <$140k base — check actual values in Target Profile)

Comp not listed is **not** a drop signal — flag it as "Comp: not listed" in the report.

If a post-read drop takes you below N candidates, return to Step 4's widening logic.

### Step 6 — Compose the report

Format (under 600 words total):

```
## N fresh roles posted in last <window>

### 1. <Title> — <Company> (<size + funding stage if visible>)
- **Location:** <city + onsite/hybrid/remote>
- **Posted:** <Xh ago>
- **URL:** <LinkedIn permalink>
- **Why it fits:** 2–3 bullets mapped to non-negotiables + strong pulls from Target Profile. Be specific — name which archetype + which JD phrases triggered the match.
- **Leetcode risk:** low / medium / high — one-line reason
- **Comp:** specific number or "not listed"

### 2. ... (repeat for each of N)

---

### What I skipped and why

2–3 sentences naming dropped results and the reason (hard-skip company, below comp floor, leetcode tell, manager track, already in Pipeline, etc.)

### Search notes (only if relevant)

- If widening happened, name it: "Widened to Tier 2" / "Extended window to 72h" / "Pulled from always-look list because Tier 1 was thin"
- If a search call failed and the diagnostic ladder fixed it, mention it
```

End the report. Do not append next-step suggestions unless the user asked. They'll decide what to do with the list.

## Hard rules

- **Never parallelize MCP calls.** Sequential only, jittered, per `linkedin-mcp-operations`.
- **Never modify files in the workspace.** This skill is read-only — no edits to Pipeline.md, no new role folders, no memory writes. If the user wants to file a result, they'll invoke `interview-prep-intake` or `jd-to-ready` separately.
- **Never apply, message, or contact anyone.** No `connect_with_person`, no `send_message`. Discovery only.
- **Never silently widen past the requested window.** If you widen, say so in the report.
- **Never invent comp.** If the JD doesn't list comp, write "not listed" — don't estimate from company size.
- **Honor the hard-skip list.** The only exception is when the title contains "Forward Deployed" / "Applied AI" / "Solutions Engineer" explicitly. If you include a hard-skip-list company because of the exception, call it out in the report.
- **Never recommend roles already in Pipeline.md.** Dedupe is mandatory.

## What "good" looks like

The user can scan the report in under 60 seconds and form an opinion on each role without clicking through. The "why it fits" bullets cite specific JD language, not generic praise. The "what I skipped" paragraph proves the filters are working (not silently passing every result). The skill takes 5–10 minutes wall-clock — most of it spent on jittered sequential MCP calls — and the user can interrupt at any point.

## When NOT to use this skill

- The user shares a single JD (PDF, URL, or pasted text) and wants it filed → use `interview-prep-intake`
- The user wants the full apply-ready package for one specific JD → use `jd-to-ready`
- The user pastes 3+ jobs from their LinkedIn Saved Jobs page → use `linkedin-saved-jobs-intake`
- The user wants to find contacts at a specific company (not jobs) → use `find-contacts`
- The user wants to research the recruiter for a role already filed → use `job-outreach`

If ambiguous between this skill and `linkedin-saved-jobs-intake`: the tell is *who did the curation*. If the user already saved jobs and is pasting them, it's `linkedin-saved-jobs-intake`. If they want you to do the search-and-filter pass, it's this skill.
