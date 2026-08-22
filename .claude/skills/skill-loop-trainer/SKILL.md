---
name: skill-loop-trainer
description: Loop-engineer any skill by having multiple provider models (Claude/Codex/Gemini), each in an isolated git worktree, improve the skill and produce outputs that are graded against a gold-standard example. Use when the user wants to optimize/train/improve a skill against a "here's the output I want" anchor, run a multi-model bake-off, or A/B skill edits across providers. Trigger on "loop-engineer this skill", "train the X skill", "run a model bake-off on X", "have different models improve X", "optimize X against this gold example". Produces a self-contained `<Name> Test/` harness (spec, acceptance gates, judge rubric, fixtures, runner, scoreboard) and runs it end to end. Generalized from the Write Outreach Test harness.
---

# Skill Loop Trainer

Turn "I have an example output I love, make this skill produce outputs like it" into a repeatable, judged, multi-model competition. Each provider model improves the target skill **in its own git worktree** (zero collision), then runs the improved skill on a fixed test set. Outputs are graded against the gold example: mechanical hard gates first, then an LLM judge on weighted dimensions derived from the gold example. Winner's skill diff is the merge candidate.

This skill is the **generalized form of the `Write Outreach Test/` harness** — same machinery, any target skill.

## When to use / not use
- **Use:** optimizing a skill's output quality against a concrete gold example; comparing how different providers edit the same skill; producing an auditable "why this edit won."
- **Not:** one-off edits to a skill (just edit it), or tasks with no gold-standard anchor to grade against (the anchor is mandatory — without it the rubric is hollow).

## Inputs (gather before building)
| Input | Required | Notes |
|-------|----------|-------|
| `target_skill` | yes | The skill to improve. Must be **vendored in-repo** at `.claude/skills/<name>/` and git-tracked — that's what makes worktrees isolate it for free. If only global (`~/.claude/skills/`), copy it in-repo first. |
| `gold_example` | yes | One example output the user loves + **why** they love it (their words). This is the single source of "better"; every rubric dimension derives from its real traits. |
| `test_set` | yes | 3–5 fixed fixtures the improved skill runs on. Each = the exact inputs the skill needs. Vary them so the skill is tested across cases, not overfit. |
| `models` | no | Default: strongest-per-provider (Claude/Codex/Gemini). Verify ids at run time (see Step 4). |
| `judge` | no | Default: single blinded judge ≠ the front-runner's family; upgrade to two-judge cross-family average before a decisive result. |

## Process (10 steps — create one TodoWrite item per step)

### Phase A — Build the harness (mirror `templates/`)
1. **Confirm the target skill is in-repo + git-tracked.** `ls .claude/skills/<target>/`. If absent, copy from global and `git add`. Worktrees only isolate tracked files.
2. **Capture the gold example.** Write `<Name> Test/fixtures/gold-example.md` with the exact output AND the user's "why it's gold" (load-bearing traits in their words). If they haven't given the why, ask for it — it sets the rubric weights. Copy `templates/gold-example.md`.
3. **Write the spec** (`<Name> Test/SPEC.md` from `templates/SPEC.md`): task contract (each model edits the skill *then* runs it — graded on outputs, deliverable is the skill diff), the test set table, the hard invariants (constraints, not optimization targets — drawn from the skill's own rules), the scoring model, the worktree matrix.
4. **Write acceptance gates** (`ACCEPTANCE.md` from `templates/ACCEPTANCE.md`): Stage 0 reproducibility (must edit the skill; outputs must regenerate from it — disqualify hand-authored runs), Stage 1 mechanical hard gates (binary, disqualifying — adapt G-list to the target skill's rules), Stage 2 judge schema + scoring math (disqualified = 0, run score = mean across fixtures).
5. **Tune the rubric** (`RUBRIC.md` from `templates/RUBRIC.md`): one dimension per real trait of the gold example, **weighted toward the 2–3 traits the user named as why it's gold**. Calibrate gold-to-itself ≈ 4.7 (reserve 5 for "beats gold") so the loop can detect improvement. Require quoted-evidence per score.
6. **Write the fixtures + task prompt.** One `fixtures/<slug>.md` per test case (real inputs, not synthetic). `fixtures/TASK_PROMPT.md` = the verbatim prompt every model runs (from `templates/TASK_PROMPT.md`): read gold + fixtures + skill → edit the in-worktree skill (never global) → run it on each fixture → write outputs to `runs/<model>/<slug>.md` + `NOTES.md` → commit the skill diff.

### Phase B — Run the competition
7. **Commit the harness to `main`**, then create one isolated worktree per model off that commit:
   ```bash
   git worktree add -b <slug>-test/<m> .claude/worktrees/<slug>-<m> HEAD   # m ∈ {claude,codex,gemini}
   ```
   Prove isolation once (edit skill in one worktree → invisible in another). See `RUNNER.md` template.
8. **Verify model ids by smoke test, then launch each run** (background, parallel). Invocations in `templates/RUNNER.md` — verified flags:
   - Claude: `claude -p "$(cat .../TASK_PROMPT.md)" --model <id> --dangerously-skip-permissions`
     (**`--dangerously-skip-permissions` is required** — `acceptEdits` still blocks writes under `.claude/skills/` and the headless run stalls).
   - Codex: `codex exec "$(cat .../TASK_PROMPT.md)" --model <id> --cd . --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check`
   - Gemini: `gemini -m <id> --approval-mode yolo "$(cat .../TASK_PROMPT.md)"` (force a strong `-m`; default is weak).
   - **`mkdir -p runs/<m>/` BEFORE redirecting any log into it, and log to `/tmp`, not into a path git might stash** (both bit this harness — see PITFALLS).

### Phase C — Judge & promote
9. **Score.** Run `scripts/gate_check.py` (mechanical G-gates, model-agnostic) across all outputs — patch its subject/body parser if the target skill's output format differs. Then the LLM judge pass per `RUBRIC.md`. Write `runs/SCOREBOARD.md`: Stage-0 reproducibility, Stage-1 gates, Stage-2 per-dimension scores, mean per model, winner + tie-break, and *what the skill edits say* (edit depth usually predicts output consistency).
10. **Promote + clean up.** If standings hold (re-judge blind cross-family first if winner = judge's family): merge the winning branch's skill diff → `main`, optionally cherry-pick a runner-up's stronger sub-edit, sync to global `~/.claude/skills/<target>/`, then `git worktree remove` + `git branch -D` all the test branches.

## Hard rules
- **The gold example is mandatory and load-bearing** — no anchor, no rubric. Don't fabricate one.
- **Each model must EDIT the skill, not hand-author outputs.** Stage-0 reproducibility enforces this; an empty skill diff disqualifies the run.
- **In-worktree skill only.** Models must edit `.claude/skills/<target>/` inside their worktree, never the global copy — global edits leak across worktrees.
- **The worktree is the blast radius** — that's why the auto-approve/skip-permission flags are safe. Still review diffs before merging.
- **Judge ≠ front-runner's family** for any decisive result; blind the judge to model identity.
- **Gates are mechanical and run first**; the judge is a backstop, not the fabrication check.

## Pitfalls (all hit on the first real run — avoid)
- **Log-redirect into a missing/stashed dir kills the command before the model runs.** `mkdir -p runs/<m>/` first; write run logs to `/tmp`. A fast exit-0 with no outputs = this bug, not success — always verify deliverables (outputs + skill commit), never trust the wrapper's "completed."
- **`claude --permission-mode acceptEdits` blocks `.claude/skills/` writes.** Use `--dangerously-skip-permissions`.
- **Gemini defaults to a weak model.** Force `-m <strong-id>`; confirm it's accepted (some pro ids 404 per account).
- **Worktrees branch off the commit you make them from** — commit the *finalized* fixtures/gold/rubric before branching, or worktrees start stale.

## Artifacts produced
```
<Name> Test/
├── README.md  SPEC.md  ACCEPTANCE.md  RUBRIC.md  RUNNER.md
├── fixtures/  gold-example.md  TASK_PROMPT.md  <slug>.md ×N
└── runs/  <model>/<slug>.md + NOTES.md  ·  SCOREBOARD.md
.claude/worktrees/<slug>-<model>/   (one per model; torn down after)
```

See `Write Outreach Test/` for a complete worked example (target skill = `write-outreach`, gold = a cold-recruiter email; Claude won, Codex close second).
