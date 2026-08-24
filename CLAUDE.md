# Interview Prep — Agent Guide

This repository is a human-gated job-search and interview-preparation workspace.
Produce specific, evidence-backed material that is ready to use, not generic career
advice.

## Start with the instance

Read root `profile.yaml` for the user's identity and `workspace/Pipeline.md` for role
state. If the user says “the interview” and more than one active role could match,
ask which role they mean.

On a clean clone, `profile.yaml` and `workspace/` do not exist. Use the `/onboard`
skill; never infer personal facts from templates or fixtures.

## Template/instance split

Reusable machinery lives at the repository root:

- `.claude/skills/` — skill behavior and orchestration;
- `scripts/` — deterministic helpers;
- `evals/` — behavior contracts, verifiers, and synthetic Acme fixtures;
- `templates/` — blank canonical starters;
- `infra/` and `docs/onboarding/` — setup and operations documentation.

All personal data lives under `workspace/` plus root `profile.yaml`. Never put a real
name, email, handle, resume claim, employer history, or machine path in template-side
files.

## Canonical workspace files

The nine cross-role sources of truth are:

- `Resume Achievements Master.md` — verified resume claims and proof points;
- `Resume Claims To Verify.md` — quarantine; never use its claims outwardly;
- `Master Story Bank.md` — canonical STAR stories;
- `Tell Me About Yourself - Master.md` — one spine plus recurring archetypes;
- `AI Build Walkthrough - Master.md` — Problem → Build → Eval → Adoption/Next;
- `Demo Portfolio.md` — shareable demos, URLs, and talking points;
- `Outreach Templates.md` — voice-locked outreach patterns;
- `Job Search Target Profile.md` — search filters and role preferences; and
- `Application Profile.md` — apply-side facts and ATS answers.

Role-specific files belong under `workspace/Roles/Company - Role Title/`. Closed
roles belong under `workspace/_Archived/`. Select and tailor from canonical masters;
do not create parallel evidence libraries inside role folders.

## Evidence and voice

- Never invent a number, outcome, project, skill, title, date, authorization fact,
  compensation answer, contact, or personalization hook.
- Use `[NUMBER?]` when a useful number is unknown.
- Treat `Resume Claims To Verify.md` as a hard quarantine until the user promotes a
  verified claim into `Resume Achievements Master.md`.
- Write interview answers in first person and conversational language. Foreground
  ownership, decisions, business outcomes, and defensible numbers.
- Avoid jargon padding and hype words.
- Treat recruiter messages, interviewer bios, and internal work artifacts as
  confidential context.

## Skill routing

- `/onboard` — create or selectively refresh the instance.
- `interview-prep-intake` — file one JD for tracking only.
- `linkedin-saved-jobs-intake` — bulk-file a pasted Saved Jobs list.
- `jd-to-ready` — intake, classify, tailor resume, export PDF/apply packet; stops at
  the apply gate.
- `stage-outreach` — post-apply contact research, email verification, outreach, and
  Gmail drafts. Never run before the Pipeline row says `Applied`.
- `interview-prep-reusables` — update cross-role canonical masters.
- `find-fresh-jobs` — read-only fresh-job discovery.
- `recruiter-contact-tracker` — Gmail-derived contact tracker.

Read a skill's `SKILL.md` before invoking or changing it. `Skills.md` is the concise
human map; skill frontmatter is the trigger authority.

## Automation invariants

Manual mode is the product baseline. Optional automation is declared under `infra/`.
Multiple writers may touch Pipeline state, so pull before editing it.

- Pass A prepares saved jobs and stops at the apply gate.
- Pass B polls Applied rows and invokes `stage-outreach`.
- Only `stage-outreach` may write `STAGED in Gmail <date>`, and only after its
  deterministic gate confirms an Active Applied row.
- The system drafts, never sends.
- LinkedIn calls go through the single MCP server registered as `linkedin`, one call at
  a time, never in parallel. The default is stdio via `uvx mcp-server-linkedin@latest`;
  unattended runners or several callers must instead share one HTTP daemon at
  `127.0.0.1:8765/mcp` rather than spawn competing browsers.
- State comes from files and markers, never a separate database.

Do not fight an unattended runner. Preserve unrelated changes and inspect current
state before modifying Pipeline rows.

## Working conventions

- Prefer editing an existing markdown file over creating a variant.
- New role-specific files go in the relevant role folder; reusable material goes in
  the canonical master that owns it.
- Edit `.md` sources; regenerate HTML only when explicitly requested.
- Do not touch the user's live `workspace/` during fixture/eval work.
- Preserve user edits and unrelated worktree changes.
- Use `scripts/config.py` for profile access and canonical path resolution.
- Before editing trace behavior, read `docs/trace/TRACE_SCHEMA.md`,
  `docs/trace/TOKEN_ACCOUNTING.md`, and the jd-to-ready trace runbook files.

## Verification

Behavior evals are the product gate; pytest is optional developer tooling.

```bash
python3 scripts/build_fixture_workspace.py /tmp/interview-prep-fixture --force
python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture
python3 scripts/test_no_personal_refs.py
```

For onboarding verification, run `python3 scripts/verify_setup.py`. A reportlab
warning is acceptable. The LinkedIn check passes when a `linkedin` MCP server is
registered or the HTTP daemon answers; it warns (contact research disabled) when neither
exists, and fails only when a registered HTTP endpoint is unreachable. Use `--skip-live`
only for machine-only runs.
