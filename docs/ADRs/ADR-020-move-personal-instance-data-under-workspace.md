# ADR-020: Move personal instance data under workspace

- **Status:** Accepted
- **Source commit(s):** `98c6d87` (refactor: move all personal/instance data under workspace/)
- **Confidence:** HIGH

## Context

The repository mixed reusable skills/scripts with named resumes, role folders, and canonical personal masters at the root.

The full commit changes `.gitignore`, `workspace/AI Build Walkthrough - Master.md`, `workspace/Application Dashboard.md`, `workspace/Application Profile.md`, `workspace/Data Agent Startup Shortlist.md`, `workspace/Demo Portfolio.md`, `workspace/Job Search Target Profile.md`, `workspace/LinkedIn About Section.txt`, `workspace/Master Story Bank.md`, `workspace/Outreach Templates.md`.

## Decision

Keep reusable blank starters under `templates/`; put the active profile at root `profile.yaml` and every personal working artifact under `workspace/`, with setup performed by onboarding.

## Alternatives evidenced by history

Continue shipping a clone whose root files double as one person’s live instance, or use populated files as templates.

## Consequences verified in later/current code

A clean clone no longer supplies identity facts. Path resolution and personal-reference tests must preserve the template/instance boundary; existing private data was migrated, not regenerated.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
