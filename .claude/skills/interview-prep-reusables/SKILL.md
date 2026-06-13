---
name: interview-prep-reusables
description: Use whenever Kanu Madhok wants to bootstrap, refresh, or extend the cross-role reusable files at the root of his Interview Prep workspace at /Users/kanumadhok/Documents/Claude/Projects/Interview Prep/ — Master Story Bank.md, Tell Me About Yourself - Master.md, Demo Portfolio.md, Outreach Templates.md, Resume Achievements Master.md. Trigger on explicit language ("update story bank", "refresh demo portfolio", "add outreach template", "rebuild TMAY master", "bootstrap reusables", "rebuild prep library") AND on bare mentions of new material for these files — a new project shipped, a new live demo URL, an outreach pattern that worked, a new role archetype, a new flagship story, a new resume bullet — or when these files are missing and he wants them seeded. Do NOT trigger for JD intake (use interview-prep-intake), cold outreach drafting (use job-outreach), or per-role prep edits inside a Company - Role folder. If ambiguous between cross-role and per-role, ask before invoking.
---

# Interview Prep — Cross-Role Reusables

This skill bootstraps and maintains the five root-level reusable files in Kanu's Interview Prep workspace. These are the cross-role assets that role-specific prep folders pull from — when a new role enters the pipeline, the interview-answer drafting, TMAY tailoring, resume tailoring, and outreach drafting all start from these files instead of being rebuilt from scratch.

Read the root `AGENTS.md` (or `CLAUDE.md`) in the Interview Prep folder before you start — the workspace conventions there are the source of truth and may have evolved since this skill was written. The steps below describe the workflow as of when this skill shipped.

## Where things live

- Workspace root: `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/`
- The five reusables, all at root:
  - `Resume Achievements Master.md` — canonical resume bullet library with phrasing variants, proof points, theme tags, and a theme→achievement index
  - `Master Story Bank.md` — STAR stories with beats, canonical lines, anticipated follow-ups, proof points, theme tags
  - `Tell Me About Yourself - Master.md` — base spine + archetype variants (Agent Builder, Consulting/Product Builder, FDE/client-facing)
  - `Demo Portfolio.md` — canonical descriptions, URLs, talking points for live demos and Walmart-internal artifacts
  - `Outreach Templates.md` — voice-locked templates for every outreach situation, with a per-archetype hook bank
- Source content the reusables draw from:
  - Each `Roles/Company - Role/Interview Answers.md` — story drafts in Kanu's voice
  - Each `Roles/Company - Role/Tell Me About Yourself - Cue Card.md` — role-tuned openers
  - Each `Roles/Company - Role/Messages with Recruiter.md` — outreach patterns that already worked
  - Each `Roles/Company - Role/Job Description.md` — role archetype signal
  - The auto-memory file `active_interview_pipeline.md` — which roles are live

If the user is in a different workspace and you can't find this structure, ask before assuming. Don't create the workspace from scratch.

## Modes

This skill runs in one of three modes — pick based on context, don't ask the user which:

- **Bootstrap.** One or more of the five reusables doesn't exist yet. Build it from existing role folders + auto-memory + the resume master.
- **Refresh.** Kanu mentioned new material (a new project, a new demo URL, an outreach pattern that landed, a new role archetype). Surgically update the relevant file(s) — don't rewrite anything that's already working.
- **Audit.** Kanu wants a sanity pass before a new round of interviews — check for staleness ([NUMBER?] placeholders never filled in, dead demo URLs, outdated project lists, archetype variants that no longer match active pipeline roles). Surface findings + propose targeted fixes; don't blindly rewrite.

If you can't tell which mode applies from context, ask Kanu in one short question — don't trigger a whole interview.

## Workflow

### 1. Orient

Before editing anything:

- Read `AGENTS.md` (or `CLAUDE.md`) at the workspace root.
- List existing root files. Note which of the five reusables exist and when each was last modified.
- Read `active_interview_pipeline.md` from the auto-memory directory (path is in your system prompt — it lives under `Library/Application Support/Claude/.../spaces/<space-id>/memory/`). This tells you which roles are live and what archetypes are in play.
- Skim the existing reusable files you'll touch. The goal is not to rewrite — it's to add, refresh, or fix specific sections.

This is fast — under 60 seconds with the right reads. Don't over-research.

### 2. Identify what changed (refresh mode)

Most invocations are refresh, not bootstrap. The unit of work is figuring out what new information Kanu surfaced and which file it belongs in. Common patterns:

| What Kanu said / did | File(s) to update |
|---|---|
| Shipped a new project / system | `Master Story Bank.md` (new story entry), `Resume Achievements Master.md` (new bullet + variants), `Demo Portfolio.md` (if public-facing) |
| Has a new live demo URL or redeployed an existing one | `Demo Portfolio.md` (URL + last-verified date) |
| Got a new piece of feedback or learned something about his own work | `Master Story Bank.md` — fill a `[TO DRAFT]` slot or add a canonical line to an existing story |
| Tried a new outreach phrasing and it worked (or didn't) | `Outreach Templates.md` — extend the relevant template or hook bank |
| Picked up a new role archetype not yet covered | `Tell Me About Yourself - Master.md` (new variant) and `Outreach Templates.md` (new hook in the hook bank) |
| Verified a `[NUMBER?]` placeholder with a real number | Find every occurrence across the reusables and replace |
| Confirmed a story is wrong or needs cutting | Remove or rewrite — don't leave half-rewritten beats |

When in doubt about which file a piece of content belongs in, default to **the most specific** — if it's a one-line outreach phrasing, that's `Outreach Templates.md`; if it's a story arc, that's `Master Story Bank.md`. If it's both (e.g., a project that's now a story AND a resume bullet AND a demo), update all the relevant files in the same pass — don't make Kanu come back tomorrow.

### 3. Edit (don't rewrite)

Prefer `Edit` over `Write` on existing files. The reusables are long and most of the content is correct; surgical edits keep the file's structure stable for Obsidian and keep diffs reviewable. Full rewrites are only justified when the file's structure itself needs to change.

When adding a new story to `Master Story Bank.md`:

- Assign a story ID. Use `S-<refid>` where `<refid>` is the matching Resume Achievements Master entry (e.g., `S-A4` for resume A4 Jira agent). If there's no resume entry, use a descriptive suffix (`S-CAREER`, `S-FEEDBACK`).
- Update the **Theme → Story map** at the top of the file so the new story is discoverable.
- Fill the standard story template: one-line hook, theme tags, 5 beats, canonical lines, anticipated follow-ups, proof points, cut-down version. Don't ship a story without proof points — that's the whole point of the bank.

When adding a new resume bullet to `Resume Achievements Master.md`:

- Place it under the right job header (current role at Walmart, FTI, Innovare, Baker Tilly, education, etc.). Don't sprawl into a new top-level section unless the new bullet doesn't fit any existing job.
- Always provide the canonical bullet + at least one variant phrasing. Same fact, different surface, so the bullet can be tuned per JD without rewriting.
- Update the **Quick-Reference Theme Index** at the bottom — every achievement needs to be findable by theme.

When adding a TMAY variant:

- Match the existing structure: archetype name, use-for line, closing line, strongest-hook note, full version, hooks-ranked list, what-changes-from-other-variants commentary.
- Variants should be archetype-level (e.g., "founder/startup CTO", "research scientist"), not role-level. If a role just needs minor tuning of an existing variant, that's per-role work, not a new master variant.

When adding to `Demo Portfolio.md`:

- A new demo gets a full block: header-line for the resume contact block, demo URL (or `[TO ADD]`), repo link, last-verified date, one-sentence pitch, canonical talking points, best-for archetype list, watch-outs.
- Internal Walmart artifacts go in the table near the bottom — don't write a full block for non-linkable items.

When adding to `Outreach Templates.md`:

- Place new templates in the numbered sequence (cold recruiter → thank-you → nudge → cold HM → post-interview thank-you → application follow-up → networking → decline). If the new template doesn't fit one of these, add a new numbered section — but first check whether it's actually a variant of an existing template rather than a new category.
- The hook bank at the top of "Cold recruiter — initial outreach" is where archetype-tuned value-prop sentences live. New archetypes get a new hook bullet; new phrasings for existing archetypes get appended.

### 4. Maintain voice + conventions

These rules come from `AGENTS.md` and apply to everything you write into the reusables:

- **First person, conversational.** Read it out loud — if it doesn't sound like Kanu talking, rewrite.
- **No corporate filler.** No "leverage," "spearhead," "synergize," "hope this finds you well," "I'm thrilled to."
- **Real numbers only.** If a number isn't verified, use `[NUMBER?]` as a placeholder — never invent.
- **Obsidian-friendly markdown.** No exotic frontmatter, fenced code blocks fine, internal `[[wiki links]]` allowed.
- **Don't paraphrase existing voice.** When pulling content from a role folder's `Interview Answers.md` into the master Story Bank, keep Kanu's phrasing — don't rewrite it into something more "polished."
- **Confidentiality.** Recruiter messages and interviewer bios are confidential. You can lift outreach *patterns* into `Outreach Templates.md` (e.g., "this short post-screen thank-you pattern got a 23-min reply from Ganna at BCG X — keep it") but don't paste verbatim recruiter content into outward-facing templates.

### 5. Report back

Keep the recap short. Kanu just told you what changed — he knows the substance. He wants to see what landed where.

Include:

- A `computer://` link to each reusable file you edited.
- One line per file describing what changed (e.g., "added S-A10 hybrid-orchestrator story under the Theme→Story map; updated the technical-depth row").
- Any `[NUMBER?]` placeholders you left behind, so Kanu can fill them on his work laptop later.
- Any inconsistency you noticed but didn't fix (e.g., "the Demo Portfolio still has `[TO ADD]` for the Cloud Run URL — want me to confirm it's live and patch?").
- If you touched something across multiple files (e.g., a new project that became a story + a resume bullet + a demo), say so explicitly so the cross-file consistency is visible.

Don't restate the new content verbatim — Kanu can read the files himself. Don't pad with motivational fluff or "let me know if you'd like anything else."

## File structures (for bootstrap mode)

If a reusable file doesn't exist yet, follow these structures. Each file should open with a **Purpose** line + a **How to use** block so future-Claude (and Kanu) know what the file is for.

### `Master Story Bank.md`

```
# Master Story Bank — Kanu Madhok

[Purpose + How to use + Conventions]

## Theme → Story map
[ordered list of themes → which story IDs fit each]

## Stories

### S-<id> — <name>
**One-line hook.**
**Theme tags.**
**Best for.**
### Beats
[5 beats]
### Canonical lines I want pulled
### Anticipated follow-ups
### Proof points
### Cut-down version (60–90 seconds)

[repeat per story]

## Stories I still need to draft
[slots for question types where Kanu doesn't yet have a polished story]

## Notes for tailoring
[per-archetype guidance on which stories to lead with]
```

Aim for 8–12 stories. Fewer = the file isn't pulling enough weight. More = sprawl; fold related stories together.

### `Tell Me About Yourself - Master.md`

```
# Tell Me About Yourself — Master

[Purpose + How to use]

## The spine (role-agnostic)
[5 beats: Present → Shift → Built → Recognition → Why]

# Variant A — <archetype>
**Use for:** ...
**Closing line:** ...
**Strongest hook to plant:** ...
**Full version:** [the full ~90-second spoken text]
**Hooks ranked by likelihood of follow-up:** ...

[repeat per variant]

# Variant tuning checklist
[pre-delivery sanity checks]

# Notes
[when to swap which variant; what universally stays]
```

Aim for 3 variants — covering the main archetypes Kanu is interviewing for. Don't proliferate.

### `Demo Portfolio.md`

```
# Demo Portfolio

[Purpose + How to use]

# Demo 1 — <name> (default)
**Header line (drop-in for resume):** ...
**Demo URL:** ...
**Repo / source:** ...
**Last verified live:** ...
### One-sentence pitch
### Canonical talking points
### Best for
### Watch-outs

[repeat per public-facing demo]

# Internal Walmart artifacts (referenced, not linkable)
[table: artifact | internal name | one-liner | story ID]

# Pre-interview demo checklist
[the morning-of-interview checks]

# Demo gaps / what to build next
```

### `Outreach Templates.md`

```
# Outreach Templates

[Purpose + Voice rules + Signature block]

# 1. Cold recruiter — initial outreach
### Template
### Hook bank (per role archetype)
### Length target

# 2. Post-recruiter-screen thank-you (same day)

# 3. Recruiter nudge — after "I'll get back to you next week"

# 4. Cold hiring manager / engineering lead

# 5. Post-interview thank-you (per panelist)

# 6. Application follow-up — no response after N days

# 7. Networking / mutual-connection ask

# 8. Decline / pause an outreach gracefully

# Outreach tracker — quick log
[table for date | to | role | channel | type | response | next action]

# Notes
```

### `Resume Achievements Master.md`

Already exists in Kanu's workspace as the canonical pattern — match its structure when adding new content. Key conventions: per-job sections, achievement entries with `Tags`, canonical bullet, variants, proof points, backstory. Plus a Skills block, Education, Honors, and a Theme Index at the bottom.

## Edge cases

- **Reusables file exists but has been edited by Kanu since the last refresh.** Treat his edits as canonical — don't overwrite them. Identify what's new and surgically add it.
- **The story Kanu wants to add already exists under a different name.** Don't duplicate. Extend the existing story with the new beat or proof point. Note the rename in the report-back.
- **Kanu shares an outreach pattern that worked but it's specific to one recruiter (e.g., "Ganna replied fast to this short thank-you").** Lift the *pattern*, not the recruiter-specific content. Reference the successful instance in the template's "Real-world reference" line, but the template itself should be archetype-generic.
- **A `[NUMBER?]` placeholder shows up in multiple files for the same fact.** Treat them as one fact with multiple homes. When Kanu verifies the number, fix all instances in the same pass — and tell him you did, so he doesn't re-ask.
- **Kanu mentions a role archetype that doesn't have a TMAY variant yet, but might be a one-off (e.g., a single interview at a research lab).** Don't create a new master variant for a one-off. Build the variant inside the role folder's `Tell Me About Yourself - Cue Card.md` instead. Only promote it to the master file if the archetype is going to recur.
- **Conflict between the Resume Achievements Master and the Master Story Bank for the same project.** The Resume Master is the source of truth for *numbers and proof points*. The Story Bank is the source of truth for *narrative arcs and canonical lines*. When they conflict on a number, fix the Story Bank to match the Resume Master.
- **Kanu asks you to make the reusables "shorter."** First ask which file — they have different purposes and tolerate different lengths. Story Bank is allowed to be long because depth matters in interview answers; Outreach Templates should be tight because templates need to scan fast.
- **Workspace doesn't exist at the expected path.** Don't create it. Tell Kanu the path you're looking for and ask whether he's working from a different workspace.

## Anti-triggers

Do NOT use this skill for:

- **JD intake.** When Kanu shares a fresh JD he wants filed (creating a new role folder, writing `Job Description.md`, updating `Pipeline.md`), use `interview-prep-intake` instead.
- **Cold outreach drafting for a specific named role.** When Kanu wants the actual cold-email written + sent for a JD (with recruiter/HM lookup), use `job-outreach`. This skill maintains the *templates* the email is drafted from; it doesn't draft the email itself.
- **Per-role prep file edits.** When Kanu wants to refine `Interview Answers.md` or `7-Day Prep Schedule.md` inside a specific `Company - Role` folder, that's normal Claude editing. Only invoke this skill if the change he's making should be pulled out into the cross-role reusables.
- **Pipeline tracker maintenance.** When Kanu is moving a row between Active / Considering / Closed in `Pipeline.md`, that's a manual edit (or part of `interview-prep-intake` for new rows). Not this skill.
- **Memory updates.** Auto-memory entries belong in the memory system, not the reusables. This skill doesn't write to memory directly.

If both this skill and another could apply and the user is ambiguous, ask which they want before invoking either.

## Voice for the report-back

Kanu reads the report at a glance. Be concrete and tight:

- Bad: "I've completed an extensive update to your interview preparation reusables, incorporating the new project you mentioned with detailed integration across multiple files."
- Good: "Added S-A11 (geo-readiness agent) to `Master Story Bank.md` and a new bullet under Walmart in `Resume Achievements Master.md`. One `[NUMBER?]` left — the geo-readiness adoption count. Both demo + outreach files unchanged."

Specific file names, specific story IDs, specific placeholders left behind. That's the format.
