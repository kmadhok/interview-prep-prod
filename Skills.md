# Skill map

This is the quick routing guide. The `description` frontmatter in each
`.claude/skills/<name>/SKILL.md` remains the trigger authority.

## Primary workflow

| Intent | Skill | Result |
| --- | --- | --- |
| Set up a clean clone or refresh canonical evidence | `onboard` | Profile, nine masters, connector walkthrough, setup verification |
| File one JD for tracking only | `interview-prep-intake` | Role folder, JD, Pipeline row |
| Prepare a JD to apply | `jd-to-ready` | Intake, classification, tailored resume/PDF, apply packet; stops at apply gate |
| Stage outreach after applying | `stage-outreach` | Contacts, verified/flagged emails, outreach file, Gmail drafts; never sends |
| Log an application-state change | `track-application` | Deterministic Pipeline update |
| Draft a thank-you or nudge | `follow-up` | Reviewable message text |

The main decision is the apply gate:

```text
Track only ───────────────▶ interview-prep-intake
Prepare to apply ─────────▶ jd-to-ready ──▶ human applies
Applied row, no STAGED ───▶ stage-outreach ──▶ human reviews and sends
```

## Discovery and intake

| Skill | Use when | Do not use when |
| --- | --- | --- |
| `find-fresh-jobs` | Find a new read-only batch matching the Job Search Target Profile. | The user already selected a role to file. |
| `verify-postings` | Check whether not-yet-applied Pipeline postings are still live. | Finding new roles or preparing a resume. |
| `linkedin-saved-jobs-intake` | Bulk-file three or more jobs pasted from LinkedIn Saved Jobs. | Filing one JD or running apply-ready prep for one role. |

## Pipeline primitives

Orchestrators compose these. Invoke one directly only when the user wants that single
piece.

| Skill | Owns |
| --- | --- |
| `tailor-resume` | Canonical-evidence-only resume tailoring. |
| `find-contacts` | Team-aware recruiter, hiring-manager, and peer discovery. |
| `enrich-contacts` | Activity-derived contacts and truthful personalization hooks. |
| `verify-emails` | Email resolution, verification, and explicit degraded status. |
| `write-outreach` | Voice-locked outreach and Gmail draft creation; never sends. |
| `linkedin-mcp-operations` | HTTP transport, sequential-call discipline, and daemon recovery. |

## Libraries and analysis

| Skill | Use when |
| --- | --- |
| `interview-prep-reusables` | A new verified project, story, demo, bullet, archetype, or outreach pattern belongs in a cross-role master. |
| `recruiter-contact-tracker` | Build or refresh the Gmail-derived reusable contact tracker. |
| `skill-loop-trainer` | Improve a skill against a user-supplied gold output in isolated worktrees. |
| `two-orchestrator-e2e-test` | Run the isolated full-pipeline contract test; never touches the live workspace. |

## Safety and source rules

- Resume content comes from `workspace/Resume Achievements Master.md` only by default.
- `workspace/Resume Claims To Verify.md` is quarantined until the user verifies and
  promotes a claim.
- Cross-role content belongs in canonical masters; role folders select and tailor it.
- LinkedIn calls use the HTTP MCP daemon sequentially, never in parallel.
- Contact research starts only after the Pipeline row is `Applied`.
- Gmail actions create drafts only. The user reviews, attaches files, and sends.
- Only `stage-outreach` writes `STAGED in Gmail <date>` after its deterministic gate.

For setup, use `docs/onboarding/`; for optional schedulers, use `infra/`; for behavior
verification, use `evals/` and `scripts/build_fixture_workspace.py`.
