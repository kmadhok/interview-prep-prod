# Trace / Work-Log Contract Implementation Plan (Plan 2 of 5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every orchestrator and primitive skill run emits `runs/<run-id>/trace.jsonl` + a rendered `report.md`, with every step carrying `reason` + `sources` — so a user can walk from "I don't like this output" to the exact file to edit.

**Architecture:** Generalize the existing `jd-to-ready` trace machinery (`trace_step.py`: state machine, step begin/end, validators, token accounting) instead of rebuilding it. Three changes: (1) relocate to `scripts/trace_step.py` as shared infrastructure with a repo-local `runs/` layout replacing the per-role + `~/.claude/logs` split; (2) schema v2 adds required `reason` + `sources` to `step_begin` and a `primitive` run-type so standalone primitive runs trace too (Decision 5); (3) a new `scripts/render_run_report.py` turns any trace into a human report whose per-step "sources" listing IS the repair manual.

**Tech Stack:** Python 3.11+ stdlib only, pytest (throwaway venv — system Python lacks pytest), existing `scripts/config.py` for REPO_ROOT.

**Spec:** `docs/spec/productionalization-v1.md` workstream 1, Decision 5, success criterion 1.
**Grounding:** `trace_step.py` is 693 lines with CLI verbs `start-run / set-role-folder / begin / end / tool-event / subagent-event / check / finish-run / abort-run`, a `RUN_TYPES` map already covering `jd-to-ready` + `stage-outreach` + legacy `full`, and 21 passing tests in `test_trace_step.py`. Current outputs: `<role folder>/.jd-to-ready-trace.jsonl` + `~/.claude/logs/jd-to-ready.jsonl` (env override `JD_TO_READY_LOG_DIR`).

**Constraints:** branch `productionalized_version` only; live system untouched (`main`, old traces in `~/.claude/logs` and role folders remain as historical artifacts — never deleted); guard test must stay green; no new dependencies.

---

## File Structure

```
scripts/trace_step.py             MOVED from .claude/skills/jd-to-ready/scripts/ (git mv), then modified
scripts/test_trace_step.py        MOVED alongside, then extended
scripts/render_run_report.py      NEW — trace.jsonl → report.md
scripts/test_render_run_report.py NEW
docs/trace/TRACE_SCHEMA.md        MOVED from .claude/skills/jd-to-ready/, updated to v2
docs/trace/TOKEN_ACCOUNTING.md    MOVED alongside (unchanged content, updated pointers)
runs/                             runtime output (already gitignored)
  <run-id>/trace.jsonl            one dir per run
  <run-id>/report.md              rendered by render_run_report.py
  .active-run.json                single active-run state (replaces ~/.claude/logs state)
  summary.jsonl                   one line per finished run (replaces ~/.claude/logs/jd-to-ready.jsonl)
.claude/skills/jd-to-ready/SKILL.md        MODIFY — new CLI path + --reason/--sources + render step
.claude/skills/stage-outreach/SKILL.md     MODIFY — same trace contract, verified/added
.claude/skills/{interview-prep-intake,tailor-resume,find-contacts,enrich-contacts,
  verify-emails,write-outreach}/SKILL.md   MODIFY — standalone trace preamble (primitive run-type)
.claude/skills/jd-to-ready/{TRACEABILITY.md,RUNBOOK.md,TRACE_TEST_PLAN.md,
  TRACEABILITY_IMPLEMENTATION_SUMMARY.md}  MODIFY — pointers to new paths
CLAUDE.md / AGENTS.md                      MODIFY — trace doc pointers
```

Design decisions locked here (do not relitigate during implementation):
- **One trace location.** `runs/<run-id>/trace.jsonl` from `start-run` onward. The per-role `.jd-to-ready-trace.jsonl` and `migrate_fallback_trace()` dance existed because the trace lived in a folder discovered mid-run; with a run dir created at start, that complexity is deleted, not ported. `role_folder` remains an event field.
- **State + summary move into `runs/`** (repo-local, multi-user safe, self-contained). Env override renamed `TRACE_RUNS_DIR` (old `JD_TO_READY_LOG_DIR` no longer honored on this branch — nothing on this branch sets it; the live system on `main` keeps its own copy of the old script untouched).
- **Schema v2 is additive** on the event level (`reason`, `sources`, `schema_version`) — old traces remain readable by the renderer (fields default to absent), but the validator REQUIRES the new fields for new runs.
- **Decision 5 mapping:** piped primitives = the orchestrator's own `step_begin/end` (current behavior, unchanged). Standalone primitives = `--run-type primitive --skill <name>` with `required_steps=["main"]`.

---

### Task 1: Relocate trace machinery to `scripts/` (pure move, suite stays green)

**Files:**
- Move: `.claude/skills/jd-to-ready/scripts/trace_step.py` → `scripts/trace_step.py`
- Move: `.claude/skills/jd-to-ready/scripts/test_trace_step.py` → `scripts/test_trace_step.py`

- [ ] **Step 1: git mv both files**

```bash
git mv ".claude/skills/jd-to-ready/scripts/trace_step.py" scripts/trace_step.py
git mv ".claude/skills/jd-to-ready/scripts/test_trace_step.py" scripts/test_trace_step.py
```

- [ ] **Step 2: Fix anything move-broken, nothing else**

Check `test_trace_step.py` for how it locates the script (`grep -n "trace_step\|__file__\|Path(" scripts/test_trace_step.py | head`). If it resolves the script relative to its own location, the co-move means it still works. Fix only breakage. Do NOT change behavior, paths, or schema in this task.

- [ ] **Step 3: Suite green**

```bash
python3 -m venv /tmp/tpvenv && /tmp/tpvenv/bin/pip -q install pytest
/tmp/tpvenv/bin/python -m pytest scripts/ 2>&1 | tail -2
```
Expected: `121 passed` (100 existing + 21 moved trace tests), 0 failed. Guard green (it scans the new location — no personal refs exist in these files since Task 5b genericized fixtures).

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "refactor: promote trace_step to shared scripts/ (pure move)"
```

---

### Task 2: `runs/` layout (TDD)

**Files:**
- Modify: `scripts/trace_step.py` (path functions + start-run + finish-run; delete `migrate_fallback_trace`)
- Modify: `scripts/test_trace_step.py` (new layout tests; update tests assuming old layout)

- [ ] **Step 1: Write failing layout tests** (append to `scripts/test_trace_step.py`; follow the file's existing helper conventions — read its first ~80 lines first; it drives the CLI via subprocess with an env-overridden log dir. Adapt these to those conventions):

```python
def test_start_run_creates_run_dir_under_runs(tmp_env):
    # tmp_env fixture must set TRACE_RUNS_DIR to a tmp dir (adapt existing fixture)
    run_id = start_run(tmp_env, company="Acme", role="PM")
    run_dir = tmp_env.runs_dir / run_id
    assert run_dir.is_dir()
    assert (run_dir / "trace.jsonl").exists()          # run_start already appended


def test_trace_never_written_to_role_folder(tmp_env):
    run_id = start_run(tmp_env, company="Acme", role="PM")
    set_role_folder(tmp_env, run_id, tmp_env.workspace_role_dir)
    begin_end_step(tmp_env, step="1")
    assert not list(tmp_env.workspace_role_dir.glob("*.jsonl"))
    events = read_trace(tmp_env, run_id)
    assert events[-1]["role_folder"] == str(tmp_env.workspace_role_dir)


def test_state_lives_in_runs_dot_active(tmp_env):
    start_run(tmp_env, company="Acme", role="PM")
    assert (tmp_env.runs_dir / ".active-run.json").exists()


def test_finish_appends_to_runs_summary(tmp_env):
    run_id = run_full_ok(tmp_env)                       # helper: start→steps→finish
    summary = (tmp_env.runs_dir / "summary.jsonl").read_text().strip().splitlines()
    assert json.loads(summary[-1])["run_id"] == run_id
```

- [ ] **Step 2: Run — verify the new tests fail, old suite still green**

- [ ] **Step 3: Implement the layout in `trace_step.py`**

Replace the path layer (current lines ~65–78) with:

```python
def runs_dir() -> Path:
    """Repo-local run store. TRACE_RUNS_DIR overrides for tests/harnesses."""
    override = os.environ.get("TRACE_RUNS_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / "runs"


def active_state_path() -> Path:
    return runs_dir() / ".active-run.json"


def run_dir_for(run_id: str) -> Path:
    return runs_dir() / run_id


def global_summary_path() -> Path:
    return runs_dir() / "summary.jsonl"
```

Then: `trace_path(state)` returns `run_dir_for(state["run_id"]) / "trace.jsonl"` unconditionally; `start-run` mkdirs the run dir; DELETE `migrate_fallback_trace()` and the `fallback_trace` state field and every call site; `set-role-folder` no longer moves the trace file. Keep every validator, the state machine, and event schemas untouched in this task.

- [ ] **Step 4: Update old-layout assumptions in existing tests** (they set `JD_TO_READY_LOG_DIR` and expect per-role traces — switch env var to `TRACE_RUNS_DIR`, expectations to `runs/<id>/trace.jsonl`). The point of the state machine tests (ordering, one-open-step, seq continuity, token validation) must survive unchanged — only WHERE files live changes.

- [ ] **Step 5: Full suite green** (`pytest scripts/` → 125 passed ±, 0 failed) **and commit**

```bash
git add scripts/ && git commit -m "feat: trace runs/ layout — one dir per run, repo-local state and summary"
```

---

### Task 3: Schema v2 — `reason` + `sources` + primitive run-type (TDD)

**Files:**
- Modify: `scripts/trace_step.py`, `scripts/test_trace_step.py`

- [ ] **Step 1: Failing tests**

```python
def test_begin_requires_reason_and_sources(tmp_env):
    start_run(tmp_env, company="Acme", role="PM")
    rc, err = begin_step_raw(tmp_env, step="1")          # no --reason/--sources
    assert rc != 0 and "reason" in err

def test_begin_records_reason_and_sources(tmp_env):
    start_run(tmp_env, company="Acme", role="PM")
    begin_step(tmp_env, step="1", reason="file the JD so downstream steps have a folder",
               sources=[".claude/skills/interview-prep-intake/SKILL.md",
                        "workspace/Pipeline.md"])
    ev = read_trace_last(tmp_env)
    assert ev["reason"] and ev["sources"][0].endswith("SKILL.md")

def test_sources_must_be_json_array(tmp_env):
    start_run(tmp_env, company="Acme", role="PM")
    rc, err = begin_step_raw(tmp_env, step="1", reason="r", sources="not-json")
    assert rc != 0

def test_run_start_carries_schema_version_2(tmp_env):
    start_run(tmp_env, company="Acme", role="PM")
    assert read_trace_first(tmp_env)["schema_version"] == 2

def test_primitive_run_type(tmp_env):
    run_id = start_run(tmp_env, run_type="primitive", skill="tailor-resume",
                       company="Acme", role="PM")
    ev = read_trace_first(tmp_env)
    assert ev["required_steps"] == ["main"] and ev["skill"] == "tailor-resume"

def test_primitive_requires_skill(tmp_env):
    rc, err = start_run_raw(tmp_env, run_type="primitive")   # no --skill
    assert rc != 0 and "skill" in err
```

- [ ] **Step 2: Implement**

In `trace_step.py`:
- `RUN_TYPES["primitive"] = ["main"]`; `start-run` gains `--skill` (required iff `--run-type primitive`, else defaults to run-type value); `skill` stored in state and stamped on `run_start`.
- `run_start` event gains `"schema_version": 2`.
- `begin` gains required `--reason` (non-empty string) and `--sources` (strict JSON array of strings; MAY be `[]` only with `--sources '[]'` explicit). Both stamped on `step_begin`.
- Validator wiring mirrors the existing `--produced/--gaps` strict-JSON pattern (`parse_json_strict` + `validate_array`).

- [ ] **Step 3: Suite green, commit**

```bash
git add scripts/ && git commit -m "feat: trace schema v2 — reason+sources on steps, primitive run-type"
```

---

### Task 4: `render_run_report.py` (TDD)

**Files:**
- Create: `scripts/render_run_report.py`, `scripts/test_render_run_report.py`

- [ ] **Step 1: Failing tests** — build a fixture trace by DRIVING THE REAL CLI in a tmp runs dir (start → two steps with reason/sources, one tool-event, one gap → finish), then:

```python
def test_report_written_next_to_trace(fixture_run):
    report = render(fixture_run.run_dir)
    assert report == fixture_run.run_dir / "report.md"

def test_report_has_repair_section_mapping_outputs_to_sources(fixture_run):
    text = render(fixture_run.run_dir).read_text()
    assert "## How to change an output" in text
    # the step that produced the resume lists its sources as the edit points
    assert "workspace/Resume Achievements Master.md" in text

def test_report_summarizes_steps_gaps_tokens_tools(fixture_run):
    text = render(fixture_run.run_dir).read_text()
    for needle in ("| Step |", "Gaps", "Tokens", "tool calls"):
        assert needle in text

def test_renderer_tolerates_schema_v1_traces(tmp_path):
    # v1 = no reason/sources/schema_version; renderer must not crash, marks fields "—"
    write_minimal_v1_trace(tmp_path / "trace.jsonl")
    assert "—" in render(tmp_path).read_text()
```

- [ ] **Step 2: Implement `scripts/render_run_report.py`**

```python
"""Render runs/<run-id>/trace.jsonl into a human report (report.md).

The report is the user's repair manual: every step shows WHY it ran (reason)
and WHICH files shaped its output (sources) — edit those files to change the
behavior. Tolerates schema v1 traces (missing reason/sources render as "—").
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DASH = "—"


def read_events(trace: Path) -> list[dict]:
    events = []
    for line in trace.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


def fmt_tokens(tokens: dict | None) -> str:
    if not tokens or tokens.get("total") is None:
        return DASH
    return str(tokens["total"])


def render(run_dir: Path) -> Path:
    events = read_events(run_dir / "trace.jsonl")
    start = next(e for e in events if e["event"] == "run_start")
    finish = next((e for e in events if e["event"] in ("run_finish", "run_abort")), None)
    begins = {e["step"]: e for e in events if e["event"] == "step_begin"}
    ends = {e["step"]: e for e in events if e["event"] == "step_end"}
    tools = [e for e in events if e["event"] == "tool_event"]

    lines = [f"# Run report — {start.get('skill', start.get('run_id'))}", ""]
    lines += [f"- **Run:** `{start['run_id']}`  ·  **Status:** "
              f"{(finish or {}).get('status', 'INCOMPLETE')}",
              f"- **Company / role:** {start.get('company', DASH)} — {start.get('role', DASH)}",
              f"- **Schema:** v{start.get('schema_version', 1)}  ·  "
              f"**Tool calls:** {len(tools)}", ""]

    lines += ["## Steps", "", "| Step | Status | Reason | Tokens |", "|---|---|---|---|"]
    for step, b in begins.items():
        e = ends.get(step, {})
        lines.append(f"| {step} | {e.get('status', 'OPEN')} | "
                     f"{b.get('reason', DASH)} | {fmt_tokens(e.get('tokens'))} |")
    lines.append("")

    lines += ["## How to change an output", ""]
    for step, b in begins.items():
        produced = ends.get(step, {}).get("produced") or []
        srcs = b.get("sources") or [DASH]
        what = ", ".join(f"`{p}`" for p in produced) if produced else "(no files)"
        lines.append(f"- **Step {step}** produced {what} — shaped by: "
                     + ", ".join(f"`{s}`" for s in srcs)
                     + f". Don't like it? Edit those files and re-run. Why it ran: {b.get('reason', DASH)}")
    lines.append("")

    gaps = [g for e in ends.values() for g in (e.get("gaps") or [])]
    lines += ["## Gaps", ""] + ([f"- `{g.get('kind', '?')}` ({g.get('source', '?')}): "
                                 f"{g.get('detail', '')}" for g in gaps] or ["- none"])
    lines.append("")

    out = run_dir / "report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: render_run_report.py <run-dir>", file=sys.stderr)
        return 2
    run_dir = Path(args[0])
    if not (run_dir / "trace.jsonl").exists():
        print(f"no trace.jsonl in {run_dir}", file=sys.stderr)
        return 1
    print(render(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

(Implementer: keep or improve, but the report MUST contain the four sections the tests pin: header, Steps table, "How to change an output", Gaps.)

- [ ] **Step 3: Suite green, commit**

```bash
git add scripts/ && git commit -m "feat: run report renderer — trace to human repair manual"
```

---

### Task 5: Wire the skills to the new contract

**Files:**
- Modify: `.claude/skills/jd-to-ready/SKILL.md` — every `trace_step.py` invocation path → `<repo root>/scripts/trace_step.py`; every `begin` gains `--reason "<why>" --sources '[<files this step reads>]'` (the skill text states per-step which sources: e.g. step 3 sources = tailor-resume SKILL.md + workspace/Resume Achievements Master.md + the JD); after `finish-run`, add: run `python3 "<repo root>/scripts/render_run_report.py" "<repo root>/runs/<run-id>"` and include the report path in the final summary.
- Modify: `.claude/skills/stage-outreach/SKILL.md` — read it first; ensure the same contract (it may lack explicit trace calls today — add them: `start-run --run-type stage-outreach`, begins with reason/sources per step 4/4b/4c/5, finish + render).
- Modify: 6 primitive SKILL.mds (`interview-prep-intake`, `tailor-resume`, `find-contacts`, `enrich-contacts`, `verify-emails`, `write-outreach`) — add a short **"Standalone trace"** section: when invoked directly (not from an orchestrator), run `start-run --run-type primitive --skill <name>`, one `begin`/`end` around the work (step `main`, reason + sources), then `finish-run` + render. When invoked from an orchestrator (pipeline mode), do NOT start a run — the orchestrator's trace owns the steps (Decision 5).
- Modify: `.claude/skills/jd-to-ready/{TRACEABILITY.md,RUNBOOK.md,TRACE_TEST_PLAN.md,TRACEABILITY_IMPLEMENTATION_SUMMARY.md}` + `.claude/skills/two-orchestrator-e2e-test/SKILL.md` — update every `trace_step.py`/schema-doc path reference; the e2e skill's "do NOT run trace_step.py" instruction remains valid (subagent Stop-hook rationale unchanged).

- [ ] Steps: edit → guard green → grep sweep `grep -rn "jd-to-ready/scripts/trace_step\|\.jd-to-ready-trace" .claude/ scripts/ docs/ CLAUDE.md AGENTS.md` returns nothing → commit `docs: skills adopt shared trace contract (reason+sources, runs/ layout)`.

---

### Task 6: Docs consolidation + end-to-end smoke

**Files:**
- Move: `.claude/skills/jd-to-ready/TRACE_SCHEMA.md` → `docs/trace/TRACE_SCHEMA.md`; `.claude/skills/jd-to-ready/TOKEN_ACCOUNTING.md` → `docs/trace/TOKEN_ACCOUNTING.md` (git mv)
- Modify: `docs/trace/TRACE_SCHEMA.md` — retitle "Trace Schema (v2, all skills)"; add `reason`/`sources` to `step_begin` required fields; add `schema_version` to `run_start`; add `primitive` to the run-type table; replace the per-role/fallback location prose with the `runs/` layout; keep failure patterns, gap registry, token rules, healthy-trace checklist as-is.
- Modify: pointers in CLAUDE.md + AGENTS.md ("Before editing its logging/tracing, read …") → new doc paths.

- [ ] **Smoke (the acceptance test of the whole plan):** drive a synthetic primitive run end-to-end with the real CLI against the real `runs/` dir:

```bash
python3 scripts/trace_step.py start-run --run-id smoke-$(date +%s) --run-type primitive \
  --skill tailor-resume --company Acme --role "Data PM" --source manual
python3 scripts/trace_step.py begin --step main --primitive tailor-resume --mode standalone \
  --prediction "resume md written" --inputs-summary "fixture JD" \
  --reason "user asked for a tailored resume" \
  --sources '[".claude/skills/tailor-resume/SKILL.md", "workspace/Resume Achievements Master.md"]'
python3 scripts/trace_step.py end --step main --primitive tailor-resume --mode standalone \
  --status ok --prediction-met true --produced '["workspace/Roles/x/resume.md"]' --gaps '[]'
python3 scripts/trace_step.py finish-run
python3 scripts/render_run_report.py runs/<the-run-id>   # then READ the report:
```
The report must let you answer: "the resume wording comes from `workspace/Resume Achievements Master.md` — edit it there." Delete the smoke run dir after (`rm -rf runs/smoke-*` — allowed for synthetic smoke runs only).

- [ ] Full suite green + guard green → commit `docs: trace schema v2 docs at docs/trace/, smoke-verified end to end`.

---

## Self-Review Notes

- **Spec coverage:** success criterion 1 fully (runs/<id>/trace.jsonl + report.md, reason+sources, repair chain); Decision 5 both halves (piped = orchestrator steps, standalone = primitive run-type). Criterion 3's tool/LLM ratio gets its raw material (`tool_event` count already in trace; renderer surfaces it) — the eval-side metric computation is Plan 3.
- **Never-break-userspace:** live system runs `main`'s copy of trace_step.py inside the jd-to-ready skill — untouched. Old traces/logs are not migrated or deleted. This branch's e2e skill keeps its no-trace rule.
- **Deliberate deletion:** `migrate_fallback_trace()` + per-role trace files — obsoleted by run-dir-from-start; called out so reviewers treat it as intended.
- **Risk:** Task 5 touches 8+ SKILL.md files (LLM prompts) — same meaning-preservation discipline as foundation Task 5; reviews must diff-read jd-to-ready fully.
- **Type consistency:** `runs_dir()/run_dir_for()/active_state_path()/global_summary_path()` names used consistently across Tasks 2–4; renderer consumes exactly the schema fields Task 3 stamps.
```
