"""Processed-ledger for the saved-jobs ingestion path. Pure + a thin CLI.

A LinkedIn saved-jobs list is a flat set with no per-job state (unlike the Gmail
`drip-queue/done/error` labels). Successful roles dedupe out naturally because
their LinkedIn job_id lands in Pipeline.md (see dedupe.py). This ledger covers
the gap: jobs we ATTEMPTED but did not file (errors, or deliberate skips) so the
runner does not re-scrape and re-attempt them every run.

Ledger file (JSON, committed in-repo so dedup state is durable across reboots):
    {"version": 1, "entries": {"<job_id>": {"status": "...", "ts": "...", "note": "..."}}}

status is one of: done | error | skipped (all terminal -> is_processed True).
Successful roles may also be recorded `done` for completeness, but Pipeline.md
remains the source of truth for "already filed".
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

TERMINAL = {"done", "error", "skipped"}


def load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"version": 1, "entries": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig", errors="ignore") or "{}")
    except json.JSONDecodeError:
        # A corrupt ledger must not silently drop dedup state; fail loud.
        raise SystemExit(f"ledger {path} is not valid JSON")
    data.setdefault("version", 1)
    data.setdefault("entries", {})
    return data


def is_processed(job_id: str, ledger: dict) -> bool:
    if not job_id:
        return False
    entry = ledger.get("entries", {}).get(str(job_id))
    return bool(entry) and entry.get("status") in TERMINAL


def mark(ledger: dict, job_id: str, status: str, note: str = "", ts: str = "") -> dict:
    if not job_id:
        raise ValueError("job_id required")
    if status not in TERMINAL:
        raise ValueError(f"status must be one of {sorted(TERMINAL)}, got {status!r}")
    ledger.setdefault("entries", {})[str(job_id)] = {"status": status, "ts": ts, "note": note}
    return ledger


def save(path: str, ledger: dict) -> None:
    # UTF-8 no BOM, trailing newline, stable key order -> clean git diffs.
    Path(path).write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="saved-jobs processed-ledger")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="is this job_id already processed?")
    c.add_argument("--job-id", required=True)
    c.add_argument("--ledger", required=True)

    m = sub.add_parser("mark", help="record a terminal outcome for a job_id")
    m.add_argument("--job-id", required=True)
    m.add_argument("--status", required=True, choices=sorted(TERMINAL))
    m.add_argument("--note", default="")
    m.add_argument("--ts", default="")
    m.add_argument("--ledger", required=True)

    args = p.parse_args(argv)
    ledger = load(args.ledger)

    if args.cmd == "check":
        done = is_processed(args.job_id, ledger)
        print("PROCESSED" if done else "NEW")
        return 0 if done else 1

    if args.cmd == "mark":
        mark(ledger, args.job_id, args.status, note=args.note, ts=args.ts)
        save(args.ledger, ledger)
        print(f"marked {args.job_id} {args.status}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
