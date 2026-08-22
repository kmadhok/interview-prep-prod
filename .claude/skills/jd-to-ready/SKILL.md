---
name: jd-to-ready
description: Use this skill when the user shares a job description and wants to file it and get a tailored resume + PDF in one shot — the apply-ready prep half. Trigger language includes "full intake", "intake and prep", "do everything for this JD", "get me apply-ready", "paste this JD" (when intent is to prep, not just track), or sharing a JD with phrases like "I want to apply to this". Orchestrates the prep chain: `interview-prep-intake` (file the JD) → JD-classification (the one bit of logic it owns, writes `.classification.json`) → `tailor-resume(pipeline)` → resume PDF export + vision verification. Stops at the apply gate. Contact research + outreach drafting are handled by the `stage-outreach` skill, which auto-stages once the Pipeline row is marked Applied. Do NOT trigger when the user only wants to file the JD with no further prep (use `interview-prep-intake` alone) or only wants outreach for a JD already filed (use `stage-outreach` alone). If ambiguous, ask whether they want the full prep pipeline or just one piece.
---

# JD → Apply-Ready (prep half: intake + classify + resume + PDF)

This skill is **near-pure orchestration** (the docker-compose model). It wires together the prep-half primitives — it never reimplements them. The one exception is step 2 (JD classification into themes + archetype): that logic lives in the orchestrator because it's the *routing* decision that selects which canonical material the downstream primitives pull — it's compose-layer wiring, not domain work any single primitive owns. The prep chain ends at the apply gate: intake → classify → tailored resume → PDF. The apply-side chain (contact research + outreach) now lives in the `stage-outreach` skill, which auto-stages once the Pipeline row is marked Applied. The prep-half primitives and the modes it calls them in:

| Step | Primitive | Mode | Owns |
|------|-----------|------|------|
| 1 | `interview-prep-intake` (`.skill` at workspace root) | — | filing the JD |
| 2 | _(inline subagent — the one bit of logic this skill owns)_ | — | classifying the JD into `themes[]` + `archetype`; **writes `.classification.json`** |
| 3 | `tailor-resume` | `pipeline` | resume tailoring (canonical-only) |
| 3.5 | `resume-export` (`build_resume_pdf.py` + vision verify) | — | one-page PDF render + gold-standard visual verification |
| 3.7 | `apply-packet` (`apply_packet.py` + WebFetch) | — | true posted date, `Application Answers.md`, Drive upload |
| 6 | `report-back` | — | the short actionable recap to the user |
| 7 | `final-log` | — | global summary line + `finish-run` |

> **Pipeline ends at the apply gate.** Steps 4 / 4b / 4c / 5 (contact research, enrichment, email verification, outreach drafting) have moved to the `stage-outreach` skill. `stage-outreach` reads `.classification.json` from this step's output to skip re-classifying.

**The classification hand-off (`.classification.json`) is the only artifact the prep half passes to the apply half.** `jd-to-ready` writes it at the end of step 2; `stage-outreach` reads it to skip re-classifying before running contact research and outreach drafting. The pipeline between the two skills is strictly linear — no step loops back.

**Mode-name convention:** each primitive names its own heavy/light modes (`pipeline` is `tailor-resume`'s "heavy, orchestrated" mode; `standalone` is its light mode). They are deliberately NOT one shared word — pass each primitive its own mode name as shown above. Every primitive returns a `gaps[]` of `{source, kind, detail}` objects; the orchestrator merges them across steps for the step-6 report and step-7 log.

`<repo root>` = the directory containing `profile.yaml`; all workspace files live under `<repo root>/workspace/`. Read the root `AGENTS.md` (or `CLAUDE.md`) at `<repo root>/` first. The workspace conventions there are the source of truth and override anything here if they conflict.

## What this skill produces

By the end of one invocation, the role folder contains:

1. `Job Description.md` — clean reading copy of the JD (from intake)
2. `<user_name> Resume - <Company> <Short Role>.md` (user_name from profile.yaml) — tailored resume pulling bullets from `workspace/Resume Achievements Master.md`, **plus a one-page `.pdf` rendered from it (BCG X gold-standard layout) and vision-verified** (step 3.5)
3. `.classification.json` — validated JD classification (themes + archetype + evidence) written at the end of step 2; the `stage-outreach` skill reads this to skip re-classifying
4. `Application Answers.md` — copy-paste ATS answers drafted from root `Application Profile.md` (never invented)
5. `.apply-packet.json` + the uploaded Drive packet (`Apply Queue/<posted-date> · <Company> - <Role>.pdf` + answers `.txt`) — the mobile-ready finish line

Plus: a new row in `Pipeline.md`, an updated `active_interview_pipeline.md` memory entry, and a short report-back with paths, hard gates, and gaps.

**End state:** the resume is ready — apply on the ATS; once you mark the Pipeline row Applied, the `stage-outreach` skill auto-stages the recruiter draft. Resume export is automated, degrading gracefully to gaps if reportlab is unavailable.

## Workspace paths (resolved once, used throughout)

- **Workspace root:** `<repo root>/workspace/` (the directory holding the reusables and role folders; `<repo root>` contains `profile.yaml`). Resolve from the workspace's own `AGENTS.md`/`CLAUDE.md` first; paths elsewhere in this file are examples, not gospel. When a run cannot update the `active_interview_pipeline.md` memory (e.g. a headless drip-runner environment), that memory update is a known no-op — record it as a `{source:"intake", kind:"memory-noop"}` gap and continue.
- **Reusables to read** (every run): `workspace/Resume Achievements Master.md`, `workspace/Demo Portfolio.md`, `workspace/Pipeline.md`
- **Memory file:** `active_interview_pipeline.md` in the session memory directory (path from system prompt; do not hardcode)
- **Role folder (to be created):** `workspace/Roles/<Company - Role Title>/` (active/considering roles live under `workspace/Roles/`; closed roles in `workspace/_Archived/`)
- **Trace helper:** `<repo root>/scripts/trace_step.py` (shared by all skills)
- **Run trace:** `<repo root>/runs/<run-id>/trace.jsonl` (append-only step/tool/subagent events; one directory per run)
- **Run report:** `<repo root>/runs/<run-id>/report.md` — rendered after `finish-run` with `scripts/render_run_report.py`; this is the user's repair manual
- **Global summary log:** `<repo root>/runs/summary.jsonl` (one compact final line per run)
- **Trace docs for coding agents:** `docs/trace/TRACE_SCHEMA.md` and `docs/trace/TOKEN_ACCOUNTING.md` at the repo root, plus `TRACEABILITY.md`, `RUNBOOK.md`, and `TRACE_TEST_PLAN.md` in this skill folder. Read these before editing trace behavior.

## Workflow

Run steps 1 → 7 in order. Don't pepper the user with questions mid-flow — make sensible defaults and surface fixes in the step 6 report.

### Trace contract - mandatory for every run

Create a run trace before Step 1 and close each step as it finishes. This is the observability contract for the orchestrator; hooks only enrich and check it. The trace helper is fail-closed for production runs: one active step at a time, required steps must close before `finish-run`, and interrupted runs must use `abort-run`. The deterministic contract for coding agents is documented in `TRACEABILITY.md` and `TRACE_SCHEMA.md`.

1. Start the run before intake:

```bash
python3 "<repo root>/scripts/trace_step.py" start-run --run-type jd-to-ready --company "<company if known>" --role "<role if known>"
```

2. After Step 1 creates or confirms the role folder, bind the run to the per-role trace:

```bash
python3 "<repo root>/scripts/trace_step.py" set-role-folder --role-folder "<absolute role folder>" --company "<company>" --role "<role title>"
```

3. Wrap every step with `begin` before work and `end` after work. The `prediction` must be a one-line, checkable claim stated before the step runs; `prediction_met` is scored after. Every `begin` MUST carry `--reason` (why this step is running now, one line) and `--sources` (the JSON array of files whose content shapes this step's output — the skill prompt plus static inputs; this is the debuggability chain, never omit or pad it). Include a `tokens` object on each `end` event; if counts are unavailable, use the explicit unknown token shape from `docs/trace/TOKEN_ACCOUNTING.md`.

```bash
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 "<repo root>/scripts/trace_step.py" begin --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --prediction "<checkable claim>" --reason "<why this step runs now>" --sources '["<files whose content shapes this step — see the sources column below>"]'
python3 "<repo root>/scripts/trace_step.py" end --step "<step>" --primitive "<primitive>" --mode "<mode-or-empty>" --status "ok|partial|failed|skipped" --prediction-met "true|false|partial|unknown" --produced '["file-or-artifact"]' --gaps '[]' --failure-pattern "<taxonomy-tag-or-empty>" --tokens "$UNKNOWN_TOKENS"
```

Per-step `--sources` (adjust paths to the actual role folder; add any extra file the step genuinely read):

| Step | Sources to declare |
|---|---|
| 1 | `.claude/skills/interview-prep-intake/SKILL.md`, `workspace/Pipeline.md` |
| 2 | `.claude/skills/jd-to-ready/SKILL.md`, `<role folder>/Job Description.md` |
| 3 | `.claude/skills/tailor-resume/SKILL.md`, `workspace/Resume Achievements Master.md`, `<role folder>/Job Description.md` |
| 3.5 | `scripts/build_resume_pdf.py`, `scripts/verify_resume.py`, `<role folder>/<tailored resume .md>` |
| 3.7 | `scripts/drip_runner/apply_packet.py`, `workspace/Application Profile.md`, `<role folder>/.classification.json` |
| 6 | `.claude/skills/jd-to-ready/SKILL.md` |
| 7 | `runs/<run-id>/trace.jsonl` |

Required traced steps:

| Step | Primitive | Prediction to record before the step |
|---|---|---|
| 1 | `interview-prep-intake` | `role folder, Job Description.md, Pipeline row, and memory update are created or a safe existing-folder decision is reached` |
| 2 | `jd-classification` | `classification returns valid JSON with 4-6 in-vocab themes, evidence quotes, and one in-vocab archetype; .classification.json is written to the role folder` |
| 3 | `tailor-resume` | `resume covers >=4 JD themes, uses canonical achievements only, and contains zero unsafe unverified claims` |
| 3.5 | `resume-export` | `one-page PDF is exported from the tailored resume, matches BCG X gold standard (verified by vision agent); overflow/defects/missing-tools are logged as gaps` |
| 6 | `report-back` | `report includes paths, hard gates, classification evidence, gaps, and stale Pipeline.html note` |
| 7 | `final-log` | `global jd-to-ready summary is appended and active run state is cleared` |

Use only these `failure_pattern` values (or `null`). Emittable by this prep skill: `generic-resume-language`, `verify-placeholder-leak`, `fabricated-hook`, `thin-jd-stub`, `theme-unmatched`, `thin-results`, `pdf-export-defect`, `apply-packet-defect`. Defined in the shared trace taxonomy but only emitted by the apply-side `stage-outreach` skill (never here): `non-decision-maker-contact`, `low-confidence-emails`.

If a step fails or is skipped, still write its `end` event with `status: failed|skipped`, the known `gaps`, and the closest `failure_pattern`. If a value is unknown, use `null` rather than inventing.

Retries happen *before* `end`: fix and re-attempt inside the open step (e.g. the step-3.5 re-render). Once a step ends `failed`, the run's computed status is final — a closed step cannot be reopened.

When editing trace behavior, do not rely on corrected summary lines. The McKinsey run showed why: artifacts can exist while required steps are missing from the per-role trace. `finish-run` now fails closed unless all required production steps are closed; use `abort-run --reason "<reason>"` when a run cannot continue.

### Step 1 — Run intake (file the JD)

Invoke the `interview-prep-intake` skill's workflow (read `interview-prep-intake.skill` at the workspace root for the authoritative version). Briefly: parse the JD → create `<Company - Role>` folder → write `Job Description.md` → add row to `Pipeline.md` (default stage: `Considering — JD reviewed, not yet applied`) → update `active_interview_pipeline.md`.

Set the Pipeline row's **Next action** to: `Resume ready — apply on the ATS; outreach auto-stages once the row is marked Applied.`

Capture from the parsed JD for downstream steps:
- Company name (the actual employer — check apply URL domain + legal footer; don't be fooled by vendor names in the title)
- Role title + short role name (for filenames)
- Folder name (matches intake's convention)
- Hard gates (citizenship, clearance, sponsorship, RTO, travel %) — flag for step 6 report
- Role archetype (see step 2)

If the folder already exists, stop and ask the user whether to refresh in place, write as a variant, or skip. Don't overwrite a folder they've already prepped.

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
- `themes`: list of `{tag, evidence}` — pass `tag`s to step 3's library lookup; keep the evidence quotes for the step 6 report so the user can spot-check the classification.
- `archetype`: drives bullet anchoring (step 3).
- `notes`: surface in the step 6 report verbatim — this is where the subagent flags things the constrained schema can't capture (title mismatch, hidden hard gates, unusual team structure).

After validating the classification, persist it for the apply-side skill. Write `<role folder>/.classification.json`:

```json
{
  "themes": [ {"tag": "<in-vocab tag>", "evidence": "<JD quote ≤25 words>"} ],
  "archetype": "<in-vocab archetype>",
  "archetype_rationale": "<1–2 sentences>",
  "notes": "<subagent notes or empty>",
  "classified_ts": "<YYYY-MM-DD>"
}
```

This is the only hand-off `stage-outreach` (the apply-side skill) needs to skip re-classifying. Same validated values you pass to step 3 — just a write to disk, no new logic.

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

**Wire the output forward:** capture the returned `gaps[]` (cross-skill schema `{source: "resume", kind, detail}` objects, or `[]`) and merge it into the step-6 report and the step-7 log alongside the other steps' gaps — they all share the `source`-keyed schema. The primitive writes the resume to `<role folder>/<user_name> Resume - <Company> <Short Role>.md` (user_name from profile.yaml); record that path for step 6.

### Step 3.5 — Export the resume to PDF + visually verify

After `tailor-resume` writes the `.md`, render a polished **one-page PDF** next to it. This is a traced step — wrap the export call in `begin`/`end` (no mode for this step) using the documented begin/end syntax:

```bash
python3 "<repo root>/scripts/trace_step.py" begin --step 3.5 --primitive resume-export --mode "" --prediction "a one-page PDF matching the BCG X gold standard is rendered from the tailored resume with no title leak and PASSes vision verification; overflow/defects/missing-tools are logged as gaps" --reason "tailored resume markdown is ready and needs its apply-ready PDF" --sources '["scripts/build_resume_pdf.py","scripts/verify_resume.py","<role folder>/<tailored resume .md>"]'

python3 "<repo root>/scripts/build_resume_pdf.py" "<role folder>/<user_name> Resume - <Company> <Short Role>.md"
```

(`<repo root>` is the directory containing `profile.yaml`; the workspace lives at `<repo root>/workspace/`.)

The script (`build_resume_pdf.py`, reportlab) renders a one-page PDF that matches the BCG X gold-standard layout, **auto-tightening font/margins through tiers down to a 9pt floor** until the content fits one US-Letter page, then prints the `PAGES=<n> TITLE_LEAK=<0|1>` contract. It writes a `.pdf` sibling only — no `.docx` (the docx-export path produced malformed layouts and is retired). A resume that won't fit even at the 9pt floor is a tailoring decision the user owns — never silently cut canonical bullets to win the page break.

**Parse the export-quality contract.** On every exit the script prints exactly one machine-readable line to stdout: `PAGES=<n|NA> TITLE_LEAK=<0|1|NA>` (alongside its human `Wrote <path>` line). Grep stdout for that `PAGES=… TITLE_LEAK=…` line and parse the two values **tolerantly** — if the line is missing or either value won't parse, do NOT crash: record one gap `{source:"resume-export", kind:"export-quality-unknown", detail:"could not parse export contract"}` and treat the export quality as unknown.

**Visually verify against the gold standard.** After the PDF is written and the contract parsed, run `python3 "<repo root>/scripts/verify_resume.py" "<role folder>/<user_name> Resume - <Company> <Short Role>.pdf"` — it rasterizes the PDF and the BCG X reference to PNG and writes a `verify.json` packet. Then dispatch a vision sub-agent (general-purpose Agent) that reads `page-1.png` and `reference-1.png` from the packet's out-dir and judges the resume against the 9 visual criteria in `verify.json`, returning PASS/FAIL with per-criterion reasons. **On FAIL** (e.g. title leak, wrapping dates, two-column defect, overflow), record the agent's specific defects as gaps `{source:"resume-export", kind:"pdf-formatting-defect", detail:"<agent reason>"}` and, when the defect is mechanically fixable (overflow/leak), re-render once and re-verify before moving on. The `.md` is always the source of truth, so this degrades gracefully — if Playwright/rasterization or the vision agent is unavailable, record `{source:"resume-export", kind:"export-quality-unknown", detail:"vision verify unavailable"}` and continue.

**Map the parsed values to gaps on the step-3.5 `end --gaps` array:**
- `PAGES` > 1 → `{source:"resume-export", kind:"pdf-overflow", detail:"<n>-page PDF; trim a bullet to fit one page"}`
- `TITLE_LEAK` = 1 → `{source:"resume-export", kind:"pdf-formatting-defect", detail:"'Resume' title leaked into PDF"}`
- `PAGES` = `NA` (script printed `not found` or the render failed) → `{source:"resume-export", kind:"export-unavailable", detail:"<reason: reportlab missing or export failed>"}` (read the human error line for the reason). The `.md` is always the source of truth; the PDF is a convenience, so this degrades gracefully — continue.
- clean (`PAGES=1`, `TITLE_LEAK=0`) → empty gaps `[]`, status `ok`.

These gaps can stack (e.g. overflow + title leak). Surface any `pdf-overflow` in the step-6 report so the user can decide whether to trim a bullet.

**Failure pattern.** Use `--failure-pattern "pdf-export-defect"` when the PDF has a real defect — a `pdf-overflow` or `pdf-formatting-defect` gap (title leak, wrapping dates, vision-verify FAIL). Leave `--failure-pattern ""` when the only gaps are environmental (`export-unavailable`, `export-quality-unknown` — the tooling couldn't run or couldn't judge; that's not a defect in the artifact).

Close the step with the parsed status and gaps, e.g.:

```bash
python3 "<repo root>/scripts/trace_step.py" end --step 3.5 --primitive resume-export --mode "" --status "ok|partial|failed" --prediction-met "true|false|partial|unknown" --produced '["<user_name> Resume - <Company> <Short Role>.pdf"]' --gaps '<gaps from the mapping above, or []>' --failure-pattern "<pdf-export-defect if a real defect gap was recorded, else empty>" --tokens "$UNKNOWN_TOKENS"
```

Use `status: ok` when the clean case holds, `partial` when files were written but a defect/overflow was logged, `failed` when no files were produced (export-unavailable). Merge whatever gaps you recorded into the step-6 report and step-7 log alongside the other steps' gaps.

### Step 3.7 — Build + upload the apply packet

The prep finish line is not "PDF in the repo" — it is "packet on the phone" (`Automation Design - Two-Orchestrator/Spec - Apply Packet.md`). This step resolves the true posting date, drafts the application answers, and uploads both artifacts to the Drive `Apply Queue/` via rclone. The PDF must NEVER be read into context or passed through an MCP call — the upload CLI moves it disk→Drive.

Begin the trace:

```bash
python3 "<repo root>/scripts/trace_step.py" begin --step 3.7 --primitive apply-packet --mode "" --prediction "canonical ATS URL + posted date resolved, Application Answers.md drafted from Application Profile.md with zero invented facts, packet uploaded to the Apply Queue with a date-prefixed filename, .apply-packet.json written" --reason "PDF is verified; the packet makes the role one-click applyable from anywhere" --sources '["scripts/drip_runner/apply_packet.py","workspace/Application Profile.md","<role folder>/.classification.json"]'
```

**3.7a — Resolve the canonical posting + true posted date.** LinkedIn's "posted X days ago" is gamed by reposts; the ATS timestamp is the honest one. From the JD source (the LinkedIn posting's outbound apply link, or a search for `<company> greenhouse|ashby|lever <role>`), find the employer's own posting. Greenhouse (`boards-api.greenhouse.io/v1/boards/<org>/jobs`), Ashby (`api.ashbyhq.com/posting-api/job-board/<org>`), and Lever (`api.lever.co/v0/postings/<org>`) expose public JSON with real `updated_at`/`publishedDate`/`createdAt` fields — WebFetch the posting or the board JSON and extract the date. If no canonical source is found after ~3 fetches, set `posted_date: null` and record a gap `{source:"apply-packet", kind:"posted-date-unknown", detail:"no canonical ATS posting found"}` — do NOT trust the LinkedIn relative date. Also note whether the LinkedIn posting offers **Easy Apply** (`easy_apply`: true/false/null if unknown).

**3.7b — Repost check** (deterministic — do not judge similarity yourself):

```bash
python3 "<repo root>/scripts/drip_runner/apply_packet.py" repost-check "<role folder>" --repo-root "<repo root>"
```

Parse the JSON line. If `repost` is true, record a gap `{source:"apply-packet", kind:"repost-detected", detail:"~<similarity> match: <match_folder>"}` — the role still gets a packet (deprioritize, don't drop).

**3.7c — Update `.classification.json`.** Add/overwrite exactly these keys on the existing JSON (preserve everything else): `posted_date` (`"YYYY-MM-DD"` or null), `canonical_url` (string or null), `easy_apply` (true/false/null), `repost` (boolean from 3.7b).

**3.7d — Draft `Application Answers.md`.** The mobile copy-paste sheet for ATS forms. Pull facts ONLY from root `Application Profile.md` (never-invent rule: copy or placeholder). Structure:

```markdown
# Application Answers — <Company> · <Role>

**Apply here:** <canonical_url or the JD source URL>

## Standard fields
- Salary expectation: <from Application Profile.md, verbatim>
- Work authorization: <from Application Profile.md, verbatim>
- Notice period: <from Application Profile.md, verbatim>
- Phone / LinkedIn / GitHub: <from Application Profile.md, verbatim>

## Why <Company>
<3-5 sentences drafted from the step-2 themes + JD evidence, the user's voice, no hype words>

## Relevant project
<the 1-2 walkthroughs from AI Build Walkthrough - Master.md matching the archetype, compressed to a form-field paragraph each>

## Custom questions visible on the posting
<question → drafted answer, one pair per question; omit the section if none are visible>
```

**3.7e — Upload:**

```bash
python3 "<repo root>/scripts/drip_runner/apply_packet.py" upload "<role folder>"
```

Honor `APPLY_PACKET_REMOTE_DIR` if the environment sets it (the e2e test does). On non-zero exit, record a gap `{source:"apply-packet", kind:"upload-failed", detail:"<stderr line>"}` and close the step `partial` — the `.md`/`.pdf` in the repo remain the source of truth, and the hourly reconcile will retry the upload via the hash-drift path once the cause is fixed. Never let an upload failure abort the run.

Close the step (gaps from 3.7a/b/e). Use `--failure-pattern "apply-packet-defect"` when the packet itself is defective — an `upload-failed` or `repost-detected` gap. Leave it `""` when the only gap is environmental (`posted-date-unknown` — no canonical source existed to find):

```bash
python3 "<repo root>/scripts/trace_step.py" end --step 3.7 --primitive apply-packet --mode "" --status "ok|partial|failed" --prediction-met "true|false|partial|unknown" --produced '["Application Answers.md",".apply-packet.json"]' --gaps '<gaps or []>' --failure-pattern "<apply-packet-defect if upload-failed/repost-detected, else empty>" --tokens "$UNKNOWN_TOKENS"
```

### Step 6 — Report back

Keep the recap short and actionable. Include:

- **Folder created** + paths to the files written (use `computer://` links where possible)
- **Hard gates flagged** — surface citizenship/clearance/sponsorship/travel/RTO blockers by name if present in the JD. Better one direct question than tailored work for a role they can't take.
- **Classification** — archetype + top 3 themes with their JD evidence quotes (from the step 2 subagent) so the user can spot-check whether the resume angle is right. Include the subagent's `notes` field verbatim if non-empty.
- **Gaps** — any `[NUMBER?]` placeholders in the resume, missing demo URL, PDF overflow or defects, anything else worth a second look
- **Apply packet** — confirm the packet uploaded (Drive `Apply Queue/` filename with its posted-date prefix), flag `repost-detected` / `posted-date-unknown` / `upload-failed` gaps, and note Easy Apply availability
- **`Pipeline.html` is now stale** — ask if they want it regenerated

End with the obvious next step: apply on the ATS; once the Pipeline row is marked Applied, `stage-outreach` auto-stages the recruiter draft. Offer to regenerate the PDF or tweak a bullet if they want the page tighter.

### Step 7 — Log the run

Close the trace by wrapping this step and then calling `finish-run`. This appends one compact summary line to `<repo root>/runs/summary.jsonl`, records the run's trace at `<repo root>/runs/<run-id>/trace.jsonl`, and clears the active-run state used by hooks. Before calling `finish-run`, confirm that steps `1`, `2`, `3`, `3.5`, `3.7`, `6`, and `7` all have `step_end` events. See `RUNBOOK.md` for inspection commands.

Begin Step 7:

```bash
python3 "<repo root>/scripts/trace_step.py" begin --step 7 --primitive final-log --mode "" --prediction "global jd-to-ready summary is appended and active run state is cleared" --reason "all prep steps are closed; the run needs its permanent summary line" --sources '["runs/<run-id>/trace.jsonl"]'
```

End Step 7 before `finish-run`:

```bash
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 "<repo root>/scripts/trace_step.py" end --step 7 --primitive final-log --mode "" --status "ok|partial|failed|skipped" --prediction-met "true|false|partial|unknown" --produced '["runs/summary.jsonl"]' --gaps '<merged gaps JSON array>' --failure-pattern "<taxonomy-tag-or-empty>" --tokens "$UNKNOWN_TOKENS"
```

Then finish the run:

```bash
python3 "<repo root>/scripts/trace_step.py" finish-run --status "ok|partial|failed" --gaps '<merged gaps JSON array>' --files-written '["Job Description.md","<user_name> Resume - <Company> <Short Role>.md",".classification.json","Application Answers.md",".apply-packet.json"]'
```

After `finish-run` succeeds, render the human run report and include its path in the step-6 summary:

```bash
python3 "<repo root>/scripts/render_run_report.py" "<repo root>/runs/<run-id>"
```

`finish-run` computes the final status from the step results and rejects a mismatched `--status`; the argument is kept only as an explicit caller assertion. If the run is interrupted, close it with:

```bash
python3 "<repo root>/scripts/trace_step.py" abort-run --reason "<why the run cannot continue>" --gaps '<merged gaps JSON array>'
```

The final summary line contains this shape:

```json
{
  "timestamp": "2026-05-24T15:42:11-05:00",
  "run_id": "jdtr-...",
  "company": "Cohere",
  "role": "Forward Deployed Engineer, Prompt Specialist",
  "role_folder": "<repo root>/workspace/Roles/Cohere - Forward Deployed Engineer Prompt Specialist",
  "trace_file": "<repo root>/runs/<run-id>/trace.jsonl",
  "status": "ok",
  "steps_closed": ["1", "2", "3", "3.5", "3.7", "6", "7"],
  "required_steps": ["1", "2", "3", "3.5", "3.7", "6", "7"],
  "gaps": [],
  "files_written": ["Job Description.md", "<user_name> Resume - Cohere FDE Prompt Specialist.md", ".classification.json", "Application Answers.md", ".apply-packet.json"],
  "steps": [{"event": "step_end", "...": "..."}]
}
```

If any field is unknown for a run, set it to `null` rather than omitting the key. Keep JSON valid and one line per event. The run trace is the audit trail for "why did the skill classify the JD this way" and "what resume bullets were selected" questions. When a run's output looks off, read `runs/<run-id>/report.md` first (or the raw `trace.jsonl`); the answer — including which source file to edit — should be visible there before re-running anything.

For coding agents changing this trace layer: keep `SKILL.md` operational, but treat `TRACEABILITY.md`, `docs/trace/TRACE_SCHEMA.md`, and `docs/trace/TOKEN_ACCOUNTING.md` as the implementation contract, with `TRACE_TEST_PLAN.md` as the regression plan. The implemented baseline is fail-closed production logging with per-step token accounting, one active step at a time, monotonic event sequence numbers, and an explicit abort path for interrupted runs.

**Regression discipline.** Self-predicted regressions are unreliable (per the AHE source: ~11% precision). Don't trust a step's own forecast of what it'll break — keep a **golden set** of already-prepped roles (Morningstar, BCG X) and, after any primitive edit, re-run and diff against the known-good output before trusting the change. The primitive-upgrade git history (`~/.claude/skills` repo) makes a bad edit one `git revert` away.

---

## Edge cases

- **Folder already exists** → stop and ask. Don't overwrite.
- **Multi-role JD** → file under the role the user names; ask if unclear.
- **JD is for a role outside the user's focus** (data, AI, AI engineering, product engineering, AI strategy) → still run the full pipeline; judgment about fit is theirs.
- **Internal mobility (current-employer role)** → still file it. Note in the report that `stage-outreach` is not needed (they can reach out internally).
- **Role has a hard gate the user likely can't clear** (e.g., active TS/SCI clearance required) → run intake + resume, but flag prominently in step 6 before they apply.

## What this skill does NOT do

- It does NOT research or contact recruiters/HMs. That is the `stage-outreach` skill's job, triggered after the Pipeline row is marked Applied.
- It does NOT draft or send outreach. All outreach is handled by `stage-outreach` after applying.
- `tailor-resume` in its `standalone` mode does NOT auto-render the `.pdf` (and never a `.docx`) — but this skill always calls it in `pipeline` mode, so step 3.5 renders + vision-verifies the PDF. (`scripts/build_resume_pdf.py` is the manual fallback.)
- It does NOT build out the full prep artifact set (Question Bank, Interview Answers, TMAY cue card, mock rubric, prep schedule). That's for after an interview is scheduled — not at apply time.
- It does NOT modify `Resume Achievements Master.md` or any other reusable. If the JD surfaces a gap in those, mention it in the report — that's the `interview-prep-reusables` skill's job, not this one's.

## Behavior contracts

The embedded classify, resume-export, and apply-packet steps are governed by
`evals/classify/contract.md`, `evals/resume-export/contract.md`, and
`evals/apply-packet/contract.md`. Put their clause IDs on trace `step_begin`
and verifier-produced clause results on the matching `step_end`.
