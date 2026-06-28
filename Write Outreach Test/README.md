# Write Outreach Test

Loop-engineering harness: have multiple provider models (Codex / Claude / Gemini), each in its own
git worktree, **improve the `write-outreach` skill**, then generate cold-recruiter emails with it.
The model whose emails land closest to a single **gold-standard email** wins; its skill diff is the
merge candidate.

## Read in this order
1. **`SPEC.md`** — the what + why. The task contract, the 3 test roles, the invariants, the scoring model, the worktree matrix.
2. **`ACCEPTANCE.md`** — machine-checkable hard gates (G1–G9) + the two-stage scoring procedure.
3. **`RUBRIC.md`** — the LLM-judge dimensions + weights (derived from the gold email).
4. **`RUNNER.md`** — (stub) how the worktrees + models actually run. Wired in a later pass.
5. **`fixtures/`** — the gold email (the anchor), the task prompt every model runs, and the 3 role inputs.

## Status
- [x] Folder + spec + acceptance + rubric scaffolded.
- [x] 3 recruiter fixtures wired from real roles (Cohere / Distyl / Sierra), each with a verified-email recruiter.
- [x] **Gold email is IN** (`fixtures/gold-email.md` — Google Cloud / FDE I) and `RUBRIC.md` is tuned to its two load-bearing traits: relevance-match + urgency-via-social-proof.
- [x] Beat-3 split wired: `cohere-fde` seeded LIVE (tests the urgency move), `distyl`/`sierra` OMIT (test clean live-sourcing).
- [x] Skill isolation solved — `write-outreach` is vendored in-repo (`.claude/skills/`), so worktrees isolate it for free. No `skill-under-test/` copy needed.
- [x] Three worktrees created + isolation proven: `.claude/worktrees/wo-{claude,codex,gemini}` on branches `wo-test/{claude,codex,gemini}`.
- [x] `RUNNER.md` written with **verified** CLI invocations (claude/codex/gemini all installed) + a full judge-model section.
- [ ] Pick exact latest `--model` id per provider, and the judge model (see `RUNNER.md` → "Judge model").
- [ ] Run it (each model → 3 emails), then gates + judge.

## What the harness is really testing
Whether a model can edit `write-outreach` so its emails reproduce the gold email's two moves — tight
JD-relevant pitch (Tip #2/#5) and the real-live-process urgency pivot (Tip #3) — across roles, while
respecting the no-fabrication rule (omit beat 3 when nothing's live). Source of principles:
`Cold Outreach Emails Best Practices.md`.
