# skill-loop-trainer templates

Generalized copies of the `Write Outreach Test/` harness docs. The orchestrator (the `skill-loop-trainer`
SKILL.md process) copies these into a new `<Name> Test/` folder and fills the `{{PLACEHOLDERS}}`:

| Placeholder | Meaning | Example (write-outreach run) |
|-------------|---------|------------------------------|
| `{{TARGET_SKILL}}` | skill being improved | `write-outreach` |
| `{{NAME}}` | harness folder name | `Write Outreach` (→ `Write Outreach Test/`) |
| `{{SLUG_BASE}}` | worktree branch prefix | `wo` (→ `wo-test/claude`, `.claude/worktrees/wo-claude`) |
| `{{GOLD_NOUN}}` | what the gold example is | `cold-recruiter email` |
| `{{OUTPUT_NOUN}}` | what each model produces | `email` |
| `{{N}}` | number of fixtures | `3` |
| `{{HARD_GATES}}` | the target skill's mechanical invariants | em-dash gate, 50-125 words, banned phrases, signature |
| `{{DIMENSIONS}}` | rubric dims from the gold example's traits | relevance_match, urgency_social_proof, voice... |

Files:
- `SPEC.md` — what + why, task contract, test set, invariants, scoring, worktree matrix.
- `ACCEPTANCE.md` — reproducibility gate + mechanical hard gates + judge schema + scoring math.
- `RUBRIC.md` — judge dimensions/weights derived from the gold example.
- `RUNNER.md` — worktree creation, verified CLI invocations, end-to-end flow, judge-model rationale.
- `TASK_PROMPT.md` — the verbatim prompt every model runs.
- `gold-example.md` — the anchor (placeholder until the user fills it).

Reference implementation (fully worked, do not template over): `Write Outreach Test/` at repo root —
target skill `write-outreach`, gold = a Google Cloud cold-recruiter email. Run 1 winner: Claude
(4.67), Codex close 2nd (4.53), Gemini 3rd (3.80). See its `runs/SCOREBOARD.md`.
