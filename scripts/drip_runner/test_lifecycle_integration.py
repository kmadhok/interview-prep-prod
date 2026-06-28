"""End-to-end lifecycle integration test for the two-orchestrator split.

Tests the full role lifecycle (saved → prepped → applied → staged) across
the real scripts, asserting that each reader gates correctly at each
transition. Unlike the unit tests (which cover each piece in isolation),
this module exercises the HAND-OFF CONTRACTS between pieces.

Scenarios:
  1. Prepped role must NOT appear in stage-outreach worklist until Applied.
  2. Applied role enters the worklist; nudge stops firing.
  3. STAGED marker removes from worklist, idempotently across repeated polls.
  4. Closed role is excluded from both worklist and nudge.
  5. .classification.json roundtrip pins the producer→consumer schema contract.
  6. Real trace_step.py CLI driven for both run-types (jd-to-ready + stage-outreach),
     proves two separate run summaries across the apply gate.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from outreach_worklist import applied_not_staged
from prepped_not_applied import stale_prepped_not_applied, role_is_resolved_in_pipeline

# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

# Real-shaped Pipeline.md rows (6 columns, em-dash, bold role cell)
_HEADER = "| Role | Stage | Next action | Date | Contacts | Folder |"
_HEADER_SEP = "| --- | --- | --- | --- | --- | --- |"

ACME_CONSIDERING = (
    "| **Acme — Agent Builder** | Considering — JD reviewed, not yet applied | "
    "Review resume | 2026-06-22 | recruiter@acme.com | [[Acme - Agent Builder]] |"
)
ACME_APPLIED = (
    "| **Acme — Agent Builder** | **Applied** — submitted via Acme careers 2026-06-24 | "
    "Await screen | 2026-06-24 | recruiter@acme.com | [[Acme - Agent Builder]] |"
)
ACME_APPLIED_STAGED = (
    "| **Acme — Agent Builder** | **Applied** — submitted via Acme careers 2026-06-24 "
    "· STAGED in Gmail 2026-06-27 | "
    "Await screen | 2026-06-24 | recruiter@acme.com | [[Acme - Agent Builder]] |"
)
BETA_CLOSED = (
    "| **Beta — ML Eng** | **Rejected** (form email) | "
    "Applied 2026-05-01 → rejected 2026-05-10 | notes |"
)


def _pipeline(active_rows: list[str], considering_rows: list[str] | None = None,
              closed_rows: list[str] | None = None) -> str:
    """Assemble a real-shaped Pipeline.md text from section rows."""
    parts: list[str] = []

    parts.append("## Active")
    parts.append(_HEADER)
    parts.append(_HEADER_SEP)
    parts.extend(active_rows)

    parts.append("")
    parts.append("## Considering / not yet applied")
    parts.append(_HEADER)
    parts.append(_HEADER_SEP)
    parts.extend(considering_rows or [])

    if closed_rows is not None:
        parts.append("")
        parts.append("## Closed / On hold")
        parts.append(_HEADER)
        parts.append(_HEADER_SEP)
        parts.extend(closed_rows)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# TRACE helper — mirrors test_trace_step.py without importing from it
# ---------------------------------------------------------------------------

TRACE_SCRIPT = (
    Path(__file__).parent.parent.parent
    / ".claude" / "skills" / "jd-to-ready" / "scripts" / "trace_step.py"
)

TOKENS_JSON = json.dumps({
    "input": None,
    "output": None,
    "cache_read": None,
    "cache_write": None,
    "total": None,
    "source": None,
    "notes": "runtime did not expose token counts",
})


def _run(cmd_args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TRACE_SCRIPT), *cmd_args],
        env=env,
        capture_output=True,
        text=True,
    )


def _assert_ok(result: subprocess.CompletedProcess, label: str) -> None:
    assert result.returncode == 0, (
        f"{label} failed (exit {result.returncode})\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )


def _close_step(step: str, env: dict) -> None:
    r = _run(["begin", "--step", step, "--primitive", f"p-{step}",
              "--prediction", f"step {step} closes"], env)
    _assert_ok(r, f"begin {step}")
    r = _run(["end", "--step", step, "--primitive", f"p-{step}",
              "--status", "ok", "--prediction-met", "true",
              "--produced", "[]", "--gaps", "[]",
              "--failure-pattern", "", "--tokens", TOKENS_JSON], env)
    _assert_ok(r, f"end {step}")


# ---------------------------------------------------------------------------
# Test 1 — prepped role must NOT enter worklist until Applied
# ---------------------------------------------------------------------------

def test_prepped_role_not_in_worklist_until_applied(tmp_path):
    """Acme is prepped (resume on disk) but only in Considering — stage-outreach
    must not run on it. Meanwhile the staleness nudge DOES fire because the role
    was never resolved (no Applied row, not closed)."""

    # Build the temp workspace
    roles_dir = tmp_path / "Roles"
    acme_folder = roles_dir / "Acme - Agent Builder"
    acme_folder.mkdir(parents=True)
    resume = acme_folder / "Kanu Madhok Resume - Acme Agent Builder.md"
    resume.write_text("# Tailored resume for Acme Agent Builder\n", encoding="utf-8")

    pipeline = _pipeline(
        active_rows=[],
        considering_rows=[ACME_CONSIDERING],
    )

    # --- ASSERT: worklist does NOT include Acme (not Applied)
    worklist = applied_not_staged(pipeline)
    companies_in_worklist = [c for c, _r in worklist]
    assert "Acme" not in companies_in_worklist, (
        f"Acme (Considering, not Applied) must not enter the stage-outreach worklist; got {worklist}"
    )

    # --- ASSERT: nudge DOES include Acme (prepped, unresolved, aged ≥ threshold)
    # age_days=5, threshold=3 → qualifies
    nudge = stale_prepped_not_applied([("Acme", "Agent Builder", 5)], pipeline, threshold_days=3)
    nudge_companies = [c for c, _r, _a in nudge]
    assert "Acme" in nudge_companies, (
        f"Acme (prepped + Considering, 5 days old) must appear in staleness nudge; got {nudge}"
    )


# ---------------------------------------------------------------------------
# Test 2 — Applied role enters worklist; nudge stops firing
# ---------------------------------------------------------------------------

def test_applied_role_enters_worklist(tmp_path):
    """Moving Acme to Active as Applied: worklist picks it up; nudge stops."""

    pipeline = _pipeline(
        active_rows=[ACME_APPLIED],
        considering_rows=[],
    )

    # --- ASSERT: worklist INCLUDES Acme (Applied, not yet staged)
    worklist = applied_not_staged(pipeline)
    assert ("Acme", "Agent Builder") in worklist, (
        f"Acme (Applied, not staged) must appear in stage-outreach worklist; got {worklist}"
    )

    # --- ASSERT: nudge does NOT include Acme (Applied = resolved)
    nudge = stale_prepped_not_applied([("Acme", "Agent Builder", 9)], pipeline, threshold_days=3)
    nudge_companies = [c for c, _r, _a in nudge]
    assert "Acme" not in nudge_companies, (
        f"Acme (Applied = resolved) must NOT appear in staleness nudge; got {nudge}"
    )


# ---------------------------------------------------------------------------
# Test 3 — STAGED marker removes from worklist, idempotent across repeated polls
# ---------------------------------------------------------------------------

def test_staged_marker_removes_from_worklist_idempotent(tmp_path):
    """The critical idempotency contract: once STAGED in Gmail is appended to
    an Applied row, repeated calls to applied_not_staged must all return empty
    for that role — no duplicate Gmail drafts, no re-burning LinkedIn budget."""

    # Start: Acme is Applied (in worklist)
    pipeline_applied = _pipeline(active_rows=[ACME_APPLIED])
    assert ("Acme", "Agent Builder") in applied_not_staged(pipeline_applied), (
        "Pre-condition: Acme must be in worklist before staging"
    )

    # Simulate stage-outreach completing — append the STAGED marker
    pipeline_staged = _pipeline(active_rows=[ACME_APPLIED_STAGED])

    # --- ASSERT poll 1: Acme excluded after staging
    result_1 = applied_not_staged(pipeline_staged)
    assert ("Acme", "Agent Builder") not in result_1, (
        f"Acme must be excluded from worklist after STAGED marker (poll 1); got {result_1}"
    )

    # --- ASSERT poll 2: still excluded (idempotent)
    result_2 = applied_not_staged(pipeline_staged)
    assert ("Acme", "Agent Builder") not in result_2, (
        f"Acme must remain excluded on repeated poll (idempotent, poll 2); got {result_2}"
    )

    # --- ASSERT case-insensitivity: lowercase 'staged' marker also excludes
    acme_lowercase_staged = (
        "| **Acme — Agent Builder** | **Applied** — submitted 2026-06-24 "
        "· Staged in Gmail 2026-06-27 | "
        "Await screen | 2026-06-24 | recruiter@acme.com | [[Acme - Agent Builder]] |"
    )
    pipeline_lc = _pipeline(active_rows=[acme_lowercase_staged])
    result_lc = applied_not_staged(pipeline_lc)
    assert ("Acme", "Agent Builder") not in result_lc, (
        f"Lowercase 'Staged in Gmail' must also exclude from worklist; got {result_lc}"
    )


# ---------------------------------------------------------------------------
# Test 4 — Closed role excluded from both worklist and nudge
# ---------------------------------------------------------------------------

def test_closed_role_neither_staged_nor_nudged(tmp_path):
    """Beta is rejected (in Closed / On hold). It must never appear in the
    stage-outreach worklist (section-scoping) and must not trigger the nudge
    (closed = resolved, don't disturb)."""

    pipeline = _pipeline(
        active_rows=[],
        considering_rows=[],
        closed_rows=[BETA_CLOSED],
    )

    # --- ASSERT: worklist does NOT include Beta (closed rows are section-scoped out)
    worklist = applied_not_staged(pipeline)
    companies = [c for c, _r in worklist]
    assert "Beta" not in companies, (
        f"Closed/rejected Beta must never appear in stage-outreach worklist; got {worklist}"
    )

    # --- ASSERT: nudge does NOT include Beta (closed = resolved, terminal)
    # age_days=9 > threshold=3, but still resolved via closed section
    nudge = stale_prepped_not_applied([("Beta", "ML Eng", 9)], pipeline, threshold_days=3)
    nudge_companies = [c for c, _r, _a in nudge]
    assert "Beta" not in nudge_companies, (
        f"Closed Beta must NOT appear in staleness nudge (closed = resolved); got {nudge}"
    )

    # Confirm role_is_resolved_in_pipeline agrees
    assert role_is_resolved_in_pipeline("Beta", pipeline), (
        "Closed role 'Beta' must be considered resolved by role_is_resolved_in_pipeline"
    )


# ---------------------------------------------------------------------------
# Test 5 — .classification.json roundtrip (producer→consumer contract)
# ---------------------------------------------------------------------------

def test_classification_json_roundtrip(tmp_path):
    """.classification.json is the only hand-off artifact between jd-to-ready
    (producer, Step 2) and stage-outreach (consumer). This test pins the
    documented schema so a schema drift between the two skills is caught.

    Documented schema (from SKILL.md):
      {
        "themes": [{"tag": "<in-vocab tag>", "evidence": "<JD quote ≤25 words>"}],
        "archetype": "<in-vocab archetype>",
        "archetype_rationale": "<1–2 sentences>",
        "notes": "<optional notes or empty string>",
        "classified_ts": "<YYYY-MM-DD>"
      }
    """
    role_folder = tmp_path / "Roles" / "Acme - Agent Builder"
    role_folder.mkdir(parents=True)

    # Write the artifact exactly as the producer (jd-to-ready Step 2) documents it
    classification = {
        "themes": [
            {"tag": "agentic-ai", "evidence": "build and deploy LLM agents in production"},
            {"tag": "data-platform", "evidence": "owns the data pipeline end-to-end"},
            {"tag": "ml-engineering", "evidence": "ship production ML systems at scale"},
            {"tag": "analytics-engineering", "evidence": "semantic layer and metric definitions"},
        ],
        "archetype": "Agent Builder",
        "archetype_rationale": "Role is 80% agent orchestration + prompt engineering, with embedded FDE flavor.",
        "notes": "Hard gate: must have shipped a production LLM agent.",
        "classified_ts": "2026-06-27",
    }
    classification_path = role_folder / ".classification.json"
    classification_path.write_text(json.dumps(classification, indent=2), encoding="utf-8")

    # --- ASSERT: consumer can parse it as valid JSON
    raw = classification_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)  # raises if malformed

    # --- ASSERT: required top-level fields present
    assert "themes" in parsed, "classification.json must have 'themes'"
    assert "archetype" in parsed, "classification.json must have 'archetype'"
    assert "archetype_rationale" in parsed, "classification.json must have 'archetype_rationale'"
    assert "notes" in parsed, "classification.json must have 'notes'"
    assert "classified_ts" in parsed, "classification.json must have 'classified_ts'"

    # --- ASSERT: archetype is a non-empty string (consumer reads this for routing)
    assert isinstance(parsed["archetype"], str) and parsed["archetype"], (
        "archetype must be a non-empty string"
    )

    # --- ASSERT: themes is a non-empty list (consumer iterates this for prompt anchoring)
    assert isinstance(parsed["themes"], list) and len(parsed["themes"]) > 0, (
        "themes must be a non-empty list"
    )

    # --- ASSERT: each theme has a 'tag' (the consumer's actual read)
    first_theme = parsed["themes"][0]
    assert "tag" in first_theme, "each theme must have a 'tag' key"
    assert isinstance(first_theme["tag"], str) and first_theme["tag"], (
        "themes[0]['tag'] must be a non-empty string"
    )

    # --- ASSERT: top theme tag is extractable (the canonical consumer read)
    top_tag = parsed["themes"][0]["tag"]
    assert top_tag == "agentic-ai", (
        f"Top theme tag must survive roundtrip; expected 'agentic-ai', got {top_tag!r}"
    )


# ---------------------------------------------------------------------------
# Test 6 — Full trace lifecycle for both run-types over the apply gate
# ---------------------------------------------------------------------------

def test_full_trace_lifecycle_both_runtypes(tmp_path):
    """Drive the REAL trace_step.py CLI via subprocess against an isolated
    JD_TO_READY_LOG_DIR and temp Roles/ folder.

    This proves:
    - jd-to-ready (steps 1,2,3,3.5,6,7) produces a summary with run_type='jd-to-ready'
      and steps_closed == exactly those 6 prep steps.
    - stage-outreach (steps 4,4b,4c,5,6,7) on the SAME role folder (simulating Kanu
      applied, then outreach staged) produces a SECOND summary with run_type='stage-outreach'.
    - set-role-folder binds the already-prepped folder without clobbering it.
    - The two skills trace as SEPARATE runs (the whole reason for the split).
    """
    log_dir = tmp_path / "logs"
    role_folder = tmp_path / "Roles" / "Acme - Agent Builder"
    role_folder.mkdir(parents=True)

    # Pre-populate resume so the folder looks truly prepped (mirrors what jd-to-ready Step 3 writes)
    resume_path = role_folder / "Kanu Madhok Resume - Acme Agent Builder.md"
    resume_path.write_text("# Tailored resume\n", encoding="utf-8")

    env = os.environ.copy()
    env["JD_TO_READY_LOG_DIR"] = str(log_dir)

    summary_path = log_dir / "jd-to-ready.jsonl"

    # ------------------------------------------------------------------
    # RUN A — jd-to-ready (prep half, steps 1,2,3,3.5,6,7)
    # ------------------------------------------------------------------
    JD_PREP_STEPS = ["1", "2", "3", "3.5", "6", "7"]

    r = _run(["start-run", "--run-type", "jd-to-ready",
              "--company", "Acme", "--role", "Agent Builder"], env)
    _assert_ok(r, "jd-to-ready start-run")

    r = _run(["set-role-folder", "--role-folder", str(role_folder),
              "--company", "Acme", "--role", "Agent Builder"], env)
    _assert_ok(r, "jd-to-ready set-role-folder")

    for step in JD_PREP_STEPS:
        _close_step(step, env)

    r = _run(["finish-run", "--status", "ok", "--gaps", "[]", "--files-written",
              json.dumps(["Job Description.md",
                          "Kanu Madhok Resume - Acme Agent Builder.md",
                          ".classification.json"])], env)
    _assert_ok(r, "jd-to-ready finish-run")

    # --- ASSERT: summary line exists with correct steps_closed and required_steps
    assert summary_path.exists(), "jd-to-ready.jsonl must exist after finish-run"
    lines_a = [l for l in summary_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines_a) == 1, f"Expected exactly 1 summary line after jd-to-ready run; got {len(lines_a)}"

    summary_a = json.loads(lines_a[0])
    # run_type is written to the global summary — the explicit discriminator of which
    # skill produced the run. required_steps is the structural backstop: jd-to-ready's
    # set ["1","2","3","3.5","6","7"] is distinct from stage-outreach's.
    assert summary_a["run_type"] == "jd-to-ready", (
        f"summary must carry run_type='jd-to-ready'; got {summary_a.get('run_type')!r}"
    )
    assert summary_a["required_steps"] == JD_PREP_STEPS, (
        f"required_steps must be jd-to-ready's set {JD_PREP_STEPS}; got {summary_a.get('required_steps')}"
    )
    assert summary_a["steps_closed"] == JD_PREP_STEPS, (
        f"steps_closed mismatch; expected {JD_PREP_STEPS}, got {summary_a.get('steps_closed')}"
    )
    assert summary_a["status"] == "ok"

    # run_type IS in the per-role trace run_start event
    trace_a = role_folder / ".jd-to-ready-trace.jsonl"
    assert trace_a.exists(), "Per-role trace file must exist after jd-to-ready run"
    trace_events_a = [json.loads(l) for l in trace_a.read_text(encoding="utf-8").splitlines() if l.strip()]
    run_start_a = next((e for e in trace_events_a if e.get("event") == "run_start"), None)
    assert run_start_a is not None, "run_start event must exist in per-role trace"
    assert run_start_a.get("run_type") == "jd-to-ready", (
        f"run_start event must carry run_type='jd-to-ready'; got {run_start_a.get('run_type')!r}"
    )

    # Binding must not clobber what Skill 1 wrote
    assert resume_path.read_text(encoding="utf-8") == "# Tailored resume\n", (
        "set-role-folder must not overwrite resume written by Skill 1"
    )

    # ------------------------------------------------------------------
    # (Simulate Kanu applying: Pipeline.md row marked Applied; we don't
    #  touch the file here — the worklist reader is exercised in Tests 1-4.
    #  What matters is that stage-outreach starts a FRESH run in the SAME folder.)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # RUN B — stage-outreach (apply half, steps 4,4b,4c,5,6,7)
    # ------------------------------------------------------------------
    STAGE_STEPS = ["4", "4b", "4c", "5", "6", "7"]

    r = _run(["start-run", "--run-type", "stage-outreach",
              "--company", "Acme", "--role", "Agent Builder"], env)
    _assert_ok(r, "stage-outreach start-run")

    # Bind the existing prepped folder (simulates stage-outreach reading it from Pipeline.md)
    r = _run(["set-role-folder", "--role-folder", str(role_folder),
              "--company", "Acme", "--role", "Agent Builder"], env)
    _assert_ok(r, "stage-outreach set-role-folder")

    for step in STAGE_STEPS:
        _close_step(step, env)

    r = _run(["finish-run", "--status", "ok", "--gaps", "[]", "--files-written",
              json.dumps(["Cold Outreach.md"])], env)
    _assert_ok(r, "stage-outreach finish-run")

    # --- ASSERT: two summary lines, second one is stage-outreach
    lines_b = [l for l in summary_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines_b) == 2, (
        f"Expected exactly 2 summary lines after both runs; got {len(lines_b)}"
    )

    summary_b = json.loads(lines_b[1])
    # The second summary is the stage-outreach run — run_type discriminates it cleanly.
    assert summary_b["run_type"] == "stage-outreach", (
        f"second summary must carry run_type='stage-outreach'; got {summary_b.get('run_type')!r}"
    )
    assert summary_b["required_steps"] == STAGE_STEPS, (
        f"required_steps must be stage-outreach's set {STAGE_STEPS}; got {summary_b.get('required_steps')}"
    )
    # steps_closed for stage-outreach includes ALL steps ever closed in the per-role trace
    # (append-only across runs), so just check the stage-outreach required steps are there.
    assert all(s in summary_b["steps_closed"] for s in STAGE_STEPS), (
        f"stage-outreach steps_closed must contain all of {STAGE_STEPS}; got {summary_b.get('steps_closed')}"
    )
    assert summary_b["status"] == "ok"

    # run_type for stage-outreach is in the fallback trace (the per-role trace already
    # existed from the jd-to-ready run, so migrate_fallback_trace is a no-op for Runs B).
    # The stage-outreach run_start event lands in logs/jd-to-ready-runs/<run_id>.jsonl.
    run_id_b = summary_b["run_id"]
    fallback_b = log_dir / "jd-to-ready-runs" / f"{run_id_b}.jsonl"
    assert fallback_b.exists(), f"stage-outreach fallback trace must exist at {fallback_b}"
    fallback_events = [json.loads(l) for l in fallback_b.read_text(encoding="utf-8").splitlines() if l.strip()]
    run_start_b = next((e for e in fallback_events if e.get("event") == "run_start"), None)
    assert run_start_b is not None, "stage-outreach run_start event must exist in fallback trace"
    assert run_start_b.get("run_type") == "stage-outreach", (
        f"stage-outreach run_start must carry run_type='stage-outreach'; got {run_start_b.get('run_type')!r}"
    )

    # --- ASSERT: the two runs have DIFFERENT run_ids (separate runs across apply gate)
    assert summary_a["run_id"] != summary_b["run_id"], (
        "jd-to-ready and stage-outreach must produce distinct run_ids (separate runs)"
    )

    # --- ASSERT: both runs bound the same role_folder (the hand-off contract)
    assert summary_a["role_folder"] == str(role_folder), (
        "jd-to-ready summary must record the role_folder"
    )
    assert summary_b["role_folder"] == str(role_folder), (
        "stage-outreach summary must record the same role_folder (binding existing prepped folder)"
    )
