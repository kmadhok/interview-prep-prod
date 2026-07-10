---
name: stage-outreach
description: Use this skill when a role Kanu has already APPLIED to needs its recruiter outreach staged — find the recruiter on LinkedIn, verify their email, draft the cold outreach, and drop Gmail drafts (recruiter + hiring manager) addressed to them (never sent). Fires from the PC's hourly Pass B poll on Pipeline rows marked Applied with no STAGED marker, or manually for an immediate draft. Reads the role folder + `.classification.json` that jd-to-ready already wrote. Do NOT trigger to file a JD (interview-prep-intake) or prep a resume (jd-to-ready) — this is strictly the post-apply, LinkedIn-bound, Gmail-drafting half.
---

# Stage Outreach (apply-side: find recruiter → verify email → Gmail draft)

This is the apply-gated half of the two-orchestrator split. It runs ONLY on roles Kanu actually applied to, so all LinkedIn flag-risk and all Gmail writes live here. Steps 4/4b/4c/5 are lifted unchanged from the former monolithic `jd-to-ready`; the primitives own their domain logic — this skill only composes them. The step bodies are VERBATIM from the former monolith; adapting them here would break the primitive contracts. Note: read root `AGENTS.md`/`CLAUDE.md` first; it overrides anything here.

## Preconditions

- The role folder exists (jd-to-ready ran) and contains the tailored resume + `.classification.json`.
- The Pipeline row is marked `Applied` and carries no `STAGED in Gmail` marker.
- If `.classification.json` is missing (role prepped before the split), re-run the step-2 classifier ONCE and write it — do NOT re-run intake or re-tailor the resume. (Reference: jd-to-ready Step 2 classifier, the `jd-classification` primitive.)

The `.classification.json` written by jd-to-ready has this schema (read `archetype` + top theme from it; do NOT re-classify):

```json
{
  "themes": [ {"tag": "<in-vocab tag>", "evidence": "<JD quote ≤25 words>"} ],
  "archetype": "<in-vocab archetype>",
  "archetype_rationale": "<1–2 sentences>",
  "notes": "<subagent notes or empty>",
  "classified_ts": "<YYYY-MM-DD>"
}
```

## Trigger & machine

- PC, cron Pass B (hourly): `git pull`, then the deterministic worklist reader `scripts/drip_runner/outreach_worklist.py` scans `Pipeline.md` for rows marked Applied with no STAGED marker → run this skill on them, ONE role at a time (sequential LinkedIn, never parallel — see `linkedin-mcp-operations`). Manual kick on a single role is also supported.
- Runs on the PC (LinkedIn daemon at 127.0.0.1:8765).
- This poll IS the apply trigger — no role_state.json, no separate detector. The "Applied" signal is Kanu's Pipeline edit or the cloud routine marking it from an app-ack.

## Trace — open a SECOND, independent run

This skill opens a **second, independent run** from jd-to-ready's run — the fail-closed trace cannot straddle the multi-day apply gate, so two runs is the only honest model. Start the run before step 4:

```bash
python3 "<repo root>/scripts/trace_step.py" start-run --run-type stage-outreach --company "<company>" --role "<role>"
```

Then bind the run to the existing role folder (this BINDS the folder jd-to-ready already created — it must not create it):

```bash
python3 "<repo root>/scripts/trace_step.py" set-role-folder --role-folder "<absolute existing role folder>" --company "<company>" --role "<role>"
```

Required steps for run-type `stage-outreach` are `{4, 4b, 4c, 5, 6, 7}`; `finish-run` fails closed until all are closed. The trace helper lives at `<repo root>/scripts/trace_step.py` (shared script; this skill uses run-type `stage-outreach`). The trace is written to `<repo root>/runs/<run-id>/trace.jsonl`; after `finish-run`, render the human report with `python3 "<repo root>/scripts/render_run_report.py" "<repo root>/runs/<run-id>"` and include the report path in the step-6 summary.

Wrap every step with `begin` before work and `end` after work. The `prediction` must be a one-line, checkable claim stated before the step runs; `prediction_met` is scored after. Every `begin` MUST carry `--reason` (why this step is running now, one line) and `--sources` (JSON array of the files whose content shapes this step's output — the skill prompt plus static inputs; this is the debuggability chain, never omit or pad it). Include a `tokens` object on each `end` event; if counts are unavailable, use the explicit unknown token shape:

```bash
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 "<repo root>/scripts/trace_step.py" begin --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --prediction "<checkable claim>" --reason "<why this step runs now>" --sources '["<files per the sources column below>"]'
python3 "<repo root>/scripts/trace_step.py" end --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --status "ok|partial|failed|skipped" --prediction-met "true|false|partial|unknown" --produced '["file-or-artifact"]' --gaps '[]' --failure-pattern "<taxonomy-tag-or-empty>" --tokens "$UNKNOWN_TOKENS"
```

Required traced steps for this run-type:

| Step | Primitive | Sources to declare on `begin` | Prediction to record before the step |
|---|---|---|---|
| 4 | `find-contacts` | `.claude/skills/find-contacts/SKILL.md`, `<role folder>/Job Description.md`, `<role folder>/.classification.json` | `5 recruiter and 5 HM/peer-IC candidates are attempted, .contacts-ledger.md is written, and low-confidence emails are flagged` |
| 4b | `enrich-contacts` | `.claude/skills/enrich-contacts/SKILL.md`, `<role folder>/.contacts-ledger.md` | `recruiter activity is checked when available, hooks are captured, and any new people are scored into .contacts-ledger.md` |
| 4c | `verify-emails` | `.claude/skills/verify-emails/SKILL.md`, `<role folder>/.contacts-ledger.md` | `top 3 recruiters' emails are SMTP-verified via EmailFinder (cached), Verified Emails.md is written, and misses degrade to inferred/flagged` |
| 5 | `write-outreach` | `.claude/skills/write-outreach/SKILL.md`, `workspace/Outreach Templates.md`, `<role folder>/Verified Emails.md`, `<role folder>/.contacts-ledger.md` | `Cold Outreach.md is drafted with real contacts/hooks only and no fabricated urgency` |
| 6 | `report-back` | `.claude/skills/stage-outreach/SKILL.md` | `report includes paths, hard gates, contacts, gaps, and Gmail draft recipient` |
| 7 | `final-log` | `runs/<run-id>/trace.jsonl` | `stage-outreach summary is appended and active run state is cleared` |

Use only these `failure_pattern` values unless the value is `null`: `generic-resume-language`, `verify-placeholder-leak`, `non-decision-maker-contact`, `low-confidence-emails`, `fabricated-hook`, `thin-jd-stub`, `theme-unmatched`, `thin-results`.

If a step fails or is skipped, still write its `end` event with `status: failed|skipped`, the known `gaps`, and the closest `failure_pattern`. If a value is unknown, use `null` rather than inventing.

`finish-run` fails closed unless all required production steps are closed; use `abort-run --reason "<reason>"` when a run cannot continue.

## Workflow

Run steps 4 → 7 in order. Don't pepper Kanu with questions mid-flow — make sensible defaults and surface fixes in the step 6 report.

### Step 4 — Contact research (sequential LinkedIn MCP)

**Call the `find-contacts` primitive in `full` mode** (it owns all contact-research logic — org-mapping the role into its team/practice, team-first recruiter search, ranking, profile drilldown, email inference, and the sequential-LinkedIn discipline). Do not reimplement it here.

Invoke:
```
find-contacts(
  company:     <employer from the Applied Pipeline row / role folder name; disambiguate subsidiaries>,
  role_title:  <role from the Applied Pipeline row / role folder name>,
  jd:          <text of <role folder>/Job Description.md — used to map the role's team/parent practice>,
  jd_region:   <cities/locations from <role folder>/Job Description.md>,
  archetype:   <archetype from <role folder>/.classification.json>,
  mode:        full,
  role_folder: <the existing role folder bound in set-role-folder>
)
```

**Wire the output forward:** `find-contacts(full)` **writes the scored-ledger artifact to `<role folder>/.contacts-ledger.md`** (Recruiters · Hiring Managers · Peer ICs, every candidate scored, each row carrying email + confidence). Each ledger row carries a pattern-inferred email at Medium confidence; the top picks are SMTP-verified later in **step 4c** (after enrichment), which writes `<role folder>/Verified Emails.md` — the table `write-outreach` reads for the Gmail draft. It also returns the three rendered tables, a provisional `top_picks` + `recommended_lead`, and `gaps[]` (`{source: "contacts", ...}`). **Do not bind `top_picks` for outreach yet** — step 4b may append a higher-ranked person and re-sort the ledger. The authoritative picks are read from the ledger *after* 4b. Capture the gaps for steps 6/7 now.

**Warm-tie check (recommended before step 4c):** if Gmail is connected, search it for prior correspondence with the company (`from:<domain> OR to:<domain>`). A recruiter Kanu already interviewed with is a header-verified, warm contact that outranks any cold pick — promote them to the top of the ledger with `High (header-verified)` email and pivot the outreach to a warm reconnect (see `write-outreach`). This is how the McKinsey run surfaced Caroline DeCorrevont over a cold top-pick.

### Step 4b — Enrich recruiters from their activity

**Call the `enrich-contacts` primitive** (it owns activity-scraping — reading each recruiter's posts/reposts to surface on-target people the keyword search missed and a real hook per recruiter). It reads the ledger find-contacts wrote, scores any new people **on find-contacts' published rubric** (it applies the rubric, doesn't redefine it), appends them, and re-sorts the ledger in place. No callback into find-contacts — the shared artifact *is* the hand-off. Do not reimplement it here.

```
enrich-contacts(
  role_folder: <the bound role folder>,   # where .contacts-ledger.md lives
  team:        <the {team, parent_practice, function} map find-contacts produced>,
  role_title:  <role from the Applied Pipeline row / role folder name>,
  jd_region:   <cities/locations from <role folder>/Job Description.md>   # required — scores appended people's location
)
```

**Wire forward:** `enrich-contacts` updates `<role folder>/.contacts-ledger.md` in place (new people appended as `Source: enrich` rows, whole ledger re-sorted) and returns `hooks[]` (one per recruiter) + `gaps[]` (`{source: "enrich", ...}`). Forward `hooks[]` to step 5. Merge its `gaps[]` into steps 6/7. If a recruiter's feed is empty/inaccessible, that's a logged `no-activity` gap, not a failure — proceed.

**Now read the authoritative top picks from the (post-enrichment) ledger:** the top recruiter row + the `recommended_lead` pick. Because there is one ledger file and one final sort, these are never stale — there is no pre/post fork to confuse. If `find-contacts` returned incomplete results (LinkedIn unreachable, no ledger written), skip 4b and proceed to step 5 with empty contacts and the failure noted — never invent contacts.

### Step 4c — Verify top-recruiter emails (EmailFinder.dev)

**Run the `verify-emails` deterministic script** (it owns all email-resolution logic — parsing the ledger, calling EmailFinder.dev's `/find-email/person` endpoint, caching paid results, and inferring-and-flagging on a miss). It runs **after** 4b so it verifies the *final*, post-enrichment top-3 recruiters. Do not reimplement it here; EmailFinder.dev owns verification.

```bash
python3 ~/.claude/skills/verify-emails/scripts/verify_emails.py \
  --ledger "<role folder>/.contacts-ledger.md" \
  --emails-md-default \
  --max-credits 5 \
  --json
```

The script reads the ledger's `**Email pattern:**` line for the domain + local-part pattern, selects the top 3 `Recruiter` rows by rank, SMTP-verifies each via EmailFinder.dev (1 credit per verified hit; 404 misses are free), and writes two things: a `## Verified Emails` section back into the ledger, and a standalone **`<role folder>/Verified Emails.md`** (`| Name | Email | Confidence |`) — the file `write-outreach` reads. A `.email-cache.json` keyed by name+company makes re-runs free (already-verified people are never re-charged).

**Wire forward:** `Verified Emails.md` now exists with one row per resolved recruiter — Confidence `High (EmailFinder-verified)` for SMTP hits, `Medium (inferred <pattern>)` for misses that fell back to the ledger's pattern. Capture a `gaps[]` entry per outcome worth surfacing: `{source:"verify-emails", kind:"inferred-email", detail:"<name>: EmailFinder miss; using inferred <pattern> address"}` for inferred rows, `{source:"verify-emails", kind:"emailfinder-unavailable", detail:"<reason>; top picks use inferred emails"}` if the API key is missing or returns 402/429 (the script marks those rows SKIPPED — never blocks). Merge into steps 6/7.

**Graceful degradation:** if the `Email_Finder_Dev` key is absent or the ledger has no `**Email pattern:**` line, the script still runs by company name and degrades to NOT FOUND / inferred rows rather than crashing. A missing `Verified Emails.md` is not fatal — `write-outreach` falls back to Kanu's own address with a flagged gap.

### Step 5 — Draft Cold Outreach.md

**Call the `write-outreach` primitive in `drip` mode** (it owns all outreach drafting — the 5-beat body, length, subject formula, the two-intro pipeline output (recruiter #1 + HM/peer-IC #1, no follow-ups), hook-finding, channel choice, and the `Cold Outreach.md` output structure, all per `Outreach Templates.md` which is the single source of truth). Do not reimplement the outreach spec here.

Invoke:
```
write-outreach(
  contacts:    <the top recruiter row + the recommended_lead pick (HM for startups, peer-IC/recruiter for big firms), read from the post-4b `.contacts-ledger.md` — each row carries name, title, inferred email + confidence>,
  channel_confidence: <the email-confidence on each chosen contact's ledger row — drives email-vs-InMail>,
  hooks:       <hooks[] from step 4b enrich-contacts — the per-recruiter activity hook, if any, for beat 1>,
  role_title:  <role from the Applied Pipeline row / role folder name>,
  company:     <employer from the Applied Pipeline row / role folder name>,
  archetype:   <archetype from .classification.json>,
  lead_theme:  <top theme from .classification.json>,
  urgency:     <derive from Pipeline.md live processes — write-outreach applies the freshness filter (today-or-future only; drops STALE/PASSED/CLOSED/REJECTED); pass `none` only to force-omit; never fabricated>,
  mode:        drip,
  role_folder: <the bound role folder>
)
```

**`urgency` defaults to live processes derived from `Pipeline.md`** (write-outreach applies the freshness filter); pass `none` only to force-omit beat 3, and never invent competing processes.

**Wire the output forward:** `write-outreach` writes `<role folder>/Cold Outreach.md` (two contact tables + two intro emails (one per top pick) + a Notes block incl. the same-company double-send guard). Capture its returned `gaps[]` (`{source: "outreach", ...}`) and merge into the step-6 report and step-7 log.

`write-outreach` (drip mode) fires its `create_draft` here, at apply time, so the template's beat-1 "I just applied for…" is literally true. Drip mode creates **two** Gmail drafts — one To: the verified #1 recruiter, one To: the `recommended_lead` (HM/peer-IC) — both per `Outreach Templates.md`, both subject to the same-company double-send guard; never sent.

### Step 6 — Report back

Wrap this step in begin/end. Produce a short apply-side report in chat covering:

- Paths: `<role folder>/.contacts-ledger.md`, `<role folder>/Verified Emails.md`, `<role folder>/Cold Outreach.md`
- Gmail draft recipients: name + email for each draft created — recruiter #1 and the HM/peer-IC lead (the To: field of each); note if the same-company guard suppressed one
- Merged `gaps[]` from steps 4, 4b, 4c, and 5 — list each gap's `source`, `kind`, and `detail`
- Any hard-gate flag carried forward from jd-to-ready: check the Pipeline row's Stage/Next-action text and `<role folder>/Job Description.md` for an unconfirmed hard gate (citizenship/clearance/seniority) that jd-to-ready flagged; if present and unconfirmed, do not stage — leave the row un-STAGED and note it here.

Keep the report brief; surface only what Kanu needs to act on or review before hitting Send.

### Step 7 — Log the run

Wrap this step in begin/end. Append a one-line summary to the global log (same discipline as jd-to-ready's step 7). Confirm steps `4`, `4b`, `4c`, `5`, `6`, `7` all have `step_end` events. Then call finish-run:

```bash
python3 "<repo root>/scripts/trace_step.py" finish-run --status "ok|partial|failed" --gaps '<merged gaps JSON array from steps 4/4b/4c/5>' --files-written '[".contacts-ledger.md","Verified Emails.md","Cold Outreach.md"]'
```

`finish-run` fails closed if any required step is missing a `step_end` event — fix before calling it. Use `abort-run --reason "<reason>"` if the run cannot complete.

## Outputs

Folder gains `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, and **two Gmail drafts** — one to the #1 recruiter, one to the HM/peer-IC lead (in Drafts, never sent; the same-company double-send guard suppresses a duplicate when both resolve to the same address). On success, write `STAGED in Gmail <YYYY-MM-DD>` to the folder AND the Pipeline row — that marker is the terminal state the poll keys off, so a role carrying it is never re-staged. (Kanu reviews each draft, attaches the resume — `create_draft` can't attach files — and hits Send.)

## State (file markers — no ledger)

On success write `STAGED in Gmail <date>` to folder + Pipeline row = terminal. No role_state.json. The worklist (`outreach_worklist.py`) keys off Pipeline `Applied` + absence of the `STAGED in Gmail` marker.

## Degradation & edge cases

- **LinkedIn daemon down** → STOP before step 4; write nothing; leave the row un-STAGED so the next poll retries.
- **Zero contacts** → write `Cold Outreach.md` with empty tables + a note; do not fabricate.
- **EmailFinder unavailable / inferred email** → verify-emails degrades to inferred rows; write-outreach still drafts, falling back to Kanu's own address with a flagged gap.
- **Internal-mobility role** → skip; write `STAGED` with a note ("internal — handled in person").
- **Unconfirmed hard gate flagged by jd-to-ready** → do not stage; leave the row un-STAGED until Kanu confirms.

## What this skill does NOT do

No intake (interview-prep-intake), no classification (reads `.classification.json` — never re-classifies), no resume work (tailor-resume). Never decides "applied" itself — acts only on rows already marked Applied. Drafts only, never sends (Gmail drafts + paste-ready LinkedIn text).
