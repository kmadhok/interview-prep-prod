#!/usr/bin/env python3
"""Audit closed primitive traces for all authoritative pipeline behaviors."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import contract_clause_ids  # noqa: E402


BEHAVIORS = (
    "interview-prep-intake",
    "classify",
    "tailor-resume",
    "resume-export",
    "apply-packet",
    "find-contacts",
    "enrich-contacts",
    "verify-emails",
    "write-outreach",
)
CLAUSE_STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}


@dataclass(frozen=True)
class TraceAuditResult:
    behavior: str
    passed: bool
    detail: str = ""
    run_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def prediction_from_clauses(results: list[dict[str, Any]]) -> str:
    statuses = {item.get("status") for item in results}
    if "FAIL" in statuses:
        return "false"
    if statuses == {"PASS"}:
        return "true"
    if "PASS" in statuses:
        return "partial"
    return "unknown"


def _read_trace(path: Path) -> list[dict[str, Any]]:
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{number}: invalid JSON: {exc}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path.name}:{number}: event must be an object")
        events.append(event)
    return events


def _only(events: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [event for event in events if event.get("event") == name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {name}; found {len(matches)}")
    return matches[0]


def _validate_behavior(
    behavior: str, path: Path, events: list[dict[str, Any]]
) -> TraceAuditResult:
    try:
        start = _only(events, "run_start")
        begin = _only(events, "step_begin")
        end = _only(events, "step_end")
        finish = _only(events, "run_finish")
        if start.get("skill") != behavior:
            raise ValueError(f"run_start.skill={start.get('skill')!r}")
        if start.get("schema_version") != 3:
            raise ValueError(f"schema_version={start.get('schema_version')!r}; expected 3")
        if start.get("run_type") != "primitive" or start.get("required_steps") != ["main"]:
            raise ValueError("run is not a primitive main-step trace")
        if begin.get("step") != "main" or end.get("step") != "main":
            raise ValueError("step_begin/step_end must use step 'main'")
        expected = contract_clause_ids(behavior)
        if begin.get("contract_clauses") != expected:
            raise ValueError(
                f"contract_clauses mismatch: expected {expected}, got {begin.get('contract_clauses')}"
            )
        if not str(begin.get("reason", "")).strip():
            raise ValueError("step_begin.reason missing")
        sources = begin.get("sources")
        if not isinstance(sources, list) or not all(isinstance(item, str) for item in sources):
            raise ValueError("step_begin.sources must be an array of strings")
        results = end.get("clause_results")
        if not isinstance(results, list):
            raise ValueError("step_end.clause_results must be an array")
        ids = [item.get("id") for item in results if isinstance(item, dict)]
        if len(ids) != len(results) or ids != expected:
            raise ValueError(f"clause_results IDs mismatch: expected {expected}, got {ids}")
        illegal = [
            item.get("status") for item in results
            if item.get("status") not in CLAUSE_STATUSES
        ]
        if illegal:
            raise ValueError(f"illegal clause result statuses: {illegal}")
        derived = prediction_from_clauses(results)
        if end.get("prediction_met") != derived:
            raise ValueError(
                f"prediction_met={end.get('prediction_met')!r}; derived={derived!r}"
            )
        for field in ("produced", "gaps"):
            if not isinstance(end.get(field), list):
                raise ValueError(f"step_end.{field} must be an array")
        positions = {
            name: events.index(event)
            for name, event in (
                ("run_start", start), ("step_begin", begin),
                ("step_end", end), ("run_finish", finish),
            )
        }
        if list(positions.values()) != sorted(positions.values()):
            raise ValueError("trace lifecycle events are out of order")
        return TraceAuditResult(
            behavior=behavior,
            passed=True,
            run_id=str(start.get("run_id", path.parent.name)),
        )
    except ValueError as exc:
        return TraceAuditResult(behavior=behavior, passed=False, detail=str(exc))


def audit_runs(runs_dir: Path) -> list[TraceAuditResult]:
    runs_dir = Path(runs_dir)
    traces: dict[str, list[tuple[Path, list[dict[str, Any]]]]] = {
        behavior: [] for behavior in BEHAVIORS
    }
    for path in sorted(runs_dir.glob("*/trace.jsonl")):
        try:
            events = _read_trace(path)
        except ValueError:
            continue
        starts = [event for event in events if event.get("event") == "run_start"]
        if len(starts) == 1 and starts[0].get("skill") in traces:
            traces[starts[0]["skill"]].append((path, events))

    results = []
    for behavior in BEHAVIORS:
        candidates = traces[behavior]
        if len(candidates) != 1:
            results.append(TraceAuditResult(
                behavior=behavior,
                passed=False,
                detail=f"expected one primitive trace; found {len(candidates)}",
            ))
            continue
        results.append(_validate_behavior(behavior, *candidates[0]))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify closed primitive traces for all nine pipeline behaviors."
    )
    parser.add_argument("--runs-dir", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runs_dir = Path(args.runs_dir)
    if not runs_dir.is_dir():
        print(f"error: runs directory does not exist: {runs_dir}", file=sys.stderr)
        return 2
    results = audit_runs(runs_dir)
    if args.as_json:
        print(json.dumps([result.as_dict() for result in results], indent=2))
    else:
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            detail = f" — {result.detail}" if result.detail else ""
            print(f"{status:<4}  {result.behavior}{detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
