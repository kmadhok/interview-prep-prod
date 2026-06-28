# Two-Orchestrator Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the monolithic `jd-to-ready` automation into two apply-gated skills — `jd-to-ready` (prep, fires on save) and `stage-outreach` (LinkedIn + Gmail, fires on apply) — so expensive, account-risky work only happens for jobs Kanu actually applies to.

**Architecture:** The primitives (`interview-prep-intake`, `tailor-resume`, `find-contacts`, `enrich-contacts`, `verify-emails`, `write-outreach`) do not change. Only the compose layer is recut and the trace helper is made run-type-aware. State lives in files that already exist (resume `.md` = prepped, Pipeline `Applied` token = applied, `STAGED in Gmail <date>` = staged) — **no `role_state.json`**. A new deterministic Pass B worklist reader (pure-function + thin-CLI, in the `dedupe.py` style) drives the apply-side poll. The two skills hand off via disk artifacts plus one new `.classification.json`.

**Tech Stack:** Python 3 (stdlib only — `argparse`, `json`, `re`, `pathlib`), `unittest`/`pytest`, Markdown SKILL.md files, PowerShell cron on the PC (ops-only, not unit-tested).

**Spec sources:** `Automation Design - Two-Orchestrator/` — `Automation Architecture - Purpose.md`, `… - Two-Orchestrator Split.md`, `… - Diagrams.md`, `Spec - Orchestrator 1 (jd-to-ready prep).md`, `Spec - Orchestrator 2 (stage-outreach).md`, `Spec - Applied Detector.md`.

**Key existing files (read before starting):**
- `.claude/skills/jd-to-ready/scripts/trace_step.py` — the trace helper. `REQUIRED_STEPS` (line 23) is a module constant referenced in `load_state`, `validate_step`, `missing_steps`, `closed_steps_from_state_and_events`, `cmd_start`, and the finish/abort summaries. Making it run-type-aware is the central code change.
- `.claude/skills/jd-to-ready/scripts/test_trace_step.py` — CLI regression tests against an isolated `JD_TO_READY_LOG_DIR`. Follow its style.
- `scripts/drip_runner/dedupe.py`, `scripts/drip_runner/saved_jobs_ledger.py` — the canonical "pure function + thin CLI, `utf-8-sig` reads, fail-loud on corrupt input" pattern the new Pass B reader must follow.
- `scripts/drip_runner/conftest.py` — puts the package dir on `sys.path` so `import dedupe` resolves from repo root.
- `.claude/skills/jd-to-ready/SKILL.md` — the monolith being cut down. Step headers at lines 100 (Step 1), 113 (Step 2), 195 (Step 3), 212 (Step 3.5), 248 (Step 4), 269 (Step 4b), 286 (Step 4c), 304 (Step 5), 328 (Step 6), 341 (Step 7).

**Invariants every task must preserve** (from `Purpose.md`): human-gated (never sends) · protect the LinkedIn channel · no babysitting · fail loud never silent · truth from existing files.

---

## File Structure

**New files:**
- `scripts/drip_runner/outreach_worklist.py` — pure reader: given `Pipeline.md` text, return roles marked `Applied` with no `STAGED` marker. Thin CLI like `dedupe.py`.
- `scripts/drip_runner/test_outreach_worklist.py` — pytest for the reader.
- `scripts/drip_runner/prepped_not_applied.py` — pure reader for the fail-loud nudge: roles `prepped` (resume `.md` in folder) but not `Applied`, older than a staleness threshold.
- `scripts/drip_runner/test_prepped_not_applied.py` — pytest for the nudge reader.
- `.claude/skills/stage-outreach/SKILL.md` — the new apply-side skill (steps 4/4b/4c/5/6/7).

**Modified files:**
- `.claude/skills/jd-to-ready/scripts/trace_step.py` — add run-type → required-steps map; thread `run_type` through state; allow `set-role-folder` to bind a pre-existing folder.
- `.claude/skills/jd-to-ready/scripts/test_trace_step.py` — tests for both run-types and the bind-existing-folder path.
- `.claude/skills/jd-to-ready/SKILL.md` — remove steps 4/4b/4c/5; add the `.classification.json` write; pass `--run-type jd-to-ready`; trim required-steps prose to `{1,2,3,3.5,6,7}`.
- `Automation Architecture - Drip Runner.md` + `scripts/drip_runner/README.md` — document the two-skill model and Pass A/Pass B.
- `scripts/drip_runner/runner-prompt.md` (or the cloud routine prompt) — drop step-3 drafting; add ack ruleset, monotonic-state guard, and the prepped-not-applied nudge.

**The two readers are split by responsibility, not layer:** `outreach_worklist.py` answers "what should Pass B stage?", `prepped_not_applied.py` answers "what should the nudge surface?". They share no state, so they are separate files with separate tests.

---

## Task 1: Run-type-aware required-steps in trace_step.py

The monolith's `finish-run` requires all of `{1,2,3,3.5,4,4b,4c,5,6,7}`. After the split, `jd-to-ready` must require only `{1,2,3,3.5,6,7}` and a new `stage-outreach` run-type must require `{4,4b,4c,5,6,7}`. The fix is a `RUN_TYPES` map; `REQUIRED_STEPS` stays as the default so existing callers and tests don't break.

**Files:**
- Modify: `.claude/skills/jd-to-ready/scripts/trace_step.py`
- Test: `.claude/skills/jd-to-ready/scripts/test_trace_step.py`

- [ ] **Step 1: Write the failing test for the run-type map**

Add to `.claude/skills/jd-to-ready/scripts/test_trace_step.py` (it currently uses `unittest`; add a plain module-level import test at the bottom of the file, before the `if __name__` guard):

```python
class RunTypeMapTests(unittest.TestCase):
    def test_run_type_required_steps(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("trace_step", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.required_steps_for("jd-to-ready"), ["1", "2", "3", "3.5", "6", "7"])
        self.assertEqual(mod.required_steps_for("stage-outreach"), ["4", "4b", "4c", "5", "6", "7"])

    def test_unknown_run_type_falls_back_to_full(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("trace_step", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # None / unknown → the legacy full list, so old callers keep working
        self.assertEqual(mod.required_steps_for(None), mod.REQUIRED_STEPS)
        self.assertEqual(mod.required_steps_for("bogus"), mod.REQUIRED_STEPS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -k RunTypeMap -v`
Expected: FAIL with `AttributeError: module 'trace_step' has no attribute 'required_steps_for'`

- [ ] **Step 3: Add the run-type map and helper**

In `.claude/skills/jd-to-ready/scripts/trace_step.py`, directly below the `REQUIRED_STEPS = [...]` definition (after line 23), add:

```python
# Per-run-type required-steps. REQUIRED_STEPS above stays the legacy "full"
# list so any caller that does not pass a run-type keeps the old contract.
RUN_TYPES = {
    "jd-to-ready": ["1", "2", "3", "3.5", "6", "7"],
    "stage-outreach": ["4", "4b", "4c", "5", "6", "7"],
}


def required_steps_for(run_type: str | None) -> list[str]:
    """Required steps for a run-type, defaulting to the legacy full list."""
    return RUN_TYPES.get(run_type, REQUIRED_STEPS)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -k RunTypeMap -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/jd-to-ready/scripts/trace_step.py .claude/skills/jd-to-ready/scripts/test_trace_step.py
git commit -m "feat(trace): add run-type → required-steps map (default = legacy full)"
```

---

## Task 2: Thread run_type through start-run and state

`start-run` must accept `--run-type`, persist it in state, and use it for the run's required-steps everywhere they're computed. Default (no flag) must stay the legacy full list so the monolith's existing tests pass unchanged.

**Files:**
- Modify: `.claude/skills/jd-to-ready/scripts/trace_step.py`
- Test: `.claude/skills/jd-to-ready/scripts/test_trace_step.py`

- [ ] **Step 1: Write the failing test**

Add to `RunTypeMapTests` in `test_trace_step.py`. This drives a full stage-outreach run through the CLI and asserts finish succeeds with only the apply-side steps closed. Reuse the existing test's env/role-folder setup pattern (`self.env`, `self.role_folder`, `TOKENS`):

```python
    def test_stage_outreach_run_finishes_with_apply_steps_only(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        log_dir = root / "logs"
        role_folder = root / "Roles" / "Acme - Agent Builder"
        role_folder.mkdir(parents=True)
        env = os.environ.copy()
        env["JD_TO_READY_LOG_DIR"] = str(log_dir)

        def run(*args):
            return subprocess.run(
                [sys.executable, str(SCRIPT), *args],
                env=env, capture_output=True, text=True,
            )

        self.assertEqual(run("start-run", "--run-type", "stage-outreach",
                             "--company", "Acme", "--role", "Agent Builder").returncode, 0)
        self.assertEqual(run("set-role-folder", "--role-folder", str(role_folder),
                             "--company", "Acme", "--role", "Agent Builder").returncode, 0)
        for step in ["4", "4b", "4c", "5", "6", "7"]:
            self.assertEqual(run("begin", "--step", step, "--primitive", "p",
                                 "--prediction", "x").returncode, 0, f"begin {step}")
            self.assertEqual(run("end", "--step", step, "--primitive", "p",
                                 "--status", "ok", "--prediction-met", "true",
                                 "--tokens", TOKENS).returncode, 0, f"end {step}")
        finished = run("finish-run", "--status", "ok")
        self.assertEqual(finished.returncode, 0, finished.stderr)
        tmp.cleanup()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -k stage_outreach_run -v`
Expected: FAIL — `finish-run` rejects because state still requires the full legacy list (step 1/2/3/3.5 missing), or `--run-type` is an unrecognized argument.

- [ ] **Step 3: Add --run-type and persist it**

In `trace_step.py`:

(a) In `build_parser`, on the `start-run` subparser (after line 579's `--test-run`), add:

```python
    p.add_argument("--run-type", default="jd-to-ready")
```

Note the default is `jd-to-ready`, NOT the legacy full list — every real start-run after the split names its run-type. The legacy full list survives only as `required_steps_for(None)` for safety; production always passes a run-type.

(b) In `cmd_start`, replace the two `REQUIRED_STEPS` uses (the `state` dict's `"required_steps"` and the `run_start` event's `required_steps`) so they derive from the run-type:

```python
def cmd_start(args: argparse.Namespace) -> int:
    if load_state():
        return fail("An active jd-to-ready run already exists. Finish or abort it before starting another.")
    ensure_dirs()
    run_id = args.run_id or f"jdtr-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    role_folder = args.role_folder
    is_test_run = bool(args.test_run)
    if role_folder:
        error = validate_role_folder(role_folder, is_test_run)
        if error:
            return fail(error)
    run_type = args.run_type
    required = required_steps_for(run_type)
    state = {
        "run_id": run_id,
        "run_type": run_type,
        "company": args.company,
        "role": args.role,
        "role_folder": role_folder,
        "started_at": now_iso(),
        "fallback_trace": str(global_run_dir() / f"{run_id}.jsonl"),
        "required_steps": required,
        "closed_steps": [],
        "current_step": None,
        "next_seq": 1,
        "is_test_run": is_test_run,
    }
    save_state(state)
    append_event(
        state,
        {
            "event": "run_start",
            "company": args.company,
            "role": args.role,
            "required_steps": required,
            "run_type": run_type,
            "source": "jd-to-ready",
            "is_test_run": is_test_run,
        },
    )
    print(run_id)
    return 0
```

(c) In `load_state`, add a default so older state files without `run_type` still load (after line 85's `state.setdefault("is_test_run", False)`):

```python
    state.setdefault("run_type", None)
```

Everywhere else (`validate_step`, `missing_steps`, `closed_steps_from_state_and_events`, the finish/abort summaries) already reads `state.get("required_steps", REQUIRED_STEPS)`, so they now pick up the run-type's list automatically — **do not change them.**

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -k stage_outreach_run -v`
Expected: PASS

- [ ] **Step 5: Run the full trace suite for regressions**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -v`
Expected: PASS — all pre-existing tests still green (the legacy default path is unchanged).

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/jd-to-ready/scripts/trace_step.py .claude/skills/jd-to-ready/scripts/test_trace_step.py
git commit -m "feat(trace): thread --run-type through start-run and state"
```

---

## Task 3: Allow set-role-folder to bind a pre-existing folder

`stage-outreach` starts on a role that Skill 1 already prepped, so its `set-role-folder` must bind an **existing** folder under `Roles/`. `validate_role_folder` (lines 166-178) already accepts any folder directly under `Roles/` and does not require absence — so binding an existing folder already works. This task adds a regression test that pins that behavior so a future edit can't break it, and confirms `set-role-folder` never creates the folder.

**Files:**
- Test: `.claude/skills/jd-to-ready/scripts/test_trace_step.py`
- Modify (only if the test fails): `.claude/skills/jd-to-ready/scripts/trace_step.py`

- [ ] **Step 1: Write the failing/pinning test**

Add to `RunTypeMapTests`:

```python
    def test_set_role_folder_binds_existing_folder_without_creating(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        env = os.environ.copy()
        env["JD_TO_READY_LOG_DIR"] = str(root / "logs")
        existing = root / "Roles" / "Acme - Agent Builder"
        existing.mkdir(parents=True)
        marker = existing / "Kanu Madhok Resume - Acme Agent Builder.md"
        marker.write_text("prepped", encoding="utf-8")

        def run(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *args],
                                  env=env, capture_output=True, text=True)

        self.assertEqual(run("start-run", "--run-type", "stage-outreach").returncode, 0)
        res = run("set-role-folder", "--role-folder", str(existing))
        self.assertEqual(res.returncode, 0, res.stderr)
        # binding must not clobber what Skill 1 wrote
        self.assertEqual(marker.read_text(encoding="utf-8"), "prepped")
        tmp.cleanup()
```

- [ ] **Step 2: Run test to verify current behavior**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -k binds_existing -v`
Expected: PASS (this behavior already works; the test pins it). If it FAILS, `set-role-folder` is rejecting existing folders — in that case make the minimal fix to `cmd_set_role_folder`/`validate_role_folder` so an existing folder directly under `Roles/` is accepted, then re-run.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/jd-to-ready/scripts/test_trace_step.py
git commit -m "test(trace): pin set-role-folder binding an existing role folder"
```

---

## Task 4: Pass B worklist reader (Applied & not STAGED)

Pass B's job is "which roles should `stage-outreach` run on?" — Pipeline rows marked `Applied` with no `STAGED in Gmail` marker. This is a deterministic, no-LLM read, pytest-covered like `dedupe.py`. It returns a list of `(company, role)` from the matching rows so the caller can locate the folder.

**Pipeline.md row format** (verify against the live file before finalizing the regex): a role row is a Markdown table line whose first bold cell is `**<Company> — <Role>**`. "Applied" and "STAGED in Gmail" appear as tokens in the row text. The reader keys on those tokens within a single row, never across rows.

**Files:**
- Create: `scripts/drip_runner/outreach_worklist.py`
- Test: `scripts/drip_runner/test_outreach_worklist.py`

- [ ] **Step 1: Confirm the real row format**

Run: `grep -n "Applied\|STAGED" "Pipeline.md" | head -20`
Read 3-4 matching lines to confirm: (a) the bold `**Company — Role**` cell shape, (b) the exact `Applied` token, (c) whether any `STAGED in Gmail` markers already exist. Adjust the regex in Step 3 to match what you see. Do not invent a format — match the file.

- [ ] **Step 2: Write the failing test**

Create `scripts/drip_runner/test_outreach_worklist.py`:

```python
from outreach_worklist import row_is_applied, row_is_staged, applied_not_staged

APPLIED = "| **Acme — Agent Builder** | Applied 2026-06-20 | ... | recruiter TBD |"
STAGED  = "| **Beta — ML Engineer** | Applied 2026-06-19 · STAGED in Gmail 2026-06-20 | ... |"
CONSID  = "| **Gamma — Data Sci** | Considering — JD reviewed, not yet applied | ... |"

PIPELINE = "\n".join([
    "## Active / applied",
    APPLIED,
    STAGED,
    "## Considering / not yet applied",
    CONSID,
])

def test_row_predicates():
    assert row_is_applied(APPLIED)
    assert not row_is_applied(CONSID)
    assert row_is_staged(STAGED)
    assert not row_is_staged(APPLIED)

def test_applied_not_staged_returns_only_actionable_rows():
    rows = applied_not_staged(PIPELINE)
    names = [company for company, role in rows]
    assert names == ["Acme"]            # Beta is STAGED, Gamma is not Applied
    assert rows[0] == ("Acme", "Agent Builder")

def test_empty_pipeline_is_empty_worklist():
    assert applied_not_staged("") == []
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd scripts/drip_runner && python3 -m pytest test_outreach_worklist.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'outreach_worklist'`

- [ ] **Step 4: Implement the reader**

Create `scripts/drip_runner/outreach_worklist.py` (mirror `dedupe.py`'s pure-function + thin-CLI shape; if your Step 1 inspection showed a different bold-cell or token format, update the regex/tokens to match):

```python
"""Pass B worklist: Pipeline rows marked Applied with no STAGED marker.

Pure functions + a thin CLI, same shape as dedupe.py. No LLM, no network.
The apply-side poll (stage-outreach) runs on exactly the rows this returns.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# First bold cell of a role row: **<Company> — <Role>**  (em dash separator)
_ROW = re.compile(r"\*\*\s*(?P<company>.+?)\s+—\s+(?P<role>.+?)\s*\*\*")
_APPLIED = re.compile(r"\bApplied\b")
_STAGED = re.compile(r"STAGED in Gmail")


def row_is_applied(row: str) -> bool:
    return bool(_APPLIED.search(row or ""))


def row_is_staged(row: str) -> bool:
    return bool(_STAGED.search(row or ""))


def applied_not_staged(pipeline_text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in (pipeline_text or "").splitlines():
        if not row_is_applied(line) or row_is_staged(line):
            continue
        m = _ROW.search(line)
        if m:
            out.append((m.group("company").strip(), m.group("role").strip()))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Pass B worklist: Applied & not STAGED")
    p.add_argument("--pipeline", required=True)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    rows = applied_not_staged(text)
    for company, role in rows:
        print(f"{company}\t{role}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd scripts/drip_runner && python3 -m pytest test_outreach_worklist.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Smoke-test against the live Pipeline.md**

Run: `cd scripts/drip_runner && python3 outreach_worklist.py --pipeline "../../Pipeline.md"`
Expected: prints zero or more `Company<TAB>Role` lines, none of which carry a STAGED marker. Eyeball against the file — if a known-applied row is missing or a STAGED row leaks through, fix the regex and re-run Steps 5-6.

- [ ] **Step 7: Commit**

```bash
git add scripts/drip_runner/outreach_worklist.py scripts/drip_runner/test_outreach_worklist.py
git commit -m "feat(drip): Pass B worklist reader (Applied & not STAGED)"
```

---

## Task 5: Prepped-but-not-applied nudge reader (fail-loud)

The one silent-failure path (`Spec - Applied Detector.md` §"Fail-loud"): a role is `prepped` (resume `.md` in folder) but never marked `Applied`, so Skill 2 never fires and the highest-value output is silently dropped. This reader surfaces those roles past a staleness threshold so the secretary/report can nudge.

Because "prepped" is read from the folder and "applied" from Pipeline.md, this reader takes both: a list of role folders (with their resume mtime/age in days, computed by the caller) and the Pipeline text. Keeping age-in-days as a caller-supplied input keeps the function pure and testable (no clock dependency, consistent with the repo's no-`Date.now` discipline).

**Files:**
- Create: `scripts/drip_runner/prepped_not_applied.py`
- Test: `scripts/drip_runner/test_prepped_not_applied.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/drip_runner/test_prepped_not_applied.py`:

```python
from prepped_not_applied import role_is_applied_in_pipeline, stale_prepped_not_applied

PIPELINE = "\n".join([
    "| **Acme — Agent Builder** | Applied 2026-06-20 | ... |",
    "| **Beta — ML Engineer** | Considering — JD reviewed, not yet applied | ... |",
])

def test_role_is_applied_in_pipeline():
    assert role_is_applied_in_pipeline("Acme", PIPELINE)
    assert not role_is_applied_in_pipeline("Beta", PIPELINE)
    assert not role_is_applied_in_pipeline("Gamma", PIPELINE)

def test_stale_prepped_not_applied_filters_on_age_and_state():
    # caller passes (company, role, age_days) for each prepped folder
    prepped = [
        ("Acme", "Agent Builder", 9),   # applied → excluded
        ("Beta", "ML Engineer", 9),     # not applied, stale → INCLUDED
        ("Gamma", "Data Sci", 1),       # not applied but fresh (< threshold) → excluded
    ]
    out = stale_prepped_not_applied(prepped, PIPELINE, threshold_days=3)
    assert out == [("Beta", "ML Engineer", 9)]

def test_threshold_boundary_is_inclusive():
    prepped = [("Beta", "ML Engineer", 3)]
    assert stale_prepped_not_applied(prepped, PIPELINE, threshold_days=3) == [("Beta", "ML Engineer", 3)]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts/drip_runner && python3 -m pytest test_prepped_not_applied.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'prepped_not_applied'`

- [ ] **Step 3: Implement the reader**

Create `scripts/drip_runner/prepped_not_applied.py`:

```python
"""Fail-loud nudge: roles prepped (resume in folder) but never marked Applied.

Pure function + thin CLI. The caller is responsible for the filesystem read
(which folders have a tailored resume .md, and each resume's age in days) so
this stays clock-free and unit-testable. The secretary/report turns the result
into a visible "did you apply?" nudge — the machine reminds, Kanu decides.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path


def role_is_applied_in_pipeline(company: str, pipeline_text: str) -> bool:
    # A role is applied iff its bold row carries the Applied token. Word-bounded
    # company match avoids a short name hitting inside another (dedupe.py rule).
    company = (company or "").strip()
    if not company:
        return False
    for line in (pipeline_text or "").splitlines():
        if re.search(r"\b" + re.escape(company) + r"\b", line, re.IGNORECASE) \
                and re.search(r"\bApplied\b", line):
            return True
    return False


def stale_prepped_not_applied(prepped, pipeline_text, threshold_days=3):
    """prepped = iterable of (company, role, age_days). Returns those that are
    NOT applied and whose age_days >= threshold_days."""
    out = []
    for company, role, age_days in prepped:
        if age_days < threshold_days:
            continue
        if role_is_applied_in_pipeline(company, pipeline_text):
            continue
        out.append((company, role, age_days))
    return out


def _scan_prepped(roles_dir: str):
    """Folders under Roles/ holding a tailored resume .md, with its age in days.

    Age is computed here (the CLI boundary) so the pure functions stay clock-free.
    """
    from datetime import datetime, timezone
    base = Path(roles_dir)
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        resumes = list(folder.glob("Kanu Madhok Resume - *.md"))
        if not resumes:
            continue
        newest = max(r.stat().st_mtime for r in resumes)
        age_days = (datetime.now(timezone.utc).timestamp() - newest) / 86400
        # company/role parsed from the folder name "Company - Role"
        name = folder.name
        company, _, role = name.partition(" - ")
        yield (company.strip(), role.strip(), int(age_days))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="prepped-but-not-applied nudge")
    p.add_argument("--roles-dir", required=True)
    p.add_argument("--pipeline", required=True)
    p.add_argument("--threshold-days", type=int, default=3)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    prepped = list(_scan_prepped(args.roles_dir))
    for company, role, age in stale_prepped_not_applied(text and prepped or prepped, text, args.threshold_days):
        print(f"{company}\t{role}\t{age}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts/drip_runner && python3 -m pytest test_prepped_not_applied.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Smoke-test against the live workspace**

Run: `cd scripts/drip_runner && python3 prepped_not_applied.py --roles-dir "../../Roles" --pipeline "../../Pipeline.md" --threshold-days 3`
Expected: prints `Company<TAB>Role<TAB>AgeDays` for any prepped-but-unapplied role older than 3 days, or nothing. Sanity-check a couple of lines against the actual folders.

- [ ] **Step 6: Commit**

```bash
git add scripts/drip_runner/prepped_not_applied.py scripts/drip_runner/test_prepped_not_applied.py
git commit -m "feat(drip): prepped-but-not-applied nudge reader (fail-loud seam)"
```

---

## Task 6: Recut jd-to-ready/SKILL.md to the prep half

Remove the apply-side steps (4/4b/4c/5) from the prose, add the `.classification.json` write after step 2, pass `--run-type jd-to-ready` to `start-run`, and update every required-steps list/instruction to `{1,2,3,3.5,6,7}`. This is a Markdown edit — no code — but it's load-bearing because the SKILL.md is the contract the orchestrator follows.

**Files:**
- Modify: `.claude/skills/jd-to-ready/SKILL.md`

- [ ] **Step 1: Update start-run to name the run-type**

In `.claude/skills/jd-to-ready/SKILL.md` (around line 62), change the start-run command to:

```
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py start-run --run-type jd-to-ready --company "<company if known>" --role "<role if known>"
```

- [ ] **Step 2: Add the .classification.json write to Step 2**

In the Step 2 section (line 113 onward), after the JSON is parsed/validated (around line 191's bullet describing `themes`), add an instruction:

```markdown
After validating the classification, **persist it for the apply-side skill**. Write `<role folder>/.classification.json`:

​```json
{
  "themes": [ {"tag": "<in-vocab tag>", "evidence": "<JD quote ≤25 words>"} ],
  "archetype": "<in-vocab archetype>",
  "archetype_rationale": "<1–2 sentences>",
  "notes": "<subagent notes or empty>",
  "classified_ts": "<YYYY-MM-DD>"
}
​```

This is the only hand-off `stage-outreach` needs to skip re-classifying. Same validated values you pass to step 3 — just a write to disk, no new logic.
```

(Strip the zero-width spaces before the inner fences when you actually write it — they're only here to keep this plan's code block from closing early.)

- [ ] **Step 3: Remove steps 4, 4b, 4c, 5 from the workflow**

Delete the Step 4 (line 248), Step 4b (269), Step 4c (286), and Step 5 (304) sections in full. Renumber nothing — steps 6 and 7 keep their numbers (the spec keeps numbers aligned with the monolith so 4/4b/4c/5 are simply absent). After deletion the workflow is: 1 → 2 → 3 → 3.5 → 6 → 7.

- [ ] **Step 4: Update the required-steps prose and finish-run instruction**

- Line ~343: change "confirm that steps `1`, `2`, `3`, `3.5`, `4`, `4b`, `4c`, `5`, `6`, and `7`" to "confirm that steps `1`, `2`, `3`, `3.5`, `6`, and `7`".
- Line ~382 (`"required_steps": [...]` in the example finish summary): change to `["1", "2", "3", "3.5", "6", "7"]`.
- Update the "What this skill produces" section (lines 26-37): remove items 3 (`.contacts-ledger.md` + `Verified Emails.md`) and 4 (`Cold Outreach.md` + Gmail drafts) from the produced list; add `.classification.json`. Change the **End state** line to: *"the resume is ready — apply on the ATS; once you mark the Pipeline row Applied, `stage-outreach` auto-stages the recruiter draft."*
- Update the primitives table (lines 12-19) and the orchestration prose (line 8): drop the 4/4b/4c/5 rows; note the pipeline now ends at the apply gate.

- [ ] **Step 5: Update the Pipeline-row Next action and description frontmatter**

- Wherever intake's Pipeline row "Next action" is set, make it: *"Resume ready — apply on the ATS; outreach auto-stages once the row is marked Applied."*
- Trim the `description:` frontmatter (line 3) so it no longer claims contacts/outreach are part of this skill — it now ends at resume + PDF. Keep the trigger language for filing/prep; remove "5 recruiter + 5 hiring-manager contacts… cold outreach drafted."

- [ ] **Step 6: Verify the skill still parses and the trace contract matches**

Run: `python3 -c "import re,sys; t=open('.claude/skills/jd-to-ready/SKILL.md').read(); assert '4c' not in t.split('## Workflow')[1].split('## Edge cases')[0] or 'absent' in t, 'apply-side step still present in workflow'; print('ok')"`
Expected: prints `ok` (no apply-side step bodies remain in the workflow section). If it asserts, you left a 4/4b/4c/5 body in — remove it.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/jd-to-ready/SKILL.md
git commit -m "feat(jd-to-ready): recut to prep half — drop steps 4/4b/4c/5, add .classification.json hand-off"
```

---

## Task 7: Author stage-outreach/SKILL.md (apply half)

The new skill: steps 4/4b/4c/5/6/7 lifted from the monolith, reading the folder + `.classification.json`, binding the existing folder in trace, run-type `stage-outreach`. Step bodies are the monolith's 4/4b/4c/5 verbatim — do not reinvent them; copy from the monolith's git history (the version before Task 6's deletion).

**Files:**
- Create: `.claude/skills/stage-outreach/SKILL.md`

- [ ] **Step 1: Recover the monolith's apply-side step bodies**

Run: `git show HEAD~1:.claude/skills/jd-to-ready/SKILL.md > /tmp/monolith_skill.md` (HEAD~1 = the commit before Task 6 deleted them; adjust the ref to the pre-deletion commit if more commits landed). Read the Step 4 / 4b / 4c / 5 sections from `/tmp/monolith_skill.md` — these are the verbatim bodies to lift.

- [ ] **Step 2: Write the skill frontmatter and trigger**

Create `.claude/skills/stage-outreach/SKILL.md` starting with:

```markdown
---
name: stage-outreach
description: Use this skill when a role Kanu has already APPLIED to needs its recruiter outreach staged — find the recruiter on LinkedIn, verify their email, draft the cold outreach, and drop a Gmail draft addressed to them (never sent). Fires from the PC's hourly Pass B poll on Pipeline rows marked Applied with no STAGED marker, or manually for an immediate draft. Reads the role folder + .classification.json that jd-to-ready already wrote. Do NOT trigger to file a JD (interview-prep-intake) or prep a resume (jd-to-ready) — this is strictly the post-apply, LinkedIn-bound, Gmail-drafting half.
---

# Stage Outreach (apply-side: find recruiter → verify email → Gmail draft)

This skill is the apply-gated half of the two-orchestrator split. It runs only on roles Kanu actually applied to, so all LinkedIn flag-risk and all Gmail writes live here. Steps 4/4b/4c/5 are lifted unchanged from the former monolithic `jd-to-ready`; the primitives own their domain logic — this skill only composes them.

Read root `AGENTS.md`/`CLAUDE.md` first; it overrides anything here.
```

- [ ] **Step 3: Write the preconditions and trace-open section**

Add:

```markdown
## Preconditions

- The role folder exists (jd-to-ready ran) and contains the tailored resume + `.classification.json`.
- The Pipeline row is marked `Applied` and carries no `STAGED in Gmail` marker.
- If `.classification.json` is missing (role prepped before the split), re-run the step-2 classifier once and write it — do NOT re-run intake or re-tailor the resume.

## Trace — open a SECOND, independent run

​```
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py start-run --run-type stage-outreach --company "<company>" --role "<role>"
python3 ~/.claude/skills/jd-to-ready/scripts/trace_step.py set-role-folder --role-folder "<absolute existing role folder>" --company "<company>" --role "<role>"
​```

`set-role-folder` binds the folder jd-to-ready already created — it must not create it. Required steps for this run-type are `{4, 4b, 4c, 5, 6, 7}`; `finish-run` fails closed until all are closed.
```

(Strip the zero-width fence guards when writing.)

- [ ] **Step 4: Paste the lifted step bodies (4/4b/4c/5) and the report/log steps**

From `/tmp/monolith_skill.md`, copy the Step 4, 4b, 4c, 5 sections verbatim into this skill, then add Step 6 (report-back) and Step 7 (final-log) sections. For Step 5's inputs, document that `archetype` + `lead_theme` come from `.classification.json` (not re-classified), `hooks[]` from 4b, `urgency` derived live from `Pipeline.md`. For Step 7's `finish-run`, the required-steps confirmation list is `{4, 4b, 4c, 5, 6, 7}`.

- [ ] **Step 5: Write the outputs, state-marker, and degradation sections**

Add (from `Spec - Orchestrator 2 (stage-outreach).md` §Outputs / §State / §Degradation):

```markdown
## Outputs

Folder gains `.contacts-ledger.md`, `Verified Emails.md`, `Cold Outreach.md`, and a Gmail draft addressed to the #1 recruiter (in Drafts, never sent). On success, write `STAGED in Gmail <YYYY-MM-DD>` to the folder and the Pipeline row — that marker is the terminal state the poll keys off, so a role carrying it is never re-staged.

## Degradation & edge cases

- LinkedIn daemon down → STOP before step 4; write nothing; leave the row un-STAGED so the next poll retries.
- Zero contacts → write `Cold Outreach.md` with empty tables + a note; do not fabricate.
- EmailFinder unavailable / inferred email → verify-emails degrades to inferred rows; write-outreach still drafts, falling back to Kanu's own address with a flagged gap.
- Internal-mobility role → skip; write `STAGED` with a note ("internal — handled in person").
- Unconfirmed hard gate flagged by jd-to-ready → do not stage; leave the row un-STAGED until Kanu confirms.

## What this skill does NOT do

No intake, no classification (reads `.classification.json`), no resume work. Never decides "applied" itself — acts only on rows already marked Applied. Drafts only, never sends.
```

- [ ] **Step 6: Verify the new skill is self-consistent**

Run: `grep -c "STAGED in Gmail" .claude/skills/stage-outreach/SKILL.md` → expect ≥ 2 (state section + outputs). Run: `grep -n "run-type stage-outreach" .claude/skills/stage-outreach/SKILL.md` → expect the two trace commands. Confirm no `interview-prep-intake` / `tailor-resume` step bodies leaked in (those belong to Skill 1).

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/stage-outreach/SKILL.md
git commit -m "feat(stage-outreach): new apply-side skill (steps 4/4b/4c/5/6/7, run-type stage-outreach)"
```

---

## Task 8: Update the cloud routine — drop drafting, add ack ruleset + nudge

The cloud routine becomes a pure Gmail secretary: sweep → reconcile Pipeline → mark Applied (with the specified ack ruleset) → detect sends → archive rejections → emit the prepped-not-applied nudge. It **drops step-3 drafting** (the PC's `stage-outreach` is now the sole drafter). Keep the no-op guard. This edits the routine's prompt; there's no unit test for an LLM prompt, so verification is a careful read against the spec.

**Files:**
- Modify: `scripts/drip_runner/runner-prompt.md` (and/or the cloud routine prompt — confirm which file the cloud `trig_…` routine actually loads; the drip runner README names it).

- [ ] **Step 1: Locate the authoritative cloud-routine prompt**

Run: `grep -rln "app ack\|mark.*Applied\|Gmail sweep\|drip-runner" scripts/drip_runner/*.md "Automation Architecture - Drip Runner.md"` and read the matches. Identify the file the cloud routine's prompt actually comes from. Edit that file (not a stale copy).

- [ ] **Step 2: Remove the step-3 drafting block**

Delete the "advance one role / stage ≤2 drafts" drafting step from the routine. The routine now ends its write phase at reconcile + archive. Add a one-line note: *"Drafting moved to the PC's `stage-outreach` skill (it has the scraped contacts). The secretary never drafts."*

- [ ] **Step 3: Encode the ack ruleset (from Spec - Applied Detector §Channel 1)**

Add an explicit ack include/exclude rule:

```markdown
A thread marks a role `Applied` IFF all hold:
1. From the employer or its ATS (greenhouse / lever / workday / icims / ashby / smartrecruiters / myworkdayjobs, or the company's own domain) — NOT a staffing agency or job board.
2. Body matches an ack pattern ("thank you for applying" / "your application has been received" / "we've received your application" / "a member of our recruiting team will review").
3. Maps to an existing Pipeline row (company, and req title/ID when present).

NOT an ack (guard against false positives): LinkedIn/Indeed "your application was sent" alerts for untracked jobs; staffing-agency/off-platform mail; newsletters/promos/digests. An ack whose company matches NO Pipeline row → do NOT auto-create a role; flag in the audit note: "ack from <company> — no tracked role; intake via interview-prep-intake if wanted."
```

- [ ] **Step 4: Add the monotonic-state guard**

Add: *"Never downgrade a row already past `Applied` (interview/offer) because an old ack was re-swept. State moves forward through the funnel until a rejection/closed event. A rejection ('we won't be moving forward') supersedes Applied → move Active→Closed, `git mv` folder to `_Archived/`, dated audit note."*

- [ ] **Step 5: Wire in the fail-loud nudge**

Add a step that runs the Task 5 reader and surfaces its output in the report:

```markdown
After reconcile, run the prepped-not-applied nudge and include any results in the report:
  python3 scripts/drip_runner/prepped_not_applied.py --roles-dir "Roles" --pipeline "Pipeline.md" --threshold-days 3
For each line, emit: "<Company> — <Role>: resume built <N> days ago, no Applied mark and no ack seen. Did you apply? Mark the row to auto-stage outreach."
```

- [ ] **Step 6: Preserve the no-op guard**

Confirm the routine still has its "if nothing changed, don't commit/push" rule so hourly no-op runs stay silent. If the cadence is being raised (per the Applied-Detector spec's hourly target), note that change here but keep the guard.

- [ ] **Step 7: Verify against the spec, then commit**

Re-read `Spec - Applied Detector.md` §"Channel 1", §"Cadence", §"Reconciliation", §"Fail-loud" and confirm each rule is now in the prompt. Then:

```bash
git add scripts/drip_runner/runner-prompt.md
git commit -m "feat(secretary): drop drafting, add ack ruleset + monotonic guard + prepped-not-applied nudge"
```

---

## Task 9: PC cron Pass A & Pass B (ops — PowerShell, no unit tests)

Wire the two PC schedules: Pass A (daily) sweeps saved jobs → `jd-to-ready`; Pass B (hourly) `git pull` → `outreach_worklist.py` → `stage-outreach` per row → commit/push. These are PowerShell scheduled tasks on the always-on PC; they're operational glue, not testable Python, so this task is "author + manually verify," not TDD. Follow the existing `scripts/drip_runner/run.ps1` and `install-tasks.ps1` patterns.

**Files:**
- Modify/Create: `scripts/drip_runner/run.ps1` (or a sibling `run-passB.ps1`), `scripts/drip_runner/install-tasks.ps1`

- [ ] **Step 1: Read the existing PC task harness**

Read `scripts/drip_runner/run.ps1` and `scripts/drip_runner/install-tasks.ps1` to learn the established pattern (how it invokes the runner prompt, how it does `git pull`/commit/push with the `drip-runner:` prefix, how tasks are registered). Match it — do not invent a new harness.

- [ ] **Step 2: Author Pass B's worklist-driven invocation**

Add a Pass B path that: (1) `git pull`, (2) runs `python3 scripts/drip_runner/outreach_worklist.py --pipeline Pipeline.md`, (3) for each returned `Company<TAB>Role`, locates the folder under `Roles/` and invokes `stage-outreach` on it (one role at a time — sequential LinkedIn, never parallel, per `linkedin-mcp-operations`), (4) commits with the `drip-runner:` prefix and pushes. If the worklist is empty, do nothing and don't commit (no-op guard).

- [ ] **Step 3: Author Pass A (if not already covered by the existing runner)**

Confirm whether the existing drip runner already does the saved-jobs→`jd-to-ready` sweep. If yes, just ensure it now calls the recut `jd-to-ready` (prep-only) and stops at the apply gate. If no, add the daily Pass A: `get_saved_jobs` → for each new `job_id` not terminal in `saved_seen.json` and with no folder → `get_job_details` → `jd-to-ready` → mark `saved_seen` done → commit/push.

- [ ] **Step 4: Register both tasks**

Update `install-tasks.ps1` to register Pass A (daily) and Pass B (hourly) as scheduled tasks. Keep the `drip-runner:` commit prefix and the git-pull-first rule (multiple repo writers: PC passes + cloud routine).

- [ ] **Step 5: Manual verification (no automated test possible)**

On the PC: run Pass B once by hand against a role you've marked `Applied` with no `STAGED` marker; confirm it produces a Gmail draft and writes the `STAGED` marker. Run it a second time; confirm the now-STAGED row is skipped (idempotent). Run Pass A once; confirm a freshly-saved job becomes a prepped folder with a resume and `.classification.json` and no Gmail/contacts artifacts.

- [ ] **Step 6: Commit**

```bash
git add scripts/drip_runner/run.ps1 scripts/drip_runner/install-tasks.ps1
git commit -m "feat(drip): PC cron Pass A (prep on save) + Pass B (outreach on apply)"
```

---

## Task 10: Update docs to the two-skill model

Bring the prose docs in line with the built system so future agents read the truth from files (invariant 5).

**Files:**
- Modify: `Automation Architecture - Drip Runner.md`, `scripts/drip_runner/README.md`
- Modify: `Automation Design - Two-Orchestrator/README.md` (flip status from "design agreed, not yet built" to "built")

- [ ] **Step 1: Update the Drip Runner architecture doc**

Edit `Automation Architecture - Drip Runner.md` to describe Pass A (prep on save) / Pass B (outreach on apply) / cloud secretary (no drafting), the `.classification.json` hand-off, and the file-marker state model (no `role_state.json`). Point readers to `Automation Design - Two-Orchestrator/` for the design rationale.

- [ ] **Step 2: Update the drip runner README**

Edit `scripts/drip_runner/README.md` to list the two new readers (`outreach_worklist.py`, `prepped_not_applied.py`) alongside `dedupe.py`/`saved_jobs_ledger.py`, and document the two passes.

- [ ] **Step 3: Flip the design-folder status**

In `Automation Design - Two-Orchestrator/README.md` and the three architecture docs' "Status:" lines, change "design agreed, not yet built" → "built `<date>`; see `docs/superpowers/plans/2026-06-27-two-orchestrator-split.md`."

- [ ] **Step 4: Commit**

```bash
git add "Automation Architecture - Drip Runner.md" scripts/drip_runner/README.md "Automation Design - Two-Orchestrator/"
git commit -m "docs: two-orchestrator split shipped — update drip-runner docs + flip design status"
```

---

## Task 11: Full regression sweep

Run every test in the touched surfaces to confirm nothing regressed end-to-end.

- [ ] **Step 1: Trace suite**

Run: `python3 -m pytest .claude/skills/jd-to-ready/scripts/test_trace_step.py -v`
Expected: all PASS (legacy + run-type tests).

- [ ] **Step 2: Drip runner suite**

Run: `cd scripts/drip_runner && python3 -m pytest -v`
Expected: all PASS — `test_dedupe`, `test_job_parser`, `test_saved_jobs_ledger`, `test_outreach_worklist`, `test_prepped_not_applied`.

- [ ] **Step 3: End-to-end trace dry-run for both run-types**

Run a `--test-run` start→finish for each run-type against a throwaway folder (use `JD_TO_READY_LOG_DIR=$(mktemp -d)` and a `Roles/Test - X` folder) to confirm `finish-run` closes cleanly with exactly each run-type's required steps. Expected: exit 0 for both; `finish-run` rejects if any required step for that run-type is unclosed.

- [ ] **Step 4: Final commit (if any fixups were needed)**

```bash
git add -A
git commit -m "test: full regression sweep green for two-orchestrator split"
```

---

## Self-Review notes (already applied)

- **Spec coverage:** Purpose invariants → preserved per-task; Split build list items 1-8 → Tasks 6,7,3(+1,2),4,9,9,8,10; Applied-Detector deltas 1-4 → Tasks 8 (cadence/ack/nudge) + 8 step 4 (monotonic guard) + 5 (nudge reader). Diagrams 3/4/5 → match Skill 1/Skill 2/topology in Tasks 6/7/9.
- **Type/name consistency:** `required_steps_for`, `RUN_TYPES`, `run_type` state key, `applied_not_staged`, `row_is_applied`, `row_is_staged`, `role_is_applied_in_pipeline`, `stale_prepped_not_applied` used identically across tasks and tests.
- **Known soft spot to resolve during build:** the `Pipeline.md` row regex (Tasks 4 & 5) is written against the spec's row shape; Task 4 Step 1 and Task 5 Step 5 force a check against the live file before trusting it. The `_scan_prepped` CLI helper computes age at the boundary so the pure functions stay clock-free (repo's no-`Date.now` discipline).
