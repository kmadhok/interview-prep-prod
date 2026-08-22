#!/usr/bin/env python3
"""Deterministic trace helper for jd-to-ready runs.

The helper writes append-only JSONL events and maintains a small active-run
state file for hooks. Production runs fail closed: one active step at a time,
all required steps must close before finish, and interrupted runs must use an
explicit abort event.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_STEPS = ["1", "2", "3", "3.5", "3.7", "4", "4b", "4c", "5", "6", "7"]

# Per-run-type required-steps. REQUIRED_STEPS above stays the legacy "full"
# list so any caller that does not pass a run-type keeps the old contract.
RUN_TYPES = {
    "full": list(REQUIRED_STEPS),
    "jd-to-ready": ["1", "2", "3", "3.5", "3.7", "6", "7"],
    "stage-outreach": ["4", "4b", "4c", "5", "6", "7"],
    "primitive": ["main"],
}


def required_steps_for(run_type: str | None) -> list[str]:
    """Required steps for a run-type, defaulting to the legacy full list."""
    return list(RUN_TYPES.get(run_type, REQUIRED_STEPS))


ALLOWED_FAILURE_PATTERNS = {
    "",
    None,
    "generic-resume-language",
    "verify-placeholder-leak",
    "non-decision-maker-contact",
    "low-confidence-emails",
    "fabricated-hook",
    "thin-jd-stub",
    "theme-unmatched",
    "thin-results",
    "pdf-export-defect",
    "apply-packet-defect",
}
TOKEN_SOURCES = {"runtime", "manual", "estimated", None}
CLAUSE_STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
UNKNOWN_TOKENS = {
    "input": None,
    "output": None,
    "cache_read": None,
    "cache_write": None,
    "total": None,
    "source": None,
    "notes": "runtime did not expose token counts",
}


def runs_dir() -> Path:
    """Repo-local run store. TRACE_RUNS_DIR overrides for tests/harnesses."""
    override = os.environ.get("TRACE_RUNS_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / "runs"


def active_state_path() -> Path:
    """Execute `active_state_path`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    return runs_dir() / ".active-run.json"


def run_dir_for(run_id: str) -> Path:
    """Execute `run_dir_for`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    return runs_dir() / run_id


def global_summary_path() -> Path:
    """Execute `global_summary_path`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    return runs_dir() / "summary.jsonl"


def now_iso() -> str:
    """Execute `now_iso`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def current_session() -> str | None:
    """The Claude Code session id driving this process, if exposed.

    Used to scope the Stop-hook completeness check to the session that started
    the run. A background drip-runner (`claude -p`) and an interactive session
    are different sessions, so the interactive session's Stop hook must not flag
    the runner's in-flight trace as incomplete.
    """
    return os.environ.get("CLAUDE_CODE_SESSION_ID") or None


def ensure_dirs() -> None:
    """Execute `ensure_dirs`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    runs_dir().mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any] | None:
    """Execute `load_state`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    path = active_state_path()
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    state.setdefault("run_type", None)
    state.setdefault("required_steps", REQUIRED_STEPS)
    state.setdefault("skill", state.get("run_type"))
    state.setdefault("closed_steps", [])
    state.setdefault("current_step", None)
    state.setdefault("next_seq", 1)
    state.setdefault("is_test_run", False)
    state.setdefault("owner_session", None)
    return state


def save_state(state: dict[str, Any]) -> None:
    """Execute `save_state`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    ensure_dirs()
    active_state_path().write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")


def trace_path(state: dict[str, Any]) -> Path:
    """Execute `trace_path`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    return run_dir_for(state["run_id"]) / "trace.jsonl"


def fail(message: str) -> int:
    """Execute `fail`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    print(message, file=sys.stderr)
    return 2


def parse_json_strict(value: str | None, field: str) -> tuple[bool, Any, str | None]:
    """Execute `parse_json_strict`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if value in (None, ""):
        return False, None, f"{field} is required and must be valid JSON"
    try:
        return True, json.loads(value), None
    except json.JSONDecodeError as exc:
        return False, None, f"{field} must be valid JSON: {exc}"


def parse_json_optional(value: str | None, default: Any, field: str) -> tuple[bool, Any, str | None]:
    """Execute `parse_json_optional`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if value in (None, ""):
        return True, default, None
    try:
        return True, json.loads(value), None
    except json.JSONDecodeError as exc:
        return False, None, f"{field} must be valid JSON: {exc}"


def validate_array(value: Any, field: str) -> str | None:
    """Execute `validate_array`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not isinstance(value, list):
        return f"{field} must be a JSON array"
    return None


def validate_clause_results(value: Any, expected: list[str]) -> str | None:
    """Execute `validate_clause_results`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not isinstance(value, list):
        return "clause_results must be a JSON array"
    ids = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            return "each clause result must be an object with a string id"
        if item.get("status") not in CLAUSE_STATUSES:
            return f"clause result status must be one of: {', '.join(sorted(CLAUSE_STATUSES))}"
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        return "clause result ids must be unique"
    unexpected = sorted(set(ids) - set(expected))
    if unexpected:
        return f"clause results were not declared at step_begin: {', '.join(unexpected)}"
    return None


def prediction_from_clauses(results: list[dict[str, Any]]) -> str:
    """Execute `prediction_from_clauses`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not results:
        return "unknown"
    statuses = {item["status"] for item in results}
    if "FAIL" in statuses:
        return "false"
    if statuses == {"PASS"}:
        return "true"
    if "PASS" in statuses:
        return "partial"
    return "unknown"


def validate_tokens(value: Any) -> str | None:
    """Execute `validate_tokens`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not isinstance(value, dict):
        return "tokens must be a JSON object"
    required = {"input", "output", "cache_read", "cache_write", "total", "source", "notes"}
    missing = sorted(required - set(value))
    if missing:
        return f"tokens missing fields: {', '.join(missing)}"
    if value.get("source") not in TOKEN_SOURCES:
        return "tokens.source must be runtime, manual, estimated, or null"
    numeric_fields = ["input", "output", "cache_read", "cache_write", "total"]
    for field in numeric_fields:
        item = value.get(field)
        if item is not None and (not isinstance(item, int) or item < 0):
            return f"tokens.{field} must be a non-negative integer or null"
    components = [value.get(field) for field in ["input", "output", "cache_read", "cache_write"]]
    if all(item is not None for item in components) and value.get("total") is not None:
        if sum(components) != value["total"]:
            return "tokens.total must equal input + output + cache_read + cache_write when all are known"
    notes = value.get("notes")
    if notes is not None and not isinstance(notes, str):
        return "tokens.notes must be a string or null"
    return None


def normalize_step(step: str | int | None) -> str | None:
    """Execute `normalize_step`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if step is None:
        return None
    return str(step)


def validate_step(step: str | None, state: dict[str, Any]) -> str | None:
    """Execute `validate_step`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if step not in [str(item) for item in state.get("required_steps", REQUIRED_STEPS)]:
        return f"step must be one of: {', '.join(state.get('required_steps', REQUIRED_STEPS))}"
    return None


def validate_role_folder(role_folder: str, is_test_run: bool) -> str | None:
    """Execute `validate_role_folder`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    path = Path(role_folder).expanduser()
    if not path.is_absolute():
        return "role_folder must be absolute"
    if is_test_run:
        return None
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path.absolute()
    if resolved.parent.name != "Roles":
        return "production role_folder must be an active role folder directly under Roles/"
    return None


def append_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    """Execute `append_event`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    ensure_dirs()
    event.setdefault("run_id", state["run_id"])
    event.setdefault("timestamp", now_iso())
    event.setdefault("event", "event")
    event.setdefault("role_folder", state.get("role_folder"))
    event["seq"] = int(state.get("next_seq", 1))
    state["next_seq"] = event["seq"] + 1
    path = trace_path(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    save_state(state)


def read_events(path: Path) -> list[dict[str, Any]]:
    """Execute `read_events`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def step_status(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Execute `step_status`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    status: dict[str, dict[str, Any]] = {}
    for event in events:
        step = normalize_step(event.get("step"))
        if not step:
            continue
        status.setdefault(step, {"begin": False, "end": False, "result": None})
        if event.get("event") == "step_begin":
            status[step]["begin"] = True
        if event.get("event") == "step_end":
            status[step]["end"] = True
            status[step]["result"] = event
    return status


def missing_steps(state: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    """Execute `missing_steps`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    status = step_status(events)
    return [
        str(step)
        for step in state.get("required_steps", REQUIRED_STEPS)
        if not status.get(str(step), {}).get("end")
    ]


def compute_finish_status(step_results: list[dict[str, Any]]) -> str:
    """Execute `compute_finish_status`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    statuses = {event.get("status") for event in step_results}
    if "failed" in statuses:
        return "failed"
    if statuses & {"partial", "skipped"}:
        return "partial"
    return "ok"


def closed_steps_from_state_and_events(state: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    """Execute `closed_steps_from_state_and_events`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    closed = set(str(step) for step in state.get("closed_steps", []))
    for step, flags in step_status(events).items():
        if flags.get("end"):
            closed.add(str(step))
    order = {step: index for index, step in enumerate(state.get("required_steps", REQUIRED_STEPS))}
    return sorted(closed, key=lambda item: order.get(item, 999))


def cmd_start(args: argparse.Namespace) -> int:
    """Execute `cmd_start`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
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
    if run_type == "primitive":
        if not args.skill or not args.skill.strip():
            return fail("skill is required when --run-type primitive")
        skill = args.skill
    else:
        skill = run_type
    required = required_steps_for(run_type)
    run_dir_for(run_id).mkdir(parents=True, exist_ok=True)
    state = {
        "run_id": run_id,
        "run_type": run_type,
        "skill": skill,
        "company": args.company,
        "role": args.role,
        "role_folder": role_folder,
        "owner_session": current_session(),
        "started_at": now_iso(),
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
            "schema_version": 3,
            "company": args.company,
            "role": args.role,
            "skill": skill,
            "required_steps": required,
            "run_type": run_type,
            "source": "jd-to-ready",
            "is_test_run": is_test_run,
        },
    )
    print(run_id)
    return 0


def cmd_set_role_folder(args: argparse.Namespace) -> int:
    """Execute `cmd_set_role_folder`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return fail("No active jd-to-ready run. Call start-run first.")
    if args.test_run:
        state["is_test_run"] = True
    error = validate_role_folder(args.role_folder, bool(state.get("is_test_run")))
    if error:
        return fail(error)
    state["role_folder"] = args.role_folder
    if args.company:
        state["company"] = args.company
    if args.role:
        state["role"] = args.role
    save_state(state)
    append_event(
        state,
        {
            "event": "role_folder_set",
            "company": state.get("company"),
            "role": state.get("role"),
            "role_folder": state.get("role_folder"),
        },
    )
    return 0


def cmd_begin(args: argparse.Namespace) -> int:
    """Execute `cmd_begin`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return fail("No active jd-to-ready run. Call start-run first.")
    step = normalize_step(args.step)
    if error := validate_step(step, state):
        return fail(error)
    if state.get("current_step"):
        return fail(f"Cannot begin step {step}; step {state['current_step']} is still open.")
    if step in [str(item) for item in state.get("closed_steps", [])]:
        return fail(f"Cannot begin step {step}; it is already closed.")
    if not args.reason.strip():
        return fail("reason is required and must be non-empty")
    ok, sources, error = parse_json_strict(args.sources, "sources")
    if not ok:
        return fail(error or "invalid sources")
    if error := validate_array(sources, "sources"):
        return fail(error)
    if not all(isinstance(item, str) for item in sources):
        return fail("sources must be a JSON array of strings")
    ok, inputs_summary, error = parse_json_optional(args.inputs_summary, args.inputs_summary, "inputs_summary")
    if not ok:
        return fail(error or "invalid inputs_summary")
    ok, contract_clauses, error = parse_json_optional(args.contract_clauses, [], "contract_clauses")
    if not ok:
        return fail(error or "invalid contract_clauses")
    if error := validate_array(contract_clauses, "contract_clauses"):
        return fail(error)
    if not all(isinstance(item, str) and item.strip() for item in contract_clauses):
        return fail("contract_clauses must be a JSON array of non-empty strings")
    if len(contract_clauses) != len(set(contract_clauses)):
        return fail("contract_clauses must be unique")
    state["current_step"] = step
    state["current_contract_clauses"] = contract_clauses
    save_state(state)
    append_event(
        state,
        {
            "event": "step_begin",
            "step": step,
            "primitive": args.primitive,
            "mode": args.mode,
            "prediction": args.prediction,
            "reason": args.reason,
            "sources": sources,
            "inputs_summary": inputs_summary,
            "contract_clauses": contract_clauses,
            "status": "running",
        },
    )
    return 0


def cmd_end(args: argparse.Namespace) -> int:
    """Execute `cmd_end`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return fail("No active jd-to-ready run. Call start-run first.")
    step = normalize_step(args.step)
    if error := validate_step(step, state):
        return fail(error)
    if state.get("current_step") != step:
        return fail(f"Cannot end step {step}; current open step is {state.get('current_step')!r}.")
    ok, produced, error = parse_json_optional(args.produced, [], "produced")
    if not ok:
        return fail(error or "invalid produced")
    if error := validate_array(produced, "produced"):
        return fail(error)
    ok, gaps, error = parse_json_optional(args.gaps, [], "gaps")
    if not ok:
        return fail(error or "invalid gaps")
    if error := validate_array(gaps, "gaps"):
        return fail(error)
    failure_pattern = args.failure_pattern
    if failure_pattern == "null":
        failure_pattern = None
    if failure_pattern not in ALLOWED_FAILURE_PATTERNS:
        return fail("failure_pattern must be one of the documented taxonomy values, empty, or null")
    ok, tokens, error = parse_json_strict(args.tokens, "tokens")
    if not ok:
        return fail(error or "invalid tokens")
    if error := validate_tokens(tokens):
        return fail(error)
    ok, clause_results, error = parse_json_optional(args.clause_results, [], "clause_results")
    if not ok:
        return fail(error or "invalid clause_results")
    expected_clauses = state.get("current_contract_clauses", [])
    if error := validate_clause_results(clause_results, expected_clauses):
        return fail(error)
    if clause_results:
        derived = prediction_from_clauses(clause_results)
        if args.prediction_met != derived:
            return fail(
                f"prediction_met {args.prediction_met!r} does not match clause outcomes {derived!r}"
            )
    append_event(
        state,
        {
            "event": "step_end",
            "step": step,
            "primitive": args.primitive,
            "mode": args.mode,
            "status": args.status,
            "prediction_met": args.prediction_met,
            "produced": produced,
            "gaps": gaps,
            "failure_pattern": failure_pattern,
            "tokens": tokens,
            "clause_results": clause_results,
        },
    )
    state["current_step"] = None
    state["current_contract_clauses"] = []
    closed = [str(item) for item in state.get("closed_steps", [])]
    if step not in closed:
        closed.append(step)
    state["closed_steps"] = closed
    save_state(state)
    return 0


def cmd_tool_event(args: argparse.Namespace) -> int:
    """Execute `cmd_tool_event`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return 0
    append_event(
        state,
        {
            "event": "tool_event",
            "tool_name": args.tool_name,
            "status": args.status,
            "summary": args.summary,
            "step": state.get("current_step"),
        },
    )
    return 0


def cmd_subagent_event(args: argparse.Namespace) -> int:
    """Execute `cmd_subagent_event`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return 0
    append_event(
        state,
        {
            "event": "subagent_event",
            "agent_name": args.agent_name,
            "status": args.status,
            "summary": args.summary,
            "step": state.get("current_step"),
        },
    )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Execute `cmd_check`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return 0
    # Session-scope the guard: if the active run was started by a different
    # Claude session (e.g. the background drip-runner) than the one whose Stop
    # hook is firing now, it is not ours to flag. Stay silent. Unstamped legacy
    # runs (owner_session=None) fall through to the original behavior.
    owner = state.get("owner_session")
    here = current_session()
    if owner is not None and here is not None and owner != here:
        return 0
    events = read_events(trace_path(state))
    missing = missing_steps(state, events)
    open_step = state.get("current_step")
    if missing or open_step:
        parts = []
        if open_step:
            parts.append(f"open step: {open_step}")
        if missing:
            parts.append(f"missing closed steps: {', '.join(missing)}")
        print(f"jd-to-ready trace incomplete for run {state['run_id']}; {'; '.join(parts)}", file=sys.stderr)
        return 2 if args.strict else 0
    print(f"jd-to-ready trace complete for run {state['run_id']}")
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    """Execute `cmd_finish`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return fail("No active jd-to-ready run; nothing to finish.")
    if state.get("current_step"):
        return fail(f"Cannot finish run; step {state['current_step']} is still open.")
    events = read_events(trace_path(state))
    missing = missing_steps(state, events)
    if missing:
        return fail(f"Cannot finish run; missing closed steps: {', '.join(missing)}")
    ok, gaps, error = parse_json_optional(args.gaps, [], "gaps")
    if not ok:
        return fail(error or "invalid gaps")
    if error := validate_array(gaps, "gaps"):
        return fail(error)
    ok, files_written, error = parse_json_optional(args.files_written, [], "files_written")
    if not ok:
        return fail(error or "invalid files_written")
    if error := validate_array(files_written, "files_written"):
        return fail(error)
    step_results = [event for event in events if event.get("event") == "step_end"]
    computed_status = compute_finish_status(step_results)
    if args.status and args.status != computed_status:
        return fail(f"Provided status {args.status!r} does not match computed status {computed_status!r}.")
    summary = {
        "timestamp": now_iso(),
        "run_id": state["run_id"],
        "run_type": state.get("run_type"),
        "company": state.get("company"),
        "role": state.get("role"),
        "role_folder": state.get("role_folder"),
        "trace_file": str(trace_path(state)),
        "steps_closed": closed_steps_from_state_and_events(state, events),
        "required_steps": state.get("required_steps", REQUIRED_STEPS),
        "status": computed_status,
        "gaps": gaps,
        "files_written": files_written,
        "steps": step_results,
    }
    append_event(
        state,
        {
            "event": "run_finish",
            "status": computed_status,
            "steps_closed": summary["steps_closed"],
            "required_steps": summary["required_steps"],
            "gaps": gaps,
            "files_written": files_written,
        },
    )
    with global_summary_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, sort_keys=True) + "\n")
    path = active_state_path()
    if path.exists():
        path.unlink()
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    """Execute `cmd_abort`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    state = load_state()
    if not state:
        return fail("No active jd-to-ready run; nothing to abort.")
    events = read_events(trace_path(state))
    ok, gaps, error = parse_json_optional(args.gaps, [], "gaps")
    if not ok:
        return fail(error or "invalid gaps")
    if error := validate_array(gaps, "gaps"):
        return fail(error)
    missing = missing_steps(state, events)
    closed_steps = closed_steps_from_state_and_events(state, events)
    abort_event = {
        "event": "run_abort",
        "status": "aborted",
        "reason": args.reason,
        "open_step": state.get("current_step"),
        "missing_steps": missing,
        "steps_closed": closed_steps,
        "gaps": gaps,
    }
    append_event(state, abort_event)
    summary = {
        "timestamp": now_iso(),
        "run_id": state["run_id"],
        "run_type": state.get("run_type"),
        "company": state.get("company"),
        "role": state.get("role"),
        "role_folder": state.get("role_folder"),
        "trace_file": str(trace_path(state)),
        "steps_closed": closed_steps,
        "required_steps": state.get("required_steps", REQUIRED_STEPS),
        "status": "aborted",
        "gaps": gaps,
        "files_written": [],
        "reason": args.reason,
        "missing_steps": missing,
        "open_step": state.get("current_step"),
    }
    with global_summary_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, sort_keys=True) + "\n")
    path = active_state_path()
    if path.exists():
        path.unlink()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Execute `build_parser`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    parser = argparse.ArgumentParser(description="Trace jd-to-ready orchestration steps.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start-run")
    p.add_argument("--run-id")
    p.add_argument("--company")
    p.add_argument("--role")
    p.add_argument("--role-folder")
    p.add_argument("--test-run", action="store_true")
    p.add_argument("--skill")
    # Fail closed on typos: an unknown run-type would silently inherit the
    # legacy 11-step contract and make the run unfinishable.
    p.add_argument("--run-type", default="jd-to-ready", choices=sorted(RUN_TYPES))
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("set-role-folder")
    p.add_argument("--company")
    p.add_argument("--role")
    p.add_argument("--role-folder", required=True)
    p.add_argument("--test-run", action="store_true")
    p.set_defaults(func=cmd_set_role_folder)

    p = sub.add_parser("begin")
    p.add_argument("--step", required=True)
    p.add_argument("--primitive", required=True)
    p.add_argument("--mode")
    p.add_argument("--prediction", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--sources", required=True)
    p.add_argument("--inputs-summary")
    p.add_argument("--contract-clauses",
                   help="JSON array of authoritative behavior contract clause IDs")
    p.set_defaults(func=cmd_begin)

    p = sub.add_parser("end")
    p.add_argument("--step", required=True)
    p.add_argument("--primitive", required=True)
    p.add_argument("--mode")
    p.add_argument("--status", choices=["ok", "partial", "failed", "skipped"], required=True)
    p.add_argument("--prediction-met", choices=["true", "false", "partial", "unknown"], required=True)
    p.add_argument("--produced")
    p.add_argument("--gaps")
    p.add_argument("--failure-pattern")
    p.add_argument("--tokens", required=True)
    p.add_argument("--clause-results",
                   help="JSON array of verifier results: {id,status,detail?}")
    p.set_defaults(func=cmd_end)

    p = sub.add_parser("tool-event")
    p.add_argument("--tool-name", required=True)
    p.add_argument("--status", default="completed")
    p.add_argument("--summary")
    p.set_defaults(func=cmd_tool_event)

    p = sub.add_parser("subagent-event")
    p.add_argument("--agent-name", default="subagent")
    p.add_argument("--status", default="completed")
    p.add_argument("--summary")
    p.set_defaults(func=cmd_subagent_event)

    p = sub.add_parser("check")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("finish-run")
    p.add_argument("--status", choices=["ok", "partial", "failed"])
    p.add_argument("--gaps")
    p.add_argument("--files-written")
    p.set_defaults(func=cmd_finish)

    p = sub.add_parser("abort-run")
    p.add_argument("--reason", required=True)
    p.add_argument("--gaps")
    p.set_defaults(func=cmd_abort)

    return parser


def main() -> int:
    """Run the command-line workflow; parse/user/provider failures terminate with the documented nonzero status."""
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
