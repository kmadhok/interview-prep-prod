---
name: onboard
description: Set up or selectively refresh a user's interview-prep instance through a conversational interview. Creates profile.yaml and the nine canonical workspace masters, walks required LinkedIn and optional Gmail setup, and finishes with verify_setup.py. Use for first-time setup, "onboard me", or refreshing canonical profile/evidence files. Never silently overwrites an existing instance.
---

# Onboard

Turn a clean clone into a truthful, usable interview-prep instance. This is a
conversation, not a form dump: ask a small group of related questions, reflect back
what you understood, and then move to the next group.

## End-state contract

A completed first run produces:

1. Root `profile.yaml`, using every key declared by `templates/profile.yaml`.
2. `workspace/`, `workspace/Roles/`, and all nine canonical masters copied from the
   template surface.
3. Five filled core masters:
   - `Resume Achievements Master.md`
   - `Master Story Bank.md`
   - `Tell Me About Yourself - Master.md`
   - `Job Search Target Profile.md`
   - `Application Profile.md`
4. The other four masters either filled from supplied evidence or copied with an
   explicit onboarding follow-up note.
5. A walkthrough of required LinkedIn MCP setup and Gmail draft staging.
6. A final `python3 scripts/verify_setup.py` run whose table is reported verbatim.

## Non-negotiable evidence rule

Never invent an employer, title, project, metric, outcome, skill, date, client,
credential, work-authorization fact, or compensation answer. Use only the user's
resume, pasted history, and explicit answers. When a useful number is unknown, write
`[NUMBER?]`; do not estimate. Put plausible-but-unconfirmed legacy claims in
`Resume Claims To Verify.md`, never in outward-facing masters.

## Re-run safety

Before asking setup questions, check for root `profile.yaml` and the nine files under
`workspace/`.

- If none exist, run the fresh flow below.
- If any exist, show which ones exist and ask which specific files the user wants to
  refresh. Treat existing text as canonical user data.
- Never pass a blanket overwrite flag. The deterministic helper requires one
  `--refresh "<filename>"` argument per approved file and leaves every other file
  untouched.
- If the requested refresh depends on new evidence, gather that evidence before
  writing. Do not rewrite unaffected sections for style.

## Fresh interview flow

### 1. Identity and file naming

Gather every field in `templates/profile.yaml`: name, email, LinkedIn, GitHub,
resume filename pattern, and timezone. Recommend the template filename pattern
unless the user has a preference. Read the template at runtime; do not hardcode its
key list.

### 2. Resume evidence

Ask for a current resume or a chronological work-history summary. For each role,
capture title, employer, dates, what the user owned, two to four strongest outcomes,
and the proof behind each outcome. Separate verified facts from claims needing
confirmation. Draft `Resume Achievements Master.md` with stable achievement IDs,
canonical bullets, proof points, theme tags, and a theme index.

### 3. Story bank

Select three to five high-coverage stories from the verified achievement set. Ask
only for missing situation, decision, conflict, failure, adoption, and result beats.
Seed `Master Story Bank.md` using the template's structure. Every proof point must
resolve to the evidence collected in step 2.

### 4. Positioning and target roles

Ask what the user does now, the through-line in their career, the roles they want,
and the interviewer follow-up they want to invite. Draft the role-agnostic TMAY
spine and the closest recurring archetype variant. Then gather target titles,
location/remote constraints, compensation floor, interview-format preferences,
hard skips, and strong pulls for `Job Search Target Profile.md`.

### 5. Application facts

Gather salary wording, work authorization, sponsorship need, notice period,
location/relocation stance, phone, links, and any standard short answers. Copy these
facts into `Application Profile.md` without inference. Sensitive facts stay in the
gitignored instance, never under `templates/`.

### 6. Optional masters

Ask one short closing question: does the user already have demo links, project
walkthrough material, outreach examples that sound like them, or unverified legacy
claims? Fill the corresponding masters when evidence exists. Otherwise retain each
starter and append the helper's explicit follow-up note.

## Deterministic write path

Assemble a temporary JSON file with this shape:

```json
{
  "profile": {
    "<every templates/profile.yaml key>": "<interview answer>"
  },
  "masters": {
    "Resume Achievements Master.md": "<complete markdown>",
    "Master Story Bank.md": "<complete markdown>",
    "Tell Me About Yourself - Master.md": "<complete markdown>",
    "Job Search Target Profile.md": "<complete markdown>",
    "Application Profile.md": "<complete markdown>"
  }
}
```

Run:

```bash
python3 scripts/onboard_workspace.py --answers "<temporary answers.json>"
```

For an approved re-run, include only the refreshed content and add one explicit
argument per file:

```bash
python3 scripts/onboard_workspace.py --answers "<temporary answers.json>" \
  --refresh "Master Story Bank.md"
```

Delete the temporary answers file after a successful write. If the helper refuses,
report the error and do not work around its overwrite protection with ad hoc file
commands.

## Connector walkthrough

Walk the user through `docs/onboarding/linkedin-mcp.md`. LinkedIn HTTP transport is
required; stdio is forbidden, calls are sequential, and launchd owns the daemon.
Then walk through `docs/onboarding/gmail.md` for draft staging. The safety model is
draft-never-send: every outward action retains a human review gate.

## Finish and report

Run the full check without `--skip-live`:

```bash
python3 scripts/verify_setup.py
```

Report its table exactly. A reportlab warning is acceptable. A LinkedIn failure is
not complete onboarding: return to the connector guide and repair it. Use
`--skip-live` only for a clearly labeled machine-only dry run, never to claim the
friend-test onboarding is complete.
