<!-- TEMPLATE — skill-loop-trainer. Copy into "{{NAME}} Test/" and fill {{PLACEHOLDERS}}.
     The cohere/distyl/recruiter/em-dash details below are the WORKED write-outreach example —
     replace them with the target skill's real fixtures, gates, and gold-example traits.
     Reference impl: repo-root "Write Outreach Test/". -->

# Runner — worktree + model execution

How the three contestant models run, each in an isolated git worktree, on the same task prompt. CLI
flags below are **verified against the installed CLIs** (`claude`, `codex`, `gemini` at
`/opt/homebrew/bin/`). The worktrees already exist — this file is the operating manual, not a stub.

---

## Why this works without a separate skill copy

The skill is **vendored in-repo** at `.claude/skills/{{TARGET_SKILL}}/SKILL.md` (identical to the global
`~/.claude/skills/` copy, and git-tracked). Because it's tracked, **a git worktree isolates it for
free** — each worktree gets its own checkout of the skill, edits stay on that worktree's branch, and
they never collide. (Proven: an edit in `{{SLUG_BASE}}-claude` is invisible to `{{SLUG_BASE}}-codex` and `main`.) No
`skill-under-test/` copy is needed.

> One caveat to respect at run time: the model's Claude/Codex/Gemini session may *also* read the
> GLOBAL skill at `~/.claude/skills/{{TARGET_SKILL}}/`. For a clean experiment each model must edit and
> be evaluated on the **in-worktree** copy (`.claude/skills/{{TARGET_SKILL}}/`), not the global one. The
> task prompt already points at the in-repo path; the judge diffs the worktree branch, not the global
> skill. Don't let a model "improve" the global copy — that would leak across worktrees.

## The worktrees (already created)

```
.claude/worktrees/{{SLUG_BASE}}-claude   →  branch {{SLUG_BASE}}-test/claude   (Anthropic, claude CLI)
.claude/worktrees/{{SLUG_BASE}}-codex    →  branch {{SLUG_BASE}}-test/codex    (OpenAI,    codex CLI)
.claude/worktrees/{{SLUG_BASE}}-gemini   →  branch {{SLUG_BASE}}-test/gemini   (Google,    gemini CLI)
```
All three branch off the harness commit, so each starts from the identical spec + fixtures + skill.

Recreate if ever needed:
```bash
git worktree add -b {{SLUG_BASE}}-test/<m> .claude/worktrees/{{SLUG_BASE}}-<m> HEAD   # m ∈ {claude,codex,gemini}
```
Tear down after the experiment:
```bash
git worktree remove .claude/worktrees/{{SLUG_BASE}}-<m> && git branch -D {{SLUG_BASE}}-test/<m>
```

---

## Verified CLI invocations

Each runs the SAME prompt — `{{NAME}} Test/fixtures/TASK_PROMPT.md` — from inside its own
worktree, so the model's cwd-relative paths resolve to the isolated skill copy. Non-interactive,
auto-approved (the model must be free to edit files + write outputs), confined to the worktree.

**Claude (Anthropic):**
```bash
cd .claude/worktrees/{{SLUG_BASE}}-claude
claude -p "$(cat '../../../{{NAME}} Test/fixtures/TASK_PROMPT.md')" \
       --model claude-opus-4-8 \
       --permission-mode acceptEdits
```

**Codex (OpenAI):**
```bash
cd .claude/worktrees/{{SLUG_BASE}}-codex
codex exec "$(cat '../../../{{NAME}} Test/fixtures/TASK_PROMPT.md')" \
      --model <latest-codex-model> \
      --cd . \
      --dangerously-bypass-approvals-and-sandbox   # worktree IS the sandbox boundary here
```

**Gemini (Google):**
```bash
cd .claude/worktrees/{{SLUG_BASE}}-gemini
gemini "$(cat '../../../{{NAME}} Test/fixtures/TASK_PROMPT.md')" \
       --model <latest-gemini-model> \
       --approval-mode yolo
```

Notes:
- Confirm the exact latest model id per provider at run time (`--model` is verified to exist on all
  three; the id strings move).
- All three auto-approve flags are acceptable **because the worktree is the blast radius** — the
  model can only touch that checkout. Still: review diffs before merging anything.
- `TASK_PROMPT.md` lives at repo root under `{{NAME}} Test/`, so from inside a worktree it's
  three levels up (`../../../`). Adjust if you relocate.

---

## End-to-end flow

1. **Pre-flight.** Working tree clean on `main`; the three worktrees exist on the harness commit;
   `fixtures/gold-email.md` is the real email (it is); `RUBRIC.md` is tuned (it is).
2. **Run each model** with its invocation above. Each: reads the gold email + fixtures + its
   in-worktree skill, edits the skill, commits to its branch, generates 3 emails to
   `runs/<model>/<role-slug>.md`, writes `runs/<model>/NOTES.md`.
   - `runs/` is at repo root, shared. Each model writes to its own `runs/<model>/` subdir — no
     collision. (The emails are *outputs*, intentionally collected centrally; only the *skill edits*
     need worktree isolation.)
3. **Reproducibility gate** (ACCEPTANCE Stage 0): from each worktree, re-run that model's edited
   skill on ONE held-out fixture; confirm the regenerated email matches (±10 words, same beats/hook).
   Empty skill diff or non-reproducible → disqualify that run.
4. **Hard gates** (ACCEPTANCE Stage 1, G1–G9): mechanical checks per email. Any fail → email scores 0.
5. **Judge pass** (ACCEPTANCE Stage 2): the judge model scores every gate-passing email against the
   gold email on the `RUBRIC.md` dimensions. Run centrally from `main`, not from a worktree.
6. **Scoreboard.** Per-model mean over the 3 fixtures (disqualified = 0). Winner per the tie-break
   ladder in ACCEPTANCE. The winning branch's skill diff is the merge candidate.
7. **Promote + clean up.** Merge the winner's `.claude/skills/{{TARGET_SKILL}}/SKILL.md` into `main`,
   copy it back to the global `~/.claude/skills/{{TARGET_SKILL}}/`, then remove the worktrees + branches.

---

## Judge model — how to choose, and why it matters

The judge is the measuring instrument. If it's biased, the whole benchmark is biased — so its choice
is a first-class decision, not an afterthought.

### The core risk: self-preference bias
LLM judges measurably prefer text written by themselves or by a sibling from the same family — same
training distribution, same stylistic priors. If you let a contestant model also be the judge, that
family wins on style affinity, not on actually matching the gold email. With Claude / Codex / Gemini
all competing, **the judge must sit outside all three families** wherever possible.

### Recommended setup (in priority order)
1. **A neutral strong model not in the contest.** Since Claude/OpenAI/Google are all contestants, a
   truly outside judge is hard. Next best: pick the strongest model from a family whose *contestant
   entry is the weakest*, OR use a model variant the contestants don't share. The point is to avoid
   the judge being a same-family sibling of a contestant it's scoring.
2. **Two-judge average (preferred for a real run).** Use two different-family judges (e.g. an
   Anthropic judge + a Google judge), average their weighted totals per email. Cross-family averaging
   cancels most single-family self-preference. If the two judges disagree by > 1.0 weighted on any
   email, flag it for a human read rather than trusting the mean.
3. **Blind the judge to model identity.** The judge prompt must NOT reveal which model wrote a
   candidate (strip the `model=` label, or pass a random alias). Identity leakage reactivates the very
   bias you're controlling for. Score emails in shuffled order.

### Make the instrument reliable, not just unbiased
- **Lock the judge prompt** (the template in `RUBRIC.md`). Same prompt every run, or scores aren't
  comparable across runs.
- **Pin temperature low** (0–0.3) so two judge runs on the same email agree within ±0.3 weighted —
  that's the reproducibility bar in ACCEPTANCE's definition-of-done.
- **Anchor with the gold email itself.** Score the gold email as a control each run; it should land
  ~4.7. If it drifts, the judge or the anchors moved — recalibrate before trusting the scoreboard.
- **Require quoted evidence.** Every dimension score must cite a candidate line (RUBRIC enforces
  this). A judge that can't quote the line that earned a 5 is guessing.
- **Fabrication is the human's job too.** The judge is a backstop for G2 (no fabrication), but the
  hard gate runs first mechanically — don't rely on the judge to catch invented numbers.

### Concrete default
For the first run: **single neutral judge, blinded, temp 0.2, gold-email control each pass.** Upgrade
to the **two-judge cross-family average** before treating any scoreboard as decisive. Whichever you
pick, the judge family should not be the same family as the *front-runner* contestant — re-check after
you see the standings, and re-judge with a different family if the winner judged its own sibling.

---

## Locked model lineup (strongest per provider, verified to run)
| Provider | Model id | How chosen |
|----------|----------|------------|
| Anthropic (claude) | `claude-opus-4-8` | strongest Opus; smoke-tested OK |
| OpenAI (codex) | `gpt-5.5` | codex CLI default = its strongest; smoke-tested OK |
| Google (gemini) | `gemini-2.5-pro` | `-m gemini-2.5-pro` accepted (default `gemini-1.5-flash` is too weak; `gemini-3-pro` returns 404 on this account) |

## To decide before first run
- [x] Exact latest `--model` id per provider (locked above).
- [ ] Judge model (single neutral vs two-judge average) + confirm it's not a contestant's sibling.
- [ ] Parallel (faster) vs serial (easier to debug) worktree execution.
- [ ] Who runs the mechanical G1–G9 checks — a small script vs by-hand for the first pass.
