# ADR-004: Move Pipeline-row and role-folder mutations into deterministic tools

- **Status:** Accepted
- **Source commit(s):** `bee9830` (feat: deterministic pipeline-row + role-folder tools; skills call them)
- **Confidence:** HIGH

## Context

Three skills described direct edits to `Pipeline.md` and role-folder naming, leaving table shape, STAGED eligibility, and collision handling to an LLM.

The full commit changes `.claude/skills/interview-prep-intake/SKILL.md`, `.claude/skills/stage-outreach/SKILL.md`, `.claude/skills/track-application/SKILL.md`, `scripts/pipeline_row.py`, `scripts/role_folder.py`, `scripts/test_pipeline_row.py`, `scripts/test_role_folder.py`.

## Decision

Make `scripts/pipeline_row.py` the owner of add/mark/stage/get mutations and `scripts/role_folder.py` the owner of canonical folder names and collision refusal; skills invoke those commands.

## Alternatives evidenced by history

The removed skill prose instructed agents to hand-edit rows and construct folders themselves.

## Consequences verified in later/current code

The STAGED invariant and naming collision behavior are executable and unit-tested instead of prompt-dependent; callers must use the helper CLI contract.

## Questions for Kanu

None; the cited diff, parent behavior, and current tree support the statements above.
