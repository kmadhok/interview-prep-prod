# Intent: Productionalization (`productionalized_version` branch)

Confirmed 2026-07-06 via interview. This is the statement of intent that all specs,
plans, and implementation work on this branch should trace back to.

## Confirmed Intent

- **Outcome:** The interview-prep system rebuilt on `productionalized_version` as a
  product others can adopt — every agent action traceable to its reason, prompt, and
  source file (so users can fix outputs themselves), all hidden infrastructure (cloud
  routines, cron jobs) declared in the repo with docs, and a conversational onboarding
  that builds each user's own resume-achievements and email-voice files plus
  Gmail/LinkedIn plugin setup.
- **User:** Friends first, GitHub strangers later — and throughout, hiring managers and
  peers reading it as proof Kanu builds traceable, maintainable agent systems (context
  engineering as portfolio signal).
- **Why now:** Kanu found a role he'll accept; the tool is graduating from personal
  utility to something built for others.
- **Success:** A friend clones it, self-onboards, runs jd-to-ready on a real JD, and can
  open the trace and follow output → skill → prompt → markdown file to tune it — without
  Kanu next to them.
- **Constraint:** The live system on `main` (drip runner, cloud routines, the active
  pipeline) keeps running untouched; all work isolated to this branch.
- **Out of scope:** Token/internal-reasoning capture (actions + reasons only),
  non-Claude harnesses for v1 (portability is architecture discipline, not tested
  support), and any hard deadline.

## Key design positions surfaced during the interview

1. **Trace = debuggability chain, not observability for its own sake.** Every
   output must be traceable to: which skill ran → which prompt → which static file it
   referenced. The trace is the user's repair manual — "I don't like this email draft"
   resolves to "edit this markdown file."
2. **Work-log contract.** Every orchestrator / jd-to-ready run emits a structured log
   file (markdown or JSON) of every action taken, tied to a reason and the prompt/file
   that produced it. Token-level and internal-reasoning capture is explicitly conceded
   as out of reach; actions + reasons is the contract.
3. **Infrastructure manifest.** Cloud routine jobs and cron jobs currently run
   undeclared, outside the repo. All scheduled automation must be defined, documented,
   and reproducible in-repo, with the user educated on setup and given the choice:
   install the automation, or invoke it manually on demand.
4. **Onboarding as conversation.** New users tune the system by talking to the model:
   an interview builds their own Resume Achievements Master, their email/outreach voice
   preferences, and walks them through Gmail + LinkedIn MCP plugin setup.
5. **Model-agnostic as architecture, not test matrix.** v1 runs on Claude Code only.
   Portability (Codex, Gemini, Cursor) is achieved by keeping all logic in portable
   markdown/JSON contracts with no harness-specific magic in the core, and documented
   as a design principle.
6. **Personal-data/template split.** Kanu's own data (Pipeline, contacts, resume
   content) must be separated from the shareable template for others to adopt it.

## Workstreams (for downstream spec/plan)

1. Trace / work-log contract
2. Infrastructure manifest (cloud routines + cron, declared and reproducible)
3. Conversational onboarding flow (resume achievements, email voice, plugin setup)
4. Personal-data / template split
