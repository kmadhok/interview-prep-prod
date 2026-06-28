# Runner — worktree + model execution (STUB, wired in a later pass)

Spec-only for now. This file holds the *intended* mechanics so the SPEC stays clean. Nothing here
is implemented yet. When wiring it: prefer the smallest thing that runs all three models on the
same prompt and drops outputs into `runs/<model>/`.

---

## Shape

One git worktree per contestant model, all off the same base commit, each running
`fixtures/TASK_PROMPT.md` verbatim:

| Worktree dir | Provider | Model | CLI invocation (placeholder) |
|--------------|----------|-------|------------------------------|
| `../wo-wt-claude` | Anthropic | claude-opus-4-8 | `claude -p "$(cat fixtures/TASK_PROMPT.md)"` |
| `../wo-wt-codex` | OpenAI | latest Codex/GPT | `codex exec "$(cat fixtures/TASK_PROMPT.md)"` |
| `../wo-wt-gemini` | Google | latest Gemini | `gemini -p "$(cat fixtures/TASK_PROMPT.md)"` |

(Exact flags depend on each CLI's current interface — confirm before running.)

## Why worktrees
Each model EDITS the shared `write-outreach` skill. Parallel edits to the same files would collide.
Worktrees give each model an isolated checkout so the skill diffs don't stomp each other, and the
judge can diff each worktree's skill independently.

> Caveat: the skill lives at `~/.claude/skills/write-outreach/`, OUTSIDE this git repo. Decide
> before running whether models edit the global skill (then a worktree doesn't isolate it) or a
> repo-local copy of the skill. **Recommended:** copy the skill into the repo for the experiment
> (e.g. `Write Outreach Test/skill-under-test/`) so worktrees actually isolate the edits, then
> promote the winner back to `~/.claude/skills/` by hand. Update TASK_PROMPT paths to match.

## Flow
1. Snapshot base commit. For each model: create worktree, copy skill-under-test in.
2. Run the model with `TASK_PROMPT.md`. It edits the skill copy + writes 3 emails to `runs/<model>/`.
3. Reproducibility gate (ACCEPTANCE Stage 0): re-run each edited skill on one held-out fixture.
4. Central judge pass (ACCEPTANCE Stage 1 gates → Stage 2 LLM judge) over all `runs/*/`.
5. Emit a ranked scoreboard; winner's skill diff is the merge candidate.

## Judge model
Pick a strong model **not** in the contestant matrix to avoid self-preference bias (e.g. if
contestants are Opus/Codex/Gemini, judge with a different one, or run a 2-judge average). Lock the
judge prompt from `RUBRIC.md` so re-runs agree within ±0.3.

## To decide before first run
- [ ] Global skill vs repo-local `skill-under-test/` copy (recommend the copy — see caveat above).
- [ ] Exact CLI flags per provider.
- [ ] Judge model + whether to average two judges.
- [ ] Whether worktrees run in parallel (faster) or serially (simpler to debug).
