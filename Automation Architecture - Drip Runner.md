# Automation Architecture — Application Drip-Runner

_Saved 2026-06-10, updated 2026-06-11. Jump-off document for automating the application pipeline (Gmail sweep → Pipeline.md bookkeeping → jd-to-ready outreach machinery) on a schedule. Status: Phase 0 live, Phase 2 mostly done (settings allowlist pending), Phases 1 and 3 not started._

## The goal

A scheduled automation that runs the **real `jd-to-ready` machinery** — intake → tailor-resume → find-contacts → enrich-contacts → write-outreach — without a human babysitting it. Hard requirements learned along the way:

- **Outward-facing output is staged, never sent.** Gmail drafts only; LinkedIn messages are prepared as paste-ready text for Kanu to send manually.
- **LinkedIn access requires the daemon** (`linkedin-scraper-mcp`, a logged-in browser on `127.0.0.1:8765`). It cannot run in Anthropic's cloud — so any full-pipeline runner must be a machine Kanu controls.
- **The skills are the source of truth for behavior**, not summaries baked into prompts. The runner must load the actual skill files so refinements propagate without redeployment.

## Current state (as of 2026-06-10)

| Component | Status | Notes |
|---|---|---|
| **Cloud routine** "Application Drip-Runner (2x weekdays)" | **LIVE** | ID `trig_01Dhy19jRLQM6sggLQ4249rm` · cron `0 13,21 * * 1-5` UTC = 8 AM + 4 PM CT weekdays (shifts 1 hr when DST ends) · Sonnet 4.6 · repo `kmadhok/interview-prep` + Gmail connector · manage at https://claude.ai/code/routines/trig_01Dhy19jRLQM6sggLQ4249rm |
| Cloud routine scope | Secretary only | Gmail sweep → Pipeline.md reconciliation → stage email drafts from existing folder material (max 2/run, backlog cap of 4 unsent). **Cannot run LinkedIn steps** — it writes `contact research needed (local)` markers into Pipeline.md instead. Commits with `drip-runner:` prefix and pushes to main. |
| Local session `/loop` | Retired 6/10 | Proved the concept (2 iterations); replaced by the cloud routine. |
| Pipeline skills | **In the repo** (6/11) | Canonical copies live in repo `.claude/skills/` (jd-to-ready, find-contacts, enrich-contacts, tailor-resume, write-outreach, linkedin-mcp-operations, interview-prep-intake). Mac `~/.claude/skills/<name>` are now symlinks into the repo; pre-move originals backed up at `~/.claude/skills-backup-pre-repo-move/`. |
| LinkedIn daemon | Mac-local | launchd job `com.kanu.linkedin-mcp`, http transport on `127.0.0.1:8765`. |

**Lessons already encoded in the cloud routine's prompt** (port these to any future runner): verify every claim in a pre-written draft against current Pipeline.md before staging (stale urgency lines were caught twice on 6/10); respect per-folder channel decisions (Morgan Stanley + Google are LinkedIn-only); log `STAGED in Gmail <date>` in both the folder and the Pipeline row so runs never duplicate; pause staging when ≥4 job drafts sit unsent.

## Target architecture: always-on PC as the single runner

An always-on PC (SSH-accessible) clones the repo and runs the full pipeline on cron. Once proven, it **replaces** the cloud routine (it matches "always on" and strictly exceeds capability), leaving one runner and one automated writer to the repo.

```
┌─ Always-on PC ──────────────────────────────────┐
│ cron (e.g. weekday mornings)                    │
│   └─ git pull                                   │
│   └─ claude -p "<proven prompt>"                │
│        ├─ loads .claude/skills/* from the repo  │
│        ├─ Gmail via claude.ai connector         │
│        ├─ LinkedIn via local daemon :8765       │
│        └─ git commit + push results             │
└─────────────────────────────────────────────────┘
        ▲                                ▲
   refine skills on Mac,            review Gmail drafts +
   push to repo                     send LinkedIn msgs (Kanu)
```

## Phase plan

### Phase 1 — Refine `jd-to-ready` via `/loop` (Mac, interactive)

The skill already works when handed a JD. What a *scheduled* run adds — and what this phase must pressure-test — is the **queue rule**: how a run picks its next role with nobody handing it a JD.

- [ ] Define the queue rule. Candidate sources, in rough priority: roles flagged `contact research needed (local)` by the cloud routine → bulk-import stubs with JD captured but no outreach → "Filed only" stubs needing JD capture. Encode gates: skip roles whose Pipeline row says research is pending Kanu's go-ahead; skip roles with unresolved apply-decision gates unless the run's job is just to *prepare* the decision.
- [ ] Run `/loop pick the next role per <queue rule> and run jd-to-ready on it` a few mornings. Watch for: wrong role picked, skill stumbles, LinkedIn budget burned on low-value roles, stale-claim leaks.
- [ ] Fold fixes into the skill itself (`~/.claude/skills/jd-to-ready/`), not into the loop prompt — the prompt should shrink toward "run the skill on the next queued role."
- [ ] Freeze the exact prompt that proved itself. That string becomes the cron payload.

### Phase 2 — Make the repo self-contained

- [x] _(6/11)_ Copy these skills from `~/.claude/skills/` into repo `.claude/skills/`: `jd-to-ready`, `find-contacts`, `enrich-contacts`, `tailor-resume`, `write-outreach`, `linkedin-mcp-operations`, `interview-prep-intake` (this one was never user-installed — unzipped from the root `.skill` file; the symlink also installs it on the Mac for the first time).
- [x] _(6/11)_ **Canonical-copy rule:** the repo version is now the source of truth. Mac `~/.claude/skills/<name>` are symlinks into the repo; pre-move originals parked at `~/.claude/skills-backup-pre-repo-move/` (delete once confident). Verified `trace_step.py` resolves through the symlink.
- [ ] Commit a `.claude/settings.json` with the tool allowlist headless runs need (Bash, Read/Write/Edit, Glob/Grep, WebFetch, `mcp__claude_ai_Gmail`, `mcp__linkedin`) so cron runs never block on a permission prompt. **Kanu must do this by hand** — the auto-mode classifier refuses to let an agent widen its own permissions, in any form.
- [x] _(6/11)_ Push. Side benefit: the cloud routine immediately gets the real tailor-resume / write-outreach logic for its secretary work.

**Discovered while executing (affects Phase 3):**

- `jd-to-ready`'s SKILL.md and its hook scripts reference `~/.claude/skills/jd-to-ready/...` (e.g. `trace_step.py`, hooks resolve via `Path.home()`). The symlink keeps these working unchanged — but it means **every runner machine needs the same symlinks** (added to Phase 3).
- `jd-to-ready`'s three hooks (PostToolUse, Stop) are registered in **user-level** `~/.claude/settings.json` on the Mac, not in the repo. A PC runner must register them too (added to Phase 3). Trace state goes to `~/.claude/logs/`, so relocation is safe.

### Phase 3 — Stand up the PC runner

_Prereq: know the PC's OS — service manager and paths differ (systemd on Linux, Task Scheduler/NSSM on Windows)._

- [ ] **Claude Code:** install CLI, `claude login` with the same account (this brings the claude.ai Gmail connector along).
- [ ] **LinkedIn daemon:** install `linkedin-scraper-mcp` pinned to the same version as the Mac; log into LinkedIn once in its browser profile; run as an always-on service; add the `linkedin` server to `~/.claude.json` as `"type": "http"` → `http://127.0.0.1:8765/mcp` (same invariant as the Mac — never stdio).
- [ ] **⚠ Single-daemon rule:** automated LinkedIn browsing from two machines/IPs on one account is a flag risk. When the PC daemon goes live, stop using the Mac daemon for automation (interactive one-off use sparingly, or retire it).
- [ ] **Git:** clone the repo; add push credentials (PAT or SSH deploy key).
- [ ] **Skill symlinks:** `ln -s <repo>/.claude/skills/<name> ~/.claude/skills/<name>` for all 7 pipeline skills — skill internals and hooks reference `~/.claude/skills/...` paths.
- [ ] **Hook registration:** add the three `jd-to-ready` hooks (PostToolUse `.*` → `jd-to-ready-post-tool.py`, Stop → `jd-to-ready-stop.py`, SubagentStop → `jd-to-ready-subagent-stop.py`) to the PC's user-level `~/.claude/settings.json`, copying the entries from the Mac's.
- [ ] **Cron:** `git pull && claude -p "<Phase-1 frozen prompt>"` in the repo dir, weekday cadence chosen after Phase 1 reveals run duration (LinkedIn sequences run 35–60 min — don't schedule runs closer together than the longest observed run).
- [ ] **Smoke test over SSH:** one manual run end-to-end (daemon healthy → skills load → Gmail drafts staged → push lands) before trusting cron.

### Phase 4 — Cutover

- [ ] Run PC cron and cloud routine in parallel for a few days (they coordinate via git; cloud stays secretary-only so no duplicate staging).
- [ ] Disable the cloud routine at https://claude.ai/code/routines/trig_01Dhy19jRLQM6sggLQ4249rm (deletion is web-UI-only) — or keep it disabled-but-armed as a fallback for PC outages.
- [ ] Update CLAUDE.md / AGENTS.md with the runner's existence so interactive sessions know to `git pull` first and not to double-stage outreach.

## Open decisions

1. **PC operating system** → determines Phase 3 specifics.
2. **Queue rule** → the real design work of Phase 1 (see candidates above).
3. **Cadence** → daily? 2x weekdays? Constrained by LinkedIn sequence duration and how fast Kanu clears the draft-review queue.
4. **Cloud routine end state** → delete vs. keep disabled as fallback.

## Standing risks

- **Three potential writers to the repo** (Mac interactive, cloud routine, PC cron) until cutover — always `git pull` before local edits; runners commit with `drip-runner:` prefix so their changes are attributable.
- **Draft pileup** — automation throughput is gated on Kanu reviewing/sending staged drafts; every runner must honor the ≥4-unsent staging pause.
- **Stale pre-written drafts** — any draft written more than a few days ago must have its claims re-verified against Pipeline.md before staging (this caught real errors on 6/10: a rejected role and a passed interview were still cited as live urgency).
- **LinkedIn account safety** — sequential-only calls, one daemon machine, no usage beyond what `linkedin-mcp-operations` already specifies.
