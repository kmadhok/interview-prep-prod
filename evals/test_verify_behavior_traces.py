from __future__ import annotations

import json
from pathlib import Path

from common import contract_clause_ids
from verify_behavior_traces import BEHAVIORS, audit_runs, main, prediction_from_clauses


def _write_trace(
    runs: Path,
    behavior: str,
    *,
    begin_ids: list[str] | None = None,
    end_ids: list[str] | None = None,
    prediction_met: str | None = None,
    blocked_live: bool = False,
) -> None:
    expected = contract_clause_ids(behavior)
    begin_ids = expected if begin_ids is None else begin_ids
    end_ids = expected if end_ids is None else end_ids
    results = [{"id": clause_id, "status": "PASS"} for clause_id in end_ids]
    if blocked_live:
        for result in results:
            if result["id"].endswith(("C4", "C5")):
                result["status"] = "BLOCKED"
    derived = prediction_from_clauses(results)
    run_id = f"trace-{behavior}"
    events = [
        {
            "event": "run_start", "run_id": run_id, "skill": behavior,
            "schema_version": 3, "run_type": "primitive",
            "required_steps": ["main"],
        },
        {
            "event": "step_begin", "run_id": run_id, "step": "main",
            "reason": f"verify {behavior}", "sources": [],
            "contract_clauses": begin_ids,
        },
        {
            "event": "step_end", "run_id": run_id, "step": "main",
            "clause_results": results,
            "prediction_met": prediction_met or derived,
            "produced": [], "gaps": [],
        },
        {"event": "run_finish", "run_id": run_id, "status": "ok"},
    ]
    target = runs / run_id
    target.mkdir(parents=True)
    (target / "trace.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )


def _write_all(runs: Path) -> None:
    for behavior in BEHAVIORS:
        _write_trace(
            runs,
            behavior,
            blocked_live=behavior in {
                "find-contacts", "enrich-contacts", "verify-emails", "write-outreach"
            },
        )


def test_all_behavior_traces_pass_with_blocked_live_clauses(tmp_path):
    runs = tmp_path / "runs"
    _write_all(runs)
    results = audit_runs(runs)
    assert len(results) == 9
    assert all(result.passed for result in results)


def test_missing_behavior_fails(tmp_path):
    runs = tmp_path / "runs"
    _write_all(runs)
    missing = runs / "trace-apply-packet" / "trace.jsonl"
    missing.unlink()
    result = next(item for item in audit_runs(runs) if item.behavior == "apply-packet")
    assert not result.passed
    assert "found 0" in result.detail


def test_mismatched_clause_ids_fail(tmp_path):
    runs = tmp_path / "runs"
    _write_all(runs)
    path = runs / "trace-classify" / "trace.jsonl"
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    events[1]["contract_clauses"] = ["classify-C1"]
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    result = next(item for item in audit_runs(runs) if item.behavior == "classify")
    assert not result.passed
    assert "contract_clauses mismatch" in result.detail


def test_bad_prediction_met_fails(tmp_path):
    runs = tmp_path / "runs"
    _write_all(runs)
    path = runs / "trace-resume-export" / "trace.jsonl"
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    events[2]["prediction_met"] = "false"
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    result = next(item for item in audit_runs(runs) if item.behavior == "resume-export")
    assert not result.passed
    assert "derived='true'" in result.detail


def test_blocked_and_not_run_are_legal_tracked_outcomes(tmp_path):
    runs = tmp_path / "runs"
    _write_all(runs)
    path = runs / "trace-write-outreach" / "trace.jsonl"
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    events[2]["clause_results"][-1]["status"] = "NOT_RUN"
    events[2]["prediction_met"] = prediction_from_clauses(events[2]["clause_results"])
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    result = next(item for item in audit_runs(runs) if item.behavior == "write-outreach")
    assert result.passed


def test_cli_exit_codes_reflect_trace_completeness(tmp_path, capsys):
    runs = tmp_path / "runs"
    _write_all(runs)
    assert main(["--runs-dir", str(runs), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)
    (runs / "trace-classify" / "trace.jsonl").unlink()
    assert main(["--runs-dir", str(runs)]) == 1
