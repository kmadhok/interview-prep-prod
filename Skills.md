# Skills — Interview Prep

_Last updated: 2026-07-01 (two-orchestrator split reflected)_


This is the human-readable map of every skill Kanu uses inside the Interview Prep workspace — what each one does, when to reach for it, and when to use a different one instead. The live skill triggers are defined in each skill's own `description` frontmatter; this file is the cheat-sheet view of all of them together.

When a skill seems like it might apply but you're not sure, the rule of thumb is: **the skill that names the file you're about to create or edit wins**. If it's a JD landing in a new role folder, that's intake. If it's the root-level reusables, that's reusables. If it's a cold email for a specific job, that's outreach. If it's a contact tracker built from Gmail, that's the recruiter tracker.

---

## Process Map — funnel stage → owning skill → source of truth

_Added 2026-05-31. This is the map of the whole application process, one stage at a time, with the single skill that owns each stage, the file its facts must come from, and the rule that stops fabrication. Read this first when you're unsure what fires._

The funnel runs left to right. **Each outward-facing stage names exactly one source-of-truth file** — if a fact isn't in that file, the skill emits a `[VERIFY:]` / `[NUMBER?]` placeholder instead of inventing it. Fabrication enters the process whenever a skill pulls a "fact" from anything other than its named source.

| #     | Funnel stage                                                         | Owning skill                       | Source of truth (facts MUST come from here)                                                      | Anti-fabrication rule                                                                                                                                                                          | Writes to                                           |
| ----- | -------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 0     | **Source** — find fresh roles                                        | `find-fresh-jobs`                  | `Job Search Target Profile.md`                                                                   | Read-only; surfaces, never files                                                                                                                                                               | chat only                                           |
| 1     | **File** — one JD into the workspace                                 | `interview-prep-intake`            | the JD itself                                                                                    | Copy JD verbatim; don't summarize claims into facts                                                                                                                                            | role folder, `Pipeline.md`, memory                  |
| 1b    | **File (bulk)** — saved-jobs paste                                   | `linkedin-saved-jobs-intake`       | the paste + LinkedIn MCP URLs                                                                    | Stub-with-placeholder where MCP finds no URL                                                                                                                                                   | `Saved Jobs Export.md`, role folders, `Pipeline.md` |
| 2     | **Tailor resume** ⚠️                                                 | `tailor-resume`                    | **`Resume Achievements Master.md`** (+ its `Resume Tailoring Contract`)                          | Don't quantify beyond verified proof points; leave `[VERIFY:]`. Scan draft against `Resume Claims To Verify.md` and strip unpromoted claims. Older tailored resumes are outputs, not evidence. | role folder resume `.md`                            |
| 3     | **Find contacts**                                                    | `find-contacts`                    | LinkedIn MCP (live)                                                                              | Never fabricate a person, title, or email; surface only what MCP returns                                                                                                                       | chat / role folder                                  |
| 3b    | **Enrich contacts** (scrape recruiter activity → new people + hooks) | `enrich-contacts`                  | LinkedIn MCP (live, recruiter feeds)                                                             | Every surfaced person / hook must cite a real scraped post; does NOT rank — hands new people back to `find-contacts`                                                                           | chat / role folder                                  |
| 3c    | **Verify emails**                                                    | `verify-emails`                    | EmailFinder/SMTP (live) + the contacts ledger                                                    | Verified beats inferred; never fabricate an address — degrade to inferred rows, flagged                                                                                                        | `Verified Emails.md`                                |
| 4     | **Draft cold outreach** ⚠️                                           | `write-outreach`                   | **`Outreach Templates.md`**                                                                      | No fabricated personalization — if no real hook exists, ask. Pull template, personalize only with verified facts (incl. `enrich-contacts` hooks)                                               | role folder draft                                   |
| 1+2   | **Apply-ready prep (save-side)**                                     | `jd-to-ready`                      | **calls** intake + inline classifier + `tailor-resume` — owns no logic itself                    | Inherits every primitive's rules; merges their `gaps[]`; **stops at the apply gate**                                                                                                           | resume `.md`+`.pdf`, `.classification.json`         |
| 3–4   | **Stage outreach (apply-side)**                                      | `stage-outreach`                   | **calls** `find-contacts` → `enrich-contacts` → `verify-emails` → `write-outreach`               | Inherits every primitive's rules; fires **only** on Pipeline rows marked Applied with no `STAGED` marker                                                                                       | ledger, `Verified Emails.md`, `Cold Outreach.md`, Gmail drafts (never sent) |
| 5     | **Submit + log applied**                                             | `track-application`                | `Pipeline.md`                                                                                    | Status/date facts only; no narrative invention                                                                                                                                                 | `Pipeline.md`, memory                               |
| 6     | **Follow up / nudge** ⚠️                                             | `follow-up`                        | `Outreach Templates.md` + the role's prior correspondence                                        | Reference only events that actually happened (a real round, a real silence window)                                                                                                             | role folder draft                                   |
| 7     | **Interview prep** (answers, Q-bank, TMAY, walkthrough)              | _no skill — normal Claude editing_ | `Master Story Bank.md`, `Tell Me About Yourself - Master.md`, `AI Build Walkthrough - Master.md` | Select + tailor from masters; `[NUMBER?]` for any missing metric                                                                                                                               | role folder                                         |
| 8     | **Library upkeep**                                                   | `interview-prep-reusables`         | the five reusables (edits them)                                                                  | Edit over rewrite; new claims land in `Resume Claims To Verify.md` until Kanu promotes them                                                                                                    | root reusables                                      |
| —     | **Contact list (cross-role)**                                        | `recruiter-contact-tracker`        | Gmail (live)                                                                                     | Mine only real correspondence                                                                                                                                                                  | `Recruiter Contacts.html`                           |

⚠️ = outward-facing text where a fabricated fact does real damage. These three (`tailor-resume`, `write-outreach`, `follow-up`) are where the "makes things up sometimes" symptom used to show up — caused by name-collision twins, now resolved (see next section).

### Containerization refactor (2026-05-31) — `jd-to-ready` is now pure orchestration

`jd-to-ready` was a 549-line skill that **reimplemented** the primitives' logic inline (two definitions of resume-tailoring, two of contact-research, two of outreach). It is now a pure orchestrator (docker-compose model): each step *calls* a primitive that owns its logic, and wires the outputs forward. _(Historical note: the step table below shows the pre-split monolith; steps 4/4b/5 moved to `stage-outreach` on 2026-06-27 — see the next section.)_

| jd-to-ready step | calls | mode | the primitive owns |
|---|---|---|---|
| 1 | `interview-prep-intake` | — | filing the JD |
| 3 | `tailor-resume` | `pipeline` | resume tailoring (canonical-only, `[VERIFY]`) |
| 4 | `find-contacts` | `full` | LinkedIn 5+5 + email inference + scoring |
| 4b | `enrich-contacts` | — | scrape recruiter activity → new people (looped back to `find-contacts` for scoring) + hooks (forwarded to `write-outreach`) |
| 5 | `write-outreach` | `drip` | cold-outreach drip per `Outreach Templates.md` |

**Conventions established:** (a) every primitive has a `## Contract` block (inputs/outputs/modes); (b) every primitive returns a cross-skill `gaps[]` of `{source, kind, detail}` objects the orchestrator merges; (c) mode names are per-primitive — `pipeline`/`full`/`drip` are each that primitive's heavy mode, `standalone`/`shortlist`/`single` the light standalone mode; (d) `Outreach Templates.md` and `Resume Achievements Master.md` are the single sources of truth — primitives *reference* them, never restate them (the old "inline rules supersede Outreach Templates" clause was deleted). The skill files now live in a git repo at `~/.claude/skills` (per-edit commits, file-granular rollback). `jd-to-ready` step 7 carries an **observability layer**: a per-step evidence record (`steps[]` with prediction / prediction_met / tokens / failure_pattern) + a failure-pattern taxonomy, so each run is traceable step-by-step.

### Two-orchestrator split (2026-06-27) — `jd-to-ready` cut at the apply gate

The monolith above ran all 7 steps on **every saved job** — burning flag-risky LinkedIn budget and piling up Gmail drafts for roles Kanu never applied to. It is now **two apply-gated skills**:

| | `jd-to-ready` (prep, save-side) | `stage-outreach` (apply-side) |
|---|---|---|
| **Fires on** | job saved (PC cron Pass A, daily; or manual JD share) | Pipeline row marked **Applied** with no `STAGED` marker (PC cron Pass B, hourly; or manual kick) |
| **Steps** | 1 intake · 2 classify · 3 resume · 3.5 PDF | 4 find-contacts · 4b enrich · 4c verify-emails · 5 write-outreach (+Gmail draft) |
| **LinkedIn / Gmail** | trigger + JD fetch only / none | contact research / drafts (never sent) |
| **Produces** | resume `.md`+`.pdf`, **`.classification.json`** (hand-off) | `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, Gmail draft, `STAGED in Gmail <date>` marker |

The primitives are unchanged — only the compose layer was recut. State is read from files that already exist (resume `.md` = prepped, `Applied` token = applied, `STAGED` marker = staged); no state database. Each skill is its own fail-closed trace run (`jd-to-ready` requires steps {1, 2, 3, 3.5, 6, 7}; `stage-outreach` {4, 4b, 4c, 5, 6, 7}). Design + specs: `Automation Design - Two-Orchestrator/` at workspace root; the running cron topology is in `Automation Architecture - Drip Runner.md`. End-to-end test harness: the `two-orchestrator-e2e-test` skill (isolated `_jd-to-ready-test/` clone, never touches real `Roles/` or `Pipeline.md`).

### Where each skill physically lives (for a fresh harness)

**Interview Prep skills — USE THESE in this workspace.** Canonical names, bound to the source-of-truth files in the table above:

| Skill `name:` | Path | Source of truth |
|---|---|---|
| `tailor-resume` | `~/.claude/skills/tailor-resume/SKILL.md` | `Resume Achievements Master.md` |
| `write-outreach` | `~/.claude/skills/write-outreach/SKILL.md` | `Outreach Templates.md` |
| `follow-up` | `~/.claude/skills/follow-up/SKILL.md` | `Outreach Templates.md` + role correspondence |
| `find-contacts` | `~/.claude/skills/find-contacts/SKILL.md` | LinkedIn MCP (live) |
| `enrich-contacts` | `~/.claude/skills/enrich-contacts/SKILL.md` | LinkedIn MCP (live, recruiter activity feeds) |
| `track-application` | `~/.claude/skills/track-application/SKILL.md` | `Pipeline.md` |
| `jd-to-ready` | `~/.claude/skills/jd-to-ready/SKILL.md` (the stale root `jd-to-ready.skill` was deleted 2026-05-31) | composes intake + classifier + `tailor-resume` (prep half — stops at the apply gate) |
| `stage-outreach` | `~/.claude/skills/stage-outreach/SKILL.md` | composes `find-contacts` + `enrich-contacts` + `verify-emails` + `write-outreach` (apply-side half) |
| `verify-emails` | `~/.claude/skills/verify-emails/SKILL.md` | EmailFinder/SMTP (live) + the contacts ledger |
| `interview-prep-intake` | `<workspace>/interview-prep-intake.skill` | the JD |
| `linkedin-saved-jobs-intake` | `<workspace>/linkedin-saved-jobs-intake.skill` | LinkedIn paste + MCP |
| `find-fresh-jobs` | `<workspace>/find-fresh-jobs.skill` | `Job Search Target Profile.md` |
| `interview-prep-reusables` | `<workspace>/interview-prep-reusables.skill` | the five reusables |
| `recruiter-contact-tracker` | `<workspace>/recruiter-contact-tracker.skill` | Gmail (live) |

(`<workspace>` = `~/Documents/Claude/Projects/Interview Prep`.)

**Projects/Job system — DO NOT USE in the Interview Prep workspace.** A separate, fully-functional job-search system rooted at `~/Documents/Claude/Projects/Job/` (its own `master-resume.md`, `applications/`, `contacts/`, `voice-samples/`). Its skills were renamed with a `js-` prefix on 2026-05-31 so they no longer collide:

| Skill `name:` | Path |
|---|---|
| `js-tailor-resume` | `~/.claude/skills/job-search/js-tailor-resume/SKILL.md` |
| `js-write-outreach` | `~/.claude/skills/job-search/js-write-outreach/SKILL.md` |
| `js-follow-up` | `~/.claude/skills/job-search/js-follow-up/SKILL.md` |
| `js-find-contacts` | `~/.claude/skills/job-search/js-find-contacts/SKILL.md` |
| `js-track-application` | `~/.claude/skills/job-search/js-track-application/SKILL.md` |

Each `js-` skill's `description` opens with `[Projects/Job system only — NOT Interview Prep.]` so trigger-matching keeps them out of this workspace.

**LinkedIn MCP — one skill, sequential-only (consolidated 2026-05-31).** There is now a single skill governing LinkedIn: `linkedin-mcp-operations` (`~/.claude/skills/linkedin-mcp-operations/SKILL.md`). It owns the http-transport invariant (avoids the FastMCP stdio bug), the daemon diagnostic ladder, the per-operation reference, and the one pacing rule: **sequential calls only, never parallel — no caps, no delays, no cool-downs.** Skills that need LinkedIn (`find-contacts`, `jd-to-ready`, the `js-` skills) call `mcp__linkedin__*` tools **directly and sequentially**; `linkedin-mcp-operations` is the reference doc they follow, not a wrapper they route through. The old heavy pacing wrapper (`job-search/linkedin-mcp`, with daily caps / jitter / session-log) was **deleted** — its caps-and-cool-downs model is gone by design.

### The fabrication root cause (resolved 2026-05-31)

`tailor-resume`, `write-outreach`, `follow-up`, `find-contacts`, and `track-application` were each **installed twice under the same `name:`** — once for Interview Prep, once under `~/.claude/skills/job-search/`. Because both declared the same `name:`, **which twin fired was non-deterministic.** When the `job-search/` twin won inside Interview Prep, it tailored from `master-resume.md` instead of `Resume Achievements Master.md` — surfacing a bullet real in *that* system but absent from the curated, verified master. That read as "made up." It was the mechanism behind inconsistent quality, not careless generation.

**Fix applied:** the `job-search/` twins' `name:` fields and directories were renamed with a `js-` prefix, their internal cross-references rewritten to the `js-` names, and a `[Projects/Job system only]` guard added to each description. The Interview Prep generation now wins unambiguously here. Re-verify if a collision ever reappears:
```bash
# Should show ONLY the top-level (Interview Prep) copy for each — job-search/ side must be empty:
for n in tailor-resume write-outreach follow-up find-contacts track-application; do
  echo "$n:"; grep -rl "^name: $n$" ~/.claude/skills --include=SKILL.md
done
```

---

## Workspace-local skills (`.skill` files at workspace root)

These are bundled `.skill` files that live with the workspace, version-controlled alongside the prep material. They are the primary skills you use day-to-day.

### `interview-prep-intake`

**Intent.** File a new job description into the workspace. Creates the `Roles/Company - Role` subfolder, writes a clean `Job Description.md`, adds a row to `Pipeline.md`, updates the auto-memory `active_interview_pipeline.md`.

**Reach for it when.** Kanu pastes, links, attaches, or shares a JD he wants tracked. Trigger language: "intake this JD", "add this to my pipeline", "track this role", "create a folder for this job", "save this JD", "file this role". Also triggers on bare JD shares inside this workspace when intent looks like saving.

**Don't reach for it when.** He's already filed the JD and is asking for prep work (drafting answers, tailoring resume) — that's normal Claude editing inside the role folder. Or when he wants cold outreach drafted for a JD (that's `job-outreach` / `write-outreach`). Or when he wants the JD turned into a contact list (that's `recruiter-contact-tracker`).

**Output.** `Roles/Company - Role/Job Description.md` + updated `Pipeline.md` + updated auto-memory.

**File.** `interview-prep-intake.skill` at workspace root.

---

### `find-fresh-jobs`

**Intent.** Morning pulse — surface a fresh batch of LinkedIn roles posted in the last 24 hours that match `Job Search Target Profile.md`. Runs the Target Profile's Tier 1 query bank via sequential LinkedIn MCP calls, applies every filter in that file (seniority, geo, geo-adjusted comp floor — NYC/SF/LA ≥ $170k / Chicago/Remote ≥ $140k, hard-skip company list with FDE/Applied/Solutions title exception, industry exclusions, post-read drop signals including leetcode tells), dedupes against `Pipeline.md`, and returns a compact evaluation-ready report.

**Reach for it when.** Kanu wants a batch of new listings to review against his target profile. Trigger language: "find fresh jobs", "find me jobs", "pull jobs", "show me new jobs", "what's new on LinkedIn today", "run the job search", "morning job pulse". Args parseable from natural language: "find me 5 jobs from last 72h", "15 fresh ones", etc.

**Don't reach for it when.** He shares one specific JD and wants it filed (that's `interview-prep-intake`). Or wants the full apply-ready package for one role (that's `jd-to-ready`). Or is pasting jobs he already saved on LinkedIn (that's `linkedin-saved-jobs-intake`). Or wants contacts at a known company, not jobs (that's `find-contacts`).

**Defaults.** N=10 jobs returned; window = posted in last 24 hours. Both overridable inline. Widening ladder if thin: Tier 2 → Tier 3 → 72h window → always-look-list company pass. Any widening is flagged in the report.

**Dedupe model.** Against `Pipeline.md` only — no separate memory of past pulses. Re-runs may re-surface the same unfiled job; that's intentional. Pipeline is the single source of truth for "already considered."

**Read-only.** Does not file roles, modify Pipeline.md, draft outreach, or apply. Decision support only — Kanu picks what to act on, then invokes `interview-prep-intake` or `jd-to-ready` separately.

**Output.** A single chat report (under 600 words): N entries each with title, company, location, posted-time, LinkedIn URL, "why it fits" bullets, leetcode risk, comp; plus a "what I skipped and why" paragraph.

**File.** `find-fresh-jobs.skill` at workspace root.

---

### `linkedin-saved-jobs-intake`

**Intent.** Bulk-file every job Kanu has copied from his LinkedIn "Saved Jobs" page in one pass. Parses the paste, runs sequential LinkedIn MCP searches to recover canonical URLs, appends a dated batch to root `Saved Jobs Export.md`, creates one `Roles/Company - Role` folder per job (skipping any that already exist), WebFetches the full JD into each new folder, and adds a "Bulk-imported YYYY-MM-DD" subsection to `Pipeline.md`.

**Reach for it when.** Kanu pastes a block of 3+ jobs copied from `linkedin.com/my-items/saved-jobs/` and wants them all filed at once. Trigger language: "here are my saved jobs", "intake my saved jobs", "file all of these", "bulk import these jobs", "pulled my saved jobs list". Also triggers on a bare paste of LinkedIn-formatted job lines (`Title \n Company · Location \n Posted Xd ago`) when intent looks like bulk-tracking.

**Don't reach for it when.** He shares one JD (that's `interview-prep-intake`). Or wants apply-ready prep for one role (that's `jd-to-ready`). Or wants a recruiter-contact list (that's `recruiter-contact-tracker`).

**Defaults.** APPEND to `Saved Jobs Export.md` across runs (cumulative log). SKIP jobs whose folder already exists (do not clobber prior prep). Stops at filing — does not auto-run `jd-to-ready` or draft outreach.

**Output.** Updated `Saved Jobs Export.md` + one new `Roles/Company - Role/Job Description.md` per parsed job (full JD where MCP found the URL; stub with placeholder where it didn't) + a new dated subsection in `Pipeline.md` `Considering / not yet applied`.

**File.** `linkedin-saved-jobs-intake.skill` at workspace root.

---

### `jd-to-ready`

**Intent.** Save-side **prep half** of the two-orchestrator pipeline. Given a fresh JD, runs intake → classifies the role (themes + archetype, persisted to `.classification.json` as the hand-off to `stage-outreach`) → tailors the resume from `Resume Achievements Master.md` → builds and vision-verifies the PDF. End state: the role folder is apply-ready — Kanu applies on the ATS, marks the row Applied, and outreach auto-stages from there. **Stops at the apply gate**: no contact research, no outreach, no Gmail.

**Resume safety rule.** When tailoring the resume, use only the canonical achievements and verified proof points in `Resume Achievements Master.md`. Role-specific resumes are prior outputs, not evidence. Do not pull from `Resume Claims To Verify.md` or older tailored resumes unless Kanu has explicitly confirmed the claim and it has been promoted into the master.

**Reach for it when.** Kanu pastes a JD with apply intent. Trigger language: "full intake", "intake and prep", "get me apply-ready", "I want to apply to this". Also fired automatically by the PC cron's daily Pass A on newly saved LinkedIn jobs.

**Don't reach for it when.** He only wants to file the JD with no further prep (that's `interview-prep-intake` alone). Or he wants outreach staged for a role he already applied to (that's `stage-outreach`). Or he's deep into interview prep and wants Question Bank / Interview Answers built (this skill stops at apply-ready, not interview-ready).

**Output.** Role folder with `Job Description.md` + `Kanu Madhok Resume - <Company> <Short Role>.md` + `.pdf` + `.classification.json`, plus a `Considering` row in `Pipeline.md` and updated `active_interview_pipeline.md` memory. Nothing in Gmail; no contacts. Pass A's finish line is the apply packet: the tailored PDF + an answers file land in the Drive `Apply Queue/` folder (rclone remote `gdrive`), the hourly run reconciles the folder against Pipeline truth, and the daily run pushes an ntfy digest — see `Automation Design - Two-Orchestrator/Spec - Apply Packet.md`.

**Traceability.** Its own fail-closed trace run, run-type `jd-to-ready`, required steps {1, 2, 3, 3.5, 6, 7}. Before editing `jd-to-ready` logging, read the canonical docs in `.claude/skills/jd-to-ready/`: `TRACEABILITY.md`, `TRACE_SCHEMA.md`, `TOKEN_ACCOUNTING.md`, `RUNBOOK.md`, and `TRACE_TEST_PLAN.md`.

**File.** `.claude/skills/jd-to-ready/SKILL.md` (the stale root `jd-to-ready.skill` was deleted in the 2026-05-31 containerization refactor — see the Process Map note).

---

### `stage-outreach`

**Intent.** Apply-side **outreach half** of the two-orchestrator pipeline. For a role Kanu has **already applied to**: find the recruiter on LinkedIn (`find-contacts` → `enrich-contacts`), verify their email (`verify-emails`), draft the outreach (`write-outreach`, drip mode), and drop Gmail drafts addressed to the recruiter (+ hiring manager) — **never sent**. Reads the role folder and the `.classification.json` that `jd-to-ready` wrote; on success writes `STAGED in Gmail <date>` to the folder + Pipeline row, the terminal marker the poll never re-stages.

**Reach for it when.** Normally not by hand — the PC's hourly Pass B cron polls `Pipeline.md` for Active rows marked **Applied** with no `STAGED` marker and fires it. Invoke manually when Kanu just applied and wants the draft now instead of within the hour.

**Don't reach for it when.** The role isn't marked Applied — the apply gate exists to ration the flag-risky LinkedIn channel; never spend it on maybes. Or he wants a one-off email to a person he already knows (that's `write-outreach`). Or the JD isn't filed/prepped yet (run `jd-to-ready` first).

**Output.** `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, Gmail draft(s) in Drafts (never sent), and the `STAGED in Gmail <date>` marker in folder + Pipeline row.

**Traceability.** A second, independent fail-closed trace run, run-type `stage-outreach`, required steps {4, 4b, 4c, 5, 6, 7}; `set-role-folder` binds the existing folder (must not create).

**File.** `.claude/skills/stage-outreach/SKILL.md`.

---

### `interview-prep-reusables`

**Intent.** Bootstrap, refresh, or extend the cross-role reusable files at workspace root: `Master Story Bank.md`, `Tell Me About Yourself - Master.md`, `Demo Portfolio.md`, `Outreach Templates.md`, `Resume Achievements Master.md`, plus the quarantine file `Resume Claims To Verify.md`. These are the assets every role's prep pulls from.

**Reach for it when.** Kanu mentions new material that belongs in one of these files — a new project he shipped, a new live demo URL, an outreach pattern that worked, a new role archetype, a new flagship story, a new resume bullet. Or when he says "update story bank", "refresh demo portfolio", "rebuild my prep library", "bootstrap reusables". Or when any of those five files is missing and he wants it seeded.

**Don't reach for it when.** He's editing a file inside a specific `Roles/Company - Role` folder (per-role work stays role-scoped) — unless the change he's making should be pulled out into a master. Or when he's filing a fresh JD (that's intake) or drafting cold email (that's outreach).

**Output.** Surgical edits to the five reusables. The skill prefers edit over rewrite — existing structure stays stable.

**File.** `interview-prep-reusables.skill` at workspace root.

---

### `recruiter-contact-tracker`

**Intent.** Mine Kanu's Gmail for every recruiter, hiring manager, sourcer, and warm referrer he's interacted with, and build/refresh a sortable HTML tracker at `Recruiter Contacts.html`.

**Reach for it when.** Kanu wants a *list* of people he could reach out to — "find my recruiters", "who has reached out to me about a role", "make me a contact list", "build out a list of recruiters", "search my email for hiring people", "refresh my recruiter tracker".

**Don't reach for it when.** He's drafting a single email for a specific role (that's `write-outreach` / `job-outreach`). Or filing one JD (that's `interview-prep-intake`). Or looking up a single person (just answer directly).

**Output.** `Recruiter Contacts.html` at workspace root.

**File.** `recruiter-contact-tracker.skill` at workspace root.

---

## Globally-installed job-search skills (`~/.claude/skills/`)

These are the granular building-block skills installed in Kanu's global Claude skills directory. The workspace-local `jd-to-ready` composes several of them in one pass; reach for these individually when only one step is needed and you don't want the full apply-ready run.

### `tailor-resume`

**Intent.** Tailor Kanu's resume for a specific role — customize bullets, reorder sections, adjust emphasis. Pulls from root `Resume Achievements Master.md`.

**Resume safety rule.** The canonical achievement entries in `Resume Achievements Master.md` are the only default source. Older tailored resumes are outputs, not source material. If a JD seems to need an unsupported metric or stronger platform claim, leave a `[VERIFY: ...]` note for Kanu instead of inventing or importing the claim from `Resume Claims To Verify.md`.

**Reach for it when.** Kanu has a JD (already filed or not) and wants the resume tuned for it without running the full `jd-to-ready` pipeline. Trigger: "tailor my resume for X", "customize bullets for this JD", "rework the resume for the [Company] role".

**Don't reach for it when.** He wants the full apply-ready package (that's `jd-to-ready`). Or he's bootstrapping/refreshing the master itself (that's `interview-prep-reusables`).

**Output.** A tailored resume `.md` (and optional fit-gap report).

---

### `find-contacts`

**Intent.** Surface recruiters, hiring managers, or team members at a target company using the LinkedIn MCP. The pure "who do I reach out to at X?" lookup.

**Reach for it when.** Kanu names a specific company + role and wants the contact list. Trigger: "find recruiters at [Company]", "who's hiring for this", "who should I message at X".

**Don't reach for it when.** He wants the full apply-ready package (that's `jd-to-ready`, which calls this internally). Or he wants the email *drafted* too (that's `write-outreach`). Or he wants every recruiter who's ever emailed him (that's `recruiter-contact-tracker` — Gmail-mined, not LinkedIn-sourced).

**Output.** A ranked list of contacts (name, title, probable email) for one target company.

---

### `write-outreach`

**Intent.** Draft LinkedIn or email outreach for a specific person + role — cold message, follow-up after applying, referral ask.

**Reach for it when.** Kanu has a contact (or has just used `find-contacts`) and wants the message written in his voice. Trigger: "draft a cold email to [Person]", "write the outreach for this role", "send a referral ask to X". This is the granular twin of the JD-level `job-outreach` skill.

**Don't reach for it when.** He wants the full apply-ready pipeline (that's `jd-to-ready`). Or he wants the outreach *templates themselves* updated (that's `interview-prep-reusables` editing `Outreach Templates.md`).

**Output.** A drafted outreach message (length-enforced — LinkedIn note vs. email vs. InMail).

---

### `follow-up`

**Intent.** Draft a follow-up message after an interview, application, or recruiter silence — thank-you notes, nudges after ghosting, application-status check-ins.

**Reach for it when.** A round just happened or silence has stretched and Kanu wants to send something. Trigger: "draft a thank-you for [Interview]", "nudge [Recruiter] — it's been [N] days", "follow up on my [Company] application".

**Don't reach for it when.** It's first-touch cold outreach (that's `write-outreach`). Or he's logging the silence as a status change without sending anything (that's `track-application`).

**Output.** A drafted follow-up message tuned to the situation (post-interview thank-you, ghost-nudge, status check).

---

### `track-application`

**Intent.** Update `Pipeline.md` with a new application status, log notes from recruiter conversations, or record key dates.

**Reach for it when.** Kanu wants to log "I applied", "got a screen", "moved to next round", "rejected", or "withdrew". Trigger: "log that I applied to X", "update pipeline — [Company] moved to onsite", "mark [Company] rejected".

**Don't reach for it when.** He's filing a brand-new JD (that's `interview-prep-intake`, which adds the initial Pipeline row). Or he's editing the auto-memory directly.

**Output.** Updated row(s) in `Pipeline.md` and (if appropriate) the `active_interview_pipeline.md` auto-memory.

> **Note.** The installed `track-application` skill is the one used; do not confuse it with manual edits to `Pipeline.md`. Both work, but the skill keeps row format consistent.

---

### `job-outreach`

**Intent.** Given a specific JD (URL, paste, or file), find likely hiring managers and recruiters at that company, surface their probable email addresses, and draft a warm, personalized cold-outreach email. The JD-level outreach skill (vs. `write-outreach`'s person-level focus).

**Reach for it when.** Kanu shares a JD and wants outreach drafted for it. Trigger language: "draft an outreach email for this JD", "cold email for this role", "help me apply to this job".

**Don't reach for it when.** He wants the JD *filed* without outreach (that's `interview-prep-intake`). Or when he wants the templates themselves updated — not a one-off email — (that's `interview-prep-reusables` touching `Outreach Templates.md`). Or when he wants a *list* of recruiters (that's `recruiter-contact-tracker`).

**Output.** A drafted cold email + identified recruiter/HM names and probable email addresses for one specific JD.

> **Note.** Overlaps significantly with `find-contacts` + `write-outreach` chained together. Reach for `job-outreach` when the JD is the starting point; reach for the two granular skills when starting from a contact list.

---

## Document creation (used opportunistically)

These aren't interview-specific — they're general-purpose skills Kanu invokes when a polished deliverable is the right output. In this workspace they show up rarely; default output is plain markdown that Obsidian renders.

| Skill | When it triggers in this workspace |
|---|---|
| `docx` | When Kanu wants a polished Word doc — e.g., a printable version of a prep schedule, or a formatted resume export for a recruiter who explicitly asks for `.docx`. |
| `pdf` | When he wants a PDF — usually a print-ready resume or a PDF of an interviewer bio. |
| `xlsx` | When he wants a spreadsheet — e.g., a side-by-side comparison of multiple offers. (`Pipeline.md` is the everyday tracker; xlsx is for one-offs that need formulas.) |
| `pptx` | Rare in this workspace. Only if he explicitly asks for a slide deck — maybe an interview presentation. |

---

## How skills overlap — quick decision tree

When Kanu shares a JD or talks about a role, pick the skill by what he wants to *produce*:

**Discovery (no JD shared yet)**
- **"Find me fresh jobs / morning pulse / what's new on LinkedIn"** → `find-fresh-jobs`

**Filing & tracking**
- **"File this / track this / save this"** (one JD) → `interview-prep-intake`
- **"Here are my saved jobs / file all of these / bulk import"** (paste of 3+ LinkedIn saved-job lines) → `linkedin-saved-jobs-intake`
- **"Log that I applied / moved to next round / got rejected"** → `track-application`

**Apply-ready prep**
- **"Get me apply-ready / full intake / I want to apply to this"** → `jd-to-ready` (intake + classification + resume + PDF; **stops at the apply gate** — outreach stages post-apply)
- **"Tailor my resume for this role"** (no intake needed) → `tailor-resume`

**Contacts & outreach**
- **"I applied — stage the outreach / get me the recruiter draft now"** → `stage-outreach` (or just mark the Pipeline row Applied and let the hourly Pass B cron fire it)
- **"Find recruiters at [Company] / who do I email"** (JD-anchored, not yet applied) → `job-outreach` OR `find-contacts` + `write-outreach`
- **"Draft a cold email to [Person]"** (contact already known) → `write-outreach`
- **"Draft a thank-you / nudge a recruiter / follow up"** → `follow-up`
- **"Find me every recruiter who's ever emailed me / build my contact list"** → `recruiter-contact-tracker`

**Library upkeep**
- **"Add this to my story bank / update my prep / new project I shipped"** → `interview-prep-reusables`

**No skill needed**
- **"Draft answers for this interview / build a question bank"** → normal Claude editing in the role folder

When two could apply, remember the apply gate: `jd-to-ready` owns everything up to the apply-ready folder; `stage-outreach` owns everything after the row is marked Applied. A JD share with "and draft outreach too" → run `jd-to-ready`, tell him outreach auto-stages once he applies and marks the row (or kick `stage-outreach` manually right after he applies). Run `interview-prep-intake` alone only when he's clearly *just* filing the JD. Run the granular skills (`find-contacts`, `write-outreach`, `tailor-resume`, `verify-emails`) when only one step is needed and a full orchestrator run would be overkill.

---

## Notes

- The live triggers are in each skill's `description` frontmatter, not in this file. If a skill's behavior seems off, check there first.
- Workspace-local `.skill` files (in this folder) take precedence over globally-installed skills with the same name.
- **Resolved name collisions (2026-05-31):** `tailor-resume`, `write-outreach`, `follow-up`, `find-contacts`, and `track-application` were each installed twice — once at `~/.claude/skills/<name>/` (the correct Interview Prep generation) and once at `~/.claude/skills/job-search/<name>/` (a parallel system rooted at `Projects/Job/`). The job-search twins pulled from a different resume/outreach source and were the root cause of inconsistent, sometimes-fabricated output. **Fixed by renaming the job-search twins to `js-<name>` (folders + `name:` fields + internal cross-references).** See "Where each skill physically lives" and "The fabrication root cause" in the Process Map above. `jd-to-ready` is also installed in both the workspace and `~/.claude/skills/` — that one is intentional and not a conflict (same generation, same sources).
- This file should change when a skill is added, removed, or has its scope meaningfully shifted. Tiny tweaks to a skill's description don't need a Skills.md update — the rule of thumb is "would someone reading this file be misled now?"
- When adding a new skill to this workspace, update both this file and `AGENTS.md` / `CLAUDE.md`'s "Skill triggers worth remembering" list. The two should stay in sync.
