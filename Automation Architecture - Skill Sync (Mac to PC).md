# Automation Architecture — Skill Sync (Mac → PC)

_Created 2026-06-20. One of two split plans. Companion: `Automation Architecture - Runtime (Email to Pipeline).md`. Parent context / history: `Automation Architecture - Drip Runner.md`._

**Scope — the dev→deploy loop and its safety net.** How you refine skills on the Mac and get them onto the always-on PC runner **without breaking the unattended pipeline.** Covers: edit → push → pull, and the regression gate that makes "any changes don't break anything" true.

**Out of scope (other plan).** The runtime intake/run loop (email → cron → queue → run → Pipeline). See the Runtime plan. This plan exists to *protect* that loop.

---

## The dev loop

```
Mac: edit skill ──▶ push to a `dev` branch
                         │
        GitHub Actions: unit tests (Layer 1)  ──red──▶ never merges
                         │ green
                    merge to `main`
                         │
PC (top of the runtime cron): git pull --rebase
                         │
   did the pull touch .claude/skills/ ?  ──no──▶ run normally
                         │ yes
   canary on a frozen golden JD (Layer 2)  ──red──▶ git reset to last-good
                         │ green                      + alert you
                    proceed to real work          + skip real work this run
```

The principle in one line: **`main` is always deployable, and the runner self-checks before it touches anything real.**

---

## Current state (verified 2026-06-20)
- Repo is canonical; PC `~/.claude/skills` is a directory **junction** into it — the PC always runs the repo copy, no separate install to update. ✅
- **No CI, no tests, no git hooks, no canary.** ❌ Current safety = manual "diff vs known-good + `git revert`" (per SKILL.md) — which only works with a human in the loop. The autonomous PC has no human in the loop.
- Today's `export_resume.py` fix is **uncommitted** (and untested by any harness).

---

## Components

### 1. Where you edit
- Skills are edited on the Mac (or in an interactive session); the repo `.claude/skills/` is the source of truth. The junction means a `git pull` on the PC *is* the deploy — no copy step.

### 2. Propagation — branch discipline (the key lever)
- **DECISION (strongly recommended): never push skill changes straight to `main`.** Push to a `dev` branch; merge to `main` only when CI is green. Because the PC pulls `main`, `main` must always be deployable.
- The PC pulls `main` at the top of each runtime cron run (`git pull --rebase`; abort the run if the pull fails).

### 3. Layer 1 — CI on push (deterministic, cheap, no secrets)
- A GitHub Actions workflow runs `pytest` on the shell helpers — `export_resume.py`, `trace_step.py`, the queue parser — on every push. Runs in seconds, needs no daemon and no credentials.
- _This is exactly the gate that would have caught today's Windows `--print-to-pdf` relative-path bug before it ever shipped._
- [ ] Add `tests/` + `.github/workflows/ci.yml`.

### 4. Layer 2 — local canary + auto-rollback (LLM/skill-level)
- After the pull, **only if `git diff --name-only HEAD@{1} HEAD -- .claude/skills/` is non-empty**, run `jd-to-ready` on a **frozen golden JD** (HappyRobot FDE — already on disk) into a scratch dir. The `git diff` gate means the canary only fires when skill *behavior* actually changed — most pulls skip it, so it costs nothing on a normal day.
- A validator asserts invariants (not byte-equality — LLM output isn't deterministic):
  - all 4 deliverables exist + non-empty;
  - classification themes ∈ the 18-string vocab, archetype ∈ the 5-string vocab, 4–6 themes;
  - resume has zero `[VERIFY]` / `[NUMBER?]` leaks and bullets trace back to `Resume Achievements Master.md`;
  - export produced a 1-page PDF (or printed a clean graceful-skip line).
- **Green** → proceed to the real queue. **Red** → `git reset --hard HEAD@{1}` to the last-good commit, alert you, and process **no** real role this run.
- The canary runs the **offline core only** by default (intake → classify → resume → export) to avoid burning LinkedIn scraping budget / adding flag risk on a fake role. A `--full` flag also exercises contacts + outreach for occasional deep checks.
- [ ] Write `scripts/canary.py` + the validator; freeze the golden JD.

### 5. "Break" taxonomy + alerting
- The failure modes the gate exists to stop: crash / partial state mid-run; fabricated or stale claims leaking into outreach; LinkedIn budget burn or account-flag risk; broken queue parsing.
- **DECISION NEEDED — alerting channel:** on canary-red or a run crash, how do you find out? Simplest options: a Gmail draft-to-self, or a committed `RUNNER-STATUS.md` you glance at. (No alert = silent failure, which defeats the point.)

### 6. Rollback
- `git reset --hard HEAD@{1}` returns the PC to the last-good commit; the bad change stays on the branch for you to fix on the Mac. One revert away — the canonical-repo + git-history model makes a bad edit cheap to undo.

---

## Open decisions
1. Branch-and-merge vs. direct-to-`main` (§2). **Strongly recommend branch + green-CI-to-merge.**
2. Alerting channel (§5).
3. Golden JD choice + how often to run the `--full` canary (§4).

## Build checklist (recommended order)
- [ ] Commit + push today's `export_resume.py` fix — also serves as the untested "first git push" smoke test.
- [ ] `tests/` + GitHub Actions CI (Layer 1) — locks in the fix and the bug class.
- [ ] `scripts/canary.py` + validator + frozen golden JD (Layer 2).
- [ ] Wire canary + rollback into the runtime cron (the `git diff` gate from §4).
- [ ] Pick branch discipline (§2) + alerting channel (§5).

## Dependency direction
- The Runtime plan **depends on** this one: do not enable the runtime cron until Layer 2 (canary + rollback) is live. Until then, every skill push is an unguarded change to an autonomous writer of outreach.
