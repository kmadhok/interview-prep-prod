---
name: jd-to-ready
description: Use this skill when Kanu Madhok shares a job description and wants the full apply-ready package in one shot — folder filed, resume tailored, 5 recruiter + 5 hiring-manager/peer-IC contacts surfaced through sequential LinkedIn MCP calls (then enriched from recruiter activity), and cold outreach drafted. Trigger language includes "full intake", "intake and prep", "do everything for this JD", "get me apply-ready", "paste this JD" (when intent is to apply, not just track), or sharing a JD with phrases like "get this ready to send" / "I want to apply to this". Near-pure orchestration: composes primitives in sequence — `interview-prep-intake` (file the JD) → JD-classification (the one bit of logic it owns) → `tailor-resume(pipeline)` → `find-contacts(full)` → `enrich-contacts` → `verify-emails` → `write-outreach(drip)` — and wires their outputs together via a shared contacts-ledger artifact. Each primitive owns its own domain logic. Do NOT trigger when Kanu only wants to file the JD with no further prep (use `interview-prep-intake` alone) or only wants outreach for a JD already filed (use `write-outreach` alone). If ambiguous, ask whether he wants the full pipeline or just one piece.
---

# JD → Apply-Ready (one-shot intake + resume + outreach)

This skill is **near-pure orchestration** (the docker-compose model). It wires together primitives that each own their own domain logic — it never reimplements them. The one exception is step 2 (JD classification into themes + archetype): that logic lives in the orchestrator because it's the *routing* decision that selects which canonical material the downstream primitives pull — it's compose-layer wiring, not domain work any single primitive owns. Everything else — resume tailoring, contact research + ranking, activity enrichment, outreach drafting — lives in a primitive. The primitives and the modes it calls them in:

| Step | Primitive | Mode | Owns |
|------|-----------|------|------|
| 1 | `interview-prep-intake` (`.skill` at workspace root) | — | filing the JD |
| 2 | _(inline subagent — the one bit of logic this skill owns)_ | — | classifying the JD into `themes[]` + `archetype` |
| 3 | `tailor-resume` | `pipeline` | resume tailoring (canonical-only) |
| 4 | `find-contacts` | `full` | LinkedIn contact research (5+5, emails) + ranking; **writes `.contacts-ledger.md`** |
| 4b | `enrich-contacts` | — | scrape recruiter activity → appends new people (scored on find-contacts' rubric) + hooks; **extends `.contacts-ledger.md`** |
| 4c | `verify-emails` (deterministic script) | — | SMTP-verifying the top-3 recruiters' emails via EmailFinder.dev; **writes `Verified Emails.md`** |
| 5 | `write-outreach` | `drip` | cold outreach (per `Outreach Templates.md`); **reads ledger top rows** |

**The contacts ledger (`<role folder>/.contacts-ledger.md`) is a shared artifact, not a callback.** `find-contacts` writes it; `enrich-contacts` reads it, appends activity-surfaced people scored on find-contacts' *published* rubric, and re-sorts it; `write-outreach` reads its top rows. The pipeline is strictly **linear** — no step loops back into an earlier one. This is what keeps "ranking logic lives in one skill" true (find-contacts owns the rubric) while letting enrichment extend the ranking (it applies that rubric to new rows).

**Mode-name convention:** each primitive names its own heavy/light modes (`pipeline`/`full`/`drip` are each that primitive's "heavy, orchestrated" mode; `standalone`/`shortlist`/`single` are the light standalone modes). They are deliberately NOT one shared word — pass each primitive its own mode name as shown above. Every primitive returns a `gaps[]` of `{source, kind, detail}` objects; the orchestrator merges them across steps for the step-6 report and step-7 log.

Read the root `AGENTS.md` (or `CLAUDE.md`) at `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/` first. The workspace conventions there are the source of truth and override anything here if they conflict.

## What this skill produces

By the end of one invocation, the role folder contains:

1. `Job Description.md` — clean reading copy of the JD (from intake)
2. `Kanu Madhok Resume - <Company> <Short Role>.md` — tailored resume pulling bullets from `Resume Achievements Master.md`, **plus a one-page `.pdf` and editable `.docx` exported from it** (step 3.5)
3. `.contacts-ledger.md` + `Verified Emails.md` — scored contacts with the top 3 recruiters' emails **SMTP-verified via EmailFinder.dev** (step 4c)
4. `Cold Outreach.md` — researched contacts with drafted cold emails, **and the lead intro auto-created as a Gmail draft** (write-outreach step 6; never sent)

Plus: a new row in `Pipeline.md`, an updated `active_interview_pipeline.md` memory entry, and a short report-back with paths, hard gates, and gaps.

**End state:** the only things left for Kanu are to click **Apply** on the ATS and hit **Send** on the Gmail draft. Everything upstream (resume export, email verification, draft creation) is automated, degrading gracefully to gaps if EmailFinder/Gmail are unavailable.

## Workspace paths (resolved once, used throughout)

- **Workspace root:** `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/`
- **Reusables to read** (every run): `Resume Achievements Master.md`, `Outreach Templates.md`, `Demo Portfolio.md`, `Pipeline.md`
- **Memory file:** `active_interview_pipeline.md` in the session memory directory (path from system prompt; do not hardcode)
- **Role folder (to be created):** `<workspace root>/Roles/<Company - Role Title>/` (active/considering roles live under `Roles/`; closed roles in `_Archived/`)
- **LinkedIn MCP usage (step 4):** call `mcp__linkedin__*` tools directly, one at a time (sequential, never parallel). Follow `linkedin-mcp-operations` for the transport invariant, the sequential-only rule, and the per-op reference.
- **Trace helper:** `~/.claude/skills/jd-to-ready/scripts/trace_step.py`
- **Per-role trace:** `<role folder>/.jd-to-ready-trace.jsonl` (append-only step/tool/subagent events)
- **Global summary log:** `~/.claude/logs/jd-to-ready.jsonl` (one compact final line per run)
- **Trace docs for coding agents:** `TRACEABILITY.md`, `TRACE_SCHEMA.md`, `TOKEN_ACCOUNTING.md`, `RUNBOOK.md`, and `TRACE_TEST_PLAN.md` in this skill folder. Read these before editing trace behavior.

## Workflow

Run steps 1 → 7 in order. Don't pepper Kanu with questions mid-flow — make sensible defaults and surface fixes in the step 6 report.

### Trace contract - mandatory for every run

Create a run trace before Step 1 and close each step as it finishes. This is the observability contract for the orchestrator; hooks only enrich and check it. The trace helper is fail-closed for production runs: one active step at a time, required steps must close before `finish-run`, and interrupted runs must use `abort-run`. The deterministic contract for coding agents is documented in `TRACEABILITY.md` and `TRACE_SCHEMA.md`.

1. Start the run before intake:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py start-run --company "<company if known>" --role "<role if known>"
```

2. After Step 1 creates or confirms the role folder, bind the run to the per-role trace:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py set-role-folder --role-folder "<absolute role folder>" --company "<company>" --role "<role title>"
```

3. Wrap every step with `begin` before work and `end` after work. The `prediction` must be a one-line, checkable claim stated before the step runs; `prediction_met` is scored after. Include a `tokens` object on each `end` event; if counts are unavailable, use the explicit unknown token shape from `TOKEN_ACCOUNTING.md`.

```bash
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py begin --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --prediction "<checkable claim>"
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py end --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --status "ok|partial|failed|skipped" --prediction-met "true|false|partial|unknown" --produced '["file-or-artifact"]' --gaps '[]' --failure-pattern "<taxonomy-tag-or-empty>" --tokens "$UNKNOWN_TOKENS"
```

Required traced steps:

| Step | Primitive | Prediction to record before the step |
|---|---|---|
| 1 | `interview-prep-intake` | `role folder, Job Description.md, Pipeline row, and memory update are created or a safe existing-folder decision is reached` |
| 2 | `jd-classification` | `classification returns valid JSON with 4-6 in-vocab themes, evidence quotes, and one in-vocab archetype` |
| 3 | `tailor-resume` | `resume covers >=4 JD themes, uses canonical achievements only, and contains zero unsafe unverified claims` |
| 4 | `find-contacts` | `5 recruiter and 5 HM/peer-IC candidates are attempted, .contacts-ledger.md is written, and low-confidence emails are flagged` |
| 4b | `enrich-contacts` | `recruiter activity is checked when available, hooks are captured, and any new people are scored into .contacts-ledger.md` |
| 4c | `verify-emails` | `top 3 recruiters' emails are SMTP-verified via EmailFinder (cached), Verified Emails.md is written, and misses degrade to inferred/flagged` |
| 5 | `write-outreach` | `Cold Outreach.md is drafted with real contacts/hooks only and no fabricated urgency` |
| 6 | `report-back` | `report includes paths, hard gates, classification evidence, contacts, gaps, and stale Pipeline.html note` |
| 7 | `final-log` | `global jd-to-ready summary is appended and active run state is cleared` |

Use only these `failure_pattern` values unless the value is `null`: `generic-resume-language`, `verify-placeholder-leak`, `non-decision-maker-contact`, `low-confidence-emails`, `fabricated-hook`, `thin-jd-stub`, `theme-unmatched`, `thin-results`.

If a step fails or is skipped, still write its `end` event with `status: failed|skipped`, the known `gaps`, and the closest `failure_pattern`. If a value is unknown, use `null` rather than inventing.

When editing trace behavior, do not rely on corrected summary lines. The McKinsey run showed why: artifacts can exist while steps 4/4b/5/6 are missing from the per-role trace. `finish-run` now fails closed unless all required production steps are closed; use `abort-run --reason "<reason>"` when a run cannot continue.

### Step 1 — Run intake (file the JD)

Invoke the `interview-prep-intake` skill's workflow (read `interview-prep-intake.skill` at the workspace root for the authoritative version). Briefly: parse the JD → create `<Company - Role>` folder → write `Job Description.md` → add row to `Pipeline.md` (default stage: `Considering — JD reviewed, not yet applied`) → update `active_interview_pipeline.md`.

Capture from the parsed JD for downstream steps:
- Company name (the actual employer — check apply URL domain + legal footer; don't be fooled by vendor names in the title)
- Role title + short role name (for filenames)
- Folder name (matches intake's convention)
- Hard gates (citizenship, clearance, sponsorship, RTO, travel %) — flag for step 6 report
- Role archetype (see step 2)

If the folder already exists, stop and ask Kanu whether to refresh in place, write as a variant, or skip. Don't overwrite a folder he's already prepped.

### Step 2 — Identify JD themes + role archetype (subagent classification)

Do NOT do keyword matching from the main thread. The JD often signals intent through phrasing, responsibilities, and team context that surface-level keyword spotting misses (e.g., "embed with customer engineering teams to ship production agents" is FDE-flavored even if the word "forward-deployed" never appears). Spawn a subagent that reads the full JD and returns a constrained classification.

**Fixed vocabularies (subagent output MUST come from these — no free-form tags).**

Themes (the canonical achievements in `Resume Achievements Master.md` are pre-tagged with these exact strings):

> `agents`, `RAG`, `NL→SQL`, `MCP`, `LLM-orchestration`, `ML-pipeline`, `platform`, `business-translation`, `end-to-end`, `RPA`, `experimentation`, `dashboards`, `consulting`, `simplification`, `leverage`, `cross-functional`, `engineering-rigor`, `evaluation`

Archetypes:
- **agent-builder** — building/shipping production agents, agent platforms, MCP, agent orchestration
- **FDE / client-facing** — forward-deployed, customer-embedded, deployment engineering
- **consulting / product-builder** — AI factory, consulting AI, productized advisory
- **platform / ML engineering** — ML pipelines, infra, eval platforms
- **data-engineering / analytics** — BigQuery, dbt, dashboards, analytics enablement

**Spawn the subagent** using `Agent` with `subagent_type: general-purpose` and a self-contained prompt. The subagent has no conversation context, so the prompt must include the full JD text, both vocabularies above, and an explicit output schema.

Prompt template (substitute `<JD_TEXT>` with the full `Job Description.md` contents):

```
You are classifying a job description for a resume-tailoring pipeline. The downstream system has a library of canonical resume achievements pre-tagged with a FIXED theme vocabulary — so your output MUST use ONLY the exact strings from the vocab lists below. Free-form tags break the pipeline.

# Job description

<JD_TEXT>

# Theme vocabulary (pick 4–6, exact strings only)

agents, RAG, NL→SQL, MCP, LLM-orchestration, ML-pipeline, platform, business-translation, end-to-end, RPA, experimentation, dashboards, consulting, simplification, leverage, cross-functional, engineering-rigor, evaluation

# Archetype vocabulary (pick exactly 1, exact string only)

agent-builder, FDE / client-facing, consulting / product-builder, platform / ML engineering, data-engineering / analytics

# Your task

Read the FULL JD — responsibilities, qualifications, team context, "about us" framing, day-to-day expectations. Infer intent, not just keywords. A JD that talks about "embedding with customer teams to deliver agentic solutions" is FDE / client-facing even if "forward-deployed" never appears. A JD heavy on dashboards + stakeholder management + SQL is data-engineering / analytics even if it says "AI Engineer" in the title.

For each theme you pick:
- Quote the SHORTEST verbatim JD phrase or sentence that justifies it (≤25 words).
- If you can't find a direct JD quote, do NOT pick the theme — it doesn't count.

Pick 4–6 themes that the JD actually leans on, not every theme it could plausibly touch. Prefer specificity over breadth.

For the archetype:
- Pick the one that matches what the role ACTUALLY DOES day-to-day, not the title. "AI Engineer" at a consulting firm where the work is client delivery → consulting / product-builder, not platform / ML engineering.
- Provide a 1–2 sentence rationale citing JD evidence.

# Output format (return EXACTLY this JSON, nothing else)

{
  "themes": [
    {"tag": "<one of the 18 theme strings>", "evidence": "<JD quote ≤25 words>"},
    ...
  ],
  "archetype": "<one of the 5 archetype strings>",
  "archetype_rationale": "<1–2 sentences citing JD evidence>",
  "notes": "<optional: anything surprising about this JD that downstream steps should know — e.g., 'title says AI Engineer but the work is 80% dashboards', or 'hard gate: active TS/SCI clearance required'. Empty string if nothing.>"
}

Validation rules you must self-check before returning:
1. Every theme tag is one of the 18 exact strings.
2. Every theme has a non-empty evidence quote pulled from the JD text above.
3. Number of themes is between 4 and 6 inclusive.
4. Archetype is one of the 5 exact strings.
5. The JSON parses. No prose before or after.
```

**Validate the subagent's response** before using it:

1. Parse as JSON. If parse fails, re-spawn once with a follow-up note ("your last reply did not parse as JSON — return only the JSON object"). If second attempt fails, fall back to main-thread keyword classification and flag in the step 6 report.
2. Check every `themes[].tag` is in the 18-string vocab. If any is off-vocab, drop it.
3. Check archetype is in the 5-string vocab. If off-vocab, re-spawn once; if still off, default to closest match by hand and flag.
4. Check theme count is 4–6. If <4 after filtering, accept what's valid and flag the gap; if >6, keep the 6 with the strongest evidence quotes.

**Capture for downstream steps:**
- `themes`: list of `{tag, evidence}` — pass `tag`s to step 3's library lookup; keep the evidence quotes for the step 6 report so Kanu can spot-check the classification.
- `archetype`: drives bullet anchoring (step 3) and outreach hook (step 5).
- `notes`: surface in the step 6 report verbatim — this is where the subagent flags things the constrained schema can't capture (title mismatch, hidden hard gates, unusual team structure).

### Step 3 — Build tailored resume

**Call the `tailor-resume` primitive** (it owns all resume-tailoring logic — canonical-only discipline, A1/F1/U1 selection, the `[VERIFY]` rule, the format and filename). Do not reimplement it here.

Invoke:
```
tailor-resume(
  role_folder: <role folder from step 1>,
  jd:          <Job Description.md text>,
  themes:      <themes[] from step 2>,
  archetype:   <archetype from step 2>,
  mode:        pipeline
)
```

**Wire the output forward:** capture the returned `gaps[]` (cross-skill schema `{source: "resume", kind, detail}` objects, or `[]`) and merge it into the step-6 report and the step-7 log alongside the other primitives' gaps — they all share the `source`-keyed schema. The primitive writes the resume to `<role folder>/Kanu Madhok Resume - <Company> <Short Role>.md`; record that path for step 6.

### Step 3.5 — Export the resume to PDF + DOCX

After `tailor-resume` writes the `.md`, render a polished **one-page PDF** and an editable **DOCX** next to it. Run the helper:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/export_resume.py "<role folder>/Kanu Madhok Resume - <Company> <Short Role>.md"
```

The script (md → styled HTML → headless-Chrome PDF; pandoc → DOCX) **measures rendered height and auto-tightens font/margins until it fits one US-Letter page**, then writes `.pdf` + `.docx` siblings. If the content genuinely exceeds one page at the 9pt floor, it stops at 9pt, writes the (2-page) files anyway, and prints `OVERFLOW` — surface that in the step-6 report so Kanu can decide whether to trim a bullet. (A resume that won't fit is a tailoring decision Kanu owns — never silently cut canonical bullets to win the page break.)

Graceful degradation: if pandoc or Chrome is missing, skip export, record `{source:"resume-export", kind:"export-unavailable", detail:"<which tool> missing; .md written, no PDF/DOCX"}`, and continue. The `.md` is always the source of truth; PDF/DOCX are conveniences.

### Step 4 — Contact research (sequential LinkedIn MCP)

**Call the `find-contacts` primitive in `full` mode** (it owns all contact-research logic — org-mapping the role into its team/practice, team-first recruiter search, ranking, profile drilldown, email inference, and the sequential-LinkedIn discipline). Do not reimplement it here.

Invoke:
```
find-contacts(
  company:     <real employer from step 1; disambiguate subsidiaries>,
  role_title:  <role from step 1>,
  jd:          <Job Description.md text — used to map the role's team/parent practice>,
  jd_region:   <cities/locations from the JD>,
  archetype:   <archetype from step 2>,
  mode:        full,
  role_folder: <role folder from step 1>
)
```

**Wire the output forward:** `find-contacts(full)` **writes the scored-ledger artifact to `<role folder>/.contacts-ledger.md`** (Recruiters · Hiring Managers · Peer ICs, every candidate scored, each row carrying email + confidence). Each ledger row carries a pattern-inferred email at Medium confidence; the top picks are SMTP-verified later in **step 4c** (after enrichment), which writes `<role folder>/Verified Emails.md` — the table `write-outreach` reads for the Gmail draft. It also returns the three rendered tables, a provisional `top_picks` + `recommended_lead`, and `gaps[]` (`{source: "contacts", ...}`). **Do not bind `top_picks` for outreach yet** — step 4b may append a higher-ranked person and re-sort the ledger. The authoritative picks are read from the ledger *after* 4b. Capture the gaps for steps 6/7 now.

**Warm-tie check (recommended before step 4c):** if Gmail is connected, search it for prior correspondence with the company (`from:<domain> OR to:<domain>`). A recruiter Kanu already interviewed with is a header-verified, warm contact that outranks any cold pick — promote them to the top of the ledger with `High (header-verified)` email and pivot the outreach to a warm reconnect (see `write-outreach`). This is how the McKinsey run surfaced Caroline DeCorrevont over a cold top-pick.

### Step 4b — Enrich recruiters from their activity

**Call the `enrich-contacts` primitive** (it owns activity-scraping — reading each recruiter's posts/reposts to surface on-target people the keyword search missed and a real hook per recruiter). It reads the ledger find-contacts wrote, scores any new people **on find-contacts' published rubric** (it applies the rubric, doesn't redefine it), appends them, and re-sorts the ledger in place. No callback into find-contacts — the shared artifact *is* the hand-off. Do not reimplement it here.

```
enrich-contacts(
  role_folder: <role folder from step 1>,   # where .contacts-ledger.md lives
  team:        <the {team, parent_practice, function} map find-contacts produced>,
  role_title:  <role from step 1>,
  jd_region:   <cities/locations from the JD>   # required — scores appended people's location
)
```

**Wire forward:** `enrich-contacts` updates `<role folder>/.contacts-ledger.md` in place (new people appended as `Source: enrich` rows, whole ledger re-sorted) and returns `hooks[]` (one per recruiter) + `gaps[]` (`{source: "enrich", ...}`). Forward `hooks[]` to step 5. Merge its `gaps[]` into steps 6/7. If a recruiter's feed is empty/inaccessible, that's a logged `no-activity` gap, not a failure — proceed.

**Now read the authoritative top picks from the (post-enrichment) ledger:** the top recruiter row + the `recommended_lead` pick. Because there is one ledger file and one final sort, these are never stale — there is no pre/post fork to confuse. If `find-contacts` returned incomplete results (LinkedIn unreachable, no ledger written), skip 4b and proceed to step 5 with empty contacts and the failure noted — never invent contacts.

### Step 4c — Verify top-recruiter emails (EmailFinder.dev)

**Run the `verify-emails` deterministic script** (it owns all email-resolution logic — parsing the ledger, calling EmailFinder.dev's `/find-email/person` endpoint, caching paid results, and inferring-and-flagging on a miss). It runs **after** 4b so it verifies the *final*, post-enrichment top-3 recruiters. Do not reimplement it here; EmailFinder.dev owns verification.

```bash
python3 "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/.claude/skills/verify-emails/scripts/verify_emails.py" \
  --ledger "<role folder>/.contacts-ledger.md" \
  --emails-md-default \
  --max-credits 5 \
  --json
```

The script reads the ledger's `**Email pattern:**` line for the domain + local-part pattern, selects the top 3 `Recruiter` rows by rank, SMTP-verifies each via EmailFinder.dev (1 credit per verified hit; 404 misses are free), and writes two things: a `## Verified Emails` section back into the ledger, and a standalone **`<role folder>/Verified Emails.md`** (`| Name | Email | Confidence |`) — the file `write-outreach` reads. A `.email-cache.json` keyed by name+company makes re-runs free (already-verified people are never re-charged).

**Wire forward:** `Verified Emails.md` now exists with one row per resolved recruiter — Confidence `High (EmailFinder-verified)` for SMTP hits, `Medium (inferred <pattern>)` for misses that fell back to the ledger's pattern. Capture a `gaps[]` entry per outcome worth surfacing: `{source:"verify-emails", kind:"inferred-email", detail:"<name>: EmailFinder miss; using inferred <pattern> address"}` for inferred rows, `{source:"verify-emails", kind:"emailfinder-unavailable", detail:"<reason>; top picks use inferred emails"}` if the API key is missing or returns 402/429 (the script marks those rows SKIPPED — never blocks). Merge into steps 6/7.

**Graceful degradation:** if the `Email_Finder_Dev` key is absent or the ledger has no `**Email pattern:**` line, the script still runs by company name and degrades to NOT FOUND / inferred rows rather than crashing. A missing `Verified Emails.md` is not fatal — `write-outreach` falls back to Kanu's own address with a flagged gap.

### Step 5 — Draft Cold Outreach.md

**Call the `write-outreach` primitive in `drip` mode** (it owns all outreach drafting — the 5-beat body, length, subject formula, the 4-email drip cadence, hook-finding, channel choice, and the `Cold Outreach.md` output structure, all per `Outreach Templates.md` which is the single source of truth). Do not reimplement the outreach spec here.

Invoke:
```
write-outreach(
  contacts:    <the top recruiter row + the recommended_lead pick (HM for startups, peer-IC/recruiter for big firms), read from the post-4b `.contacts-ledger.md` — each row carries name, title, inferred email + confidence>,
  channel_confidence: <the email-confidence on each chosen contact's ledger row — drives email-vs-InMail>,
  hooks:       <hooks[] from step 4b enrich-contacts — the per-recruiter activity hook, if any, for beat 1>,
  role_title:  <role from step 1>,
  company:     <company from step 1>,
  archetype:   <archetype from step 2>,
  lead_theme:  <top theme from step 2>,
  urgency:     <real competing-processes list, or `none` — never fabricated>,
  mode:        drip,
  role_folder: <role folder from step 1>
)
```

**Ask Kanu for `urgency` at the start of this step** if competing processes aren't already known (drives beat 3; omit the beat entirely if none — never invent).

**Wire the output forward:** `write-outreach` writes `<role folder>/Cold Outreach.md` (two contact tables + a 4-email drip per top pick + Notes). Capture its returned `gaps[]` (`{source: "outreach", ...}`) and merge into the step-6 report and step-7 log.

### Step 6 — Report back

Keep the recap short and actionable. Include:

- **Folder created** + paths to the three files written (use `computer://` links where possible)
- **Hard gates flagged** — surface citizenship/clearance/sponsorship/travel/RTO blockers by name if present in the JD. Better one direct question than tailored work for a role he can't take.
- **Classification** — archetype + top 3 themes with their JD evidence quotes (from the step 2 subagent) so Kanu can spot-check whether the resume angle is right. Include the subagent's `notes` field verbatim if non-empty.
- **Contacts found** — name + confidence level for each; flag if zero matches
- **Gaps** — any `[NUMBER?]` placeholders in the resume, low-confidence emails, missing demo URL, anything else worth a second look
- **`Pipeline.html` is now stale** — ask if he wants it regenerated

End with the obvious next step: review the drafts, run `.docx` conversion if he wants a Word resume, send the outreach.

### Step 7 — Log the run

Close the trace by wrapping this step and then calling `finish-run`. This appends one compact summary line to `~/.claude/logs/jd-to-ready.jsonl`, links that summary to `<role folder>/.jd-to-ready-trace.jsonl`, and clears the active-run state used by hooks. Before calling `finish-run`, confirm that steps `1`, `2`, `3`, `4`, `4b`, `4c`, `5`, `6`, and `7` all have `step_end` events. See `RUNBOOK.md` for inspection commands.

Begin Step 7:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py begin --step 7 --primitive final-log --mode "" --prediction "global jd-to-ready summary is appended and active run state is cleared"
```

End Step 7 before `finish-run`:

```bash
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py end --step 7 --primitive final-log --mode "" --status "ok|partial|failed|skipped" --prediction-met "true|false|partial|unknown" --produced '["~/.claude/logs/jd-to-ready.jsonl"]' --gaps '<merged gaps JSON array>' --failure-pattern "<taxonomy-tag-or-empty>" --tokens "$UNKNOWN_TOKENS"
```

Then finish the run:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py finish-run --status "ok|partial|failed" --gaps '<merged gaps JSON array>' --files-written '["Job Description.md","Kanu Madhok Resume - <Company> <Short Role>.md","Cold Outreach.md"]'
```

`finish-run` computes the final status from the step results and rejects a mismatched `--status`; the argument is kept only as an explicit caller assertion. If the run is interrupted, close it with:

```bash
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py abort-run --reason "<why the run cannot continue>" --gaps '<merged gaps JSON array>'
```

The final summary line contains this shape:

```json
{
  "timestamp": "2026-05-24T15:42:11-05:00",
  "run_id": "jdtr-...",
  "company": "Cohere",
  "role": "Forward Deployed Engineer, Prompt Specialist",
  "role_folder": "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Cohere - Forward Deployed Engineer Prompt Specialist",
  "trace_file": "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/Cohere - Forward Deployed Engineer Prompt Specialist/.jd-to-ready-trace.jsonl",
  "status": "ok",
  "steps_closed": ["1", "2", "3", "4", "4b", "4c", "5", "6", "7"],
  "required_steps": ["1", "2", "3", "4", "4b", "4c", "5", "6", "7"],
  "gaps": [],
  "files_written": ["Job Description.md", "Kanu Madhok Resume - Cohere FDE Prompt Specialist.md", "Cold Outreach.md"],
  "steps": [{"event": "step_end", "...": "..."}]
}
```

If any field is unknown for a run, set it to `null` rather than omitting the key. Keep JSON valid and one line per event. The per-role trace is the audit trail for "why did the skill pick this recruiter" questions. When a run's output looks off, read `<role folder>/.jd-to-ready-trace.jsonl` first; the answer should be visible there before re-running anything.

For coding agents changing this trace layer: keep `SKILL.md` operational, but treat `TRACEABILITY.md`, `TRACE_SCHEMA.md`, and `TOKEN_ACCOUNTING.md` as the implementation contract, with `TRACE_TEST_PLAN.md` as the regression plan. The implemented baseline is fail-closed production logging with per-step token accounting, one active step at a time, monotonic event sequence numbers, and an explicit abort path for interrupted runs.

**Regression discipline.** Self-predicted regressions are unreliable (per the AHE source: ~11% precision). Don't trust a step's own forecast of what it'll break — keep a **golden set** of already-prepped roles (Morningstar, BCG X) and, after any primitive edit, re-run and diff against the known-good output before trusting the change. The primitive-upgrade git history (`~/.claude/skills` repo) makes a bad edit one `git revert` away.

---

## Edge cases

- **Folder already exists** → stop and ask. Don't overwrite.
- **JD has zero recruiter/HM matches on LinkedIn** → write `Cold Outreach.md` with empty contacts table + a note. Don't fabricate.
- **Multi-role JD** → file under the role Kanu names; ask if unclear.
- **JD is for a role outside Kanu's focus** (data, AI, AI engineering, product engineering, AI strategy) → still run the full pipeline; judgment about fit is his.
- **Internal mobility (Walmart Data Ventures role)** → still file it. Skip outreach drafting (he can talk to people internally) and note that in the report.
- **Role has a hard gate Kanu likely can't clear** (e.g., active TS/SCI clearance required) → run intake + resume, but skip outreach until he confirms the gate is OK. Flag prominently in step 6.

## What this skill does NOT do

- It does NOT send messages. All outreach is drafted to a file for Kanu's review.
- It does NOT generate `.docx` / `.pdf` automatically. Mention it as a follow-up if relevant.
- It does NOT build out the full prep artifact set (Question Bank, Interview Answers, TMAY cue card, mock rubric, prep schedule). That's for after an interview is scheduled — not at apply time.
- It does NOT modify `Resume Achievements Master.md`, `Outreach Templates.md`, or any other reusable. If the JD surfaces a gap in those, mention it in the report — that's the `interview-prep-reusables` skill's job, not this one's.
