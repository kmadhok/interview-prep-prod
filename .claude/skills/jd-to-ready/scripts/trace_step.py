#!/usr/bin/env python3
"""Trace helper for jd-to-ready runs.

The helper writes append-only JSONL events to a per-role trace when a role folder
is known, plus a small active-run state file for hooks. It is intentionally
forgiving: missing optional fields become null/empty values instead of causing
the orchestration run to fail.
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


LOG_DIR = Path.home() / ".claude" / "logs"
ACTIVE_STATE = LOG_DIR / "jd-to-ready-active.json"
GLOBAL_RUN_DIR = LOG_DIR / "jd-to-ready-runs"
GLOBAL_SUMMARY = LOG_DIR / "jd-to-ready.jsonl"
TRACE_NAME = ".jd-to-ready-trace.jsonl"
REQUIRED_STEPS = ["1", "2", "3", "4", "4b", "5", "6", "7"]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_json(value: str | None, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    GLOBAL_RUN_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any] | None:
    if not ACTIVE_STATE.exists():
        return None
    try:
        return json.loads(ACTIVE_STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    ACTIVE_STATE.write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")


def trace_path(state: dict[str, Any]) -> Path:
    role_folder = state.get("role_folder")
    if role_folder:
        return Path(role_folder) / TRACE_NAME
    return Path(state["fallback_trace"])


def append_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    ensure_dirs()
    event.setdefault("run_id", state["run_id"])
    event.setdefault("timestamp", now_iso())
    event.setdefault("event", "event")
    event.setdefault("role_folder", state.get("role_folder"))
    path = trace_path(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def normalize_step(step: str | int | None) -> str | None:
    if step is None:
        return None
    return str(step)


def cmd_start(args: argparse.Namespace) -> int:
    ensure_dirs()
    run_id = args.run_id or f"jdtr-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    state = {
        "run_id": run_id,
        "company": args.company,
        "role": args.role,
        "role_folder": args.role_folder,
        "started_at": now_iso(),
        "fallback_trace": str(GLOBAL_RUN_DIR / f"{run_id}.jsonl"),
        "required_steps": REQUIRED_STEPS,
    }
    save_state(state)
    append_event(state, {
        "event": "run_start",
        "company": args.company,
        "role": args.role,
        "required_steps": REQUIRED_STEPS,
        "source": "jd-to-ready",
    })
    print(run_id)
    return 0


def cmd_set_role_folder(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        state = {
            "run_id": args.run_id or f"jdtr-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
            "company": args.company,
            "role": args.role,
            "role_folder": None,
            "started_at": now_iso(),
            "fallback_trace": str(GLOBAL_RUN_DIR / f"late-{uuid.uuid4().hex[:8]}.jsonl"),
            "required_steps": REQUIRED_STEPS,
        }
    state["role_folder"] = args.role_folder
    if args.company:
        state["company"] = args.company
    if args.role:
        state["role"] = args.role
    save_state(state)
    append_event(state, {
        "event": "role_folder_set",
        "company": state.get("company"),
        "role": state.get("role"),
    })
    return 0


def cmd_begin(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        print("No active jd-to-ready run. Call start-run first.", file=sys.stderr)
        return 2
    step = normalize_step(args.step)
    append_event(state, {
        "event": "step_begin",
        "step": step,
        "primitive": args.primitive,
        "mode": args.mode,
        "prediction": args.prediction,
        "inputs_summary": parse_json(args.inputs_summary, args.inputs_summary),
        "status": "running",
    })
    return 0


def cmd_end(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        print("No active jd-to-ready run. Call start-run first.", file=sys.stderr)
        return 2
    step = normalize_step(args.step)
    append_event(state, {
        "event": "step_end",
        "step": step,
        "primitive": args.primitive,
        "mode": args.mode,
        "status": args.status,
        "prediction_met": args.prediction_met,
        "produced": parse_json(args.produced, []),
        "gaps": parse_json(args.gaps, []),
        "failure_pattern": args.failure_pattern,
        "tokens": parse_json(args.tokens, None),
    })
    return 0


def cmd_tool_event(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        return 0
    append_event(state, {
        "event": "tool_event",
        "tool_name": args.tool_name,
        "status": args.status,
        "summary": args.summary,
    })
    return 0


def cmd_subagent_event(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        return 0
    append_event(state, {
        "event": "subagent_event",
        "agent_name": args.agent_name,
        "status": args.status,
        "summary": args.summary,
    })
    return 0


def read_events(path: Path) -> list[dict[str, Any]]:
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


def step_status(events: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
    status: dict[str, dict[str, bool]] = {}
    for event in events:
        step = normalize_step(event.get("step"))
        if not step:
            continue
        status.setdefault(step, {"begin": False, "end": False})
        if event.get("event") == "step_begin":
            status[step]["begin"] = True
        if event.get("event") == "step_end":
            status[step]["end"] = True
    return status


def cmd_check(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        return 0
    events = read_events(trace_path(state))
    status = step_status(events)
    missing = [
        step for step in state.get("required_steps", REQUIRED_STEPS)
        if not status.get(str(step), {}).get("end")
    ]
    if missing:
        print(f"jd-to-ready trace incomplete for run {state['run_id']}; missing closed steps: {', '.join(missing)}", file=sys.stderr)
        return 2 if args.strict else 0
    print(f"jd-to-ready trace complete for run {state['run_id']}")
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    state = load_state()
    if not state:
        return 0
    events = read_events(trace_path(state))
    status = step_status(events)
    step_results = [event for event in events if event.get("event") == "step_end"]
    summary = {
        "timestamp": now_iso(),
        "run_id": state["run_id"],
        "company": state.get("company"),
        "role": state.get("role"),
        "role_folder": state.get("role_folder"),
        "trace_file": str(trace_path(state)),
        "steps_closed": sorted([step for step, flags in status.items() if flags.get("end")]),
        "required_steps": state.get("required_steps", REQUIRED_STEPS),
        "status": args.status,
        "gaps": parse_json(args.gaps, []),
        "files_written": parse_json(args.files_written, []),
        "steps": step_results,
    }
    ensure_dirs()
    with GLOBAL_SUMMARY.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, sort_keys=True) + "\n")
    append_event(state, {"event": "run_finish", "status": args.status})
    if ACTIVE_STATE.exists():
        ACTIVE_STATE.unlink()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trace jd-to-ready orchestration steps.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start-run")
    p.add_argument("--run-id")
    p.add_argument("--company")
    p.add_argument("--role")
    p.add_argument("--role-folder")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("set-role-folder")
    p.add_argument("--run-id")
    p.add_argument("--company")
    p.add_argument("--role")
    p.add_argument("--role-folder", required=True)
    p.set_defaults(func=cmd_set_role_folder)

    p = sub.add_parser("begin")
    p.add_argument("--step", required=True)
    p.add_argument("--primitive", required=True)
    p.add_argument("--mode")
    p.add_argument("--prediction", required=True)
    p.add_argument("--inputs-summary")
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
    p.add_argument("--tokens")
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
    p.add_argument("--status", choices=["ok", "partial", "failed"], required=True)
    p.add_argument("--gaps")
    p.add_argument("--files-written")
    p.set_defaults(func=cmd_finish)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
