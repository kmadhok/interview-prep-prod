# ADR-017: Separate blank templates from private workspace instances

- **Status:** Accepted
- **Source commit(s):** `736933a` (feat: blank canonical templates + workspace-aware agent guides)
- **Confidence:** HIGH

## Context

The repository mixed reusable skills/scripts with named resumes, role folders, and canonical personal masters at the root.

The full commit changes `AGENTS.md`, `CLAUDE.md`, `templates/Application Profile.md`, `templates/Job Search Target Profile.md`, `templates/Master Story Bank.md`, `templates/Outreach Templates.md`, `templates/Resume Achievements Master.md`, `templates/Tell Me About Yourself - Master.md`, `templates/profile.yaml`.

## Decision

Keep reusable blank starters under `templates/`; put the active profile at root `profile.yaml` and every personal working artifact under `workspace/`, with setup performed by onboarding.

## Alternatives evidenced by history

Continue shipping a clone whose root files double as one person’s live instance, or use populated files as templates.

## Consequences verified in later/current code

A clean clone no longer supplies identity facts. Path resolution and personal-reference tests must preserve the template/instance boundary; existing private data was migrated, not regenerated.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
